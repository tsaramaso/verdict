# src/app/engine/events.py
"""
The event envelope, matching events_and_logging.md §2 field-for-field.
This is the ONE shape every event uses — the engine never emits
anything else. `scoped_fields` values are ScopedField instances; an
empty `visible_to` list is valid and means "recorded truth, visible to
no one live" (e.g. true_eligibility, shuffle_seed).

`EventType` here is the schema-level enforcement of events_and_logging.md
§1.3: one member per event type, each traceable to exactly one edge/node
in game_flow.mermaid.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum, auto
from uuid import uuid4


class EventType(StrEnum):
    # 3.1 Game & round lifecycle
    GAME_STARTED = auto()
    ROUND_STARTED = auto()
    INITIAL_GLANCE = auto()
    TURN_START_ADVANCED = auto()  # TURN_START → DRAWING phase transition
    ROUND_ENDED = auto()
    SCORES_UPDATED = auto()
    RENAISSANCE_TRIGGERED = auto()
    GAME_ENDED = auto()

    # 3.2 Turn — draw & action
    CARD_DRAWN = auto()
    ACTION_TAKEN = auto()

    # 3.3 Power cards
    SPELL_INVOCATION_DECISION = auto()
    SPELL_REVEALED = auto()
    SPELL_SWAP_DECISION = auto()

    # 3.4 Quick-discard
    QUICK_DISCARD_PLAYED = auto()

    # 3.5 The Trial
    TESTIMONY_GIVEN = auto()
    TESTIMONY_WINDOW_PASSED = auto()
    CHALLENGE_GIVEN = auto()
    CHALLENGE_WINDOW_PASSED = auto()
    PERJURY_CHECK_RESOLVED = auto()
    DUEL_RESOLVED = auto()
    PLEA_TAKEN = auto()
    PLEA_WINDOW_PASSED = auto()
    HAND_EMPTIED = auto()


@dataclass
class ScopedField:
    visible_to: list[str]
    value: object

    def to_dict(self) -> dict:
        return {"visible_to": self.visible_to, "value": self.value}


@dataclass
class Event:
    type: EventType
    game_id: str
    round_id: str | None
    sequence: int
    actor: str | None
    public_fields: dict = field(default_factory=dict)
    scoped_fields: dict[str, ScopedField] = field(default_factory=dict)
    turn_id: str | None = None
    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "game_id": self.game_id,
            "round_id": self.round_id,
            "turn_id": self.turn_id,
            "sequence": self.sequence,
            "timestamp": self.timestamp.isoformat(),
            "type": self.type,
            "actor": self.actor,
            "public_fields": self.public_fields,
            "scoped_fields": {k: v.to_dict() for k, v in self.scoped_fields.items()},
        }

    def payload_for(self, player_id: str | None) -> dict:
        """
        What a specific player (or None for an unauthenticated/spectator
        context, which currently sees only public_fields) is allowed to
        receive over the wire. This is the ONE place scoping is enforced
        for outbound delivery — see events_and_logging.md §1.4.
        """
        visible_scoped = {
            k: v.value
            for k, v in self.scoped_fields.items()
            if player_id is not None and player_id in v.visible_to
        }
        return {
            "event_id": self.event_id,
            "type": self.type,
            "sequence": self.sequence,
            "actor": self.actor,
            "public_fields": self.public_fields,
            "scoped_fields": visible_scoped,
        }