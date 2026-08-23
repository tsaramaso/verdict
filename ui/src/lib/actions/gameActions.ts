/**
 * src/lib/actions/gameActions.ts
 * Centralized game action handlers + timeout fallbacks
 *
 * All API calls go through here. Single source of truth for game logic.
 * Each handler accepts gameId, payload, and optional callbacks.
 * Fallback functions handle timeout auto-actions per phase.
 */

import { API_ENDPOINTS, getFullUrl } from '$lib/constants/api';

// ============================================
// DRAW PHASE HANDLERS
// ============================================

export async function drawFromDeck(
	gameId: string
): Promise<{ drawn_card?: { rank: string; suit: string } } | null> {
	try {
		const url = getFullUrl(API_ENDPOINTS.draw(gameId));
		console.log('[gameActions] drawFromDeck: POST to', url);
		const response = await fetch(url, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ source: 'deck' })
		});

		console.log('[gameActions] drawFromDeck: Response status', response.status);
		if (!response.ok) {
			const error = await response.text();
			console.error('[gameActions] drawFromDeck failed:', response.status, error);
			return null;
		}

		const data = await response.json();
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
		const url = getFullUrl(API_ENDPOINTS.draw(gameId));
		console.log('[gameActions] drawFromDiscard: POST to', url);
		const response = await fetch(url, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ source: 'discard' })
		});

		console.log('[gameActions] drawFromDiscard: Response status', response.status);
		if (!response.ok) {
			const error = await response.text();
			console.error('[gameActions] drawFromDiscard failed:', response.status, error);
			return null;
		}

		const data = await response.json();
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
		const response = await fetch(getFullUrl(API_ENDPOINTS.action(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ choice: 'discard_immediate', source })
		});

		if (!response.ok) {
			console.error('[discardImmediate] Failed:', response.status);
			return false;
		}

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
		const response = await fetch(getFullUrl(API_ENDPOINTS.action(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ choice: 'swap', slot_index: slotIndex, source })
		});

		if (!response.ok) {
			console.error('[swapCard] Failed:', response.status);
			return false;
		}

		return true;
	} catch (error) {
		console.error('[swapCard] Error:', error);
		return false;
	}
}

export async function passBack(gameId: string): Promise<boolean> {
	try {
		const response = await fetch(getFullUrl(API_ENDPOINTS.action(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ choice: 'pass_back', source: 'discard' })
		});

		if (!response.ok) {
			console.error('[passBack] Failed:', response.status);
			return false;
		}

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
		const response = await fetch(getFullUrl(API_ENDPOINTS.power.invoke(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				own_slot: ownSlotIndex,
				target_player_id: targetOwner,
				target_slot: targetIndex
			})
		});

		if (!response.ok) {
			console.error('[invokePower] Failed:', response.status);
			return false;
		}

		return true;
	} catch (error) {
		console.error('[invokePower] Error:', error);
		return false;
	}
}

export async function declinePower(gameId: string): Promise<boolean> {
	try {
		const response = await fetch(getFullUrl(API_ENDPOINTS.power.decline(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' }
		});

		if (!response.ok) {
			console.error('[declinePower] Failed:', response.status);
			return false;
		}

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
		const response = await fetch(getFullUrl(API_ENDPOINTS.power.decreeSwap(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ swap, own_slot: ownSlotIndex })
		});

		if (!response.ok) {
			console.error('[decreeSwap] Failed:', response.status);
			return false;
		}

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
		const response = await fetch(getFullUrl(API_ENDPOINTS.quickDiscard(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ slot_index: slotIndex })
		});

		if (!response.ok) {
			console.error('[quickDiscard] Failed:', response.status);
			return false;
		}

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
		const response = await fetch(getFullUrl(API_ENDPOINTS.trial.testifyFirst(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' }
		});

		if (!response.ok) {
			console.error('[testifyFirst] Failed:', response.status);
			return false;
		}

		return true;
	} catch (error) {
		console.error('[testifyFirst] Error:', error);
		return false;
	}
}

export async function testifyCross(gameId: string): Promise<boolean> {
	try {
		const response = await fetch(getFullUrl(API_ENDPOINTS.trial.testifyCross(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' }
		});

		if (!response.ok) {
			console.error('[testifyCross] Failed:', response.status);
			return false;
		}

		return true;
	} catch (error) {
		console.error('[testifyCross] Error:', error);
		return false;
	}
}

export async function challenge(gameId: string): Promise<boolean> {
	try {
		const response = await fetch(getFullUrl(API_ENDPOINTS.trial.challenge(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' }
		});

		if (!response.ok) {
			console.error('[challenge] Failed:', response.status);
			return false;
		}

		return true;
	} catch (error) {
		console.error('[challenge] Error:', error);
		return false;
	}
}

export async function takePlea(gameId: string): Promise<boolean> {
	try {
		const response = await fetch(getFullUrl(API_ENDPOINTS.trial.plea(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ plea: true })
		});

		if (!response.ok) {
			console.error('[takePlea] Failed:', response.status);
			return false;
		}

		return true;
	} catch (error) {
		console.error('[takePlea] Error:', error);
		return false;
	}
}

export async function declinePlea(gameId: string): Promise<boolean> {
	try {
		const response = await fetch(getFullUrl(API_ENDPOINTS.trial.plea(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ plea: false })
		});

		if (!response.ok) {
			console.error('[declinePlea] Failed:', response.status);
			return false;
		}

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
		const url = getFullUrl(API_ENDPOINTS.draw(gameId)).replace('/draw', '/advance-phase');
		console.log('[gameActions] advancePhase: POST to', url);
		const response = await fetch(url, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' }
		});

		console.log('[gameActions] advancePhase: Response status', response.status);
		if (!response.ok) {
			const error = await response.text();
			console.error('[gameActions] advancePhase failed:', response.status, error);
			return false;
		}

		console.log('[gameActions] advancePhase: Success');
		return true;
	} catch (error) {
		console.error('[gameActions] advancePhase exception:', error);
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