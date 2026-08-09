# src/app/engine/engine.py
"""
The rules engine. One public method per legal player action (plus a
few system-triggered ones like closing a window). Every method:
  1. validates the command is legal for the current Phase/actor
     (raises IllegalAction otherwise, no state mutated, no event
     emitted) — this is the enforcement of "nothing reachable in code
     that isn't reachable in game_flow.mermaid",
  2. builds one or more Event objects matching events_and_logging.md,
  3. mutates `state` directly to reflect them (there is deliberately no
     separate "reducer" indirection — for this MVP, live mutation and
     the event construction happen in the same place, by the same
     method, so they cannot drift apart. Replay recomputation, if
     needed later for server-restart recovery, reruns these exact same
     methods against a fresh GameState in the recorded sequence — see
     README "Architecture notes" for the case this doesn't yet cover),
  4. returns the list of Events for the caller (event_log.py) to
     persist and broadcast.

This module never touches the database or a socket directly.

Enum convention (see constants.py): every parameter that represents a
closed vocabulary (source, choice, rank, decision, window, ...) is typed
as its actual enum, not `str`. Callers at the real boundary (an HTTP
request body, a socket message) are responsible for turning a raw wire
string into the right enum member — via `SomeEnum(raw_value)`, which
raises ValueError on anything invalid — before ever calling into this
module. That keeps every check in here enum-to-enum, never
member-to-literal, and means a typo in a caller's string surfaces as an
immediate ValueError at the boundary rather than a silent no-op or a
runtime AttributeError three calls deep in engine logic.
"""

from __future__ import annotations

import functools
import inspect
from uuid import uuid4

from src.app.engine import scoring
from src.app.engine.cards import build_deck
from src.app.engine.constants import (
    BASE_RULES,
    POWER_RANKS,
    ActionChoice,
    DrawSource,
    Power,
    RoundEndReason,
    Rules,
    ScoreBucket,
    SpellDecision,
    SwapDecision,
    TestimonyWindow,
    TrialResolution,
    TurnDirection,
    power_for_rank,
)
from src.app.engine.errors import IllegalAction
from src.app.engine.events import Event, EventType, ScopedField
from src.app.engine.state import GameState, PendingPower, Phase, PlayerState, TrialState


def require_phase(phase: Phase):
    """
    Declarative replacement for hand-writing `_require_phase(state,
    Phase.X, player_id)` as the first line of every function. Binds the
    decorated function's actual parameters BY NAME (not position), so
    it works whether the function takes `player_id` positionally, as a
    keyword, or not at all — e.g. `close_quick_discard_window(state)`
    is system-triggered and has no `player_id` parameter; `bound.arguments.get`
    just returns None for it, matching the old explicit `actor=None` call.
    Same runtime check as before, same IllegalAction, nothing mutated
    and no event built if it fails — just spelled at the def line
    instead of buried as the function's first statement.
    """

    def decorator(fn):
        sig = inspect.signature(fn)

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            state = bound.arguments["state"]
            player_id = bound.arguments.get("player_id")
            _require_phase(state, phase, player_id)
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def new_game(
    game_id: str,
    player_ids: list[str],
    rules_config: dict,
    turn_direction: TurnDirection = TurnDirection.CLOCKWISE,
) -> tuple[GameState, list[Event]]:
    # Convert rules_config dict to Rules object, or use BASE_RULES if empty
    if rules_config:
        try:
            rules = Rules(**rules_config)
        except Exception as e:
            raise IllegalAction(f"Invalid rules_config: {e}")
    else:
        rules = BASE_RULES

    if not (rules.min_players <= len(player_ids) <= rules.max_players):
        raise IllegalAction(
            f"Player count must be {rules.min_players}-{rules.max_players}, got {len(player_ids)}"
        )
    state = GameState(
        game_id=game_id,
        player_order=list(player_ids),
        turn_direction=turn_direction,
        rules=rules,
    )
    for p in player_ids:
        state.scores[p] = 0
        state.players[p] = PlayerState(player_id=p)

    # __post_init__ runs after __init__, initializing player hands based on rules
    state.__post_init__()

    ev = Event(
        type=EventType.GAME_STARTED,
        game_id=game_id,
        round_id=None,  # game-level, no round exists yet
        sequence=state.next_sequence(),
        actor=None,
        public_fields={
            "player_order": list(player_ids),
            "turn_direction": turn_direction,
            "rules_config": rules_config,
        },
    )
    events = [ev]
    events += _start_round(state)
    return state, events


