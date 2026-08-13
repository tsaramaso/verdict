// src/lib/constants/cards.ts
/**
 * Card rank, suit, and value constants.
 * These match the backend card definitions exactly.
 */

/**
 * Card ranks from Ace to King
 */
export const CARD_RANKS = [
  'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K'
] as const;

export type CardRank = typeof CARD_RANKS[number];

/**
 * Card suits
 */
export const CARD_SUITS = [
  'HEARTS', 'DIAMONDS', 'CLUBS', 'SPADES'
] as const;

export type CardSuit = typeof CARD_SUITS[number];

/**
 * Card values for scoring
 * Ace = 1, 2-9 = face value, 10/J/Q/K = 10
 */
export const CARD_VALUES: Record<CardRank, number> = {
  'A': 1,
  '2': 2,
  '3': 3,
  '4': 4,
  '5': 5,
  '6': 6,
  '7': 7,
  '8': 8,
  '9': 9,
  '10': 10,
  'J': 10,
  'Q': 10,
  'K': 10,
};

/**
 * Suit display names
 */
export const SUIT_LABELS: Record<CardSuit, string> = {
  'HEARTS': '♥',
  'DIAMONDS': '♦',
  'CLUBS': '♣',
  'SPADES': '♠',
};

/**
 * Suit colors for UI display
 */
export const SUIT_COLORS: Record<CardSuit, { light: string; dark: string }> = {
  'HEARTS': {
    light: '#fca5a5', // Red light
    dark: '#dc2626',  // Red dark
  },
  'DIAMONDS': {
    light: '#fca5a5', // Red light (diamonds are red)
    dark: '#dc2626',  // Red dark
  },
  'CLUBS': {
    light: '#6b7280', // Gray light
    dark: '#1f2937',  // Gray dark
  },
  'SPADES': {
    light: '#6b7280', // Gray light
    dark: '#1f2937',  // Gray dark
  },
};

/**
 * Power card ranks and their names
 */
export const POWER_CARDS = {
  '7': { name: 'Glance', ability: 'Peek at your own slot' },
  '8': { name: 'Glance', ability: 'Peek at your own slot' },
  '9': { name: 'Spy', ability: 'Peek at opponent slot' },
  '10': { name: 'Spy', ability: 'Peek at opponent slot' },
  'J': { name: 'Smuggle', ability: 'Blind card exchange' },
  'Q': { name: 'Decree', ability: 'Peek and optional swap' },
} as const;

/**
 * Is this rank a power card?
 */
export function isPowerCard(rank: CardRank): boolean {
  return rank in POWER_CARDS;
}

/**
 * Get power card name
 */
export function getPowerName(rank: CardRank): string | null {
  const power = POWER_CARDS[rank as keyof typeof POWER_CARDS];
  return power?.name || null;
}

/**
 * Color scheme for player scores in leaderboard
 */
export const SCORE_COLORS = {
  excellent: '#22c55e', // Green: <20 to Renaissance
  good: '#f97316',      // Orange: 20-30
  warning: '#ef4444',   // Red: >30
} as const;

/**
 * Renaissance breakpoints
 */
export const RENAISSANCE_POINTS = [50, 100] as const;

/**
 * Get points to next Renaissance
 */
export function getPointsToRenaissance(score: number): number {
  for (const target of RENAISSANCE_POINTS) {
    if (score < target) {
      return target - score;
    }
  }
  return Number.MAX_SAFE_INTEGER; // Beyond final Renaissance
}

/**
 * Get color for points-to-Renaissance indicator
 */
export function getRenaissanceColor(pointsToNext: number): string {
  if (pointsToNext > 30) return SCORE_COLORS.warning;
  if (pointsToNext > 20) return SCORE_COLORS.good;
  return SCORE_COLORS.excellent;
}
