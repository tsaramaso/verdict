/**
 * Game configuration and constants
 * Colors, timings, card definitions, UI settings all in one place
 */

// ============================================
// TIMERS & GAME TIMING (in seconds)
// ============================================
export const TIMERS = {
  // Phase durations
  TURN_START: 10,
  DRAWING: 10,
  AWAITING_ACTION: 10,
  AWAITING_SPELL_INVOCATION: 10,
  AWAITING_QUICK_DISCARD: 10,
  AWAITING_CALL_WINDOW: 10,
  AWAITING_MATCH_WINDOW: 10,
  AWAITING_DUEL_WINDOW: 10,
  AWAITING_FINAL_PLEA_WINDOW: 10,
  ROUND_OVER: 10,
  GAME_OVER: 10,

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
// GAME CARDS
// ============================================
export const CARD_RANKS = [
  'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
] as const;

export type CardRank = typeof CARD_RANKS[number];

export const CARD_SUITS = ['HEARTS', 'DIAMONDS', 'CLUBS', 'SPADES'] as const;

export type CardSuit = typeof CARD_SUITS[number];

export const CARD_VALUES: Record<CardRank, number> = {
  A: 1,
  '2': 2,
  '3': 3,
  '4': 4,
  '5': 5,
  '6': 6,
  '7': 7,
  '8': 8,
  '9': 9,
  '10': 10,
  J: 10,
  Q: 10,
  K: 10,
} as const;

export const SUIT_SYMBOLS: Record<CardSuit, string> = {
  HEARTS: '♥',
  DIAMONDS: '♦',
  CLUBS: '♣',
  SPADES: '♠',
} as const;

export const SUIT_COLORS: Record<CardSuit, string> = {
  HEARTS: COLORS.hearts,
  DIAMONDS: COLORS.diamonds,
  CLUBS: COLORS.clubs,
  SPADES: COLORS.spades,
} as const;

// Power cards mapping
export const POWER_CARDS: Record<CardRank, { name: string; ability: string } | undefined> = {
  A: undefined,
  '2': undefined,
  '3': undefined,
  '4': undefined,
  '5': undefined,
  '6': undefined,
  '7': { name: 'Glance', ability: 'Peek at your own slot' },
  '8': { name: 'Glance', ability: 'Peek at your own slot' },
  '9': { name: 'Spy', ability: 'Peek at opponent slot' },
  '10': { name: 'Spy', ability: 'Peek at opponent slot' },
  J: { name: 'Smuggle', ability: 'Blind card exchange' },
  Q: { name: 'Decree', ability: 'Peek and optional swap' },
  K: undefined,
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
// RENAISSANCE MECHANICS
// ============================================
export const RENAISSANCE = {
  thresholds: [50, 100] as const,
  colors: {
    excellent: COLORS.success, // Green: <20 to Renaissance
    good: COLORS.warning, // Orange: 20-30
    warning: COLORS.danger, // Red: >30
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
  return SUIT_SYMBOLS[suit];
}

export function getCardValue(rank: CardRank): number {
  return CARD_VALUES[rank];
}

export function isPowerCard(rank: CardRank): boolean {
  return !!POWER_CARDS[rank];
}

export function getPowerName(rank: CardRank): string | null {
  return POWER_CARDS[rank]?.name || null;
}

export function getPointsToRenaissance(score: number): number {
  for (const target of RENAISSANCE.thresholds) {
    if (score < target) {
      return target - score;
    }
  }
  return Number.MAX_SAFE_INTEGER;
}

export function getRenaissanceColor(pointsToNext: number): string {
  if (pointsToNext > 30) return RENAISSANCE.colors.warning;
  if (pointsToNext > 20) return RENAISSANCE.colors.good;
  return RENAISSANCE.colors.excellent;
}

export function isAutoAdvancePhase(phase: string): boolean {
  return UI.autoAdvancePhases.includes(phase);
}

export function isActivePlayerPhase(phase: string): boolean {
  return UI.activePlayerPhases.includes(phase);
}

export function isSimultaneousPhase(phase: string): boolean {
  return UI.simultaneousPhases.includes(phase);
}
