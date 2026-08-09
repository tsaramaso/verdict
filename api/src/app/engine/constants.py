# src/app/engine/constants.py
"""
Constants sourced directly from rules.md, plus every closed-vocabulary
enum the engine uses.

Convention (decided): every StrEnum value is `auto()` — no hardcoded
string is ever hand-typed as a value here, and nothing anywhere in this
package ever compares an enum against a literal string. Every check is
enum-member-to-enum-member (`rank is Rank.SEVEN`), never member-to-literal
(`rank == "seven"`). A typo in a member name is a NameError/import error
caught immediately; a typo in a hardcoded string is invisible until it's
hit at runtime. That trade costs us the doc-literal wire casing
(rules.md's "Q", events_and_logging.md's "CardDrawn") — StrEnum + auto()
gives lowercase snake_case values instead. If byte-for-byte doc casing is
ever wanted on the wire (e.g. for the analysis layer), that's a
deliberate, explicit translation step at the serialization boundary —
not something threaded back through engine logic.

If you're tempted to add a new magic number, it belongs in rules.md
first, not here.
"""

from enum import StrEnum, auto

from pydantic import BaseModel

RED_KING_VALUE = 0
BLACK_KING_VALUE = 13
HAND_SIZE = 4  # rules.md §3
ELIGIBLE_THRESHOLD = 7  # rules.md §1 glossary — "Eligible"
MIN_PLAYERS = 2  # rules.md §3, confirmed
MAX_PLAYERS = 5  # rules.md §3, confirmed
PERJURY_PENALTY = 25  # rules.md §6.7 — capped +25, stacked with true sum
DUEL_LOSS_PENALTY = 50  # rules.md §6.7
FALSE_CROSS_TESTIMONY_PENALTY = 25  # rules.md §6.7
PLEA_PENALTY = 25  # rules.md §6.7
RENAISSANCE_THRESHOLDS = {50: 25, 100: 50}  # rules.md §9 — landing on X resets to Y
GAME_OVER_SCORE = 120  # rules.md §10 — hard wall, no Renaissance protection

# --- Cards ---------------------------------------------------------------


class Suit(StrEnum):
    HEARTS = auto()
    DIAMONDS = auto()
    CLUBS = auto()
    SPADES = auto()


RED_SUITS = frozenset({Suit.HEARTS, Suit.DIAMONDS})
BLACK_SUITS = frozenset({Suit.CLUBS, Suit.SPADES})


class Rank(StrEnum):
    ACE = auto()
    TWO = auto()
    THREE = auto()
    FOUR = auto()
    FIVE = auto()
    SIX = auto()
    SEVEN = auto()
    EIGHT = auto()
    NINE = auto()
    TEN = auto()
    JACK = auto()
    QUEEN = auto()
    KING = auto()


# rules.md §4 — face value per rank. King is excluded here and handled
# separately in card_value(), since its value depends on suit color too.
RANK_FACE_VALUE: dict[Rank, int] = {
    Rank.ACE: 1,
    Rank.TWO: 2,
    Rank.THREE: 3,
    Rank.FOUR: 4,
    Rank.FIVE: 5,
    Rank.SIX: 6,
    Rank.SEVEN: 7,
    Rank.EIGHT: 8,
    Rank.NINE: 9,
    Rank.TEN: 10,
    Rank.JACK: 11,
    Rank.QUEEN: 12,
}


def card_value(
    rank: Rank, suit: Suit, red_king_value: int, black_king_value: int
) -> int:
    """rules.md §4: black King = 13, red King = 0, everything else fixed."""
    if rank is Rank.KING:
        return red_king_value if suit in RED_SUITS else black_king_value
    return RANK_FACE_VALUE[rank]


# --- Powers (rules.md §7) -------------------------------------------------


class Power(StrEnum):
    GLANCE = auto()  # 7 or 8 — view one of your own slots
    SPY = auto()  # 9 or 10 — view one of an opponent's slots
    SMUGGLE = auto()  # J — blind swap, your slot <-> opponent's slot
    DECREE = auto()  # Q — peek an opponent's slot, then optional swap


POWER_RANKS: frozenset[Rank] = frozenset(
    {Rank.SEVEN, Rank.EIGHT, Rank.NINE, Rank.TEN, Rank.JACK, Rank.QUEEN}
)

