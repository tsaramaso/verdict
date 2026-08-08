# src/app/engine/cards.py
"""
Card identity persists across swaps (rules.md §7: "any knowledge a
player already had about a specific card correctly follows it to its
new slot/owner"). We model that literally: each physical Card instance
has a stable id and carries its own `known_by` set, which travels with
it wherever it's moved. Slots just hold a reference to a Card or None.

Reconciled understanding of `known_by` (see project chat): it's keyed by
card identity, not by slot or by player-memory. A player who knew card X
still knows card X after it moves — they now know WHERE it is (owner +
slot), not what's currently sitting in its old slot, and not the
abstract slot position itself. `known_by` on Card only tracks WHO knows
this card's identity; WHERE each known card currently sits is derived
by looking at where the Card object is referenced in the live
GameState.players[...].hand structure, not stored redundantly here.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field

from src.app.engine.constants import (
    BASE_RULES,
    RED_SUITS,
    Rank,
    Rules,
    Suit,
    card_value,
)


@dataclass
class Card:
    id: str  # stable, unique within one standard 52-card deck
    rank: Rank
    suit: Suit
    black_king_value: int
    red_king_value: int
    # Player IDs who currently know this specific card's identity.
    # Persists across swaps (Smuggle/Decree) by design — it's a property
    # of the card, not the slot.
    known_by: set[str] = field(default_factory=set)

    @property
    def is_red_king(self) -> bool:
        return self.rank is Rank.KING and self.suit in RED_SUITS

    @property
    def value(self) -> int:
        return card_value(
            self.rank, self.suit, self.red_king_value, self.black_king_value
        )

    def to_public_dict(self) -> dict:
        return {"rank": self.rank, "suit": self.suit}


def build_deck(seed: str, rules: Rules = BASE_RULES) -> list[Card]:
    """
    Deterministically reconstructible from `seed` alone — per
    events_and_logging.md, the shuffle seed is what's stored (scoped to
    nobody), never a materialized card-order array.
    """
    cards = [
        Card(
            id=f"{rank.name}-{suit.name}",
            rank=rank,
            suit=suit,
            black_king_value=rules.black_king_value,
            red_king_value=rules.red_king_value,
        )
        for suit in Suit
        for rank in Rank
    ]
    rng = random.Random(seed)
    rng.shuffle(cards)
    return cards
