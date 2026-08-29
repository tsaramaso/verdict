# api/src/app/websocket_helpers.py
"""
WebSocket state scoping and helper functions.
Converts GameState into player-scoped views for WebSocket transmission.

Reference: WEBSOCKET_STATE_SCOPING_CORRECTED.md
"""

from loguru import logger
from src.app.engine.state import GameState


def scope_state_for_player(
    game_state: GameState, player_id: str, player_names: dict[str, str] | None = None
) -> dict:
    """
    Return only what this player should see.

    Scoping rules:
    - Self hand: slots 0-1 are "known" (initial glance), others unknown
      unless card.known_by contains this player
    - Opponent hands: only card count visible, no card details
    - Opponent knowledge: which opponents know YOUR slots (for 👁️ icon)
    - Trial state: full trial tracking for button eligibility gating
    - Discard pile: all visible cards shown

    Args:
        game_state: Full GameState from registry
        player_id: Player UUID receiving this state
        player_names: Optional dict mapping player_id -> player_name for responses

    Returns:
        Dict with structure:
        {
            "type": "game_state",
            "game": {...},
            "self": {...},
            "opponents": [...],
            "my_opponent_knowledge": {...},
            "trial": {...},
            "discard_pile": {...}
        }
    """
    if player_names is None:
        player_names = {}

    # === SELF HAND ===
    # Player knows their own initial glance (slots 0-1)
    # Plus any cards they've learned about through gameplay
    self_hand = []
    self_player = game_state.players[player_id]

    logger.debug(
        f"[HAND_DEBUG] Player {player_id[:8]} hand before scoping",
        hand_length=len(self_player.hand),
        hand_state=[
            f"Slot{i}: {c.rank.name if c else 'None'}"
            for i, c in enumerate(self_player.hand)
        ],
    )

    for slot_idx, card in enumerate(self_player.hand):
        if card is None:
            # Slot was quick-discarded
            logger.debug(
                f"[HAND_DEBUG] Slot {slot_idx}: None (discarded) → sending null"
            )
            self_hand.append(None)
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
                "player_name": player_names.get(opp_id, "Unknown"),  # Include name
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

    # === MY OPPONENT KNOWLEDGE ===
    # Which opponents know about YOUR slots (unified "Opponent Knows" icon)
    # Scoping rule: For each opponent, if they're in any of your cards' known_by,
    # they know that slot.
    my_opponent_knowledge: dict[str, list[int]] = {}
    self_player = game_state.players[player_id]
    for slot_idx, card in enumerate(self_player.hand):
        if card is None:
            # Empty slot (quick-discarded)
            continue
        # Who knows about this slot?
        for opponent_id in game_state.player_order:
            if opponent_id == player_id:
                continue
            if opponent_id in card.known_by:
                # This opponent knows this card (hence knows this slot)
                if opponent_id not in my_opponent_knowledge:
                    my_opponent_knowledge[opponent_id] = []
                my_opponent_knowledge[opponent_id].append(slot_idx)

    # === TRIAL STATE ===
    # Include full trial state for button eligibility gating
    trial_state = {
        "first_window_callers": game_state.trial.first_window_callers,
        "passed_first": list(game_state.trial.passed_first),
        "cross_callers": game_state.trial.cross_callers,
        "passed_cross": list(game_state.trial.passed_cross),
        "perjury_removed": list(game_state.trial.perjury_removed),
        "truly_eligible": game_state.trial.truly_eligible,
        "challenged": list(game_state.trial.challenged),
        "passed_challenge": list(game_state.trial.passed_challenge),
        "duel_occurred": game_state.trial.duel_occurred,
        "duel_winners": game_state.trial.duel_winners,
        "plea_taken": list(game_state.trial.plea_taken),
        "plea_declined": list(game_state.trial.plea_declined),
    }

    # === RULES ===
    # Include the game rules for UI initialization and card value lookup
    rules_dict = (
        game_state.rules.model_dump()
        if hasattr(game_state.rules, "model_dump")
        else {
            "red_king_value": game_state.rules.red_king_value,
            "black_king_value": game_state.rules.black_king_value,
            "hand_size": game_state.rules.hand_size,
            "nb_of_starting_draw": game_state.rules.nb_of_starting_draw,
            "eligible_threshold": game_state.rules.eligible_threshold,
            "min_players": game_state.rules.min_players,
            "max_players": game_state.rules.max_players,
            "perjury_penalty": game_state.rules.perjury_penalty,
            "duel_loss_penalty": game_state.rules.duel_loss_penalty,
            "false_cross_testimony_penalty": game_state.rules.false_cross_testimony_penalty,
            "plea_penalty": game_state.rules.plea_penalty,
            "renaissance_thresholds": game_state.rules.renaissance_thresholds,
            "game_over_score": game_state.rules.game_over_score,
            "rank_values": game_state.rules.rank_values,
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
            "player_name": game_state.players[player_id].player_name,
            "hand": self_hand,
            "score": game_state.scores.get(player_id, 0),
            "position": game_state.player_order.index(player_id),
        },
        "opponents": opponents,
        "my_opponent_knowledge": my_opponent_knowledge,
        "trial": trial_state,
        "discard_pile": {
            "count": len(game_state.discard_pile),
            "visible_cards": discard_pile_cards,
        },
        "rules": rules_dict,
    }
