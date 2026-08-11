"""
DB/API-layer-only enums — anything the engine already defines a canonical
version of (Rank, Suit, TurnDirection, RoundEndReason, DrawSource,
ActionChoice, SpellDecision, SwapDecision, TestimonyWindow, ScoreBucket,
EventType) lives in src.app.engine.constants / src.app.engine.events and
is imported from there, never redefined here. Redefining any of those a
second time is exactly the drift the project is trying to rule out — one
enum value changing in the engine without its DB-layer twin changing to
match, silently, is a real bug class, and StrEnum + auto() offers zero
protection against a SECOND independent definition being wrong relative
to the first.

GameStatus has no engine equivalent — it's a lookup-table-only concept
(brief §3.3 layer 3), so it's genuinely only defined here.
"""

from enum import StrEnum, auto


class GameStatus(StrEnum):
    """
    Coarse status for the thin `games` lookup row (brief §3.3, layer 3).
    Deliberately NOT tracking round/turn/window-level state here — that's
    the in-memory live-state layer's job. This is just enough to list and
    filter games.
    """

    WAITING_FOR_PLAYERS = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    ABANDONED = auto()
    CANCELLED = auto()
