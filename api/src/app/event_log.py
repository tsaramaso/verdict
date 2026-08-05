# src/app/event_log.py
"""
Event-log persistence — the ONE place an engine.events.Event (in-memory
dataclass, framework-agnostic) becomes a models.db.Event row (the
durable, DB-backed source of truth — brief §3.3 layer 1). No other
translation between these two shapes should exist anywhere else in the
codebase; if a field gets added to one side, this file is where the
other side needs to be taught about it.

Deliberately scoped to ONLY the append-only log itself. Updating the
thin lookup/cache tables (Game.status, GamePlayer.current_score — brief
§3.3 layer 3) in response to specific event types (ScoresUpdated,
GameEnded, ...) is a related but separate concern, not handled here —
see the handoff doc for where that lands next.
"""

from __future__ import annotations

from sqlmodel import Session

from src.app.engine.events import Event as EngineEvent
from src.app.models.db import Event as DBEvent


def _to_db_event(event: EngineEvent) -> DBEvent:
    return DBEvent(
        event_id=event.event_id,
        game_id=event.game_id,
        round_id=event.round_id,
        turn_id=event.turn_id,
        sequence=event.sequence,
        timestamp=event.timestamp,
        type=event.type,
        actor_uuid=event.actor,
        public_fields=event.public_fields,
        # Keep the full {visible_to, value} envelope shape on the way in —
        # same reasoning as models/db.py:Event's own docstring: visibility
        # filtering should happen against a spec-shaped structure, not
        # something already lossily flattened before it ever reaches disk.
        scoped_fields={k: v.to_dict() for k, v in event.scoped_fields.items()},
    )


def persist_events(session: Session, events: list[EngineEvent]) -> list[DBEvent]:
    """
    Writes a whole batch from a single engine call atomically. One
    engine action (e.g. new_game) can return several Events — GameStarted
    + RoundStarted + one InitialGlance per player — and the log's
    sequence-continuity guarantee (models/db.py's UniqueConstraint on
    (game_id, sequence)) only means anything if a batch lands together
    or not at all; a partial write would leave a silently-broken log.
    """
    if not events:
        return []
    rows = [_to_db_event(e) for e in events]
    session.add_all(rows)
    try:
        session.commit()
    except Exception:
        # Leaving the session in SQLAlchemy's post-failure "aborted
        # transaction" state would break every subsequent operation on
        # it — and routes hold one session for their whole request
        # (get_session), so this isn't hypothetical. Roll back, then
        # let the caller's exception handling decide what the client
        # sees (e.g. a 409/500), same "fail loud and stop cleanly"
        # posture as everywhere else in this project.
        session.rollback()
        raise
    for row in rows:
        session.refresh(row)
    return rows