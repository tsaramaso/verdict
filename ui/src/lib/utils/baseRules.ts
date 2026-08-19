import { apiCall } from '$lib/api';
import { CardRank } from '$lib/constants/cards';
import type { Rules } from '$lib/stores/gameState';
import { transformRules } from './rulesTransform';

let cachedBaseRules: Rules | null = null;

/**
 * Fetch BASE_RULES from API and cache it.
 * This is sourced from the backend's BASE_RULES constant.
 */
export async function fetchBaseRules(): Promise<Rules> {
	if (cachedBaseRules) {
		return cachedBaseRules;
	}

	try {
		const backendRules = await apiCall('/games/base-rules');
		cachedBaseRules = transformRules(backendRules);
		return cachedBaseRules;
	} catch (error) {
		console.error('Failed to fetch BASE_RULES from API:', error);
		// Fallback to hardcoded defaults if API is unavailable
		return getHardcodedBaseRules();
	}
}

/**
 * Hardcoded fallback that matches backend BASE_RULES.
 * Only used if API is unavailable.
 */
export function getHardcodedBaseRules(): Rules {
	return {
		red_king_value: 0,
		black_king_value: 13,
		hand_size: 4,
		nb_of_starting_draw: 2,
		eligible_threshold: 7,
		min_players: 2,
		max_players: 5,
		perjury_penalty: 25,
		duel_loss_penalty: 50,
		false_cross_testimony_penalty: 25,
		plea_penalty: 25,
		renaissance_thresholds: { 50: 25, 100: 50 },
		game_over_score: 120,
		rank_values: {
			[CardRank.ACE]: 1,
			[CardRank.TWO]: 2,
			[CardRank.THREE]: 3,
			[CardRank.FOUR]: 4,
			[CardRank.FIVE]: 5,
			[CardRank.SIX]: 6,
			[CardRank.SEVEN]: 7,
			[CardRank.EIGHT]: 8,
			[CardRank.NINE]: 9,
			[CardRank.TEN]: 10,
			[CardRank.JACK]: 11,
			[CardRank.QUEEN]: 12
		}
	};
}

/**
 * Clear cached rules (useful for testing or re-fetching).
 */
export function clearBaseRulesCache(): void {
	cachedBaseRules = null;
}