def _start_round(state: GameState) -> list[Event]:
    state.round_number += 1
    state.round_id = str(uuid4())
    state.turn_id = None
    seed = uuid4().hex
    state.deck = build_deck(seed, state.rules)
    state.discard_pile = []
    state.current_turn_index = state.dealer_index
    state.is_last_turn = False
    state.trial = TrialState()
    state.phase = Phase.TURN_START

    events = [
        Event(
            type=EventType.ROUND_STARTED,
            game_id=state.game_id,
            round_id=state.round_id,
            sequence=state.next_sequence(),
            actor=None,
            public_fields={
                "round_number": state.round_number,
                "dealer": state.player_order[state.dealer_index],
            },
            scoped_fields={"shuffle_seed": ScopedField(visible_to=[], value=seed)},
        )
    ]

    # Deal: deterministic round-robin from the shuffled deck, starting
    # at the dealer, rules.hand_size cards each. Deliberately NOT its own
    # event type — fully reconstructible from RoundStarted's seed plus
    # this fixed dealing order, per events_and_logging.md §1.5.
    for _ in range(state.rules.hand_size):
        for i in range(len(state.player_order)):
            idx = (state.dealer_index + i) % len(state.player_order)
            player_id = state.player_order[idx]
            player = state.players[player_id]
            slot = next(s for s in range(state.rules.hand_size) if player.hand[s] is None)
            player.hand[slot] = state.deck.pop()

    # Initial Glance: each player privately views their first two
    # dealt slots (rules.md §3 / §4). Slot indices 0 and 1 by
    # convention — the two slots dealt to them first.
    for player_id in state.player_order:
        player = state.players[player_id]
        for slot in range(state.rules.nb_of_starting_draw):
            card = player.hand[slot]
            assert card is not None
            card.known_by.add(player_id)
            events.append(
                Event(
                    type=EventType.INITIAL_GLANCE,
                    game_id=state.game_id,
                    round_id=state.round_id,
                    sequence=state.next_sequence(),
                    actor=player_id,
                    public_fields={"player": player_id, "slot_index": slot},
                    scoped_fields={
                        "true_value": ScopedField(
                            visible_to=[player_id], value=card.to_public_dict()
                        )
                    },
                )
            )

    return events


# ---------------------------------------------------------------------
# Turn — Draw & Action  (rules.md §4-5, game_flow.mermaid TurnStart..)
# ---------------------------------------------------------------------


@require_phase(Phase.TURN_START)
def draw_card(state: GameState, player_id: str, source: DrawSource) -> list[Event]:
    if source is DrawSource.DISCARD_PILE and not state.discard_pile:
        raise IllegalAction("Discard pile is empty")
    if source is DrawSource.DECK and not state.deck:
        raise IllegalAction(
            "Deck is empty"
        )  # should never happen given is_last_turn gating

    if source is DrawSource.DECK:
        card = state.deck.pop()
        if not state.deck:
            # This was the last card in the deck — rules.md §5.5.
            state.is_last_turn = True
    else:
        card = state.discard_pile.pop()

    card.known_by.add(player_id)
    state.drawn_card = card
    state.draw_source = source
    state.turn_id = str(uuid4())
    state.phase = Phase.AWAITING_ACTION

    return [
        Event(
            type=EventType.CARD_DRAWN,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
            public_fields={"player": player_id, "source": source},
            scoped_fields={
                "true_card": ScopedField(
                    visible_to=[player_id], value=card.to_public_dict()
                )
            },
        )
    ]


