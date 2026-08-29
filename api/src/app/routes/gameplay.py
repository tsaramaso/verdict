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

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from src.app.engine.timer import SIMULTANEOUS_PHASES
from src.app.auth import get_current_player
from src.app.engine import engine
from src.app.engine.state import GameState
from src.app.game_registry import get_locked_game_state
from src.app.routes._shared import _call, _persist, _result
from src.app.websocket_helpers import scope_state_for_player
from src.logging_config import get_logger
from src.app.engine.state import Phase


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

router = APIRouter(prefix="/api/games", tags=["gameplay"])


# ===== Broadcast Helper =====
async def broadcast_game_update(game_id: str, game_state, events: list):
    """Broadcast game state update to all connected players (scoped per player)."""

    logger = get_logger("broadcast")

    # Get all connected players for this game
    connected_players = manager.get_players_in_game(game_id)

    if not connected_players:
        logger.debug("broadcast_no_players", game_id=str(game_id)[:8])
        return

    # Get player names from game state (no DB query needed)
    player_names = {
        pid: game_state.players[pid].player_name for pid in game_state.player_order
    }

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
            "draw_source": (
                str(game_state.draw_source) if game_state.draw_source else None
            ),
            "events": scoped_events,
            # Include updated state snapshot
            "self": scoped_state["self"],
            "opponents": scoped_state["opponents"],
            "my_opponent_knowledge": scoped_state["my_opponent_knowledge"],
            "trial": scoped_state["trial"],
            "discard_pile": scoped_state["discard_pile"],
            "rules": scoped_state["rules"],
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
        request.own_slot,
        request.target_player_id,
        request.target_slot,
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
        request.own_slot,
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
    engine.log_player_response(state, player_id)  # Log response for collection window
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
    engine.log_player_response(state, player_id)  # Log response for collection window
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-call", response_model=ActionResult)
async def pass_call(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_call_window, state, player_id)
    engine.log_player_response(state, player_id)  # Log response for collection window
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


@router.post("/{game_id}/trial/testify-cross", response_model=ActionResult)
async def testify_cross(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.give_testimony_cross, state, player_id)
    engine.log_player_response(state, player_id)  # Log response for collection window
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-match", response_model=ActionResult)
async def pass_match(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_match_window, state, player_id)
    engine.log_player_response(state, player_id)  # Log response for collection window
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)


