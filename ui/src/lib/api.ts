import type { Rules } from './stores/gameState';

/**
 * Base API URL (from environment or default)
 * Set VITE_API_URL in .env.local to override
 */
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Endpoint builder functions
 * Each returns the full path (ready for fetch)
 * All endpoints include /api/ prefix
 */
export const API_ENDPOINTS = {
	// ============================================
	// DRAW & ACTION
	// ============================================
	draw: (gameId: string) => `/api/games/${gameId}/draw`,
	action: (gameId: string) => `/api/games/${gameId}/action`,

	// ============================================
	// PHASE ADVANCEMENT
	// ============================================
	advancePhase: (gameId: string) => `/api/games/${gameId}/advance-phase`,

	// ============================================
	// SPELL POWERS (Section 7, rules.md)
	// ============================================
	power: {
		invoke: (gameId: string) => `/api/games/${gameId}/power/invoke`,
		decline: (gameId: string) => `/api/games/${gameId}/power/decline`,
		decreeSwap: (gameId: string) => `/api/games/${gameId}/power/decree-swap`
	},

	// ============================================
	// QUICK DISCARD (Section 5.4, rules.md)
	// ============================================
	quickDiscard: (gameId: string) => `/api/games/${gameId}/quick-discard`,
	quickDiscardClose: (gameId: string) => `/api/games/${gameId}/quick-discard/close`,

	// ============================================
	// TRIAL PHASES (Section 6, rules.md)
	// ============================================
	trial: {
		testifyFirst: (gameId: string) => `/api/games/${gameId}/trial/testify-first`,
		testifyCross: (gameId: string) => `/api/games/${gameId}/trial/testify-cross`,
		challenge: (gameId: string) => `/api/games/${gameId}/trial/challenge`,
		challengePass: (gameId: string) => `/api/games/${gameId}/trial/challenge-pass`,
		plea: (gameId: string) => `/api/games/${gameId}/trial/plea`
	},

	// ============================================
	// GAME LIFECYCLE
	// ============================================
	game: {
		get: (gameId: string) => `/api/games/${gameId}`,
		leaveGame: (gameId: string) => `/api/games/${gameId}/leave`
	},

	// ============================================
	// WEBSOCKET (handled separately in GamePage)
	// ============================================
	websocket: (gameId: string, token: string) => {
		const protocol =
			typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const host = typeof window !== 'undefined' ? window.location.host : 'localhost:8000';
		return `${protocol}//${host}/ws/games/${gameId}?token=${token}`;
	}
};

/**
 * Get auth token from localStorage or cookie
 */
function getAuthToken(): string | null {
	if (typeof window === 'undefined') return null;

	// Try localStorage first
	const token = localStorage.getItem('auth_token');
	if (token) return token;

	// Fall back to cookie
	const name = 'auth_token=';
	const decodedCookie = decodeURIComponent(document.cookie);
	const cookieArray = decodedCookie.split(';');

	for (let cookie of cookieArray) {
		cookie = cookie.trim();
		if (cookie.indexOf(name) === 0) {
			return cookie.substring(name.length);
		}
	}

	return null;
}

export async function apiCall(endpoint: string, options: RequestInit = {}) {
	const token = getAuthToken();

	const headers: HeadersInit = {
		'Content-Type': 'application/json',
		...(options.headers || {})
	};

	if (token) {
		headers['Authorization'] = `Bearer ${token}`;
	}

	const response = await fetch(`${API_URL}${endpoint}`, {
		...options,
		headers
	});

	if (!response.ok) {
		throw new Error(`API error: ${response.statusText}`);
	}

	return response.json();
}

export async function login(uuid: string) {
	const response = await apiCall('/users/login', {
		method: 'POST',
		body: JSON.stringify({ uuid })
	});

	// Store token in localStorage for subsequent requests
	if (response.token) {
		localStorage.setItem('auth_token', response.token);
	}

	return response;
}

// Types
export interface User {
	uuid: string;
	name: string;
	is_active: boolean;
	created_at: string;
}

export interface GameSummary {
	game_id: string;
	status: string;
	turn_direction: string;
	current_round: number;
	seat_order: string[];
	created_at: string;
	started_at: string | null;
	ended_at: string | null;
	rules: Rules;
}

// API Functions
export async function getCurrentUser(): Promise<User> {
	return apiCall('/users/me');
}

export async function listUsers(): Promise<User[]> {
	const data = await apiCall('/users');
	const currentUser = await getCurrentUser();
	return (data.users || []).filter((u: User) => u.uuid !== currentUser.uuid);
}

export async function listGames(): Promise<GameSummary[]> {
	const data = await apiCall('/games');
	return data.games;
}

export async function getGameStatus(gameId: string) {
	return apiCall(`/games/${gameId}/status`);
}

export async function createGame(playerIds: string[], rulesConfig?: Record<string, any>) {
	return apiCall('/games', {
		method: 'POST',
		body: JSON.stringify({
			player_ids: playerIds,
			rules_config: rulesConfig || {}
		})
	});
}

export async function getGameRecap(gameId: string) {
	return apiCall(`/games/${gameId}/recap`);
}