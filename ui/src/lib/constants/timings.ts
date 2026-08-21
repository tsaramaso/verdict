/**
 * src/lib/constants/timings.ts
 * Game phase timings reference
 * 
 * All values in milliseconds (ms).
 * 
 * TUNING GUIDE:
 * Run actual games, watch how fast/slow phases feel, update values below.
 * Changes take effect on next game (hot reload enabled).
 * 
 * Format: PHASE_NAME: milliseconds
 */

// Re-export from config for convenience + add detailed comments
import { TIMERS } from '../config';

/**
 * PHASE TIMINGS (milliseconds)
 * 
 * These are per-phase duration defaults.
 * When phase starts, a timer with this duration is shown to players.
 * On timeout, fallback action fires automatically.
 * 
 * Adjust based on:
 * - Are players rushed? Increase timer
 * - Do phases feel slow/boring? Decrease timer
 * - Trial windows simultaneous? Can be shorter (less wait)
 * - Turn phases sequential? Might need longer (active player slowness)
 */

export const PHASE_TIMINGS = {
	/**
	 * TURN_START (3s)
	 * Phase: Auto-advance, no player input needed
	 * Display: Cosmetic flip animation on 2 slots per player
	 * Timeout behavior: Auto-advances (no fallback action)
	 * 
	 * Tuning: Adjust if animation feels too slow/fast
	 */
	TURN_START: TIMERS.TURN_START,

	/**
	 * DRAWING (30s)
	 * Phase: Active player chooses to draw from Deck or Discard
	 * Display: Deck + Discard highlighted
	 * Timeout behavior: Auto-draw from Discard
	 * 
	 * Tuning: 30s allows player to think. Reduce if games stall.
	 */
	DRAWING: TIMERS.DRAWING,

	/**
	 * AWAITING_ACTION (30s)
	 * Phase: Active player decides what to do with drawn card
	 * Actions: Discard Immediate, Swap into slot, Pass Back
	 * Timeout behavior: 
	 *   - If drawn from Deck: Auto-discard immediate
	 *   - If drawn from Discard: Auto-pass back
	 * 
	 * Tuning: 30s for deciding + potentially reading power card
	 */
	AWAITING_ACTION: TIMERS.AWAITING_ACTION,

	/**
	 * AWAITING_SPELL_INVOCATION (15s)
	 * Phase: Player chooses to invoke or skip spell power (7-Q)
	 * Display: Power card name + effect, relevant zones highlighted
	 * Timeout behavior: Auto-skip (decline spell)
	 * 
	 * Tuning: 15s shorter than ACTION because choice is simpler
	 * (either invoke on target or skip, no strategy needed)
	 */
	AWAITING_SPELL_INVOCATION: TIMERS.AWAITING_SPELL_INVOCATION,

	/**
	 * AWAITING_QUICK_DISCARD (10s)
	 * Phase: ALL players can simultaneously quick-discard matching-rank cards
	 * Display: Discard rank highlighted, matching slots in your hand glowing
	 * Timeout behavior: Auto-pass (skip quick-discard, hand unchanged)
	 * 
	 * Tuning: 10s simultaneous window. Can be shorter if quick-discard is rare.
	 * Watch: Do quick-discards happen fast? If yes, 10s is fine.
	 * If players don't realize they can quick-discard, increase timer.
	 */
	AWAITING_QUICK_DISCARD: TIMERS.AWAITING_QUICK_DISCARD,

	/**
	 * AWAITING_CALL_WINDOW (10s)
	 * Phase: ALL players can claim Testimony (call "eligible")
	 * Display: "Give Testimony" button enabled for all
	 * Timeout behavior: Auto-pass (didn't give testimony)
	 * 
	 * Tuning: 10s for simultaneous first-window calls.
	 * Usually quick decision (am I <= 7?), so 10s is reasonable.
	 */
	AWAITING_CALL_WINDOW: TIMERS.AWAITING_CALL_WINDOW,

	/**
	 * AWAITING_MATCH_WINDOW (10s)
	 * Phase: Non-first-callers can join with Cross-Testimony
	 * Display: "Give Cross-Testimony" button (only if didn't testify first)
	 * Timeout behavior: Auto-pass (didn't give cross-testimony)
	 * 
	 * Tuning: 10s for simultaneous cross-window calls.
	 * Same as CALL_WINDOW, should be quick.
	 */
	AWAITING_MATCH_WINDOW: TIMERS.AWAITING_MATCH_WINDOW,

	/**
	 * AWAITING_DUEL_WINDOW (10s)
	 * Phase: Testimony-givers decide to Challenge
	 * Display: "Challenge" button (only if gave testimony)
	 * Timeout behavior: Auto-pass (didn't challenge)
	 * 
	 * Tuning: 10s for challenge decision.
	 * Usually one person challenges (or nobody does), quick decision.
	 */
	AWAITING_DUEL_WINDOW: TIMERS.AWAITING_DUEL_WINDOW,

	/**
	 * AWAITING_FINAL_PLEA_WINDOW (10s)
	 * Phase: Eligible bystanders decide to take Plea or true sum
	 * Display: "Take Plea (+25)" or "Decline (true sum)" buttons
	 * Timeout behavior: Auto-decline (take true sum, Renaissance-eligible)
	 * 
	 * Tuning: 10s for plea decision. This is informed (Perjury + Duel resolved),
	 * so should be quick. If players are hesitating, they might need more info.
	 */
	AWAITING_FINAL_PLEA_WINDOW: TIMERS.AWAITING_FINAL_PLEA_WINDOW,

	/**
	 * ROUND_OVER (10s)
	 * Phase: Display round verdict (scores, perjury, duel results, plea outcomes)
	 * Display: Modal overlay with summary
	 * Timeout behavior: Auto-advance to next round or game over
	 * 
	 * Tuning: 10s to read verdicts. Players can click to advance immediately.
	 * If players are always waiting full 10s, increase. If they skip early, decrease.
	 */
	ROUND_OVER: TIMERS.ROUND_OVER,

	/**
	 * GAME_OVER (10s)
	 * Phase: Display final standings + 1st/2nd/3rd ranking
	 * Display: Modal overlay with final scores
	 * Timeout behavior: Auto-dismiss to home menu (or allow manual return)
	 * 
	 * Tuning: 10s to admire winner. Can be longer for celebration.
	 */
	GAME_OVER: TIMERS.GAME_OVER
} as const;

