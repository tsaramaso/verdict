/**
 * src/lib/constants/api.ts
 * Centralized API endpoint definitions
 * 
 * All backend routes go here. Import from this file instead of hardcoding.
 * Prevents copy-paste errors and makes endpoint changes trivial.
 */

/**
 * Base API URL (from environment or default)
 * Set VITE_API_URL in .env.local to override
 */
export const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Endpoint builder functions
 * Each returns the full path (ready for fetch)
 */
export const API_ENDPOINTS = {
  // ============================================
  // DRAW & ACTION
  // ============================================
  draw: (gameId: string) => `/api/games/${gameId}/draw`,
  action: (gameId: string) => `/api/games/${gameId}/action`,

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
    const protocol = typeof window !== 'undefined' && window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = typeof window !== 'undefined' ? window.location.host : 'localhost:8000';
    return `${protocol}//${host}/ws/games/${gameId}?token=${token}`;
  }
};

/**
 * Helper to make full URL (API_BASE + endpoint)
 * @param endpoint from API_ENDPOINTS
 * @returns full URL ready for fetch()
 */
export function getFullUrl(endpoint: string): string {
  return `${API_BASE}${endpoint}`;
}

/**
 * RED FLAG 🚩: Endpoint verification needed
 * These paths assume backend matches exactly. Confirm before testing:
 * - /power/invoke ✅ confirmed in gameplay.py
 * - /power/decline ✅ confirmed in gameplay.py
 * - /power/decree-swap ✅ confirmed in gameplay.py
 * - /quick-discard (needs verification)
 * - /trial/* (needs verification for exact naming)
 */