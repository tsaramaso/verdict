"""
Lobby management endpoints.
Lobbies are ephemeral (in-memory), players join by short ID.
Game creation handled by /games/create endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException, Body
import string
import random
from datetime import datetime, timezone
from sqlmodel import Session

from src.app.auth import get_current_user
from src.app.websocket import manager
from src.app.schemas import GameCreateRequest
from src.db.session import get_session

router = APIRouter(prefix="/lobbies", tags=["lobbies"])

lobbies = {}


def generate_short_id(length: int = 6) -> str:
    """Generate short alphanumeric ID for lobby."""
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


@router.post("/create")
async def create_lobby(user=Depends(get_current_user)) -> dict:
    """Create ephemeral lobby. Returns short ID. 
    Broadcasts to global lobbies channel."""
    player_id = user.uuid
    short_id = generate_short_id()

    while short_id in lobbies:
        short_id = generate_short_id()

    created_at = datetime.now(timezone.utc)
    lobbies[short_id] = {
        "host_player_id": player_id,
        "host_name": user.name or player_id,
        "players": {
            player_id: {
                "id": player_id,
                "name": user.name or player_id,
                "ready": False,
                "connected": True,
            }
        },
        "created_at": created_at,
    }

    # Broadcast new lobby to all connected clients in global lobbies channel
    await manager.broadcast(
        "lobbies",  # Global channel (no specific lobby_id)
        {
            "type": "lobby_created",
            "lobby_id": short_id,
            "host": user.name or player_id,
            "player_count": 1,
            "created_at": created_at.isoformat(),
        },
    )

    return {"lobby_id": short_id, "host_player_id": player_id}


@router.get("/{lobby_id}")
def get_lobby(lobby_id: str, user=Depends(get_current_user)) -> dict:
    """Get lobby state. Auto-adds player if joining."""
    if lobby_id not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")

    lobby = lobbies[lobby_id]
    player_id = user.uuid
    if player_id not in lobby["players"]:
        lobby["players"][player_id] = {
            "id": player_id,
            "name": user.name or player_id,
            "ready": False,
            "connected": True,
        }

    return {
        "lobby_id": lobby_id,
        "host_player_id": lobby["host_player_id"],
        "players": lobby["players"],
        "player_count": len(lobby["players"]),
    }


@router.post("/{lobby_id}/player/ready")
async def set_lobby_player_ready(
    lobby_id: str, body: dict = Body(...), user=Depends(get_current_user)
) -> dict:
    """Mark player ready in lobby. Broadcasts update to all connected WS clients."""
    if lobby_id not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")

    lobby = lobbies[lobby_id]
    player_id = user.uuid
    if player_id not in lobby["players"]:
        raise HTTPException(status_code=404, detail="Player not in lobby")

    ready = body.get("ready", False)

    # Update internal state
    lobby["players"][player_id]["ready"] = ready

    # Broadcast to all WS clients in this lobby
    await manager.broadcast(
        lobby_id, {"type": "player_ready", "player_id": player_id, "ready": ready}
    )

    return {"player_id": player_id, "ready": ready}


@router.post("/{lobby_id}/start")
async def start_lobby_game(
    lobby_id: str,
    user=Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """
    Host-only: Start the game from the lobby.

    Validates:
    - Lobby exists
    - User is host
    - All players are ready

    Creates game via /games endpoint, broadcasts to all lobby WS clients.
    """
    if lobby_id not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")

    lobby = lobbies[lobby_id]
    player_id = user.uuid

    # VALIDATE: Host only
    if lobby["host_player_id"] != player_id:
        raise HTTPException(status_code=403, detail="Only the host can start the game")

    # VALIDATE: All players ready
    for pid, player in lobby["players"].items():
        if not player["ready"]:
            raise HTTPException(
                status_code=409, detail=f"Player {player['name']} is not ready"
            )

    # EXTRACT: Player IDs (ordered by join, or arbitrary)
    player_ids = list(lobby["players"].keys())

    if len(player_ids) < 2:
        raise HTTPException(
            status_code=409, detail="At least 2 players required to start game"
        )

    # CREATE: Game via internal call (avoid HTTP round-trip)
    from src.app.routes.games import create_game

    game_request = GameCreateRequest(player_ids=player_ids)
    try:
        # get_current_user already authenticated; reuse
        game_result = create_game(
            request=game_request,
            user=user,
            session=session,
            registry=__import__(
                "src.app.game_registry", fromlist=["get_registry"]
            ).get_registry(),
        )
        game_id = game_result.game_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create game: {str(e)}")

    # BROADCAST: game_started to all lobby-specific WS clients
    await manager.broadcast(lobby_id, {"type": "game_started", "game_id": game_id})

    # BROADCAST: lobby_deleted to global lobbies channel
    await manager.broadcast("lobbies", {"type": "lobby_deleted", "lobby_id": lobby_id})

    # CLEANUP: Delete lobby from memory
    del lobbies[lobby_id]

    return {"game_id": game_id, "player_count": len(player_ids)}


@router.get("")
def list_lobbies() -> dict:
    """List all active lobbies."""
    return {
        "lobbies": [
            {
                "lobby_id": lid,
                "host": lobby["host_name"],
                "player_count": len(lobby["players"]),
                "created_at": lobby["created_at"].isoformat(),
            }
            for lid, lobby in lobbies.items()
        ]
    }