@require_phase(Phase.AWAITING_ACTION)
def take_action(
    state: GameState,
    player_id: str,
    choice: ActionChoice,
    slot_index: int | None = None,
) -> list[Event]:
    if (
        choice is ActionChoice.PASS_BACK
        and state.draw_source is not DrawSource.DISCARD_PILE
    ):
        raise IllegalAction(
            "pass_back is only legal after drawing from the discard pile"
        )
    if choice is ActionChoice.SWAP and (
        slot_index is None or not (0 <= slot_index < state.rules.hand_size)
    ):
        raise IllegalAction("swap requires a valid slot_index")

    assert state.drawn_card is not None
    drawn = state.drawn_card
    public_fields: dict = {"player": player_id, "choice": choice}
    affected_slots: list[dict] = []

    if choice is ActionChoice.DISCARD_IMMEDIATE:
        state.discard_pile.append(drawn)
        public_fields["discarded_card"] = drawn.to_public_dict()
    elif choice is ActionChoice.SWAP:
        player = state.players[player_id]
        outgoing = player.hand[slot_index]
        assert outgoing is not None
        state.discard_pile.append(outgoing)
        player.hand[slot_index] = drawn
        drawn.known_by.add(player_id)
        public_fields["discarded_card"] = outgoing.to_public_dict()
        affected_slots = [{"owner": player_id, "index": slot_index}]
    else:  # PASS_BACK
        state.discard_pile.append(drawn)

    if affected_slots:
        public_fields["affected_slots"] = affected_slots

    state.drawn_card = None
    state.draw_source = None

    events = [
        Event(
            type=EventType.ACTION_TAKEN,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
            public_fields=public_fields,
        )
    ]

    # RankCheck — only DISCARD_IMMEDIATE can ever trigger a power
    # (rules.md §7), and only for POWER_RANKS.
    top_rank = state.discard_pile[-1].rank
    if choice is ActionChoice.DISCARD_IMMEDIATE and top_rank in POWER_RANKS:
        state.phase = Phase.AWAITING_SPELL_INVOCATION
    else:
        state.phase = Phase.AWAITING_QUICK_DISCARD
        state.quick_discard_rank = top_rank if state.discard_pile else None
        state.hand_emptied_this_window = False

    return events


# ---------------------------------------------------------------------
# Power cards (rules.md §7)
# ---------------------------------------------------------------------


@require_phase(Phase.AWAITING_SPELL_INVOCATION)
def decline_power(state: GameState, player_id: str) -> list[Event]:
    rank = state.discard_pile[-1].rank
    events = [
        Event(
            type=EventType.SPELL_INVOCATION_DECISION,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
            public_fields={
                "player": player_id,
                "rank": rank,
                "decision": SpellDecision.DECLINED,
            },
        )
    ]
    state.phase = Phase.AWAITING_QUICK_DISCARD
    state.quick_discard_rank = rank
    state.hand_emptied_this_window = False
    return events


@require_phase(Phase.AWAITING_SPELL_INVOCATION)
def invoke_power(
    state: GameState,
    player_id: str,
    own_slot_index: int | None = None,
    target_owner: str | None = None,
    target_index: int | None = None,
) -> list[Event]:
    rank = state.discard_pile[-1].rank
    power = power_for_rank(rank)
    if power is None:
        raise IllegalAction("Top discard has no power")

    events = [
        Event(
            type=EventType.SPELL_INVOCATION_DECISION,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
            public_fields={
                "player": player_id,
                "power": power,
                "decision": SpellDecision.INVOKED,
            },
        )
    ]

    if power is Power.GLANCE:
        if own_slot_index is None or not (0 <= own_slot_index < state.rules.hand_size):
            raise IllegalAction("Glance requires own_slot_index")
        card = state.players[player_id].hand[own_slot_index]
        if card is None:
            raise IllegalAction("That slot is empty")
        card.known_by.add(player_id)
        events.append(
            _spell_revealed(
                state, player_id, power, player_id, own_slot_index, [player_id]
            )
        )
        state.phase = Phase.AWAITING_QUICK_DISCARD
        state.quick_discard_rank = rank
        state.hand_emptied_this_window = False

    elif power is Power.SPY:
        _validate_target(state, target_owner, target_index)
        card = state.players[target_owner].hand[target_index]  # type: ignore[index]
        if card is None:
            raise IllegalAction("That slot is empty")
        card.known_by.add(player_id)
        state.players[target_owner].spied_slots.add(target_index)  # type: ignore[arg-type]
        events.append(
            _spell_revealed(
                state, player_id, power, target_owner, target_index, [player_id]
            )
        )
        state.phase = Phase.AWAITING_QUICK_DISCARD
        state.quick_discard_rank = rank
        state.hand_emptied_this_window = False

    elif power is Power.DECREE:
        _validate_target(state, target_owner, target_index)
        card = state.players[target_owner].hand[target_index]  # type: ignore[index]
        if card is None:
            raise IllegalAction("That slot is empty")
        card.known_by.add(player_id)
        events.append(
            _spell_revealed(
                state, player_id, power, target_owner, target_index, [player_id]
            )
        )
        state.pending_power = PendingPower(
            power=power, target_owner=target_owner, target_index=target_index
        )
        state.phase = Phase.AWAITING_SPELL_SWAP_DECISION

    elif power is Power.SMUGGLE:
        if own_slot_index is None or not (0 <= own_slot_index < state.rules.hand_size):
            raise IllegalAction("Smuggle requires own_slot_index")
        _validate_target(state, target_owner, target_index)
        _swap_slots(state, player_id, own_slot_index, target_owner, target_index)  # type: ignore[arg-type]
        events.append(
            Event(
                type=EventType.SPELL_SWAP_DECISION,
                game_id=state.game_id,
                round_id=state.round_id,
                turn_id=state.turn_id,
                sequence=state.next_sequence(),
                actor=player_id,
                public_fields={
                    "power": power,
                    "decision": SwapDecision.SWAP,
                    "from_slot": {"owner": target_owner, "index": target_index},
                    "to_slot": {"owner": player_id, "index": own_slot_index},
                },
            )
        )
        state.phase = Phase.AWAITING_QUICK_DISCARD
        state.quick_discard_rank = rank
        state.hand_emptied_this_window = False

    return events


