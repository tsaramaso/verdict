# api/src/app/websocket.py
"""
WebSocket connection manager for multi-game support.
Tracks active connections per game and provides broadcast utilities.
"""

from typing import Dict
from fastapi import WebSocket


class ConnectionManager:
    """
    Manages WebSocket connections for all active games.

    Structure:
      active_connections = {
        "game-id-1": {
          "player-uuid-a": WebSocket,
          "player-uuid-b": WebSocket,
          ...
        },
        "game-id-2": {
          ...
        }
      }
    """

    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}

    async def connect(self, game_id: str, player_id: str, websocket: WebSocket):
        """
        Register a new WebSocket connection for a player in a game.

        Args:
            game_id: The game this player is connecting to
            player_id: The player's UUID
            websocket: The WebSocket connection object
        """
        if game_id not in self.active_connections:
            self.active_connections[game_id] = {}

        self.active_connections[game_id][player_id] = websocket
        print(f"[WS] Connected: {player_id[:8]}... to game {game_id[:8]}...")

    async def disconnect(self, game_id: str, player_id: str):
        """
        Unregister a WebSocket connection.

        Args:
            game_id: The game to disconnect from
            player_id: The player's UUID
        """
        if game_id not in self.active_connections:
            return

        self.active_connections[game_id].pop(player_id, None)

        # Clean up empty game entries
        if not self.active_connections[game_id]:
            del self.active_connections[game_id]

        print(f"[WS] Disconnected: {player_id[:8]}... from game {game_id[:8]}...")

    async def broadcast(self, game_id: str, message: dict):
        """
        Send a message to all players connected to a specific game.

        Args:
            game_id: The game to broadcast to
            message: Dict to send (will be converted to JSON)
        """
        if game_id not in self.active_connections:
            print(f"[WS] Broadcast to {game_id[:8]}...: no active connections")
            return

        disconnected_players = []

        for player_id, connection in self.active_connections[game_id].items():
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"[WS] Error sending to {player_id[:8]}...: {e}")
                disconnected_players.append(player_id)

        # Clean up broken connections
        for player_id in disconnected_players:
            await self.disconnect(game_id, player_id)

        print(
            f"[WS] Broadcast to game {game_id[:8]}...: "
            f"{len(self.active_connections[game_id])} players"
        )

    def get_players_in_game(self, game_id: str) -> set:
        """
        Get all player IDs currently connected to a game.

        Args:
            game_id: The game to check

        Returns:
            Set of player UUIDs connected to the game
        """
        return set(self.active_connections.get(game_id, {}).keys())

    def get_connection_count(self, game_id: str) -> int:
        """Get the number of players connected to a game."""
        return len(self.active_connections.get(game_id, {}))

    def get_all_games(self) -> list:
        """Get all game IDs with active connections."""
        return list(self.active_connections.keys())


# Global instance
manager = ConnectionManager()
