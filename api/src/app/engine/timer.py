from src.app.engine.state import Phase

PHASE_TIMERS: dict[Phase, int | float] = {
    Phase.TURN_START: 10,
    Phase.DRAWING: 10,
    Phase.AWAITING_ACTION: 10,
    Phase.AWAITING_SPELL_INVOCATION: 10,
    Phase.AWAITING_SPELL_SWAP_DECISION: 10,
    Phase.AWAITING_QUICK_DISCARD: 10,
    Phase.AWAITING_CALL_WINDOW: 10,
    Phase.AWAITING_MATCH_WINDOW: 10,
    Phase.AWAITING_DUEL_WINDOW: 10,
    Phase.AWAITING_FINAL_PLEA_WINDOW: 10,
    Phase.ROUND_OVER: 10,
    Phase.GAME_OVER: 10,
}
OTHER_TIMERS: dict[str, int | float] = {
    "MIN_COLLECTION_WINDOW": 2,
    "MAX_COLLECTION_WINDOW": 12.0,
    "TIMEOUT_GRACE_PERIOD": 0.5,
    "TIMER_WARNING_THRESHOLD": 3,
    "TIMER_CRITICAL_THRESHOLD": 1,
}

# ============================================
# PHASE GROUPINGS
# ============================================

SIMULTANEOUS_PHASES = frozenset(
    [
        Phase.AWAITING_QUICK_DISCARD,
        Phase.AWAITING_CALL_WINDOW,
        Phase.AWAITING_MATCH_WINDOW,
        Phase.AWAITING_DUEL_WINDOW,
        Phase.AWAITING_FINAL_PLEA_WINDOW,
    ]
)

SINGLE_PLAYER_PHASES = frozenset(
    [
        Phase.DRAWING,
        Phase.AWAITING_ACTION,
        Phase.AWAITING_SPELL_INVOCATION,
        Phase.AWAITING_SPELL_SWAP_DECISION,
    ]
)

NO_TIMER_PHASES = frozenset(
    [
        Phase.TURN_START,
        Phase.ROUND_OVER,
        Phase.GAME_OVER,
    ]
)

TIMED_PHASES = SIMULTANEOUS_PHASES | SINGLE_PLAYER_PHASES
