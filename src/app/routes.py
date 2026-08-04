# src/app/routes.py
"""
The routes themselves — auth -> state lookup -> engine call -> persist
-> response, for every action in src.app.engine.engine. This is
milestone 0 item 3 (handoff doc §0): a game playable entirely through
Swagger. Deliberately does NOT include:

  - GET /games/{id}/events — the events-inspection endpoint is its own
    listed item (handoff doc §0 item 5), explicitly ordered after this
    one. Building it here would jump the stated order.
  - GET /games (list games a user belongs to) — no response schema
    for it exists in schemas.py yet; not invented here.
  - Any write to Game.status / GamePlayer.current_score / final_rank
    in response to ScoresUpdated/GameEnded/RoundEnded events. This is
    the same boundary event_log.py's own docstring already draws
    ("a related but separate concern, not handled here") — kept
    consistent rather than quietly doing it here instead. Every route
    below only ever writes the Event log itself, never the thin lookup
    row's derived fields.

Every mutating route follows the exact same five-step shape:
  1. auth       — get_current_player (401/403 handled by the dependency)
  2. state      — get_locked_game_state (404 handled by the dependency,
                  lock held for the whole request)
  3. engine call — the one function in engine.py this route exists for
  4. persist    — persist_events(session, events), the ONE place an
                  in-memory Event becomes a durable row (event_log.py)
  5. response   — ActionResult, scoped to the ACTING player only
                  (never a bystander's view of their own action)

Step 3's IllegalAction -> HTTP translation is centralized in `_call`
below rather than repeated as a try/except in every route body.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.app.auth import get_current_player, get_current_user
from src.app.engine import engine
from src.app.engine.errors import IllegalAction
from src.app.engine.events import Event as EngineEvent
from src.app.engine.state import GameState
from src.app.event_log import persist_events
from src.app.game_registry import GameRegistry, get_game_state, get_locked_game_state, get_registry
from src.app.models.db import Game, GamePlayer, User
from src.app.models.enums import GameStatus
from src.app.schemas import (
    ActionRequest,
    ActionResult,
    DecreeSwapRequest,
    DrawRequest,
    EventOut,
    GameCreateRequest,
    GameCreateResult,
    GameStatusOut,
    InvokePowerRequest,
    QuickDiscardRequest,
)
from src.db.session import get_session

router = APIRouter(prefix="/games", tags=["games"])


def _call(fn, *args, **kwargs) -> list[EngineEvent]:
    """
    Every engine function's only failure mode is IllegalAction (see
    engine.py's module docstring: validate-then-mutate, nothing partial
    on failure). One error shape in the engine maps to one HTTP status
    here — 409, since every case is "the request is well-formed but
    conflicts with the game's current state" (wrong phase, wrong turn,
    already-responded, targeting an empty slot, ...), never a 400-shaped
    "the request itself is malformed" (Pydantic/enum validation already
    catches that earlier, before this is ever called). Deliberately NOT
    split into finer-grained statuses yet — that would mean parsing
    IllegalAction's message text to distinguish cases, which is more
    fragile than the single-status simplification it would replace.
    """
    try:
        return fn(*args, **kwargs)
    except IllegalAction as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e


def _result(state: GameState, events: list[EngineEvent], viewer: str) -> ActionResult:
    return ActionResult(
        phase=state.phase,
        events=[EventOut.from_engine_event(e, viewer) for e in events],
    )


# ---------------------------------------------------------------------
# Game creation
# ---------------------------------------------------------------------


@router.post("", response_model=GameCreateResult, status_code=status.HTTP_201_CREATED)
def create_game(
    request: GameCreateRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    registry: GameRegistry = Depends(get_registry),
) -> GameCreateResult:
    if user.uuid not in request.player_ids:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            detail="The creating user must be one of player_ids",
        )
    if len(set(request.player_ids)) != len(request.player_ids):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="Duplicate player_ids")

    # engine.new_game only checks COUNT (MIN_PLAYERS <= n <= MAX_PLAYERS)
    # — it has no concept of a User row at all (framework-agnostic, see
    # engine.py's module docstring). IDENTITY validation belongs here,
    # at the actual DB-aware boundary — otherwise a fabricated player_id
    # would sail through the engine and only fail later as a raw
    # IntegrityError on GamePlayer's FK, instead of a clean 400 now.
    found_users = session.exec(
        select(User).where(User.uuid.in_(request.player_ids))
    ).all()
    found_uuids = {u.uuid for u in found_users}
    missing = set(request.player_ids) - found_uuids
    if missing:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"Unknown player_ids: {sorted(missing)}"
        )
    inactive = sorted(u.uuid for u in found_users if not u.is_active)
    if inactive:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail=f"Inactive player_ids: {inactive}"
        )

    game_id = str(uuid4())
    # engine.new_game's return shape (GameState, list[Event]) is the one
    # exception to every other engine function's plain list[Event] —
    # it's the only function that BUILDS a GameState rather than
    # mutating one passed in, since no state exists yet to pass in.
    # Unpacked directly here rather than teaching _call a second return
    # shape just for this one caller.
    try:
        state, events = engine.new_game(
            game_id, request.player_ids, request.turn_direction, request.rules_config
        )
    except IllegalAction as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e

    # WAITING_FOR_PLAYERS (models/enums.py) is unused by this creation
    # flow on purpose — every player is supplied up front in
    # GameCreateRequest, so there is no separate "lobby, waiting for
    # more players to join" phase to represent. Retained in the enum
    # for a possible future creation path, not wired to anything yet.
    game_row = Game(
        id=game_id,
        status=GameStatus.IN_PROGRESS,
        turn_direction=request.turn_direction,
        current_round=state.round_number,
        started_at=datetime.now(timezone.utc),
    )
    session.add(game_row)
    session.add_all(
        GamePlayer(game_id=game_id, user_uuid=pid, seat_order=seat)
        for seat, pid in enumerate(request.player_ids)
    )
    # Deliberately NOT session.commit()'d here — persist_events() below
    # commits once, atomically, over this Game row + these GamePlayer
    # rows + every Event row together. A Game row that exists with no
    # matching GameStarted event (or vice versa) would be exactly the
    # partial-write failure mode event_log.py's docstring already rules
    # out for event batches; extending that same guarantee to cover the
    # lookup rows created alongside them costs nothing extra here.
    persist_events(session, events)

    registry.register(state)
    return GameCreateResult(
        game_id=game_id,
        phase=state.phase,
        events=[EventOut.from_engine_event(e, user.uuid) for e in events],
    )


# ---------------------------------------------------------------------
# Live status (read-only, unlocked — see game_registry.py's docstring)
# ---------------------------------------------------------------------


@router.get("/{game_id}/status", response_model=GameStatusOut)
def get_status(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_game_state),
) -> GameStatusOut:
    return GameStatusOut(
        game_id=state.game_id,
        phase=state.phase,
        current_player=state.current_player,
        round_number=state.round_number,
        scores=dict(state.scores),
        is_last_turn=state.is_last_turn,
        game_over=state.game_over,
    )


# ---------------------------------------------------------------------
# Turn — draw & action (rules.md §4-5)
# ---------------------------------------------------------------------


@router.post("/{game_id}/draw", response_model=ActionResult)
def draw(
    request: DrawRequest,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.draw_card, state, player_id, request.source)
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/action", response_model=ActionResult)
def take_action(
    request: ActionRequest,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.take_action, state, player_id, request.choice, request.slot_index)
    persist_events(session, events)
    return _result(state, events, player_id)


# ---------------------------------------------------------------------
# Power cards (rules.md §7)
# ---------------------------------------------------------------------


@router.post("/{game_id}/power/decline", response_model=ActionResult)
def decline_power(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.decline_power, state, player_id)
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/power/invoke", response_model=ActionResult)
def invoke_power(
    request: InvokePowerRequest,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(
        engine.invoke_power,
        state,
        player_id,
        request.own_slot_index,
        request.target_owner,
        request.target_index,
    )
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/power/decree-swap", response_model=ActionResult)
def decree_swap(
    request: DecreeSwapRequest,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(
        engine.decree_swap_decision, state, player_id, request.swap, request.own_slot_index
    )
    persist_events(session, events)
    return _result(state, events, player_id)


# ---------------------------------------------------------------------
# Quick-discard (rules.md §5.4)
# ---------------------------------------------------------------------


@router.post("/{game_id}/quick-discard", response_model=ActionResult)
def quick_discard(
    request: QuickDiscardRequest,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.quick_discard, state, player_id, request.slot_index)
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/quick-discard/close", response_model=ActionResult)
def close_quick_discard(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    """
    System-triggered in engine.py (no player_id parameter — closing the
    window isn't itself a Testimony/Perjury-bearing act). Still gated
    behind get_current_player rather than get_current_user: the ability
    to advance a game's phase should require being seated in it, even
    though the engine call itself doesn't attribute the action to
    anyone. See handoff doc / rules.md open items — this window's
    closing trigger (any seated player, on demand) is a UI/orchestration
    choice, not a rules requirement; rules.md never specifies a timer
    or an explicit close condition for this particular window.
    """
    events = _call(engine.close_quick_discard_window, state)
    persist_events(session, events)
    return _result(state, events, player_id)


# ---------------------------------------------------------------------
# The Trial (rules.md §6)
# ---------------------------------------------------------------------


@router.post("/{game_id}/trial/testify-first", response_model=ActionResult)
def testify_first(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.give_testimony_first, state, player_id)
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-call", response_model=ActionResult)
def pass_call(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_call_window, state, player_id)
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/testify-cross", response_model=ActionResult)
def testify_cross(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.give_testimony_cross, state, player_id)
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-match", response_model=ActionResult)
def pass_match(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_match_window, state, player_id)
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/challenge", response_model=ActionResult)
def challenge(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.give_challenge, state, player_id)
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-duel", response_model=ActionResult)
def pass_duel(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_duel_window, state, player_id)
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/plea", response_model=ActionResult)
def plea(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.take_plea, state, player_id)
    persist_events(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-plea", response_model=ActionResult)
def pass_plea(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_final_plea_window, state, player_id)
    persist_events(session, events)
    return _result(state, events, player_id)
