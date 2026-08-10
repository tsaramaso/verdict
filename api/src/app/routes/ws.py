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
from sqlalchemy import select

from src.app.websocket import manager
from src.db.session import get_session
from src.config import HASH_SECRET_KEY, ALGORITHM

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
    print("[WS] DEBUG: websocket_endpoint called!")
    print(f"[WS] DEBUG: game_id={game_id}")
    print(f"[WS] DEBUG: token={token[:20]}...")
    player_id = None

    try:
        # STEP 1: AUTHENTICATE
        print(f"[WS] Connection attempt to game {game_id[:8]}... with token")
        player_id = await verify_ws_token(token)
        print(f"[WS] Authenticated: {player_id[:8]}...")

        # STEP 2: ACCEPT CONNECTION
        await websocket.accept()
        print(f"[WS] Connection accepted for {player_id[:8]}...")

        # STEP 3: REGISTER WITH MANAGER
        await manager.connect(game_id, player_id, websocket)

        # STEP 4: SEND INITIAL GAME STATE
        # Fetch current state from registry and scope it for this player
        from src.app.game_registry import get_registry
        from src.app.websocket_helpers import scope_state_for_player
        from src.app.models.db import User

        registry = get_registry()
        try:
            game_state = registry.get(game_id)

            # Get player names for better logging/display
            player_ids = [player_id] + [
                pid for pid in game_state.player_order if pid != player_id
            ]
            session = get_session().__next__()
            users = session.exec(select(User).where(User.uuid.in_(player_ids))).all()
            player_names = {u.uuid: u.name or u.uuid for u in users}
            session.close()

            scoped_state = scope_state_for_player(game_state, player_id, player_names)
            await websocket.send_json(scoped_state)
        except Exception as e:
            print(f"[WS] Error fetching game state: {e}")
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

                elif msg_type == "ready":
                    # Client ready for game state
                    print(f"[WS] Player {player_id[:8]}... is ready")
                    await websocket.send_json(
                        {"type": "ready_ack", "message": "Ready to receive updates"}
                    )

                else:
                    print(f"[WS] Unknown message type: {msg_type}")

            except json.JSONDecodeError:
                print(f"[WS] Invalid JSON from {player_id[:8]}...")
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})

    except WebSocketException as e:
        # Auth failed or other WS error
        print(f"[WS] WebSocket exception: {e.reason}")
        await websocket.close(code=e.code, reason=e.reason)

    except WebSocketDisconnect:
        # Client closed connection normally
        if player_id:
            await manager.disconnect(game_id, player_id)

            # Notify remaining players
            await manager.broadcast(
                game_id, {"type": "player_disconnected", "player_id": player_id}
            )
        print(f"[WS] Disconnected: {player_id[:8] if player_id else 'unknown'}...")

    except Exception as e:
        # Unexpected error
        print(f"[WS] Unexpected error: {type(e).__name__}: {e}")
        if player_id:
            await manager.disconnect(game_id, player_id)
        try:
            await websocket.close(code=1011, reason="Internal server error")
        except Exception:
            pass  # Connection may already be closed
