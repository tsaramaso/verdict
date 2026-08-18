"""
Lobby management endpoints.
Lobbies are ephemeral (in-memory), players join by short ID.
Game creation handled by /games/create endpoint.
"""

from fastapi import APIRouter, Depends, HTTPException
import string
import random
from datetime import datetime, timezone

from src.app.auth import get_current_player, get_current_user

router = APIRouter(prefix="/lobbies", tags=["lobbies"])

# In-memory lobby storage: { shortId: { host_player_id, host_name, players, created_at } }
lobbies = {}


def generate_short_id(length: int = 6) -> str:
    """Generate short alphanumeric ID for lobby."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


@router.post("/create")
def create_lobby(
    user = Depends(get_current_user)
) -> dict:
    """Create ephemeral lobby. Returns short ID."""
    player_id = user.uuid
    short_id = generate_short_id()
    
    while short_id in lobbies:
        short_id = generate_short_id()
    
    lobbies[short_id] = {
        "host_player_id": player_id,
        "host_name": user.name or player_id,
        "players": {
            player_id: {
                "id": player_id,
                "name": user.name or player_id,
                "ready": False,
                "connected": True
            }
        },
        "created_at": datetime.now(timezone.utc)
    }
    
    return {
        "lobby_id": short_id,
        "host_player_id": player_id
    }


@router.get("/{lobby_id}")
def get_lobby(
    lobby_id: str,
    user = Depends(get_current_user)
) -> dict:
    """Get lobby state. Auto-adds player if joining."""
    if lobby_id not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")

    lobby = lobbies[lobby_id]
    player_id = user.uuid
    
    if player_id not in lobby["players"]:
        lobby["players"][player_id] = {
            "id": player_id,
            "name": player_id,
            "ready": False,
            "connected": True
        }
    
    return {
        "lobby_id": lobby_id,
        "host_player_id": lobby["host_player_id"],
        "players": lobby["players"],
        "player_count": len(lobby["players"])
    }


@router.post("/{lobby_id}/player/ready")
def set_lobby_player_ready(
    lobby_id: str,
    ready: bool,
    user = Depends(get_current_user)
) -> dict:
    """Mark player ready in lobby."""
    if lobby_id not in lobbies:
        raise HTTPException(status_code=404, detail="Lobby not found")
    
    lobby = lobbies[lobby_id]
    player_id = user.uuid
    if player_id not in lobby["players"]:
        raise HTTPException(status_code=404, detail="Player not in lobby")
    
    lobby["players"][player_id]["ready"] = ready
    
    return {"player_id": player_id, "ready": ready}


@router.get("")
def list_lobbies() -> dict:
    """List all active lobbies."""
    return {
        "lobbies": [
            {
                "lobby_id": lid,
                "host": lobby["host_name"],
                "player_count": len(lobby["players"]),
                "created_at": lobby["created_at"].isoformat()
            }
            for lid, lobby in lobbies.items()
        ]
    }