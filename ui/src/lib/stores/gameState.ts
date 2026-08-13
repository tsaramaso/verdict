import { writable, derived, type Writable, type Readable } from 'svelte/store';

// ============================================
// TYPE DEFINITIONS
// ============================================

export interface CardSlot {
  known: boolean;
  rank?: string;
  suit?: string;
}

export interface OpponentInfo {
  player_id: string;
  player_name: string;
  hand_count: number;
  known_cards: { slot: number; rank: string; suit: string }[];
  spied_slots: number[];
  score: number;
}

export interface SelfInfo {
  player_id: string;
  hand: CardSlot[];
  score: number;
  position: number;
}

export interface TrialState {
  first_window_callers: string[];
  passed_first: string[];
  cross_callers: string[];
  passed_cross: string[];
  perjury_removed: string[];
  truly_eligible: string[];
  challenged: string[];
  passed_challenge: string[];
  duel_occurred: boolean;
  duel_winners: string[];
  plea_taken: string[];
  plea_declined: string[];
}

export interface DiscardPile {
  count: number;
  visible_cards: { rank: string; suit: string }[];
}

export interface GameState {
  game_id: string;
  phase: string;
  current_player: string;
  round_number: number;
  self: SelfInfo;
  opponents: OpponentInfo[];
  my_opponent_knowledge: Record<string, number[]>;
  trial: TrialState;
  discard_pile: DiscardPile;
}

// ============================================
// DEFAULT STATE
// ============================================

const DEFAULT_STATE: GameState = {
  game_id: '',
  phase: 'TURN_START',
  current_player: '',
  round_number: 0,
  self: {
    player_id: '',
    hand: [],
    score: 0,
    position: 0,
  },
  opponents: [],
  my_opponent_knowledge: {},
  trial: {
    first_window_callers: [],
    passed_first: [],
    cross_callers: [],
    passed_cross: [],
    perjury_removed: [],
    truly_eligible: [],
    challenged: [],
    passed_challenge: [],
    duel_occurred: false,
    duel_winners: [],
    plea_taken: [],
    plea_declined: [],
  },
  discard_pile: {
    count: 0,
    visible_cards: [],
  },
};

// ============================================
// WRITABLE STORE
// ============================================

export const gameState: Writable<GameState> = writable(DEFAULT_STATE);

// Current player ID (for derived stores)
let currentPlayerId: string = '';

export function setCurrentPlayerId(playerId: string): void {
  currentPlayerId = playerId;
}

export function getCurrentPlayerId(): string {
  return currentPlayerId;
}

// ============================================
// DERIVED STORES - TRIAL GATING
// ============================================

export const canTestifyFirst: Readable<boolean> = derived(gameState, ($state) => {
  return (
    !$state.trial.first_window_callers.includes(currentPlayerId) &&
    !$state.trial.passed_first.includes(currentPlayerId)
  );
});

export const canTestifyCross: Readable<boolean> = derived(gameState, ($state) => {
  return (
    $state.trial.passed_first.includes(currentPlayerId) &&
    !$state.trial.cross_callers.includes(currentPlayerId) &&
    !$state.trial.passed_cross.includes(currentPlayerId)
  );
});

export const canChallenge: Readable<boolean> = derived(gameState, ($state) => {
  return (
    $state.trial.truly_eligible.includes(currentPlayerId) &&
    !$state.trial.challenged.includes(currentPlayerId) &&
    !$state.trial.passed_challenge.includes(currentPlayerId)
  );
});

export const canPlea: Readable<boolean> = derived(gameState, ($state) => {
  const testified = new Set([
    ...$state.trial.first_window_callers,
    ...$state.trial.cross_callers,
  ]);
  return (
    !testified.has(currentPlayerId) &&
    !$state.trial.plea_taken.includes(currentPlayerId) &&
    !$state.trial.plea_declined.includes(currentPlayerId)
  );
});

// ============================================
// DERIVED STORES - UI STATE
// ============================================

export const isActivePlayer: Readable<boolean> = derived(gameState, ($state) => {
  return $state.current_player === currentPlayerId;
});

export const isGameInProgress: Readable<boolean> = derived(gameState, ($state) => {
  return $state.phase !== 'GAME_OVER' && $state.phase !== 'ROUND_OVER';
});

export const deckSize: Readable<number> = derived(gameState, ($state) => {
  const numPlayers = 1 + $state.opponents.length;
  const dealtCards = 4 * numPlayers;
  const discardCount = $state.discard_pile.count;
  return 52 - dealtCards - discardCount;
});

export const myOpponentKnowledge: Readable<Record<string, number[]>> = derived(
  gameState,
  ($state) => $state.my_opponent_knowledge
);

export const trialState: Readable<TrialState> = derived(gameState, ($state) => $state.trial);

// ============================================
// HELPER FUNCTIONS
// ============================================

export function getOpponentById(state: GameState, opponentId: string): OpponentInfo | undefined {
  return state.opponents.find((opp) => opp.player_id === opponentId);
}

export function getOpponentsThatKnowSlot(
  opponentKnowledge: Record<string, number[]>,
  slotIndex: number
): string[] {
  const opponents: string[] = [];
  for (const [opponentId, slotIndices] of Object.entries(opponentKnowledge)) {
    if (slotIndices.includes(slotIndex)) {
      opponents.push(opponentId);
    }
  }
  return opponents;
}

export function calculateKnownSum(hand: CardSlot[]): number {
  let sum = 0;
  for (const slot of hand) {
    if (slot.known && slot.rank) {
      const values: Record<string, number> = {
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
      };
      sum += values[slot.rank] || 0;
    }
  }
  return sum;
}

export function isPowerCardRank(rank: string): boolean {
  return ['7', '8', '9', '10', 'J', 'Q'].includes(rank);
}

export function getPowerCardName(rank: string): string {
  const powers: Record<string, string> = {
    '7': 'Glance',
    '8': 'Glance',
    '9': 'Spy',
    '10': 'Spy',
    J: 'Smuggle',
    Q: 'Decree',
  };
  return powers[rank] || '';
}
