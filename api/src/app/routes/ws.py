# api/src/app/routes/ws.py
"""
WebSocket endpoint for real-time game updates.

Connection flow:
  1. Client connects to /ws/games/{game_id}?token={jwt}
  2. Server verifies token
  3. If valid: accept connection, register with ConnectionManager
  4. Server sends initial game state
  5. Server waits for keep-alive pings, broadcasts updates from HTTP endpoints
  6. On disconnect: cleanup
"""

import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, WebSocketException
from jose import jwt
from src.app.game_registry import get_registry
from src.app.websocket_helpers import scope_state_for_player
from src.app.websocket import manager
from src.config import HASH_SECRET_KEY, ALGORITHM
from src.logging_config import get_logger

logger = get_logger("websocket")

router = APIRouter(prefix="/ws")


async def verify_ws_token(token: str) -> str:
    """
    Verify JWT token from WebSocket connection.

    Args:
        token: JWT token string

    Returns:
        player_id (UUID) if valid

    Raises:
        WebSocketException: If token is invalid/expired
    """
    try:
        payload = jwt.decode(token, HASH_SECRET_KEY, algorithms=[ALGORITHM])
        player_id = payload.get("uuid")

        if not player_id:
            raise WebSocketException(code=1008, reason="Invalid token: no uuid")

        return player_id

    except jwt.ExpiredSignatureError:
        raise WebSocketException(code=1008, reason="Token expired")
    except jwt.InvalidTokenError as e:
        raise WebSocketException(code=1008, reason=f"Invalid token: {str(e)}")
    except Exception as e:
        raise WebSocketException(
            code=1011, reason=f"Token verification error: {str(e)}"
        )


@router.websocket("/lobbies")
async def global_lobbies_websocket_endpoint(
    websocket: WebSocket, token: str = Query(...)
):
    """
    WebSocket endpoint for real-time lobby list updates (global, no specific lobby).

    Broadcasts:
      - initial_lobbies: all active lobbies on connect
      - lobby_created: new lobby created
      - lobby_deleted: lobby closed (game started)

    Query params:
        token: JWT authentication token (required)
    """
    player_id = None

    try:
        # STEP 1: AUTHENTICATE
        logger.debug("ws_global_lobbies_connection_attempt")
        player_id = await verify_ws_token(token)
        logger.info("ws_global_lobbies_authenticated", player_id=str(player_id)[:8])

        # STEP 2: ACCEPT CONNECTION
        await websocket.accept()
        logger.debug(
            "ws_global_lobbies_connection_accepted", player_id=str(player_id)[:8]
        )

        # STEP 3: REGISTER WITH MANAGER 
        # (use fixed "lobbies" as room_id for global channel)
        await manager.connect("lobbies", player_id, websocket)
        logger.debug(
            "ws_global_lobbies_registered_manager", player_id=str(player_id)[:8]
        )

        # STEP 4: SEND INITIAL LOBBY LIST
        from src.app.routes.lobbies import lobbies

        initial_lobbies = [
            {
                "lobby_id": lid,
                "host": lobby["host_name"],
                "player_count": len(lobby["players"]),
                "created_at": lobby["created_at"].isoformat(),
            }
            for lid, lobby in lobbies.items()
        ]
        initial_state = {"type": "initial_lobbies", "lobbies": initial_lobbies}
        await websocket.send_json(initial_state)
        logger.info(
            "ws_global_lobbies_initial_state_sent", lobby_count=len(initial_lobbies)
        )

        # STEP 5: LISTEN FOR MESSAGES (ping/pong)
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)
                msg_type = msg.get("type")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    logger.debug(
                        "ws_global_lobbies_pong_sent", player_id=str(player_id)[:8]
                    )
                else:
                    logger.warning(
                        "ws_global_lobbies_unknown_message_type",
                        msg_type=msg_type,
                        player_id=str(player_id)[:8],
                    )

            except json.JSONDecodeError:
                logger.warning(
                    "ws_global_lobbies_invalid_json", player_id=str(player_id)[:8]
                )
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketException as e:
        logger.warning("ws_global_lobbies_exception", reason=str(e.reason))
        await websocket.close(code=e.code, reason=e.reason)

    except WebSocketDisconnect:
        if player_id:
            await manager.disconnect("lobbies", player_id)
            logger.info("ws_global_lobbies_disconnected", player_id=str(player_id)[:8])

    except Exception as e:
        logger.error(
            "ws_global_lobbies_unexpected_error",
            player_id=str(player_id)[:8] if player_id else "unknown",
            error_type=type(e).__name__,
            error=str(e),
        )
        if player_id:
            await manager.disconnect("lobbies", player_id)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass


