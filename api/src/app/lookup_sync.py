# src/app/lookup_sync.py
"""
event_log.py turns an engine.events.Event into a durable models.db.Event
row -- the append-only log itself (brief §3.3 layer 1). This module is
its sibling: it reads that same batch of events and updates the thin
lookup/cache rows (brief §3.3 layer 3) that event_log.py's own docstring
explicitly deferred -- "a related but separate concern, not handled
here". This is where it lands:

  - Game.status        -> COMPLETED, off GameEnded.
  - Game.ended_at       -> GameEnded's event timestamp.
  - Game.current_round  -> RoundStarted's round_number.
  - GamePlayer.current_score -> ScoresUpdated's new_total, then
    overridden by RenaissanceTriggered's new_score for that player if
    one follows in the same batch (engine.py:_resolve_scoring always
    emits ScoresUpdated before any RenaissanceTriggered for the round,
    so processing the batch in order is sufficient).
  - GamePlayer.final_rank -> derived from GameEnded's final_scores /
    final_ranks, see _standard_competition_ranks below.

Game.status -> ABANDONED has no corresponding event anywhere in the
engine (nothing currently models a game being abandoned mid-play), so
there is deliberately no branch for it here -- not an oversight.

Deliberately tolerant of its own failure. By the time sync_lookup_tables
runs, persist_events() has already committed the authoritative Event
log for this batch -- that write is what actually matters, and it's
done. If updating these lookup rows fails for any reason, the correct
behavior is to roll back *only* this update, log it, and let the
request succeed anyway: the log stays complete and correct, and these
caches are (by construction, per models/db.py's own docstrings) always
rebuildable from it later. Silently failing an otherwise-successful
game action over a cache-table write would be strictly worse than a
briefly-stale cache.
"""

from __future__ import annotations

import sys

from sqlmodel import Session, select

from src.app.engine.events import Event as EngineEvent, EventType
from src.app.models.db import Game, GamePlayer
from src.app.models.enums import GameStatus


def _standard_competition_ranks(final_scores: dict, final_ranks: list) -> dict[str, int]:
    """
    engine.py:_end_game's `final_ranks` is just player_order sorted
    ascending by score -- it doesn't itself express ties (GABO is
    low-score-wins, so ascending = best-first). GamePlayer.final_rank's
    own docstring promises "standard competition ranking" (1224: tied
    scores share a rank, the next distinct score's rank skips ahead by
    the number tied), not "position in this list", so ties are
    re-derived here from final_scores rather than taken as final_ranks'
    plain index.
    """
    ranks: dict[str, int] = {}
    prev_score = None
    prev_rank = 0
    for position, player_id in enumerate(final_ranks, start=1):
        score = final_scores[player_id]
        rank = prev_rank if score == prev_score else position
        ranks[player_id] = rank
        prev_score, prev_rank = score, rank
    return ranks


def _get_player(session: Session, game_id: str, user_uuid: str) -> GamePlayer | None:
    return session.exec(
        select(GamePlayer).where(
            GamePlayer.game_id == game_id, GamePlayer.user_uuid == user_uuid
        )
    ).first()


def _apply(session: Session, events: list[EngineEvent]) -> None:
    if not events:
        return
    game_id = events[0].game_id

    for event in events:
        if event.type == EventType.ROUND_STARTED:
            game = session.get(Game, game_id)
            if game is not None:
                game.current_round = event.public_fields["round_number"]
                session.add(game)

        elif event.type == EventType.SCORES_UPDATED:
            for result in event.public_fields["results"]:
                player = _get_player(session, game_id, result["player"])
                if player is not None:
                    player.current_score = result["new_total"]
                    session.add(player)

        elif event.type == EventType.RENAISSANCE_TRIGGERED:
            # actor is the player whose score renaissance'd (engine.py
            # sets actor=player_id for this event type specifically).
            player = _get_player(session, game_id, event.actor)
            if player is not None:
                player.current_score = event.public_fields["new_score"]
                session.add(player)

        elif event.type == EventType.GAME_ENDED:
            game = session.get(Game, game_id)
            if game is not None:
                game.status = GameStatus.COMPLETED
                game.ended_at = event.timestamp
                session.add(game)

            ranks = _standard_competition_ranks(
                event.public_fields["final_scores"], event.public_fields["final_ranks"]
            )
            for player_id, rank in ranks.items():
                player = _get_player(session, game_id, player_id)
                if player is not None:
                    player.final_rank = rank
                    session.add(player)

    session.commit()


def sync_lookup_tables(session: Session, events: list[EngineEvent]) -> None:
    """
    Call right after persist_events() for the same batch (see
    routes.py's `_persist` wrapper, the one place both are called
    together). Never raises -- see module docstring on why failures
    here are swallowed rather than propagated.
    """
    try:
        _apply(session, events)
    except Exception as exc:  # noqa: BLE001 -- deliberately broad, see module docstring
        session.rollback()
        game_id = events[0].game_id if events else "?"
        print(
            f"lookup_sync: failed to sync lookup tables for game {game_id}: {exc!r}",
            file=sys.stderr,
        )