@require_phase(Phase.AWAITING_SPELL_SWAP_DECISION)
def decree_swap_decision(
    state: GameState, player_id: str, swap: bool, own_slot_index: int | None = None
) -> list[Event]:
    pending = state.pending_power
    assert pending is not None
    if swap:
        if own_slot_index is None or not (0 <= own_slot_index < state.rules.hand_size):
            raise IllegalAction("swap requires own_slot_index")
        _swap_slots(
            state, player_id, own_slot_index, pending.target_owner, pending.target_index  # type: ignore[arg-type]
        )
        public_fields = {
            "power": pending.power,
            "decision": SwapDecision.SWAP,
            "from_slot": {"owner": pending.target_owner, "index": pending.target_index},
            "to_slot": {"owner": player_id, "index": own_slot_index},
        }
    else:
        public_fields = {"power": pending.power, "decision": SwapDecision.NONE}

    events = [
        Event(
            type=EventType.SPELL_SWAP_DECISION,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
            public_fields=public_fields,
        )
    ]
    rank = state.discard_pile[-1].rank
    state.pending_power = None
    state.phase = Phase.AWAITING_QUICK_DISCARD
    state.quick_discard_rank = rank
    state.hand_emptied_this_window = False
    return events


def _spell_revealed(
    state: GameState,
    actor: str,
    power: Power,
    target_owner: str,
    target_index: int,
    visible_to: list[str],
) -> Event:
    card = state.players[target_owner].hand[target_index]
    assert card is not None
    return Event(
        type=EventType.SPELL_REVEALED,
        game_id=state.game_id,
        round_id=state.round_id,
        turn_id=state.turn_id,
        sequence=state.next_sequence(),
        actor=actor,
        public_fields={
            "power": power,
            "target_slot": {"owner": target_owner, "index": target_index},
        },
        scoped_fields={
            "revealed_value": ScopedField(
                visible_to=visible_to, value=card.to_public_dict()
            )
        },
    )


def _validate_target(
    state: GameState, target_owner: str | None, target_index: int | None
) -> None:
    if target_owner is None or target_index is None:
        raise IllegalAction("target_owner and target_index are required")
    if target_owner not in state.players:
        raise IllegalAction("unknown target_owner")
    if not (0 <= target_index < state.rules.hand_size):
        raise IllegalAction("target_index out of range")


