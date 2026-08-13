/**
 * Game configuration and constants
 * Colors, timings, card definitions, UI settings all in one place
 */

import { CardRank, SUIT_COLORS, SUIT_LABELS, CardSuit, POWER_CARDS } from "./constants/cards";
import type { CardSlot } from "./stores/gameState";


// ============================================
// TIMERS & GAME TIMING (in seconds)
// ============================================
export const TIMERS = {
  // Phase durations
  TURN_START: 100,
  DRAWING: 100,
  AWAITING_ACTION: 100,
  AWAITING_SPELL_INVOCATION: 100,
  AWAITING_QUICK_DISCARD: 100,
  AWAITING_CALL_WINDOW: 100,
  AWAITING_MATCH_WINDOW: 100,
  AWAITING_DUEL_WINDOW: 100,
  AWAITING_FINAL_PLEA_WINDOW: 100,
  ROUND_OVER: 100,
  GAME_OVER: 100,

  // Timer color transitions
  TIMER_CRITICAL_THRESHOLD: 5, // Below 5s = red
  TIMER_WARNING_THRESHOLD: 10, // Below 10s = orange
} as const;

// ============================================
// COLORS - Game UI Theme
// ============================================
export const COLORS = {
  // Primary
  primary: '#007bff',
  primaryDark: '#0056b3',
  primaryLight: '#e7f1ff',

  // Status colors
  success: '#4caf50',
  successLight: '#e8f5e9',
  warning: '#ff9800',
  warningLight: '#fff3e0',
  danger: '#d32f2f',
  dangerLight: '#ffebee',

  // Background & text
  bg: '#f5f5f5',
  bgCard: '#ffffff',
  text: '#333333',
  textLight: '#666666',
  textLighter: '#999999',

  // Borders
  border: '#dddddd',
  borderLight: '#eeeeee',

  // Card-specific
  cardBack: '#2a2a3e',
  cardBackGradient: '#1a1a2e',

  // Suits
  hearts: '#dc2626',
  diamonds: '#dc2626',
  clubs: '#1f2937',
  spades: '#1f2937',

  // Development/debug (for use in dev environment only)
  dev: {
    error: '#ff0000',
    warning: '#ffaa00',
    info: '#00aaff',
    success: '#00ff00',
  },
} as const;

// ============================================
// GAME PHASES
// ============================================
export const GAME_PHASES = {
  TURN_START: 'TURN_START',
  DRAWING: 'DRAWING',
  AWAITING_ACTION: 'AWAITING_ACTION',
  AWAITING_SPELL_INVOCATION: 'AWAITING_SPELL_INVOCATION',
  AWAITING_QUICK_DISCARD: 'AWAITING_QUICK_DISCARD',
  AWAITING_CALL_WINDOW: 'AWAITING_CALL_WINDOW',
  AWAITING_MATCH_WINDOW: 'AWAITING_MATCH_WINDOW',
  AWAITING_DUEL_WINDOW: 'AWAITING_DUEL_WINDOW',
  AWAITING_FINAL_PLEA_WINDOW: 'AWAITING_FINAL_PLEA_WINDOW',
  ROUND_OVER: 'ROUND_OVER',
  GAME_OVER: 'GAME_OVER',
} as const;

export const PHASE_LABELS: Record<string, string> = {
  TURN_START: 'Round Starting',
  DRAWING: 'Draw Phase',
  AWAITING_ACTION: 'Action Phase',
  AWAITING_SPELL_INVOCATION: 'Power Card',
  AWAITING_QUICK_DISCARD: 'Quick Discard',
  AWAITING_CALL_WINDOW: 'Call Window',
  AWAITING_MATCH_WINDOW: 'Match Window',
  AWAITING_DUEL_WINDOW: 'Duel',
  AWAITING_FINAL_PLEA_WINDOW: 'Final Plea',
  ROUND_OVER: 'Round Over',
  GAME_OVER: 'Game Over',
} as const;

