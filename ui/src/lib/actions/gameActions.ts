/**
 * src/lib/actions/gameActions.ts
 * Centralized game action handlers + timeout fallbacks
 *
 * All API calls go through here. Single source of truth for game logic.
 * Each handler accepts gameId, payload, and optional callbacks.
 * Fallback functions handle timeout auto-actions per phase.
 */

import { API_ENDPOINTS, apiCall } from '$lib/api';
import { getLogger } from '$lib/utils/logger';

const log = getLogger('actions');

// ============================================
// DRAW PHASE HANDLERS
// ============================================

export async function drawFromDeck(
	gameId: string
): Promise<{ drawn_card?: { rank: string; suit: string } } | null> {
	try {
		const data = await apiCall(API_ENDPOINTS.draw(gameId), {
			method: 'POST',
			body: JSON.stringify({ source: 'deck' })
		});
		return data;
	} catch (error) {
		log.error('drawFromDeck_failed', {
			error: error instanceof Error ? error.message : String(error)
		});
		return null;
	}
}

export async function drawFromDiscard(
	gameId: string
): Promise<{ drawn_card?: { rank: string; suit: string } } | null> {
	try {
		const data = await apiCall(API_ENDPOINTS.draw(gameId), {
			method: 'POST',
			body: JSON.stringify({ source: 'discard_pile' })
		});
		return data;
	} catch (error) {
		log.error('drawFromDiscard_failed', {
			error: error instanceof Error ? error.message : String(error)
		});
		return null;
	}
}

// ============================================
// ACTION PHASE HANDLERS
// ============================================

export async function discardImmediate(
	gameId: string,
	source: 'deck' | 'discard'
): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.action(gameId), {
			method: 'POST',
			body: JSON.stringify({ choice: 'discard_immediate', source })
		});
		return true;
	} catch (error) {
		log.error('discardImmediate_failed', { error: String(error) });
		return false;
	}
}

export async function swapCard(
	gameId: string,
	slotIndex: number,
	source: 'deck' | 'discard'
): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.action(gameId), {
			method: 'POST',
			body: JSON.stringify({ choice: 'swap', slot_index: slotIndex, source })
		});
		return true;
	} catch (error) {
		log.error('swapcard_failed', { error: error} );
		return false;
	}
}

export async function passBack(gameId: string): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.action(gameId), {
			method: 'POST',
			body: JSON.stringify({ choice: 'pass_back', source: 'discard' })
		});
		return true;
	} catch (error) {
		log.error('passback_failed', { error: error} );
		return false;
	}
}

// ============================================
// SPELL POWER HANDLERS
// ============================================

export async function invokePower(
	gameId: string,
	ownSlotIndex?: number,
	targetOwner?: string,
	targetIndex?: number
): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.power.invoke(gameId), {
			method: 'POST',
			body: JSON.stringify({
				own_slot: ownSlotIndex,
				target_player_id: targetOwner,
				target_slot: targetIndex
			})
		});
		return true;
	} catch (error) {
		log.error('invokepower_failed', { error: error });
		return false;
	}
}

export async function declinePower(gameId: string): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.power.decline(gameId), {
			method: 'POST'
		});
		return true;
	} catch (error) {
		log.error('declinepower_failed', { error: error });
		return false;
	}
}

export async function decreeSwap(
	gameId: string,
	swap: boolean,
	ownSlotIndex?: number
): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.power.decreeSwap(gameId), {
			method: 'POST',
			body: JSON.stringify({ swap, own_slot: ownSlotIndex })
		});
		return true;
	} catch (error) {
		log.error('decreeswap_failed', { error: error });
		return false;
	}
}

// ============================================
// QUICK DISCARD HANDLER
// ============================================

export async function quickDiscard(gameId: string, slotIndex: number): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.quickDiscard(gameId), {
			method: 'POST',
			body: JSON.stringify({ slot_index: slotIndex })
		});
		return true;
	} catch (error) {
		log.error('quickdiscard_failed', { error: error} );
		return false;
	}
}

// ============================================
// TRIAL PHASE HANDLERS
// ============================================

