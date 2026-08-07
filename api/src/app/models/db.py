"""
Table models. Three of the brief's three state-architecture layers are
represented here, deliberately unevenly:

  1. Event log (durable, DB, source of truth)      -> Event, in full.
  2. Live game state (in-memory, per active game)   -> NOT here. No table.
     Built via replay of Event rows when a game starts / server restarts,
     held in process memory, updated incrementally as events arrive.
  3. Thin lookup/cache table (DB, minimal)          -> Game, GamePlayer.
     Enough to list/filter games and show history without replaying
     anything. If either ever disagrees with the Event log, the log wins.

User follows the reference project's auth pattern verbatim (UUID PK,
soft-delete via is_active) per project_bootstrap_brief.md §3.2.

ASSUMPTION FLAGGED (not silently resolved): events_and_logging.md's event
envelope marks `turn_id` as nullable ("null for round/game-level events")
but doesn't explicitly say the same for `round_id`. GameStarted/GameEnded
fire before any round exists / after the last one ends, so round_id can't
always be populated for them. Modeled `round_id` as nullable here to make
that representable — flagging this as a real gap in the spec worth
confirming, per START_HERE.md's "stop and ask" ground rule, not something
to bury silently.
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from src.app.engine.constants import TurnDirection
from src.app.engine.events import EventType
from src.app.models.enums import GameStatus


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """UUID-as-bearer-credential, no password, CLI-managed. Mirrors the
    reference project's User model shape exactly (brief §3.2)."""

    __tablename__ = "users"

    uuid: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str | None = Field(default=None, max_length=120)
    is_active: bool = Field(default=True, nullable=False)
    created_at: datetime = Field(default_factory=_utcnow, nullable=False)

    game_memberships: list["GamePlayer"] = Relationship(back_populates="user")


class Game(SQLModel, table=True):
    """
    Thin lookup row per game (brief §3.3, layer 3) — status, turn
    direction, timestamps. Explicitly NOT a mirror of hands/slots/rounds;
    rebuildable from the Event log at any time.
    """

    __tablename__ = "games"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    status: GameStatus = Field(default=GameStatus.WAITING_FOR_PLAYERS, nullable=False)
    turn_direction: TurnDirection = Field(nullable=False)

    # Denormalized, cheap-to-read progress markers — cache only, the Event
    # log (RoundStarted/RoundEnded) is authoritative if these ever drift.
    current_round: int = Field(default=0, nullable=False)

    created_at: datetime = Field(default_factory=_utcnow, nullable=False)
    started_at: datetime | None = Field(default=None)
    ended_at: datetime | None = Field(default=None)

    players: list["GamePlayer"] = Relationship(
        back_populates="game",
        sa_relationship_kwargs={"order_by": "GamePlayer.seat_order"},
    )
    events: list["Event"] = Relationship(back_populates="game")


class GamePlayer(SQLModel, table=True):
    """
    Link table between Game and User, carrying the extra fields a plain
    many-to-many can't: seat order (rules.md §3 — fixed turn order) and a
    cached running score (rules.md §9/§10 — cumulative across rounds).

    `current_score` is a cache for cheap listing/history reads, same as
    the Game row it lives next to — ScoresUpdated events remain the
    source of truth if this and the log ever disagree.
    """

    __tablename__ = "game_players"
    __table_args__ = (
        UniqueConstraint("game_id", "user_uuid", name="uq_game_player_user"),
        UniqueConstraint("game_id", "seat_order", name="uq_game_player_seat"),
    )

    id: int | None = Field(default=None, primary_key=True)
    game_id: str = Field(foreign_key="games.id", nullable=False, index=True)
    user_uuid: str = Field(foreign_key="users.uuid", nullable=False, index=True)

    seat_order: int = Field(nullable=False)  # 0-indexed, fixed turn order
    current_score: int = Field(default=0, nullable=False)
    final_rank: int | None = Field(
        default=None
    )  # standard competition ranking, set at GameEnded

    joined_at: datetime = Field(default_factory=_utcnow, nullable=False)

    game: Game = Relationship(back_populates="players")
    user: User = Relationship(back_populates="game_memberships")


class Event(SQLModel, table=True):
    """
    The append-only event log — the single source of truth (brief §3.3
    layer 1, events_and_logging.md §1). Never mutated, only appended to.

    `public_fields` / `scoped_fields` are stored as JSONB rather than
    modeled relationally: their shape varies per EventType (see
    events_and_logging.md §3's per-type column), and the whole point of
    this layer is that it stays a faithful, replayable record of exactly
    what events_and_logging.md specifies — not a second, drifting
    interpretation of it in relational form.

    `scoped_fields` keeps its full envelope shape as documented
    (`{field_name: {visible_to: [...], value: ...}}`) so visibility
    filtering happens in application code against a spec-shaped
    structure, not against something already lossily flattened.
    """

    __tablename__ = "events"
    __table_args__ = (
        UniqueConstraint("game_id", "sequence", name="uq_event_game_sequence"),
    )

    event_id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    game_id: str = Field(foreign_key="games.id", nullable=False, index=True)

    # Nullable per the flagged assumption above (GameStarted/GameEnded are
    # not scoped to a round).
    round_id: str | None = Field(default=None, index=True)
    turn_id: str | None = Field(default=None)

    sequence: int = Field(nullable=False, index=True)  # strict, per-game increasing
    timestamp: datetime = Field(default_factory=_utcnow, nullable=False)

    type: EventType = Field(nullable=False, index=True)
    actor_uuid: str | None = Field(default=None, foreign_key="users.uuid")

    public_fields: dict = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )
    scoped_fields: dict = Field(
        default_factory=dict, sa_column=Column(JSONB, nullable=False)
    )

    game: Game = Relationship(back_populates="events")