@router.post("/{game_id}/trial/challenge", response_model=ActionResult)
def challenge(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.give_challenge, state, player_id)
    engine.log_player_response(state, player_id)  # Log response for collection window
    _persist(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-duel", response_model=ActionResult)
def pass_duel(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_duel_window, state, player_id)
    engine.log_player_response(state, player_id)  # Log response for collection window
    _persist(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/plea", response_model=ActionResult)
def plea(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.take_plea, state, player_id)
    engine.log_player_response(state, player_id)  # Log response for collection window
    _persist(session, events)
    return _result(state, events, player_id)


@router.post("/{game_id}/trial/pass-plea", response_model=ActionResult)
def pass_plea(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    events = _call(engine.pass_final_plea_window, state, player_id)
    engine.log_player_response(state, player_id)  # Log response for collection window
    _persist(session, events)
    return _result(state, events, player_id)


# ============================================
# TIMER & COLLECTION WINDOW (NEW)
# ============================================


@router.post("/{game_id}/timeout", response_model=ActionResult)
async def handle_timeout(
    game_id: str,
    phase: str,  # Query param: phase name for validation
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    """
    Handle timeout for single-player phases (DRAWING, AWAITING_ACTION, etc).

    Validates:
    1. Phase matches server state
    2. Enough time has elapsed (prevents reload exploitation)
    3. Player is active player

    Applies fallback action per gameplay.md §7 and broadcasts to all players.
    """
    logger = get_logger("timeout")

    # Auth: must be active player
    if player_id != state.current_player:
        logger.warning(
            "timeout_not_active",
            game_id=str(game_id)[:8],
            claimed_player=str(player_id)[:8],
            actual_player=str(state.current_player)[:8],
        )
        raise HTTPException(
            status_code=403,
            detail="Only active player can timeout",
        )

    # Validate timeout is valid (phase match + time elapsed)
    is_valid, error_msg = engine.validate_timeout_attempt(state, phase)
    if not is_valid:
        logger.warning(
            "timeout_rejected",
            game_id=str(game_id)[:8],
            phase=phase,
            reason=error_msg,
        )
        raise HTTPException(status_code=409, detail=error_msg)

    logger.info("timeout_accepted", game_id=str(game_id)[:8], phase=phase)

    # Apply timeout action per phase
    events = []

    if state.phase is Phase.DRAWING:
        events = _call(engine.draw_card, state, player_id, "discard")

    elif state.phase is Phase.AWAITING_ACTION:
        # Use draw_source from state to determine fallback
        source = state.draw_source or "deck"
        if source == "deck":
            events = _call(
                engine.take_action, state, player_id, "discard_immediate", None
            )
        else:
            events = _call(engine.take_action, state, player_id, "pass_back", None)

    elif state.phase is Phase.AWAITING_SPELL_INVOCATION:
        events = _call(engine.decline_power, state, player_id)

    elif state.phase is Phase.AWAITING_SPELL_SWAP_DECISION:
        # Decree swap declined
        events = _call(engine.decree_swap_decision, state, player_id, False, None)

    else:
        raise HTTPException(
            status_code=409,
            detail=f"Timeout not allowed on phase {state.phase}",
        )

    # Persist events
    _persist(session, events)

    # Broadcast to all players
    await broadcast_game_update(game_id, state, events)

    logger.info(
        "timeout_applied",
        game_id=str(game_id)[:8],
        phase=phase,
        player=str(player_id)[:8],
        events_count=len(events),
    )

    return _result(state, events, player_id)


@router.post("/{game_id}/close-phase-window", response_model=ActionResult)
async def close_phase_window(
    game_id: str,
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    """
    Close collection window for simultaneous phases (QUICK_DISCARD, CALL_WINDOW, etc).

    Can be called by any seated player (typically first to finish or background job).
    Server validates phase is actually a collection window.

    Applies fallbacks to non-responders and advances phase.
    Works for: AWAITING_QUICK_DISCARD, AWAITING_CALL_WINDOW, AWAITING_MATCH_WINDOW,
               AWAITING_DUEL_WINDOW, AWAITING_FINAL_PLEA_WINDOW
    """
    logger = get_logger("phase_window")

    # Only proceed if we're in a simultaneous phase
    if state.phase not in SIMULTANEOUS_PHASES:
        logger.warning(
            "window_close_invalid_phase",
            game_id=str(game_id)[:8],
            phase=str(state.phase),
        )
        raise HTTPException(
            status_code=409,
            detail=f"Phase {state.phase} is not a collection window",
        )

    # Check if we should close (all responded OR enough time elapsed)
    all_responded = engine.check_collection_complete(state)
    elapsed = engine.get_phase_elapsed_seconds(state)
    min_window = 2.0  # Minimum collection window (seconds) — can tune

    if not all_responded and elapsed < min_window:
        logger.debug(
            "window_still_open",
            game_id=str(game_id)[:8],
            phase=str(state.phase),
            elapsed=elapsed,
            min_window=min_window,
        )
        raise HTTPException(
            status_code=409,
            detail=f"Collection window still open ({elapsed:.1f}s / {min_window}s)",
        )

    logger.info(
        "phase_window_closing",
        game_id=str(game_id)[:8],
        phase=str(state.phase),
        responded=len(state.phase_responses),
        total=len(state.phase_participants),
        elapsed=elapsed,
    )

    # Apply fallbacks for non-responders
    fallback_events = engine.apply_timeout_fallbacks(state)

    # Advance phase based on current phase
    # NOTE: These use existing engine functions that check "maybe" conditions
    # For MVP, we force-advance by calling the _maybe functions which will
    # cascade through phase transitions automatically
    events = []

    if state.phase is Phase.AWAITING_QUICK_DISCARD:
        # Transition through trial or end round
        print(
            f"DEBUG: hand_emptied_this_window = {state.hand_emptied_this_window}"
        )  # ADD THIS
        events = _call(engine.close_quick_discard_window, state)

    elif state.phase is Phase.AWAITING_CALL_WINDOW:
        # Mark any remaining players as passed_first
        for pid in state.phase_participants - set(state.trial.first_window_callers):
            if pid not in state.trial.passed_first:
                state.trial.passed_first.add(pid)

        # Now manually cascade instead of calling _maybe_close_call_window
        # because we've artificially filled passed_first
        engine.enter_phase(state, Phase.AWAITING_MATCH_WINDOW)
        events = engine._maybe_close_match_window(state)

    elif state.phase is Phase.AWAITING_MATCH_WINDOW:
        # Force close match window
        # Mark any remaining players as passed_cross
        for pid in state.phase_participants - set(state.trial.cross_callers):
            if pid not in state.trial.passed_cross:
                state.trial.passed_cross.add(pid)
        # Now cascade through perjury check to duel or plea
        events = engine._maybe_close_match_window(state)

    elif state.phase is Phase.AWAITING_DUEL_WINDOW:
        # Force close duel window
        # Mark any remaining testifiers as passed challenge
        for pid in state.phase_participants - set(state.trial.passed_challenge):
            state.trial.passed_challenge.add(pid)
        # Cascade to plea window
        events = engine._maybe_close_duel_window(state)

    elif state.phase is Phase.AWAITING_FINAL_PLEA_WINDOW:
        # Force close plea window
        # Mark any remaining bystanders as plea_declined
        for pid in (
            state.phase_participants
            - set(state.trial.plea_taken)
            - set(state.trial.plea_declined)
        ):
            state.trial.plea_declined.add(pid)
        # End round
        events = engine._maybe_close_final_plea_window(state)

    # Combine fallback events + phase advance events
    all_events = fallback_events + events

    # Persist
    _persist(session, all_events)

    # Broadcast
    await broadcast_game_update(game_id, state, all_events)

    logger.info(
        "phase_window_closed",
        game_id=str(game_id)[:8],
        phase=str(state.phase),
        fallbacks_applied=len(fallback_events),
        events_total=len(all_events),
    )

    return _result(state, all_events, player_id)


# ============================================
# PHASE ADVANCEMENT (existing)
# ============================================


@router.post("/{game_id}/advance-phase", response_model=ActionResult)
async def advance_phase(
    player_id: str = Depends(get_current_player),
    state: GameState = Depends(get_locked_game_state),
    session: Session = Depends(get_session),
) -> ActionResult:
    """
    Advance TURN_START → DRAWING phase.
    Called by UI after animation delay (3s) for all players.
    Emits TURN_START_ADVANCED event for audit trail.
    Only valid during TURN_START phase.
    """
    events = _call(engine.advance_turn_start, state)
    _persist(session, events)

    # Broadcast update to all players
    await broadcast_game_update(state.game_id, state, events)

    return _result(state, events, player_id)