@router.websocket("/lobbies/{lobby_id}")
async def lobby_websocket_endpoint(
    websocket: WebSocket, lobby_id: str, token: str = Query(...)
):
    """
    WebSocket endpoint for real-time lobby updates.

    Broadcasts:
      - player_connected: new player joined
      - player_ready: player marked ready
      - player_disconnected: player left
      - game_started: game creation confirmed

    Query params:
        token: JWT authentication token (required)

    Path params:
        lobby_id: The lobby to connect to
    """
    from src.app.routes.lobbies import lobbies  # Import lobbies dict

    player_id = None

    try:
        # STEP 1: AUTHENTICATE
        logger.debug("ws_lobby_connection_attempt", lobby_id=lobby_id)
        player_id = await verify_ws_token(token)
        logger.info(
            "ws_lobby_authenticated", lobby_id=lobby_id, player_id=str(player_id)[:8]
        )

        # STEP 2: ACCEPT CONNECTION
        await websocket.accept()
        logger.debug(
            "ws_lobby_connection_accepted",
            lobby_id=lobby_id,
            player_id=str(player_id)[:8],
        )

        # STEP 3: VALIDATE LOBBY EXISTS
        if lobby_id not in lobbies:
            await websocket.close(code=1008, reason="Lobby not found")
            return

        # STEP 4: REGISTER WITH MANAGER (reuse ConnectionManager with lobby_id)
        await manager.connect(lobby_id, player_id, websocket)
        logger.debug(
            "ws_lobby_registered_manager",
            lobby_id=lobby_id,
            player_id=str(player_id)[:8],
        )

        # STEP 5: SEND INITIAL LOBBY STATE
        lobby = lobbies[lobby_id]
        initial_state = {
            "type": "lobby_state",
            "lobby_id": lobby_id,
            "host_player_id": lobby["host_player_id"],
            "players": [
                {
                    "player_id": pid,
                    "player_name": p["name"],
                    "ready": p["ready"],
                    "connected": p["connected"],
                }
                for pid, p in lobby["players"].items()
            ],
        }
        await websocket.send_json(initial_state)
        logger.info(
            "ws_lobby_initial_state_sent",
            lobby_id=lobby_id,
            player_id=str(player_id)[:8],
        )

        # STEP 6: BROADCAST PLAYER JOINED TO OTHERS
        await manager.broadcast(
            lobby_id,
            {
                "type": "player_connected",
                "player_id": player_id,
                "player_name": lobby["players"]
                .get(player_id, {})
                .get("name", player_id),
            },
        )

        # STEP 7: LISTEN FOR MESSAGES (ping/pong)
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)
                msg_type = msg.get("type")

                if msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    logger.debug("ws_lobby_pong_sent", player_id=str(player_id)[:8])
                else:
                    logger.warning(
                        "ws_lobby_unknown_message_type",
                        msg_type=msg_type,
                        player_id=str(player_id)[:8],
                    )

            except json.JSONDecodeError:
                logger.warning("ws_lobby_invalid_json", player_id=str(player_id)[:8])
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketException as e:
        logger.warning("ws_lobby_exception", lobby_id=lobby_id, reason=str(e.reason))
        await websocket.close(code=e.code, reason=e.reason)

    except WebSocketDisconnect:
        if player_id:
            await manager.disconnect(lobby_id, player_id)
            logger.info(
                "ws_lobby_disconnected",
                lobby_id=lobby_id,
                player_id=str(player_id)[:8],
            )
            await manager.broadcast(
                lobby_id, {"type": "player_disconnected", "player_id": player_id}
            )

    except Exception as e:
        logger.error(
            "ws_lobby_unexpected_error",
            lobby_id=lobby_id,
            player_id=str(player_id)[:8] if player_id else "unknown",
            error_type=type(e).__name__,
            error=str(e),
        )
        if player_id:
            await manager.disconnect(lobby_id, player_id)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass


