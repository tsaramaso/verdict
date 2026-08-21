/**
 * src/lib/actions/gameActions.ts
 * Centralized game action handlers
 * 
 * All API calls go through here. Single source of truth for game logic.
 * Each handler accepts gameId, payload, and optional callbacks.
 */

import { API_ENDPOINTS, getFullUrl } from '$lib/constants/api';

// ============================================
// DRAW PHASE HANDLERS
// ============================================

export async function drawFromDeck(gameId: string): Promise<{ drawn_card?: { rank: string; suit: string } } | null> {
	try {
		const response = await fetch(getFullUrl(API_ENDPOINTS.draw(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ source: 'deck' })
		});

		if (!response.ok) {
			console.error('[drawFromDeck] Failed:', response.status);
			return null;
		}

		return await response.json();
	} catch (error) {
		console.error('[drawFromDeck] Error:', error);
		return null;
	}
}

export async function drawFromDiscard(gameId: string): Promise<{ drawn_card?: { rank: string; suit: string } } | null> {
	try {
		const response = await fetch(getFullUrl(API_ENDPOINTS.draw(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ source: 'discard' })
		});

		if (!response.ok) {
			console.error('[drawFromDiscard] Failed:', response.status);
			return null;
		}

		return await response.json();
	} catch (error) {
		console.error('[drawFromDiscard] Error:', error);
		return null;
	}
}

// ============================================
// ACTION PHASE HANDLERS
// ============================================

export async function discardImmediate(gameId: string, source: 'deck' | 'discard'): Promise<boolean> {
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

export async function swapCard(gameId: string, slotIndex: number, source: 'deck' | 'discard'): Promise<boolean> {
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
				own_slot_index: ownSlotIndex,
				target_owner: targetOwner,
				target_index: targetIndex
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

export async function decreeSwap(gameId: string, swap: boolean, ownSlotIndex?: number): Promise<boolean> {
	try {
		const response = await fetch(getFullUrl(API_ENDPOINTS.power.decreeSwap(gameId)), {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ swap, own_slot_index: ownSlotIndex })
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