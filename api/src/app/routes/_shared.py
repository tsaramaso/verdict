# src/app/routes/_shared.py
"""
Helpers shared across every routes sub-module. Nothing here is a route.

_call     — IllegalAction -> HTTP 409, centralised so no route body
            needs its own try/except for the engine's one error type.

_persist  — persist_events() + sync_lookup_tables() in one call, so
            every route writes the log and syncs lookup rows together;
            neither step can be done without the other.

_result   — builds the ActionResult every mutating route returns,
            scoped to the acting player.
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session

from src.app.engine.errors import IllegalAction
from src.app.engine.events import Event as EngineEvent
from src.app.engine.state import GameState
from src.app.event_log import persist_events
from src.app.lookup_sync import sync_lookup_tables
from src.app.models.db import Event as DBEvent
from src.app.schemas import ActionResult, EventOut


def _call(fn, *args, **kwargs) -> list[EngineEvent]:
    """
    Every engine function's only failure mode is IllegalAction (see
    engine.py's module docstring: validate-then-mutate, nothing partial
    on failure). One error shape in the engine maps to one HTTP status
    here — 409, since every case is "the request is well-formed but
    conflicts with the game's current state" (wrong phase, wrong turn,
    already-responded, targeting an empty slot, ...), never a 400-shaped
    "the request itself is malformed" (Pydantic/enum validation already
    catches that earlier, before this is ever called).
    """
    try:
        return fn(*args, **kwargs)
    except IllegalAction as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e


def _persist(session: Session, events: list[EngineEvent]) -> list[DBEvent]:
    """
    The one call every mutating route makes after invoking the engine:
    write the Event log (event_log.py, source of truth), then sync the
    thin Game/GamePlayer lookup rows off that same batch (lookup_sync.py).
    A single wrapper so there's exactly one place a future third
    post-persist step would get added.
    """
    rows = persist_events(session, events)
    sync_lookup_tables(session, events)
    return rows


def _result(state: GameState, events: list[EngineEvent], viewer: str) -> ActionResult:
    return ActionResult(
        phase=state.phase,
        events=[EventOut.from_engine_event(e, viewer) for e in events],
    )