/**
 * TIMER COLOR THRESHOLDS (milliseconds)
 * 
 * Timer component uses these to change color as countdown approaches 0:
 * - Green: Normal
 * - Yellow: Below TIMER_WARNING_THRESHOLD
 * - Red + Pulsing: Below TIMER_CRITICAL_THRESHOLD
 */
export const TIMER_THRESHOLDS = {
	/**
	 * Below 5 seconds = yellow warning color
	 * Signals "hurry up, time running out"
	 */
	WARNING: TIMERS.TIMER_WARNING_THRESHOLD,

	/**
	 * Below 2 seconds = red critical color + pulsing animation
	 * Signals "act NOW or timeout fires"
	 */
	CRITICAL: TIMERS.TIMER_CRITICAL_THRESHOLD
} as const;

/**
 * ANIMATION TIMINGS (milliseconds)
 * Used for visual transitions (card reveal, swap animations, etc.)
 */
export const ANIMATION_TIMINGS = {
	/**
	 * Card peek animation (reveal + fade back)
	 * When player Glances own slot or Spies opponent slot
	 */
	PEEK_REVEAL: 500, // Time card stays visible
	PEEK_FADE: 300, // Time to fade back to face-down

	/**
	 * Card swap animation (Smuggle, Decree)
	 * When cards exchange positions
	 */
	SWAP_SLIDE: 400, // Smooth slide to new position

	/**
	 * Quick discard card slide out
	 * When quick-discard plays and card leaves hand
	 */
	QUICK_DISCARD_SLIDE: 400,

	/**
	 * Spell invocation modal appear/disappear
	 */
	MODAL_FADE_IN: 200,
	MODAL_FADE_OUT: 150,

	/**
	 * Verdict/outcomes display animation
	 * When round over screen appears
	 */
	VERDICT_APPEAR: 300,

	/**
	 * Renaissance celebration animation
	 * When player hits exactly 50 or 100
	 */
	RENAISSANCE_SPARKLE: 2000 // Duration of sparkle effect
} as const;

/**
 * RED FLAG 🚩: Timer Unit Inconsistency
 * 
 * Current state:
 * - TIMERS object: milliseconds (1000ms = 1s)
 * - TIMER_THRESHOLDS: milliseconds
 * - ANIMATION_TIMINGS: milliseconds
 * 
 * Make sure Timer.svelte component receives milliseconds and converts to seconds for display.
 * Example: 30000ms should display as "0:30" (30 seconds)
 * 
 * If Timer component expects seconds, convert before passing:
 *   duration_seconds = PHASE_TIMINGS.DRAWING / 1000
 */

/**
 * RED FLAG 🚩: Timeout Fallback Actions
 * 
 * Confirm these are implemented in GamePage/API handlers:
 * - DRAWING timeout → auto-draw from discard
 * - ACTION timeout → auto-discard-immediate (if from deck) or auto-pass-back (if from discard)
 * - SPELL timeout → auto-skip spell
 * - QUICK_DISCARD timeout → auto-pass
 * - CALL_WINDOW timeout → auto-pass
 * - MATCH_WINDOW timeout → auto-pass
 * - DUEL_WINDOW timeout → auto-pass
 * - FINAL_PLEA_WINDOW timeout → auto-decline (take true sum)
 * - ROUND_OVER timeout → auto-advance to next round
 * - GAME_OVER timeout → auto-return to lobby
 */

/**
 * HELPER: Get timer duration for a phase (in milliseconds)
 * @param phase GamePhase string
 * @returns Duration in milliseconds
 */
export function getPhaseTimer(phase: string): number {
	return (PHASE_TIMINGS as Record<string, number>)[phase] || 10000;
}

/**
 * HELPER: Convert milliseconds to seconds (for display)
 * @param ms milliseconds
 * @returns seconds (rounded down)
 */
export function msToSeconds(ms: number): number {
	return Math.floor(ms / 1000);
}

/**
 * HELPER: Get color for timer based on remaining time
 * @param remaining milliseconds remaining
 * @param total milliseconds total
 * @returns 'normal' | 'warning' | 'critical'
 */
export function getTimerColor(remaining: number, total: number): 'normal' | 'warning' | 'critical' {
	if (remaining <= TIMER_THRESHOLDS.CRITICAL) return 'critical';
	if (remaining <= TIMER_THRESHOLDS.WARNING) return 'warning';
	return 'normal';
}