def _swap_slots(
    state: GameState, a_owner: str, a_index: int, b_owner: str, b_index: int
) -> None:
    a_hand = state.players[a_owner].hand
    b_hand = state.players[b_owner].hand
    if a_hand[a_index] is None or b_hand[b_index] is None:
        raise IllegalAction("Cannot swap with an empty slot")
    a_hand[a_index], b_hand[b_index] = b_hand[b_index], a_hand[a_index]


# ---------------------------------------------------------------------
# Quick-Discard window (rules.md §5.4)
# ---------------------------------------------------------------------


@require_phase(Phase.AWAITING_QUICK_DISCARD)
def quick_discard(state: GameState, player_id: str, slot_index: int) -> list[Event]:
    player = state.players[player_id]
    if not (0 <= slot_index < state.rules.hand_size):
        raise IllegalAction("slot_index out of range")
    card = player.hand[slot_index]
    if card is None:
        raise IllegalAction("That slot is already empty")
    if card.rank is not state.quick_discard_rank:
        raise IllegalAction(
            f"Card rank does not match required rank {state.quick_discard_rank}"
        )

    player.hand[slot_index] = None
    state.discard_pile.append(card)

    events = [
        Event(
            type=EventType.QUICK_DISCARD_PLAYED,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
            public_fields={"player": player_id, "card": card.to_public_dict()},
        )
    ]

    if player.hand_size == 0:
        state.hand_emptied_this_window = True
        events.append(
            Event(
                type=EventType.HAND_EMPTIED,
                game_id=state.game_id,
                round_id=state.round_id,
                turn_id=state.turn_id,
                sequence=state.next_sequence(),
                actor=player_id,
                public_fields={"player": player_id},
            )
        )

    return events


@require_phase(Phase.AWAITING_QUICK_DISCARD)
def close_quick_discard_window(state: GameState) -> list[Event]:
    """
    No dedicated event type — a pure phase transition (rules.md and
    events_and_logging.md agree there's nothing to log for the window
    closing itself). Called by the app layer once its window-close
    condition is met (see README — this is a UI/orchestration timing
    decision, not a rules decision).
    """
    if state.hand_emptied_this_window:
        return _end_round_empty_hand(state)
    state.trial = TrialState()
    state.phase = Phase.AWAITING_CALL_WINDOW
    return []


# ---------------------------------------------------------------------
# The Trial (rules.md §6)
# ---------------------------------------------------------------------


@require_phase(Phase.AWAITING_CALL_WINDOW)
def give_testimony_first(state: GameState, player_id: str) -> list[Event]:
    _require_not_yet_responded(
        state, player_id, state.trial.first_window_callers, state.trial.passed_first
    )
    state.trial.first_window_callers.append(player_id)
    ev = _testimony_event(state, player_id, TestimonyWindow.FIRST)
    events = [ev]
    events += _maybe_close_call_window(state)
    return events


@require_phase(Phase.AWAITING_CALL_WINDOW)
def pass_call_window(state: GameState, player_id: str) -> list[Event]:
    _require_not_yet_responded(
        state, player_id, state.trial.first_window_callers, state.trial.passed_first
    )
    state.trial.passed_first.add(player_id)
    events = [
        Event(
            type=EventType.TESTIMONY_WINDOW_PASSED,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
            public_fields={"window": TestimonyWindow.FIRST},
        )
    ]
    events += _maybe_close_call_window(state)
    return events


def _maybe_close_call_window(state: GameState) -> list[Event]:
    responded = set(state.trial.first_window_callers) | state.trial.passed_first
    if responded != set(state.player_order):
        return []
    state.phase = Phase.AWAITING_MATCH_WINDOW
    # Same class of stall as the Final Plea Window below: if literally
    # everyone testified in the Call Window, the Match Window's
    # population (players who passed_first) is already empty — nothing
    # will ever fire the player action that would otherwise close it.
    return _maybe_close_match_window(state)


@require_phase(Phase.AWAITING_MATCH_WINDOW)
def give_testimony_cross(state: GameState, player_id: str) -> list[Event]:
    _require_eligible_for_match_window(state, player_id)
    state.trial.cross_callers.append(player_id)
    ev = _testimony_event(state, player_id, TestimonyWindow.CROSS)
    events = [ev]
    events += _maybe_close_match_window(state)
    return events


