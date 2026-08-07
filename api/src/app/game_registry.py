# src/app/game_registry.py
"""
Process-level, in-memory home for every currently-active GameState
(brief §3.3 layer 2 — "this is what actually drives live play; it is
not a database concern"). Keyed by game_id only, never by connection or
session — that's what makes disconnect/reconnect free: a player
dropping an HTTP connection (or, later, a socket) and coming back just
means another request/connection with the same game_id, which finds
the exact same GameState still sitting here, mutated in place by
whatever happened while they were gone. Nothing about presence or
connection lifetime is tracked at this layer — PlayerState.connected
exists for that and stays unused until the socket layer is built.

Concurrency: one asyncio.Lock per game_id, held for the duration of any
request that mutates that game's state, so two concurrent actions on
the same game can't interleave and corrupt it. Dict access itself
(`.setdefault`, `[]`) needs no separate meta-lock — plain dict
operations are atomic between asyncio's scheduling points (no `await`
occurs mid-operation).
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator

from fastapi import Depends, HTTPException, Path, status

from src.app.engine.state import GameState


class GameNotFoundError(Exception):
    def __init__(self, game_id: str):
        self.game_id = game_id
        super().__init__(f"No active game: {game_id}")


class GameRegistry:
    def __init__(self) -> None:
        self._games: dict[str, GameState] = {}
        self._locks: dict[str, asyncio.Lock] = {}

    def register(self, state: GameState) -> None:
        self._games[state.game_id] = state
        self._locks.setdefault(state.game_id, asyncio.Lock())

    def get(self, game_id: str) -> GameState:
        try:
            return self._games[game_id]
        except KeyError:
            raise GameNotFoundError(game_id) from None

    def lock_for(self, game_id: str) -> asyncio.Lock:
        # get-or-create: a lock may need to exist even before register()
        # has run for this id (e.g. a request racing game creation, or
        # a bogus/typo game_id) — actual existence is checked inside the
        # lock, in get(). Known MVP simplification: a bogus game_id
        # permanently allocates an empty Lock here that's never cleaned
        # up. Acceptable for the "small trusted group" scope (brief §4)
        # — not something to harden against yet, flagged rather than
        # silently ignored.
        return self._locks.setdefault(game_id, asyncio.Lock())


_registry = GameRegistry()


def get_registry() -> GameRegistry:
    return _registry


def get_game_state(
    game_id: str = Path(...), registry: GameRegistry = Depends(get_registry)
) -> GameState:
    """
    Unlocked, read-only access — for GET routes. A concurrent mutation
    could in principle be interleaved mid-request; for a read-only
    status/history view on a small trusted group (brief §4), that
    staleness window is an accepted MVP trade-off, not an oversight.
    Every route that calls an engine function (i.e. mutates state) uses
    get_locked_game_state below instead, never this one.

    NOTE: this 404 path is currently unreachable in practice — every
    route also depends on auth.get_current_player, which runs first and
    returns 403 for a nonexistent game_id (no seated-player row exists
    for it either). That's an intentional decision, not a bug — see
    auth.py's docstring. This 404 still exists for any future route
    that might reasonably skip get_current_player (e.g. a public,
    unauthenticated game-existence check, if one is ever wanted).
    """
    try:
        return registry.get(game_id)
    except GameNotFoundError:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND, detail="Game not found"
        ) from None


async def get_locked_game_state(
    game_id: str = Path(...), registry: GameRegistry = Depends(get_registry)
) -> AsyncGenerator[GameState, None]:
    """
    Locked access. The lock is held for the entire request and released
    automatically on teardown (yield-dependency, same pattern as
    get_session) — so two concurrent actions against the same game
    queue up instead of interleaving.
    """
    lock = registry.lock_for(game_id)
    async with lock:
        try:
            state = registry.get(game_id)
        except GameNotFoundError:
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, detail="Game not found"
            ) from None
        yield state
