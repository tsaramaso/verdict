/**
 * src/lib/actions/gameActions.ts
 * Centralized game action handlers + timeout fallbacks
 *
 * All API calls go through here. Single source of truth for game logic.
 * Each handler accepts gameId, payload, and optional callbacks.
 * Fallback functions handle timeout auto-actions per phase.
 */

import { API_ENDPOINTS, apiCall } from '$lib/api';

// ============================================
// DRAW PHASE HANDLERS
// ============================================

export async function drawFromDeck(
	gameId: string
): Promise<{ drawn_card?: { rank: string; suit: string } } | null> {
	try {
		const endpoint = API_ENDPOINTS.draw(gameId);
		console.log('[gameActions] drawFromDeck: POST to', endpoint);
		const data = await apiCall(endpoint, {
			method: 'POST',
			body: JSON.stringify({ source: 'deck' })
		});
		console.log('[gameActions] drawFromDeck: Success', data);
		return data;
	} catch (error) {
		console.error(
			'[gameActions] drawFromDeck exception:',
			error instanceof Error ? error.message : error
		);
		return null;
	}
}

export async function drawFromDiscard(
	gameId: string
): Promise<{ drawn_card?: { rank: string; suit: string } } | null> {
	try {
		const endpoint = API_ENDPOINTS.draw(gameId);
		console.log('[gameActions] drawFromDiscard: POST to', endpoint);
		const data = await apiCall(endpoint, {
			method: 'POST',
			body: JSON.stringify({ source: 'discard' })
		});
		console.log('[gameActions] drawFromDiscard: Success', data);
		return data;
	} catch (error) {
		console.error(
			'[gameActions] drawFromDiscard exception:',
			error instanceof Error ? error.message : error
		);
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
		console.error('[discardImmediate] Error:', error);
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
		console.error('[swapCard] Error:', error);
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
		console.error('[passBack] Error:', error);
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
		console.error('[invokePower] Error:', error);
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
		console.error('[declinePower] Error:', error);
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
		console.error('[decreeSwap] Error:', error);
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
		console.error('[quickDiscard] Error:', error);
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
		console.error('[testifyFirst] Error:', error);
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
		console.error('[testifyCross] Error:', error);
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
		console.error('[challenge] Error:', error);
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
		console.error('[takePlea] Error:', error);
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
		console.error('[declinePlea] Error:', error);
		return false;
	}
}

// ============================================
// PHASE ADVANCEMENT (for TURN_START → DRAWING)
// ============================================

export async function advancePhase(gameId: string): Promise<boolean> {
	try {
		const endpoint = API_ENDPOINTS.advancePhase(gameId);
		console.log('[gameActions] advancePhase: POST to', endpoint);
		await apiCall(endpoint, { method: 'POST' });
		console.log('[gameActions] advancePhase: Success');
		return true;
	} catch (error) {
		console.error('[gameActions] advancePhase failed:', error);
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
		const endpoint = `${API_ENDPOINTS.timeout(gameId)}`;
		console.log('[gameActions] submitTimeout:', endpoint);

		const data = await apiCall(endpoint, {
			method: 'POST'
		});

		console.log('[gameActions] submitTimeout success:', data);
		return true;
	} catch (error) {
		console.error('[gameActions] submitTimeout error:', error);
		return false;
	}
}

/**
 * Legacy timeout handlers (kept for compatibility, now delegates to submitTimeout).
 * Each phase still has its own method for clarity in call sites.
 */

export async function timeoutDrawing(gameId: string): Promise<boolean> {
	console.log('[gameActions] timeoutDrawing → submitTimeout(DRAWING)');
	return await submitTimeout(gameId, 'DRAWING');
}

export async function timeoutAction(gameId: string, source: 'deck' | 'discard'): Promise<boolean> {
	// Server uses draw_source from state, no need to pass here
	console.log('[gameActions] timeoutAction → submitTimeout(AWAITING_ACTION)');
	return await submitTimeout(gameId, 'AWAITING_ACTION');
}

export async function timeoutSpell(gameId: string): Promise<boolean> {
	console.log('[gameActions] timeoutSpell → submitTimeout(AWAITING_SPELL_INVOCATION)');
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
		const endpoint = `${API_ENDPOINTS.closePhaseWindow(gameId)}`;
		console.log('[gameActions] closePhaseWindow:', endpoint);

		const data = await apiCall(endpoint, {
			method: 'POST'
		});

		console.log('[gameActions] closePhaseWindow success:', data);
		return true;
	} catch (error) {
		console.error('[gameActions] closePhaseWindow error:', error);
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
	console.log(`[gameActions] Local response logged for phase: ${phase}`);
	// Can be used for optimistic UI updates (e.g., disable button if already voted)
}
