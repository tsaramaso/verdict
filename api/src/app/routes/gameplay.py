# src/app/routes/gameplay.py
"""
In-game action routes — every route that advances a live game's state.
All require get_current_player (seated-in-this-game auth) and
get_locked_game_state (registry lock held for the whole request).

Every route follows the same five-step shape:
  1. auth       — get_current_player (401/403 handled by the dependency)
  2. state      — get_locked_game_state (404 handled, lock held)
  3. engine call — via _call(), which maps IllegalAction -> HTTP 409
  4. persist    — _persist(): Event log commit + lookup row sync, atomic
  5. response   — ActionResult scoped to the acting player only

Grouped by rules.md section:
  Turn          — /draw, /action            (§4-5)
  Power cards   — /power/*                  (§7)
  Quick-discard — /quick-discard, /quick-discard/close  (§5.4)
  The Trial     — /trial/*                  (§6)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from src.app.auth import get_current_player
from src.app.engine import engine
from src.app.engine.state import GameState
from src.app.game_registry import get_locked_game_state
from src.app.routes._shared import _call, _persist, _result
from src.app.schemas import (
    ActionRequest,
    ActionResult,
    DecreeSwapRequest,
    DrawRequest,
    InvokePowerRequest,
    QuickDiscardRequest,
)
from src.app.websocket import manager
from src.db.session import get_session

router = APIRouter(prefix="/games", tags=["gameplay"])


# ===== Broadcast Helper =====
async def broadcast_game_update(game_id: str, game_state, events: list):
    """Broadcast game state update to all connected players (scoped per player)."""
    from src.app.websocket_helpers import scope_state_for_player
    from src.app.models.db import User
    from src.db.session import get_session
    from sqlalchemy import select
    from src.logging_config import get_logger

    logger = get_logger("broadcast")

    # Get all connected players for this game
    connected_players = manager.get_players_in_game(game_id)

    if not connected_players:
        logger.debug("broadcast_no_players", game_id=str(game_id)[:8])
        return

    # Get player names for responses
    session = get_session().__next__()
    users = session.exec(
        select(User).where(User.uuid.in_(game_state.player_order))
    ).all()
    player_names = {u.uuid: u.name or u.uuid for u in users}
    session.close()

    # Send scoped message to each player
    for player_id in connected_players:
        # Scope events for this player (what they're allowed to see)
        scoped_events = [event.payload_for(player_id) for event in events]

        # Scope the full state for this player
        scoped_state = scope_state_for_player(game_state, player_id, player_names)

        # Build message with scoped events
        message = {
            "type": "game_state_update",
            "game_id": game_id,
            "phase": str(game_state.phase),
            "current_player": game_state.current_player,
            "round_number": game_state.round_number,
            "events": scoped_events,
            # Include updated state snapshot
            "self": scoped_state["self"],
            "opponents": scoped_state["opponents"],
            "my_opponent_knowledge": scoped_state["my_opponent_knowledge"],
            "trial": scoped_state["trial"],
            "discard_pile": scoped_state["discard_pile"],
        }

        # Send to this specific player
        try:
            websocket = manager.active_connections[game_id][player_id]
            await websocket.send_json(message)
            logger.debug(
                "broadcast_sent",
                game_id=str(game_id)[:8],
                player=str(player_id)[:8],
                player_name=player_names.get(player_id, "unknown"),
                events_count=len(scoped_events),
            )
        except Exception as e:
            logger.error(
                "broadcast_send_failed",
                game_id=str(game_id)[:8],
                player=str(player_id)[:8],
                error=str(e),
            )
            await manager.disconnect(game_id, player_id)

    logger.info(
        "broadcast_complete",
        game_id=str(game_id)[:8],
        players_count=len(connected_players),
        events_count=len(events),
    )


# ---------------------------------------------------------------------
# Turn — draw & action (rules.md §4-5)
# ---------------------------------------------------------------------


@router.post("/{game_id}/draw", response_model=ActionResult)
async def draw(
    request: DrawRequest,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.draw_card, state, player_id, request.source)
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


@router.post("/{game_id}/action", response_model=ActionResult)
async def take_action(
    request: ActionRequest,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(
        engine.take_action, state, player_id, request.choice, request.slot_index
    )
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


# ---------------------------------------------------------------------
# Power cards (rules.md §7)
# ---------------------------------------------------------------------


@router.post("/{game_id}/power/decline", response_model=ActionResult)
async def decline_power(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.decline_power, state, player_id)
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


@router.post("/{game_id}/power/invoke", response_model=ActionResult)
async def invoke_power(
    request: InvokePowerRequest,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(
        engine.invoke_power,
        state,
        player_id,
        request.own_slot_index,
        request.target_owner,
        request.target_index,
    )
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


@router.post("/{game_id}/power/decree-swap", response_model=ActionResult)
async def decree_swap(
    request: DecreeSwapRequest,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(
        engine.decree_swap_decision,
        state,
        player_id,
        request.swap,
        request.own_slot_index,
    )
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


# ---------------------------------------------------------------------
# Quick-discard (rules.md §5.4)
# ---------------------------------------------------------------------


@router.post("/{game_id}/quick-discard", response_model=ActionResult)
async def quick_discard(
    request: QuickDiscardRequest,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.quick_discard, state, player_id, request.slot_index)
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


@router.post("/{game_id}/quick-discard/close", response_model=ActionResult)
async def close_quick_discard(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    """
    System-triggered in the engine (no player_id parameter — closing the
    window isn't a Testimony/Perjury-bearing act). Still gated behind
    get_current_player rather than get_current_user: advancing a game's
    phase requires being seated in it, even when the engine call doesn't
    attribute it to anyone. The "any seated player can close this window
    on demand" trigger is a UI/orchestration choice, not a rules
    requirement — rules.md never specifies a timer or explicit close
    condition for this window.
    """
    events = _call(engine.close_quick_discard_window, state)
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


# ---------------------------------------------------------------------
# The Trial (rules.md §6)
# ---------------------------------------------------------------------


@router.post("/{game_id}/trial/testify-first", response_model=ActionResult)
async def testify_first(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.give_testimony_first, state, player_id)
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-call", response_model=ActionResult)
def pass_call(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_call_window, state, player_id)
    _persist(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/testify-cross", response_model=ActionResult)
def testify_cross(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.give_testimony_cross, state, player_id)
    _persist(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-match", response_model=ActionResult)
def pass_match(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_match_window, state, player_id)
    _persist(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/challenge", response_model=ActionResult)
def challenge(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.give_challenge, state, player_id)
    _persist(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-duel", response_model=ActionResult)
def pass_duel(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_duel_window, state, player_id)
    _persist(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/plea", response_model=ActionResult)
def plea(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.take_plea, state, player_id)
    _persist(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-plea", response_model=ActionResult)
def pass_plea(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_final_plea_window, state, player_id)
    _persist(session, events)
    return _result(state, events, player_id)

@router.post("/{game_id}/advance-phase")
async def advance_phase(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    """
    Advance TURN_START → DRAWING phase.
    Called by UI after animation delay (3s) for all players.
    Only valid during TURN_START phase.
    """
    from src.app.engine.state import Phase
    from src.app.routes._shared import _result
    
    if state.phase != Phase.TURN_START:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot advance phase from {state.phase}. Only valid during TURN_START."
        )
    
    # Advance phase
    state.phase = Phase.DRAWING
    
    # No events needed (pure phase transition)
    events = []
    _persist(session, events)
    
    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)
    
    return _result(state, events, player_id)
 
