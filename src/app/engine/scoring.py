# src/app/engine/scoring.py
"""
Pure scoring computation — takes a concluded Trial's bookkeeping and
returns a bucket + points_added per player, matching rules.md §6.7's
outcome table row for row. No side effects; engine.py calls this once
a Trial (or Empty Hand / Forced End path) has fully resolved, then
emits the ScoresUpdated event from the result.
"""

from __future__ import annotations

from src.app.engine.constants import (
    DUEL_LOSS_PENALTY,
    FALSE_CROSS_TESTIMONY_PENALTY,
    PERJURY_PENALTY,
    PLEA_PENALTY,
    ScoreBucket,
)
from src.app.engine.state import GameState


def compute_trial_scores(state: GameState) -> list[tuple[str, ScoreBucket, int]]:
    trial = state.trial
    results: list[tuple[str, ScoreBucket, int]] = []

    for player_id in state.player_order:
        player = state.players[player_id]

        if player_id in trial.perjury_removed:
            # rules.md §6.7 — capped penalty AND true hand sum, stacked.
            results.append(
                (player_id, ScoreBucket.PERJURY, PERJURY_PENALTY + player.true_sum)
            )
            continue

        if player_id in trial.truly_eligible:
            if trial.duel_occurred:
                if player_id in trial.duel_winners:
                    results.append((player_id, ScoreBucket.DUEL_WINNER, 0))
                else:
                    results.append(
                        (player_id, ScoreBucket.DUEL_LOSER, DUEL_LOSS_PENALTY)
                    )
            else:
                # Covers both "2+ callers, no Challenge" and the solo
                # truly-eligible-caller case — see events_and_logging.md
                # §3.1 bucket-naming note.
                results.append((player_id, ScoreBucket.PLAIN_AGREEMENT, 0))
            continue

        if player_id in trial.cross_callers:
            # In cross_callers but not truly_eligible => false cross
            # testimony. rules.md §6.6 — flat penalty, no matter what
            # else happened (Challenge press is a no-op for them).
            results.append(
                (
                    player_id,
                    ScoreBucket.FALSE_CROSS_TESTIMONY,
                    FALSE_CROSS_TESTIMONY_PENALTY,
                )
            )
            continue

        if player_id in trial.plea_taken:
            results.append((player_id, ScoreBucket.PLEA, PLEA_PENALTY))
            continue

        # Declined Plea at the Final Plea Window (rules.md §6.5) — scored
        # as a true bystander regardless of whether Perjury occurred
        # elsewhere this round; that's an informational difference in
        # rules.md's table, not a scoring difference. See rules.md §6.7.
        results.append((player_id, ScoreBucket.TRUE_BYSTANDER, player.true_sum))

    return results


def compute_bystander_scores(
    state: GameState, empty_hand_trigger: str | None = None
) -> list[tuple[str, ScoreBucket, int]]:
    """
    Used for both the Empty-Hand path (rules.md §5.4/§6.7) and the
    Forced-Round-End-No-Testimony path (rules.md §6.8) — in both cases
    every player is scored as a true bystander, no Perjury check is
    even possible, EXCEPT the empty-hand trigger player themselves
    (if any), who scores flat +0.
    """
    results: list[tuple[str, ScoreBucket, int]] = []
    for player_id in state.player_order:
        if player_id == empty_hand_trigger:
            results.append((player_id, ScoreBucket.EMPTY_HAND_TRIGGER, 0))
            continue
        player = state.players[player_id]
        results.append((player_id, ScoreBucket.TRUE_BYSTANDER, player.true_sum))
    return results