export async function testifyFirst(gameId: string): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.trial.testifyFirst(gameId), {
			method: 'POST'
		});
		return true;
	} catch (error) {
		log.error('testifyfirst_failed', { error: error} );
		return false;
	}
}

export async function testifyCross(gameId: string): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.trial.testifyCross(gameId), {
			method: 'POST'
		});
		return true;
	} catch (error) {
		log.error('testifycross_failed', { error: error});
		return false;
	}
}

export async function challenge(gameId: string): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.trial.challenge(gameId), {
			method: 'POST'
		});
		return true;
	} catch (error) {
		log.error('challenge_failed', { error: error});
		return false;
	}
}

export async function takePlea(gameId: string): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.trial.plea(gameId), {
			method: 'POST',
			body: JSON.stringify({ plea: true })
		});
		return true;
	} catch (error) {
		log.error('takeplea_failed', { error: error});
		return false;
	}
}

export async function declinePlea(gameId: string): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.trial.plea(gameId), {
			method: 'POST',
			body: JSON.stringify({ plea: false })
		});
		return true;
	} catch (error) {
		log.error('declineplea_failed', { error: error});
		return false;
	}
}

// ============================================
// PHASE ADVANCEMENT (for TURN_START → DRAWING)
// ============================================

export async function advancePhase(gameId: string): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.advancePhase(gameId), { method: 'POST' });
		return true;
	} catch (error) {
		log.error('advancePhase_failed', {
			error: error instanceof Error ? error.message : String(error)
		});
		return false;
	}
}

// ============================================
// SINGLE-PLAYER TIMEOUT (replaces old handlers)
// ============================================

/**
 * Send timeout validation to server for single-player phases.
 * Server validates phase match + elapsed time before applying fallback.
 */
export async function submitTimeout(gameId: string, phase: string): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.timeout(gameId), {
			method: 'POST'
		});
		return true;
	} catch (error) {
		log.error('submitTimeout_failed', {
			phase,
			error: error instanceof Error ? error.message : String(error)
		});
		return false;
	}
}

/**
 * Legacy timeout handlers (kept for compatibility, now delegates to submitTimeout).
 * Each phase still has its own method for clarity in call sites.
 */

export async function timeoutDrawing(gameId: string): Promise<boolean> {
	return await submitTimeout(gameId, 'DRAWING');
}

export async function timeoutAction(gameId: string, source: 'deck' | 'discard'): Promise<boolean> {
	// Server uses draw_source from state, no need to pass here
	return await submitTimeout(gameId, 'AWAITING_ACTION');
}

export async function timeoutSpell(gameId: string): Promise<boolean> {
	return await submitTimeout(gameId, 'AWAITING_SPELL_INVOCATION');
}

export async function timeoutQuickDiscard(gameId: string): Promise<boolean> {
	// Server will auto-close collection window. Client can request early close.
	return await closePhaseWindow(gameId);
}

export async function timeoutTestifyWindow(gameId: string): Promise<boolean> {
	// Server will auto-close collection window. Client can request early close.
	return await closePhaseWindow(gameId);
}

export async function timeoutDuelWindow(gameId: string): Promise<boolean> {
	return await closePhaseWindow(gameId);
}

export async function timeoutPleaWindow(gameId: string): Promise<boolean> {
	return await closePhaseWindow(gameId);
}

/**
 * Manually close phase collection window (all players responded or minimum wait time passed).
 * Server validates before closing.
 */
export async function closePhaseWindow(gameId: string): Promise<boolean> {
	try {
		await apiCall(API_ENDPOINTS.closePhaseWindow(gameId), {
			method: 'POST'
		});
		return true;
	} catch (error) {
		log.error('closePhaseWindow_failed', {
			error: error instanceof Error ? error.message : String(error)
		});
		return false;
	}
}

// ============================================
// RESPONSE LOGGING (Optional Client-side)
// ============================================

/**
 * Optional: Log that player has submitted action in simultaneous phase.
 * Server tracks this via endpoint call (action routes call log_player_response).
 * This is informational only; server is source of truth.
 */
export function logLocalResponse(phase: string): void {
	log.debug('player_response_logged', { phase });
	// Can be used for optimistic UI updates (e.g., disable button if already voted)
}