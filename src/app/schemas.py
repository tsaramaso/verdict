# src/app/schemas.py
"""
Request/response Pydantic models for the HTTP layer. Deliberately kept
separate from src.app.engine.events.Event and src.app.engine.state — the
engine package stays framework-agnostic (see engine/engine.py's module
docstring), these ARE the translation at the actual API boundary the
earlier "isn't Pydantic serializable by default" conversation was about.

Every field representing a closed vocabulary is typed as the real engine
enum (DrawSource, ActionChoice, ...), never `str` — Pydantic validates
against the real allowed values and FastAPI documents them for real in
Swagger, per the enum convention (handoff doc §3): raw-string validation
happens exactly once, here, at the one true boundary.
"""

from __future__ import annotations

from pydantic import BaseModel

from src.app.engine.constants import ActionChoice, DrawSource, TurnDirection
from src.app.engine.events import Event as EngineEvent, EventType
from src.app.engine.state import Phase


class EventOut(BaseModel):
    event_id: str
    type: EventType
    sequence: int
    actor: str | None
    public_fields: dict
    scoped_fields: dict

    @classmethod
    def from_engine_event(cls, event: EngineEvent, viewer: str | None) -> "EventOut":
        # payload_for() is the ONE place scoping is enforced for outbound
        # delivery (events.py) — every route response goes through this,
        # never event.to_dict() (that's the DB-persistence shape, which
        # deliberately carries full scoped_fields regardless of viewer).
        return cls(**event.payload_for(viewer))


class ActionResult(BaseModel):
    """What every mutating route returns: the resulting phase, and only
    the events THIS caller is entitled to see from what just happened."""

    phase: Phase
    events: list[EventOut]


class GameCreateRequest(BaseModel):
    player_ids: list[str]
    turn_direction: TurnDirection
    rules_config: dict = {}


class GameCreateResult(ActionResult):
    game_id: str


class DrawRequest(BaseModel):
    source: DrawSource


class ActionRequest(BaseModel):
    choice: ActionChoice
    slot_index: int | None = None


class InvokePowerRequest(BaseModel):
    own_slot_index: int | None = None
    target_owner: str | None = None
    target_index: int | None = None


class DecreeSwapRequest(BaseModel):
    swap: bool
    own_slot_index: int | None = None


class QuickDiscardRequest(BaseModel):
    slot_index: int


class GameStatusOut(BaseModel):
    """Minimal live-status read, from the in-memory registry — NOT the DB
    lookup row (that's GET /games/{id}/events's neighbor, still pending,
    see handoff doc §0 item 5). Only meaningful while the game is live in
    this process — no replay yet, see handoff doc §6.2."""

    game_id: str
    phase: Phase
    current_player: str
    round_number: int
    scores: dict[str, int]
    is_last_turn: bool
    game_over: bool