/**
 * src/lib/actions/gameActions.ts
 * Centralized game action handlers + timeout fallbacks
 *
 * All API calls go through here. Single source of truth for game logic.
 * Each handler accepts gameId, payload, and optional callbacks.
 * Fallback functions handle timeout auto-actions per phase.
 */

import { API_ENDPOINTS, getFullUrl } from '$lib/constants/api';
import { apiCall } from '$lib/api';

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
		console.error('[gameActions] drawFromDeck exception:', error);
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
		console.error('[gameActions] drawFromDiscard exception:', error);
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
		const endpoint = `/games/${gameId}/advance-phase`;
		console.log('[gameActions] advancePhase: POST to', endpoint);
		await apiCall(endpoint, { method: 'POST' });
		console.log('[gameActions] advancePhase: Success');
		return true;
	} catch (error) {
		console.error('[gameActions] advancePhase failed:', error);
		return false;
	}
}

export async function timeoutDrawing(gameId: string): Promise<boolean> {
	return await drawFromDiscard(gameId).then((result) => !!result);
}

export async function timeoutAction(gameId: string, source: 'deck' | 'discard'): Promise<boolean> {
	if (source === 'deck') {
		return await discardImmediate(gameId, source);
	} else {
		return await passBack(gameId);
	}
}

export async function timeoutSpell(gameId: string): Promise<boolean> {
	return await declinePower(gameId);
}

export async function timeoutQuickDiscard(gameId: string): Promise<boolean> {
	// No action needed, game continues
	return true;
}

export async function timeoutTestifyWindow(gameId: string): Promise<boolean> {
	// No action needed, player passes automatically
	return true;
}

export async function timeoutDuelWindow(gameId: string): Promise<boolean> {
	// No action needed, player didn't challenge
	return true;
}

export async function timeoutPleaWindow(gameId: string): Promise<boolean> {
	// No action needed, player declines plea (takes true sum)
	return true;
}