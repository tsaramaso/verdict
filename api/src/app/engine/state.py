# src/app/engine/state.py
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum, auto

from src.app.engine.cards import Card
from src.app.engine.constants import (
    BASE_RULES,
    ELIGIBLE_THRESHOLD,
    DrawSource,
    Power,
    Rank,
    TurnDirection,
)


class Phase(StrEnum):
    """
    Player-facing wait-states only — i.e. the subset of game_flow.mermaid
    nodes where the engine is actually waiting on a player decision.
    Purely computed/transient nodes (RankCheck, PowerFlowExit, CW_Resolve,
    MW_Resolve, DW_Resolve) aren't represented as states here; they're
    just intermediate steps inside a single command handler.

    Values are auto() per the enum convention (comparisons are all
    `state.phase is Phase.X`, never against a literal) — the mermaid
    node each one corresponds to is kept as a comment for traceability,
    not as the enum's actual value.
    """

    TURN_START = auto()  # mermaid: TurnStart
    DRAWING = auto()  # mermaid: Drawing
    AWAITING_ACTION = auto()  # mermaid: CardDrawn
    AWAITING_SPELL_INVOCATION = auto()  # mermaid: SpellInvocationDecision
    AWAITING_SPELL_SWAP_DECISION = auto()  # mermaid: SpellSwapDecision_Decree
    AWAITING_QUICK_DISCARD = auto()  # mermaid: QuickDiscardWindow
    AWAITING_CALL_WINDOW = auto()  # mermaid: TrialCallWindow
    AWAITING_MATCH_WINDOW = auto()  # mermaid: MatchWindow
    AWAITING_DUEL_WINDOW = auto()  # mermaid: DuelWindow
    AWAITING_FINAL_PLEA_WINDOW = auto()  # mermaid: FinalPleaWindow
    ROUND_OVER = auto()  # mermaid: post-ScoresUpdated, pre-next-RoundStarted
    GAME_OVER = auto()  # mermaid: GameOver


@dataclass
class PlayerState:
    player_id: str
    # Fixed-length, index = slot number. None means quick-discarded away
    # (slot stays but is permanently empty — hand "shrinking" means
    # fewer non-None entries, not a shorter list). rules.md §5.4.
    hand: list[Card | None] = field(
        default_factory=lambda: [None] * BASE_RULES.hand_size
    )
    # Slots of THIS player's hand that have been Spied on by someone, at
    # any point this round — persists in the UI per the resolved open
    # item (rules.md §12 item 2). Purely a display concern; doesn't
    # affect legality of anything.
    spied_slots: set[int] = field(default_factory=set)
    connected: bool = True

    @property
    def hand_size(self) -> int:
        return sum(1 for c in self.hand if c is not None)

    @property
    def true_sum(self) -> int:
        return sum(c.value for c in self.hand if c is not None)

    @property
    def is_eligible(self) -> bool:
        return self.true_sum <= ELIGIBLE_THRESHOLD


@dataclass
class PendingPower:
    """Scratch state for an in-progress power resolution."""

    power: Power
    # Decree only: the slot it revealed, so the later swap decision
    # knows what it's choosing to swap.
    target_owner: str | None = None
    target_index: int | None = None


@dataclass
class TrialState:
    """
    All bookkeeping scoped to a single Trial (game_flow.mermaid's
    TrialCallWindow through FinalPleaWindow). Reset fresh each Trial.
    """

    first_window_callers: list[str] = field(default_factory=list)
    passed_first: set[str] = field(default_factory=set)
    cross_callers: list[str] = field(default_factory=list)
    passed_cross: set[str] = field(default_factory=set)
    perjury_removed: set[str] = field(default_factory=set)
    # Truly-eligible Testimony-givers surviving the perjury check (first-window
    # survivors + cross callers who are actually eligible). Determines
    # whether the Duel Window even appears — rules.md §6.4.
    truly_eligible: list[str] = field(default_factory=list)
    challenged: set[str] = field(default_factory=set)
    passed_challenge: set[str] = field(default_factory=set)
    duel_occurred: bool = False
    duel_winners: list[str] = field(default_factory=list)
    plea_taken: set[str] = field(default_factory=set)
    plea_declined: set[str] = field(default_factory=set)


@dataclass
class GameState:
    game_id: str
    player_order: list[str]
    turn_direction: TurnDirection
    dealer_index: int = 0
    round_number: int = 0
    scores: dict[str, int] = field(default_factory=dict)
    players: dict[str, PlayerState] = field(default_factory=dict)
    deck: list[Card] = field(default_factory=list)
    discard_pile: list[Card] = field(default_factory=list)
    current_turn_index: int = 0
    phase: Phase = Phase.TURN_START
    is_last_turn: bool = False
    game_over: bool = False

    # Turn-scoped scratch state
    drawn_card: Card | None = None
    draw_source: DrawSource | None = None
    pending_power: PendingPower | None = None
    quick_discard_rank: Rank | None = None
    hand_emptied_this_window: bool = False

    trial: TrialState = field(default_factory=TrialState)

    round_id: str | None = None
    turn_id: str | None = None
    sequence: int = 0  # next sequence number to assign

    @property
    def current_player(self) -> str:
        return self.player_order[self.current_turn_index]

    def next_sequence(self) -> int:
        self.sequence += 1
        return self.sequence

    def player_after_perjury_and_testimony_removed(self) -> list[str]:
        """Players still undetermined going into the Final Plea Window:
        never gave Testimony (first or cross), not removed for Perjury."""
        determined = set(self.trial.first_window_callers) | set(
            self.trial.cross_callers
        )
        return [p for p in self.player_order if p not in determined]