_POWER_BY_RANK: dict[Rank, Power] = {
    Rank.SEVEN: Power.GLANCE,
    Rank.EIGHT: Power.GLANCE,
    Rank.NINE: Power.SPY,
    Rank.TEN: Power.SPY,
    Rank.JACK: Power.SMUGGLE,
    Rank.QUEEN: Power.DECREE,
}


def power_for_rank(rank: Rank) -> Power | None:
    return _POWER_BY_RANK.get(rank)


# --- Turn — draw & action (rules.md §5) -----------------------------------


class DrawSource(StrEnum):
    DECK = auto()
    DISCARD_PILE = auto()


class ActionChoice(StrEnum):
    DISCARD_IMMEDIATE = auto()
    SWAP = auto()
    PASS_BACK = auto()


# --- Power resolution ------------------------------------------------------


class SpellDecision(StrEnum):
    INVOKED = auto()
    DECLINED = auto()


class SwapDecision(StrEnum):
    """Decree's optional swap. Smuggle always logs SWAP (mandatory once
    invoked, per events_and_logging.md §3.3)."""

    SWAP = auto()
    NONE = auto()


# --- The Trial (rules.md §6) ----------------------------------------------


class TestimonyWindow(StrEnum):
    FIRST = auto()
    CROSS = auto()


class TrialResolution(StrEnum):
    """How the Duel Window itself closed. Distinct from ScoreBucket below:
    this describes the WINDOW's resolution path; ScoreBucket describes
    each PLAYER's individual outcome."""

    DUEL = auto()
    PLAIN_AGREEMENT = auto()


class RoundEndReason(StrEnum):
    TRIAL = auto()
    EMPTY_HAND = auto()
    FORCED_END = auto()


class ScoreBucket(StrEnum):
    """rules.md §6.7 full outcome table. No `solo_winner` bucket — the
    zero-Duel single-caller case shares PLAIN_AGREEMENT, see
    events_and_logging.md §3.1 bucket-naming note."""

    PERJURY = auto()
    DUEL_WINNER = auto()
    DUEL_LOSER = auto()
    PLAIN_AGREEMENT = auto()
    FALSE_CROSS_TESTIMONY = auto()
    PLEA = auto()
    TRUE_BYSTANDER = auto()
    EMPTY_HAND_TRIGGER = auto()  # the player who emptied their hand

    @property
    def renaissance_eligible(self) -> bool:
        # rules.md §9 — only a genuine true-hand-sum result can trigger
        # Renaissance. TRUE_BYSTANDER is the only bucket whose score
        # effect IS the true hand sum. (Perjury's true-sum component is
        # explicitly blocked despite being a real addition — rules.md §9.)
        return self is ScoreBucket.TRUE_BYSTANDER


# --- Game-level (rules.md §3) ----------------------------------------------


class TurnDirection(StrEnum):
    CLOCKWISE = auto()
    COUNTERCLOCKWISE = auto()


class Rules(BaseModel):
    red_king_value: int
    black_king_value: int
    hand_size: int
    nb_of_starting_draw: int
    eligible_threshold: int
    min_players: int
    max_players: int
    perjury_penalty: int
    duel_loss_penalty: int
    false_cross_testimony_penalty: int
    plea_penalty: int
    renaissance_thresholds: dict[int, int]
    game_over_score: int


BASE_RULES = Rules(
    red_king_value=0,
    black_king_value=13,
    hand_size=4,
    nb_of_starting_draw=2,
    eligible_threshold=7,
    min_players=2,
    max_players=5,
    perjury_penalty=25,
    duel_loss_penalty=50,
    false_cross_testimony_penalty=25,
    plea_penalty=25,
    renaissance_thresholds={50: 25, 100: 50},
    game_over_score=120,
)

# Sanity check, not a runtime guard against user input: every Suit member
# is classified as exactly one of red/black. Catches a maintenance mistake
# (e.g. a new Suit member added without updating RED_SUITS/BLACK_SUITS),
# not anything a player could trigger.
assert RED_SUITS | BLACK_SUITS == set(Suit)
assert not (RED_SUITS & BLACK_SUITS)
