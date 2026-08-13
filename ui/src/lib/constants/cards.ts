// src/lib/constants/cards.ts
/**
 * Card rank, suit, and value constants.
 * These match the backend card definitions exactly.
 */

/**
 * Card ranks from Ace to King
 */

export enum CardRank {
	ACE,
	TWO,
	THREE,
	FOUR,
	FIVE,
	SIX,
	SEVEN,
	EIGHT,
	NINE,
	TEN,
	JACK,
	QUEEN,
	KING
}

export enum CardSuit {
	DIAMOND,
	SPADE,
	HEART,
	CLUB
}

export const RANK_LABELS: Record<CardRank, string> = {
	[CardRank.ACE]: 'A',
	[CardRank.TWO]: '2',
	[CardRank.THREE]: '3',
	[CardRank.FOUR]: '4',
	[CardRank.FIVE]: '5',
	[CardRank.SIX]: '6',
	[CardRank.SEVEN]: '7',
	[CardRank.EIGHT]: '8',
	[CardRank.NINE]: '9',
	[CardRank.TEN]: '10',
	[CardRank.JACK]: 'J',
	[CardRank.QUEEN]: 'Q',
	[CardRank.KING]: 'K'
};

export const SUIT_LABELS: Record<CardSuit, string> = {
	[CardSuit.DIAMOND]: '♦',
	[CardSuit.SPADE]: '♠',
	[CardSuit.HEART]: '♥',
	[CardSuit.CLUB]: '♣'
};
/**
 * Suit colors for UI display
 */
export const SUIT_COLORS: Record<CardSuit, string> = {
	[CardSuit.HEART]: '#b40808',
	[CardSuit.DIAMOND]: '#df9409',
	[CardSuit.CLUB]: '#01788b',
	[CardSuit.SPADE]: '#000000'
};
/**
 * Power card ranks and their names mapped to the enum values
 */
export const POWER_CARDS: Partial<Record<CardRank, { name: string; ability: string }>> = {
	[CardRank.SEVEN]: { name: 'Glance', ability: 'Peek at your own slot' },
	[CardRank.EIGHT]: { name: 'Glance', ability: 'Peek at your own slot' },
	[CardRank.NINE]: { name: 'Spy', ability: 'Peek at opponent slot' },
	[CardRank.TEN]: { name: 'Spy', ability: 'Peek at opponent slot' },
	[CardRank.JACK]: { name: 'Smuggle', ability: 'Blind card exchange' },
	[CardRank.QUEEN]: { name: 'Decree', ability: 'Peek and optional swap' }
};

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
	const power = POWER_CARDS[rank];
	return power ? power.name : null;
}
