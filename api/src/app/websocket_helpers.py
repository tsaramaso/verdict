# api/src/app/websocket_helpers.py
"""
WebSocket state scoping and helper functions.
Converts GameState into player-scoped views for WebSocket transmission.

Reference: WEBSOCKET_STATE_SCOPING_CORRECTED.md
"""

from src.app.engine.state import GameState


def scope_state_for_player(game_state: GameState, player_id: str) -> dict:
    """
    Return only what this player should see.

    Scoping rules:
    - Self hand: slots 0-1 are "known" (initial glance), others unknown
      unless card.known_by contains this player
    - Opponent hands: only card count visible, no card details
    - Opponent knowledge: which slots they've spied on THIS player
    - Discard pile: all visible cards shown

    Args:
        game_state: Full GameState from registry
        player_id: Player UUID receiving this state

    Returns:
        Dict with structure:
        {
            "type": "game_state",
            "game": {...},
            "self": {...},
            "opponents": [...],
            "discard_pile": {...}
        }
    """

    # === SELF HAND ===
    # Player knows their own initial glance (slots 0-1)
    # Plus any cards they've learned about through gameplay
    self_hand = []
    self_player = game_state.players[player_id]

    for slot_idx, card in enumerate(self_player.hand):
        if card is None:
            # Slot was quick-discarded
            self_hand.append({"known": False})
        else:
            # Check if this player knows this card
            # Initially: know slots 0-1 from initial glance
            # Later: know if card.known_by contains our player_id
            is_initially_known = slot_idx < 2  # Slots 0-1 from initial glance
            is_learned = player_id in card.known_by  # Learned through powers/gameplay

            if is_initially_known or is_learned:
                # Player knows this card
                self_hand.append(
                    {
                        "rank": card.rank.name,
                        "suit": card.suit.name,
                        "known": True,
                    }
                )
            else:
                # Card is in player's hand but they haven't learned it yet
                # (shouldn't happen in normal play, but handle it)
                self_hand.append({"known": False})

    # === OPPONENTS ===
    # For each opponent, show only what this player knows about them
    opponents = []
    for opp_id in game_state.player_order:
        if opp_id == player_id:
            continue

        opp_player = game_state.players[opp_id]

        # Opponent's hand: only show cards that THIS player knows about
        # (via Spy, Decree, or discard pile visibility)
        known_opponent_cards = []
        for slot_idx, card in enumerate(opp_player.hand):
            if card and player_id in card.known_by:
                # This player knows this card
                known_opponent_cards.append(
                    {
                        "slot": slot_idx,
                        "rank": card.rank.name,
                        "suit": card.suit.name,
                    }
                )

        opponents.append(
            {
                "player_id": opp_id,
                "hand_count": opp_player.hand_size,
                "known_cards": known_opponent_cards,
                "spied_slots": list(
                    opp_player.spied_slots
                ),  # Slots opponent knows WE spied
                "score": game_state.scores.get(opp_id, 0),
            }
        )

    # === DISCARD PILE ===
    # Public to all players
    discard_pile_cards = []
    for card in game_state.discard_pile:
        discard_pile_cards.append(
            {
                "rank": card.rank.name,
                "suit": card.suit.name,
            }
        )

    # === ASSEMBLE RESPONSE ===
    return {
        "type": "game_state",
        "game": {
            "game_id": game_state.game_id,
            "phase": str(game_state.phase),
            "current_player": game_state.current_player,
            "round_number": game_state.round_number,
        },
        "self": {
            "player_id": player_id,
            "hand": self_hand,
            "score": game_state.scores.get(player_id, 0),
            "position": game_state.player_order.index(player_id),
        },
        "opponents": opponents,
        "discard_pile": {
            "count": len(game_state.discard_pile),
            "visible_cards": discard_pile_cards,
        },
    }
