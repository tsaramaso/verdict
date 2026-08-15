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
from src.app.engine.events import Event as EngineEvent
from src.app.engine.events import EventType
from src.app.engine.state import Phase
from src.app.models.db import Event as DBEvent
from src.app.models.enums import GameStatus


class EventOut(BaseModel):
    event_id: str
    type: EventType
    sequence: int
    actor: str | None
    public_fields: dict
    scoped_fields: dict

    @classmethod
    def from_engine_event(cls, event: EngineEvent, viewer: str | None) -> EventOut:
        # payload_for() is the ONE place scoping is enforced for outbound
        # delivery (events.py) — every route response goes through this,
        # never event.to_dict() (that's the DB-persistence shape, which
        # deliberately carries full scoped_fields regardless of viewer).
        return cls(**event.payload_for(viewer))

    @classmethod
    def from_db_event(cls, row: DBEvent, viewer: str) -> EventOut:
        """
        Same scoping principle as from_engine_event, applied to a
        persisted row instead of the live dataclass. This is exactly
        why models/db.py:Event.scoped_fields keeps the full
        {visible_to, value} envelope on disk rather than something
        already flattened at write time — filtering happens here,
        against the spec-shaped structure, every time it's read.
        """
        visible_scoped = {
            k: v["value"]
            for k, v in row.scoped_fields.items()
            if viewer in v.get("visible_to", [])
        }
        return cls(
            event_id=row.event_id,
            type=row.type,
            sequence=row.sequence,
            actor=row.actor_uuid,
            public_fields=row.public_fields,
            scoped_fields=visible_scoped,
        )


class EventLogOut(BaseModel):
    game_id: str
    events: list[EventOut]


class ActionResult(BaseModel):
    """What every mutating route returns: the resulting phase, and only
    the events THIS caller is entitled to see from what just happened."""

    phase: Phase
    events: list[EventOut]


class GameCreateRequest(BaseModel):
    player_ids: list[str]
    rules_config: dict | None = None  # Optional rules override, None defaults to BASE_RULES


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


class GameSummaryOut(BaseModel):
    """One row of GET /games (list games the caller is seated in) — reads
    the thin DB lookup row (Game + GamePlayer), not the in-memory
    registry, so this works even for games not currently loaded in this
    process (finished games, or — once replay exists — games from before
    a restart)."""

    game_id: str
    status: GameStatus
    turn_direction: TurnDirection
    current_round: int
    seat_order: int
    created_at: str
    started_at: str | None
    ended_at: str | None


class GameListOut(BaseModel):
    games: list[GameSummaryOut]