@require_phase(Phase.AWAITING_MATCH_WINDOW)
def pass_match_window(state: GameState, player_id: str) -> list[Event]:
    _require_eligible_for_match_window(state, player_id)
    state.trial.passed_cross.add(player_id)
    events = [
        Event(
            type=EventType.TESTIMONY_WINDOW_PASSED,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
            public_fields={"window": TestimonyWindow.CROSS},
        )
    ]
    events += _maybe_close_match_window(state)
    return events


def _require_eligible_for_match_window(state: GameState, player_id: str) -> None:
    if player_id not in state.trial.passed_first:
        raise IllegalAction("Only players who passed the Call Window act here")
    if player_id in state.trial.cross_callers or player_id in state.trial.passed_cross:
        raise IllegalAction("Already responded in the Match Window")


def _testimony_event(
    state: GameState, player_id: str, window: TestimonyWindow
) -> Event:
    eligible = state.players[player_id].is_eligible(state.rules.eligible_threshold)
    return Event(
        type=EventType.TESTIMONY_GIVEN,
        game_id=state.game_id,
        round_id=state.round_id,
        turn_id=state.turn_id,
        sequence=state.next_sequence(),
        actor=player_id,
        public_fields={"window": window},
        scoped_fields={"true_eligibility": ScopedField(visible_to=[], value=eligible)},
    )


def _maybe_close_match_window(state: GameState) -> list[Event]:
    needed = state.trial.passed_first
    responded = set(state.trial.cross_callers) | state.trial.passed_cross
    if responded != needed:
        return []
    total_testimony = len(state.trial.first_window_callers) + len(
        state.trial.cross_callers
    )
    if total_testimony == 0:
        if state.is_last_turn:
            return _end_round_forced_no_testimony(state)
        return _advance_to_next_player(state)
    return _resolve_perjury_check(state)


def _resolve_perjury_check(state: GameState) -> list[Event]:
    results = []
    truly_eligible: list[str] = []
    for player_id in state.trial.first_window_callers:
        eligible = state.players[player_id].is_eligible(state.rules.eligible_threshold)
        results.append({"player": player_id, "perjury": not eligible})
        if eligible:
            truly_eligible.append(player_id)
        else:
            state.trial.perjury_removed.add(player_id)
    for player_id in state.trial.cross_callers:
        if state.players[player_id].is_eligible(state.rules.eligible_threshold):
            truly_eligible.append(player_id)
    state.trial.truly_eligible = truly_eligible

    events = [
        Event(
            type=EventType.PERJURY_CHECK_RESOLVED,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=None,
            public_fields={"results": results},
        )
    ]

    if len(truly_eligible) >= 2:
        state.phase = Phase.AWAITING_DUEL_WINDOW
        return events
    return events + _enter_final_plea_window(state)


def _surviving_testifiers(state: GameState) -> set[str]:
    return (set(state.trial.first_window_callers) - state.trial.perjury_removed) | set(
        state.trial.cross_callers
    )


@require_phase(Phase.AWAITING_DUEL_WINDOW)
def give_challenge(state: GameState, player_id: str) -> list[Event]:
    _require_surviving_testifier_undecided(state, player_id)
    state.trial.challenged.add(player_id)
    events = [
        Event(
            type=EventType.CHALLENGE_GIVEN,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
        )
    ]
    events += _maybe_close_duel_window(state)
    return events


@require_phase(Phase.AWAITING_DUEL_WINDOW)
def pass_duel_window(state: GameState, player_id: str) -> list[Event]:
    _require_surviving_testifier_undecided(state, player_id)
    state.trial.passed_challenge.add(player_id)
    events = [
        Event(
            type=EventType.CHALLENGE_WINDOW_PASSED,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
        )
    ]
    events += _maybe_close_duel_window(state)
    return events


def _require_surviving_testifier_undecided(state: GameState, player_id: str) -> None:
    if player_id not in _surviving_testifiers(state):
        raise IllegalAction("Only surviving Testimony-givers act in the Duel Window")
    if player_id in state.trial.challenged or player_id in state.trial.passed_challenge:
        raise IllegalAction("Already responded in the Duel Window")


