import { CardRank, CardSuit } from '$lib/constants/cards';

/**
 * Map backend rank strings to frontend CardRank enums
 * Backend sends: "ACE", "TWO", "QUEEN", "KING" (uppercase from Rank.name)
 * Frontend expects: CardRank.ACE, CardRank.QUEEN, etc.
 */
const BACKEND_RANK_MAP: Record<string, CardRank> = {
	ACE: CardRank.ACE,
	TWO: CardRank.TWO,
	THREE: CardRank.THREE,
	FOUR: CardRank.FOUR,
	FIVE: CardRank.FIVE,
	SIX: CardRank.SIX,
	SEVEN: CardRank.SEVEN,
	EIGHT: CardRank.EIGHT,
	NINE: CardRank.NINE,
	TEN: CardRank.TEN,
	JACK: CardRank.JACK,
	QUEEN: CardRank.QUEEN,
	KING: CardRank.KING
};

/**
 * Map backend suit strings to frontend CardSuit enums
 * Backend sends: "HEARTS", "DIAMONDS", "CLUBS", "SPADES" (uppercase from Suit.name)
 * Frontend enums are singular: HEART, DIAMOND, CLUB, SPADE
 * THIS IS THE NAMING MISMATCH!
 */
const BACKEND_SUIT_MAP: Record<string, CardSuit> = {
	HEARTS: CardSuit.HEART, // Note: HEARTS → HEART
	DIAMONDS: CardSuit.DIAMOND,
	CLUBS: CardSuit.CLUB, // Note: CLUBS → CLUB
	SPADES: CardSuit.SPADE
};

export function transformRank(backendRank: string): CardRank {
	const rank = BACKEND_RANK_MAP[backendRank];
	if (!rank && rank !== 0) {
		console.error(`Unknown rank: ${backendRank}`);
		return CardRank.ACE; // Fallback
	}
	return rank;
}

export function transformSuit(backendSuit: string): CardSuit {
	const suit = BACKEND_SUIT_MAP[backendSuit];
	if (!suit && suit !== 0) {
		console.error(`Unknown suit: ${backendSuit}`);
		return CardSuit.HEART; // Fallback
	}
	return suit;
}

/**
 * Transform a card object from API (strings) to frontend (enums)
 */
export function transformCard(apiCard: { rank?: string; suit?: string; known: boolean }) {
	if (!apiCard.known || !apiCard.rank || !apiCard.suit) {
		return apiCard as { rank?: CardRank; suit?: CardSuit; known: boolean };
	}

	return {
		known: apiCard.known,
		rank: transformRank(apiCard.rank),
		suit: transformSuit(apiCard.suit)
	};
}

/**
 * Transform a list of card slots (self hand or opponent known cards)
 */
export function transformCardList(
	apiCards: Array<{ rank?: string; suit?: string; known: boolean }>
) {
	return apiCards.map((card) => transformCard(card));
}