@router.websocket("/games/{game_id}")
async def websocket_endpoint(
    websocket: WebSocket, game_id: str, token: str = Query(...)
):
    """
    WebSocket endpoint for real-time game updates.

    Query params:
        token: JWT authentication token (required)

    Path params:
        game_id: The game to connect to
    """
    player_id = None

    try:
        # STEP 1: AUTHENTICATE
        logger.debug("ws_connection_attempt", game_id=str(game_id)[:8])
        player_id = await verify_ws_token(token)
        logger.info(
            "ws_authenticated", game_id=str(game_id)[:8], player_id=str(player_id)[:8]
        )

        # STEP 2: ACCEPT CONNECTION
        await websocket.accept()
        logger.debug(
            "ws_connection_accepted",
            game_id=str(game_id)[:8],
            player_id=str(player_id)[:8],
        )

        # STEP 3: REGISTER WITH MANAGER
        await manager.connect(game_id, player_id, websocket)
        logger.debug(
            "ws_registered_manager",
            game_id=str(game_id)[:8],
            player_id=str(player_id)[:8],
        )

        registry = get_registry()
        try:
            game_state = registry.get(game_id)

            player_names = {
                pid: game_state.players[pid].player_name
                for pid in game_state.player_order
            }

            scoped_state = scope_state_for_player(game_state, player_id, player_names)
            await websocket.send_json(scoped_state)
            logger.info(
                "ws_initial_state_sent",
                game_id=str(game_id)[:8],
                player_id=str(player_id)[:8],
            )
        except Exception as e:
            print(f"WS INITIAL STATE ERROR: {type(e).__name__}: {e}")  # ADD THIS
            import traceback

            print(traceback.format_exc())  # ADD THIS
            logger.error(
                "ws_initial_state_failed",
                game_id=str(game_id)[:8],
                player_id=str(player_id)[:8] if player_id else "unknown",
                error=str(e),
                exc_info=True,
            )
            await websocket.close(code=1011, reason="Could not load game state")
            return

        # STEP 5: LISTEN FOR MESSAGES
        # This loop keeps the connection open and listens for:
        # - Keep-alive pings from client
        # - Other control messages
        # Server broadcasts are sent directly via manager.broadcast()
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)

                msg_type = msg.get("type")

                if msg_type == "ping":
                    # Keep-alive ping
                    await websocket.send_json({"type": "pong"})
                    logger.debug(
                        "ws_pong_sent",
                        player_id=str(player_id)[:8] if player_id else "unknown",
                    )

                elif msg_type == "ready":
                    # Client ready for game state
                    logger.debug(
                        "ws_player_ready",
                        game_id=str(game_id)[:8],
                        player_id=str(player_id)[:8] if player_id else "unknown",
                    )
                    await websocket.send_json(
                        {"type": "ready_ack", "message": "Ready to receive updates"}
                    )

                else:
                    logger.warning(
                        "ws_unknown_message_type",
                        msg_type=msg_type,
                        player_id=str(player_id)[:8] if player_id else "unknown",
                    )

            except json.JSONDecodeError:
                logger.warning(
                    "ws_invalid_json",
                    player_id=str(player_id)[:8] if player_id else "unknown",
                )
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketException as e:
        # Auth failed or other WS error
        logger.warning("ws_exception", game_id=str(game_id)[:8], reason=str(e.reason))
        await websocket.close(code=e.code, reason=e.reason)

    except WebSocketDisconnect:
        # Client closed connection normally
        if player_id:
            await manager.disconnect(game_id, player_id)
            logger.info(
                "ws_disconnected",
                game_id=str(game_id)[:8],
                player_id=str(player_id)[:8],
            )

            # Notify remaining players
            await manager.broadcast(
                game_id, {"type": "player_disconnected", "player_id": player_id}
            )

    except Exception as e:
        # Unexpected error
        logger.error(
            "ws_unexpected_error",
            game_id=str(game_id)[:8],
            player_id=str(player_id)[:8] if player_id else "unknown",
            error_type=type(e).__name__,
            error=str(e),
        )
        if player_id:
            await manager.disconnect(game_id, player_id)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass  # Connection may already be closed