def _maybe_close_duel_window(state: GameState) -> list[Event]:
    needed = _surviving_testifiers(state)
    responded = state.trial.challenged | state.trial.passed_challenge
    if responded != needed:
        return []

    truly_eligible = state.trial.truly_eligible
    if state.trial.challenged:
        sums = {p: state.players[p].true_sum for p in truly_eligible}
        min_sum = min(sums.values())
        winners = [p for p, s in sums.items() if s == min_sum]
        state.trial.duel_occurred = True
        state.trial.duel_winners = winners
        public_fields = {
            "resolution": TrialResolution.DUEL,
            "participants": truly_eligible,
            "true_sums": sums,
            "winners": winners,
        }
    else:
        state.trial.duel_occurred = False
        state.trial.duel_winners = list(truly_eligible)
        public_fields = {
            "resolution": TrialResolution.PLAIN_AGREEMENT,
            "participants": truly_eligible,
            "winners": list(truly_eligible),
        }

    events = [
        Event(
            type=EventType.DUEL_RESOLVED,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=None,
            public_fields=public_fields,
        )
    ]
    return events + _enter_final_plea_window(state)


def _enter_final_plea_window(state: GameState) -> list[Event]:
    state.phase = Phase.AWAITING_FINAL_PLEA_WINDOW
    if not state.player_after_perjury_and_testimony_removed():
        # Nobody is eligible to act here — e.g. every player gave
        # Testimony (first or cross) this Trial. Nothing to wait for;
        # resolve scoring immediately rather than stalling forever
        # waiting for a player action that can never come.
        return _resolve_trial_scoring(state)
    return []


@require_phase(Phase.AWAITING_FINAL_PLEA_WINDOW)
def take_plea(state: GameState, player_id: str) -> list[Event]:
    _require_undetermined_for_final_plea(state, player_id)
    state.trial.plea_taken.add(player_id)
    events = [
        Event(
            type=EventType.PLEA_TAKEN,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
        )
    ]
    events += _maybe_close_final_plea_window(state)
    return events


@require_phase(Phase.AWAITING_FINAL_PLEA_WINDOW)
def pass_final_plea_window(state: GameState, player_id: str) -> list[Event]:
    _require_undetermined_for_final_plea(state, player_id)
    state.trial.plea_declined.add(player_id)
    events = [
        Event(
            type=EventType.PLEA_WINDOW_PASSED,
            game_id=state.game_id,
            round_id=state.round_id,
            turn_id=state.turn_id,
            sequence=state.next_sequence(),
            actor=player_id,
        )
    ]
    events += _maybe_close_final_plea_window(state)
    return events


def _require_undetermined_for_final_plea(state: GameState, player_id: str) -> None:
    if player_id not in state.player_after_perjury_and_testimony_removed():
        raise IllegalAction("Not eligible for the Final Plea Window")
    if player_id in state.trial.plea_taken or player_id in state.trial.plea_declined:
        raise IllegalAction("Already responded at the Final Plea Window")


def _maybe_close_final_plea_window(state: GameState) -> list[Event]:
    needed = set(state.player_after_perjury_and_testimony_removed())
    responded = state.trial.plea_taken | state.trial.plea_declined
    if responded != needed:
        return []
    return _resolve_trial_scoring(state)


# ---------------------------------------------------------------------
# Round-ending special paths (rules.md §5.4, §6.8)
# ---------------------------------------------------------------------


def _end_round_empty_hand(state: GameState) -> list[Event]:
    trigger = next(p for p in state.player_order if state.players[p].hand_size == 0)
    events = [
        Event(
            type=EventType.ROUND_ENDED,
            game_id=state.game_id,
            round_id=state.round_id,
            sequence=state.next_sequence(),
            actor=None,
            public_fields={"end_reason": RoundEndReason.EMPTY_HAND},
        )
    ]
    events += _resolve_scoring(state, scoring.compute_bystander_scores(state, trigger))
    return events


def _end_round_forced_no_testimony(state: GameState) -> list[Event]:
    events = [
        Event(
            type=EventType.ROUND_ENDED,
            game_id=state.game_id,
            round_id=state.round_id,
            sequence=state.next_sequence(),
            actor=None,
            public_fields={"end_reason": RoundEndReason.FORCED_END},
        )
    ]
    events += _resolve_scoring(state, scoring.compute_bystander_scores(state))
    return events


