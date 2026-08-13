// src/lib/constants/phases.ts
/**
 * Game phase enum and related constants.
 * These match the backend GamePhase enum exactly.
 */

export enum GamePhase {
  TURN_START = 'TURN_START',
  DRAWING = 'DRAWING',
  AWAITING_ACTION = 'AWAITING_ACTION',
  AWAITING_SPELL_INVOCATION = 'AWAITING_SPELL_INVOCATION',
  AWAITING_QUICK_DISCARD = 'AWAITING_QUICK_DISCARD',
  AWAITING_CALL_WINDOW = 'AWAITING_CALL_WINDOW',
  AWAITING_MATCH_WINDOW = 'AWAITING_MATCH_WINDOW',
  AWAITING_DUEL_WINDOW = 'AWAITING_DUEL_WINDOW',
  AWAITING_FINAL_PLEA_WINDOW = 'AWAITING_FINAL_PLEA_WINDOW',
  ROUND_OVER = 'ROUND_OVER',
  GAME_OVER = 'GAME_OVER',
}

/**
 * Human-readable phase labels for UI display
 */
export const PHASE_LABELS: Record<GamePhase, string> = {
  [GamePhase.TURN_START]: 'Round Starting',
  [GamePhase.DRAWING]: 'Draw Phase',
  [GamePhase.AWAITING_ACTION]: 'Action Phase',
  [GamePhase.AWAITING_SPELL_INVOCATION]: 'Power Card',
  [GamePhase.AWAITING_QUICK_DISCARD]: 'Quick Discard',
  [GamePhase.AWAITING_CALL_WINDOW]: 'Call Window',
  [GamePhase.AWAITING_MATCH_WINDOW]: 'Match Window',
  [GamePhase.AWAITING_DUEL_WINDOW]: 'Duel',
  [GamePhase.AWAITING_FINAL_PLEA_WINDOW]: 'Final Plea',
  [GamePhase.ROUND_OVER]: 'Round Over',
  [GamePhase.GAME_OVER]: 'Game Over',
};

/**
 * Phase durations in seconds (for timer)
 */
export const PHASE_DURATIONS: Record<GamePhase, number> = {
  [GamePhase.TURN_START]: 3,
  [GamePhase.DRAWING]: 30,
  [GamePhase.AWAITING_ACTION]: 30,
  [GamePhase.AWAITING_SPELL_INVOCATION]: 60,
  [GamePhase.AWAITING_QUICK_DISCARD]: 20,
  [GamePhase.AWAITING_CALL_WINDOW]: 15,
  [GamePhase.AWAITING_MATCH_WINDOW]: 15,
  [GamePhase.AWAITING_DUEL_WINDOW]: 15,
  [GamePhase.AWAITING_FINAL_PLEA_WINDOW]: 15,
  [GamePhase.ROUND_OVER]: 5,
  [GamePhase.GAME_OVER]: 10,
};

/**
 * Phases that have active players (not everyone waits)
 */
export const ACTIVE_PLAYER_PHASES = new Set([
  GamePhase.DRAWING,
  GamePhase.AWAITING_ACTION,
]);

/**
 * Phases that are simultaneous (all players act at once)
 */
export const SIMULTANEOUS_PHASES = new Set([
  GamePhase.AWAITING_QUICK_DISCARD,
  GamePhase.AWAITING_CALL_WINDOW,
  GamePhase.AWAITING_MATCH_WINDOW,
  GamePhase.AWAITING_DUEL_WINDOW,
  GamePhase.AWAITING_FINAL_PLEA_WINDOW,
]);

/**
 * Phases where UI is non-interactive (auto-advance)
 */
export const AUTO_ADVANCE_PHASES = new Set([
  GamePhase.TURN_START,
  GamePhase.ROUND_OVER,
]);