// ============================================
// LAYOUT & SPACING
// ============================================
export const LAYOUT = {
  // Circular opponent layout
  circleRadius: 300, // pixels from center
  circleRadiusMobile: 150,
  circleRadiusTablet: 200,

  // Card dimensions (aspect ratio 2.5:3.5)
  cardWidth: 120,
  cardHeight: 168,
  cardWidthSmall: 80,
  cardHeightSmall: 112,

  // Deck/Discard zones
  deckWidth: 120,
  deckHeight: 180,
  deckGap: 60,

  // Player positions
  maxPlayers: 5,
  minPlayers: 2,

  // Z-indexes for layers
  zIndexes: {
    card: 10,
    cardHovered: 20,
    tooltip: 30,
    modal: 100,
  },
} as const;

// ============================================
// UI BEHAVIOR
// ============================================
export const UI = {
  // Auto-advance phases (no player input needed)
  autoAdvancePhases: [
    GAME_PHASES.TURN_START,
    GAME_PHASES.ROUND_OVER,
  ],

  // Phases where only active player can act
  activePlayerPhases: [
    GAME_PHASES.DRAWING,
    GAME_PHASES.AWAITING_ACTION,
  ],

  // Phases where all players act simultaneously
  simultaneousPhases: [
    GAME_PHASES.AWAITING_QUICK_DISCARD,
    GAME_PHASES.AWAITING_CALL_WINDOW,
    GAME_PHASES.AWAITING_MATCH_WINDOW,
    GAME_PHASES.AWAITING_DUEL_WINDOW,
    GAME_PHASES.AWAITING_FINAL_PLEA_WINDOW,
  ],

  // Animation timings
  animationDuration: 300, // ms
  transitionDuration: 150, // ms

  // Hover effects
  hoverLift: 4, // pixels
  hoverShadow: '0 8px 16px rgba(0, 0, 0, 0.2)',
} as const;

// ============================================
// HELPER FUNCTIONS
// ============================================

export function getTimerDuration(phase: string): number {
  return (TIMERS as Record<string, number>)[phase] || TIMERS.DRAWING;
}

export function getSuitColor(suit: CardSuit): string {
  return SUIT_COLORS[suit];
}

export function getSuitSymbol(suit: CardSuit): string {
  return SUIT_LABELS[suit];
}

export function getCardValue(rank: CardRank, suit: CardSuit, black_king_value: number, red_king_value: number, face_rank_values: Record<CardRank, number>): number {
  if (rank == CardRank.KING) {
    return (suit == CardSuit.SPADE || suit == CardSuit.CLUB) ? black_king_value : red_king_value;
  }
  return face_rank_values[rank];
}

export function isPowerCard(rank: CardRank): boolean {
  return rank in POWER_CARDS;
}

export function getPowerName(rank: CardRank): string | null {
  return POWER_CARDS[rank]?.name || null;
}

export function getPointsToRenaissance(score: number, thresholds: number[]): number {
  for (const target of thresholds) {
    if (score < target) {
      return target - score;
    }
  }
  throw new Error("Thresholds missing in rules (Status: 404)");
}
export function calculateKnownSum(
  hand: CardSlot[], 
  black_king_value: number, 
  red_king_value: number, 
  face_rank_values: Record<CardRank, number>
): number {
  return hand
    .filter((slot): slot is Required<CardSlot> => 
      slot.known && slot.rank !== undefined && slot.suit !== undefined
    )
    .reduce((total, currentSlot) => {
      const cardValue = getCardValue(
        currentSlot.rank, 
        currentSlot.suit, 
        black_king_value, 
        red_king_value, 
        face_rank_values
      );
      return total + cardValue;
    }, 0); //
}

type AutoAdvancePhase = typeof UI.autoAdvancePhases[number];

export function isAutoAdvancePhase(phase: string): phase is AutoAdvancePhase {
  return (UI.autoAdvancePhases as readonly string[]).includes(phase);
}

type IsActivePlayerPhase = typeof UI.activePlayerPhases[number];

export function isActivePlayerPhase(phase: string): phase is IsActivePlayerPhase {
  return (UI.activePlayerPhases as readonly string[]).includes(phase);
}

type SimultaneousPhases = typeof UI.simultaneousPhases[number];

export function isSimultaneousPhase(phase: string): phase is SimultaneousPhases {
  return (UI.simultaneousPhases as readonly string[]).includes(phase);
}