def _resolve_trial_scoring(state: GameState) -> list[Event]:
    """
    The normal (non-Empty-Hand, non-Forced-End) round-ending path: a
    Trial actually ran to completion. events_and_logging.md §3.1 lists
    RoundEnded(Trial) as one of the three end-reason variants, alongside
    EmptyHand/ForcedEnd — this is the one place it needs to fire, since
    a Trial has no other single closing event of its own to attach it to.
    """
    events = [
        Event(
            type=EventType.ROUND_ENDED,
            game_id=state.game_id,
            round_id=state.round_id,
            sequence=state.next_sequence(),
            actor=None,
            public_fields={"end_reason": RoundEndReason.TRIAL},
        )
    ]
    events += _resolve_scoring(state, scoring.compute_trial_scores(state))
    return events


def _advance_to_next_player(state: GameState) -> list[Event]:
    state.current_turn_index = (state.current_turn_index + 1) % len(state.player_order)
    state.trial = TrialState()
    state.turn_id = None
    state.phase = Phase.TURN_START
    return []


# ---------------------------------------------------------------------
# Scoring, Renaissance, round/game lifecycle (rules.md §6.7, §9, §10)
# ---------------------------------------------------------------------


def _resolve_scoring(
    state: GameState, raw_results: list[tuple[str, ScoreBucket, int]]
) -> list[Event]:
    results_public = []
    for player_id, bucket, points in raw_results:
        results_public.append(
            {
                "player": player_id,
                "bucket": bucket,
                "points_added": points,
                "new_total": state.scores[player_id] + points,
            }
        )
    events: list[Event] = [
        Event(
            type=EventType.SCORES_UPDATED,
            game_id=state.game_id,
            round_id=state.round_id,
            sequence=state.next_sequence(),
            actor=None,
            public_fields={"results": results_public},
        )
    ]

    for player_id, bucket, points in raw_results:
        old_score = state.scores[player_id]
        new_total = old_score + points
        final_score = new_total
        if (
            bucket.renaissance_eligible
            and points > 0
            and new_total in state.rules.renaissance_thresholds
        ):
            final_score = state.rules.renaissance_thresholds[new_total]
            events.append(
                Event(
                    type=EventType.RENAISSANCE_TRIGGERED,
                    game_id=state.game_id,
                    round_id=state.round_id,
                    sequence=state.next_sequence(),
                    actor=player_id,
                    public_fields={
                        "player": player_id,
                        "old_score": new_total,
                        "new_score": final_score,
                    },
                )
            )
        state.scores[player_id] = final_score

    state.phase = Phase.ROUND_OVER

    if any(score >= state.rules.game_over_score for score in state.scores.values()):
        events += _end_game(state)
    else:
        state.dealer_index = (state.dealer_index + 1) % len(state.player_order)
        for player in state.players.values():
            player.hand = [None] * state.rules.hand_size
            player.spied_slots = set()
        events += _start_round(state)

    return events


def _end_game(state: GameState) -> list[Event]:
    state.game_over = True
    state.phase = Phase.GAME_OVER
    ranked = sorted(state.player_order, key=lambda p: state.scores[p])
    return [
        Event(
            type=EventType.GAME_ENDED,
            game_id=state.game_id,
            round_id=state.round_id,
            sequence=state.next_sequence(),
            actor=None,
            public_fields={
                "final_scores": dict(state.scores),
                "final_ranks": ranked,  # ascending score, GABO is low-score-wins
            },
        )
    ]


# ---------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------


def _require_phase(state: GameState, phase: Phase, actor: str | None) -> None:
    if state.phase is not phase:
        raise IllegalAction(f"Illegal in phase {state.phase}, expected {phase}")
    if actor is not None and phase in (
        Phase.TURN_START,
        Phase.AWAITING_ACTION,
        Phase.AWAITING_SPELL_INVOCATION,
        Phase.AWAITING_SPELL_SWAP_DECISION,
    ):
        if actor != state.current_player:
            raise IllegalAction("Not this player's turn")


def _require_not_yet_responded(
    state: GameState, player_id: str, called: list[str], passed: set[str]
) -> None:
    if player_id in called or player_id in passed:
        raise IllegalAction("Already responded in this window")