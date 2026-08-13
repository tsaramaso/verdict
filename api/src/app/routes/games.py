# src/app/routes/games.py
"""
Game lifecycle routes — everything outside a live turn:

  POST   /games                 create a game (all players supplied up-front,
                                no separate join step — single-creator flow)
  GET    /games                 list games the caller is seated in (DB lookup,
                                not the in-memory registry — works for finished
                                games and, once replay lands, pre-restart games)
  GET    /games/{id}/status     live snapshot from the in-memory registry
  GET    /games/{id}/events     full persisted event log for a game, scoped to
                                the caller

Auth shape:
  create_game / list_games  — get_current_user (no game_id in path yet)
  status / events           — get_current_player (seated-in-this-game check)
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Path
from loguru import logger
from sqlmodel import Session, select

from src.app.engine.constants import TurnDirection
from src.app.auth import get_current_player, get_current_user
from src.app.engine import engine
from src.app.engine.errors import IllegalAction
from src.app.engine.state import GameState
from src.app.game_registry import GameRegistry, get_game_state, get_registry
from src.app.models.db import Event as DBEvent
from src.app.models.db import Game, GamePlayer, User, Recap
from src.app.models.enums import GameStatus
from src.app.routes._shared import _persist
from src.app.schemas import (
    EventLogOut,
    EventOut,
    GameCreateRequest,
    GameCreateResult,
    GameListOut,
    GameStatusOut,
    GameSummaryOut,
)
from src.db.session import get_session

router = APIRouter(prefix="/games", tags=["games"])


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
    # mutating one passed in. Unpacked directly here rather than
    # teaching _call a second return shape just for this one caller.
    try:
        player_names = {u.uuid: u.name or u.uuid for u in found_users}
        state, events = engine.new_game(
            game_id, player_names, request.rules_config, TurnDirection.CLOCKWISE
        )
    except IllegalAction as e:
        raise HTTPException(status.HTTP_409_CONFLICT, detail=str(e)) from e

    # Populate player names from found_users
    for user in found_users:
        state.players[user.uuid].player_name = user.name or user.uuid
    # WAITING_FOR_PLAYERS is unused by this creation flow on purpose —
    # every player is supplied up front, so there's no lobby phase.
    # Retained in the enum for a possible future creation path.
    game_row = Game(
        id=game_id,
        status=GameStatus.IN_PROGRESS,
        turn_direction=TurnDirection.CLOCKWISE,
        current_round=state.round_number,
        started_at=datetime.now(timezone.utc),
    )
    session.add(game_row)
    session.add_all(
        GamePlayer(game_id=game_id, user_uuid=pid, seat_order=seat)
        for seat, pid in enumerate(request.player_ids)
    )
    # Deliberately NOT session.commit()'d here — _persist() below commits
    # once, atomically, over Game + GamePlayer + every Event row together.
    _persist(session, events)
    registry.register(state)

    return GameCreateResult(
        game_id=game_id,
        phase=state.phase,
        events=[EventOut.from_engine_event(e, user.uuid) for e in events],
    )


@router.get("", response_model=GameListOut)
def list_games(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> GameListOut:
    """
    Reads the thin DB lookup row (Game + GamePlayer), NOT the in-memory
    registry — deliberately, so this works for games this process doesn't
    currently have loaded (finished games; and once replay exists,
    pre-restart games too). Auth is get_current_user, not
    get_current_player, since there's no single game_id in the path to
    scope against.
    """
    games = session.exec(
        select(Game, GamePlayer)
        .join(GamePlayer, GamePlayer.game_id == Game.id)
        .where(GamePlayer.user_uuid == user.uuid)
        .where(Game.status != GameStatus.CANCELLED)
        .order_by(Game.created_at.desc())
    ).all()
    return GameListOut(
        games=[
            GameSummaryOut(
                game_id=game.id,
                status=game.status,
                turn_direction=game.turn_direction,
                current_round=game.current_round,
                seat_order=player.seat_order,
                created_at=game.created_at.isoformat(),
                started_at=game.started_at.isoformat() if game.started_at else None,
                ended_at=game.ended_at.isoformat() if game.ended_at else None,
            )
            for game, player in games
        ]
    )


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


@router.get("/{game_id}/events", response_model=EventLogOut)
def get_events(
    game_id: str,
    player_id: str = Depends(get_current_player),
    session: Session = Depends(get_session),
) -> EventLogOut:
    """
    The inspect-logs endpoint. Reads the persisted DB log, NOT the
    in-memory registry — this is deliberately the one route that proves
    persist_events() actually wrote something durable. Full log, no
    pagination yet (flagged, not an oversight — fine at this scale).

    Scoped the same way every live response is: EventOut.from_db_event
    filters scoped_fields against the stored {visible_to, value}
    envelope for THIS caller only.
    """
    rows = session.exec(
        select(DBEvent).where(DBEvent.game_id == game_id).order_by(DBEvent.sequence)
    ).all()
    return EventLogOut(
        game_id=game_id,
        events=[EventOut.from_db_event(r, player_id) for r in rows],
    )

@router.delete("/{game_id}", status_code=status.HTTP_200_OK)
def cancel_game(
    game_id: str = Path(...),
    player_id: str = Depends(get_current_player),
    session: Session = Depends(get_session),
):
    game = session.exec(
        select(Game).where(Game.id == game_id)
    ).first()
    
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    
    if game.status == GameStatus.CANCELLED:
        raise HTTPException(status_code=409, detail="Game already cancelled")
    
    if game.status != GameStatus.WAITING_FOR_PLAYERS:
        raise HTTPException(status_code=409, detail="Cannot cancel a game in progress")
    
    creator = session.exec(
        select(GamePlayer)
        .where(GamePlayer.game_id == game_id)
        .where(GamePlayer.seat_order == 0)
    ).first()
    
    if not creator or creator.user_uuid != player_id:
        raise HTTPException(status_code=403, detail="Only creator can cancel")
    
    # Soft delete
    game.status = GameStatus.CANCELLED
    session.add(game)
    session.commit()
    
    logger.info("game_cancelled", game_id=game_id, cancelled_by=player_id)
    
    return {"message": "Game cancelled"}


@router.get("/{game_id}/recap")
def get_recap(
    game_id: str = Path(...),
    player_id: str = Depends(get_current_player),
    session: Session = Depends(get_session),
):
    """Get end-game recap (final rankings, score progression)."""
    recap = session.exec(
        select(Recap).where(Recap.game_id == game_id)
    ).first()
    
    if not recap:
        raise HTTPException(status_code=404, detail="Recap not found")
    
    return recap.data