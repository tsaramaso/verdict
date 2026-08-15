import { CardRank } from '$lib/constants/cards';
import type { Rules } from '$lib/stores/gameState';

/**
 * Transform rules from API format to UI format
 * 
 * Backend sends:
 * {
 *   red_king_value: number,
 *   black_king_value: number,
 *   hand_size: number,
 *   nb_of_starting_draw: number,
 *   eligible_threshold: number,
 *   min_players: number,
 *   max_players: number,
 *   perjury_penalty: number,
 *   duel_loss_penalty: number,
 *   false_cross_testimony_penalty: number,
 *   plea_penalty: number,
 *   renaissance_thresholds: Record<number, number>,
 *   game_over_score: number,
 *   face_rank_values: { "ACE": 1, "TWO": 2, ... }  // String keys, string names
 * }
 * 
 * Frontend expects:
 * {
 *   ... same fields ...
 *   rank_values: { 0: 1, 1: 2, ... }  // Numeric CardRank enum keys
 * }
 */
export function transformRules(backendRules: any): Rules {
	if (!backendRules) {
		return getDefaultRules();
	}

	// Map backend rank names ("ACE", "TWO", etc.) to CardRank enum values (0, 1, etc.)
	const transformedRankValues: Record<string, number> = {};

	if (backendRules.face_rank_values) {
		// Convert string keys like "ACE" to CardRank enum numeric indices
		transformedRankValues[CardRank.ACE] = backendRules.face_rank_values['ACE'] ?? 1;
		transformedRankValues[CardRank.TWO] = backendRules.face_rank_values['TWO'] ?? 2;
		transformedRankValues[CardRank.THREE] = backendRules.face_rank_values['THREE'] ?? 3;
		transformedRankValues[CardRank.FOUR] = backendRules.face_rank_values['FOUR'] ?? 4;
		transformedRankValues[CardRank.FIVE] = backendRules.face_rank_values['FIVE'] ?? 5;
		transformedRankValues[CardRank.SIX] = backendRules.face_rank_values['SIX'] ?? 6;
		transformedRankValues[CardRank.SEVEN] = backendRules.face_rank_values['SEVEN'] ?? 7;
		transformedRankValues[CardRank.EIGHT] = backendRules.face_rank_values['EIGHT'] ?? 8;
		transformedRankValues[CardRank.NINE] = backendRules.face_rank_values['NINE'] ?? 9;
		transformedRankValues[CardRank.TEN] = backendRules.face_rank_values['TEN'] ?? 10;
		transformedRankValues[CardRank.JACK] = backendRules.face_rank_values['JACK'] ?? 11;
		transformedRankValues[CardRank.QUEEN] = backendRules.face_rank_values['QUEEN'] ?? 12;
	} else {
		// Fallback to defaults if face_rank_values is missing
		transformedRankValues[CardRank.ACE] = 1;
		transformedRankValues[CardRank.TWO] = 2;
		transformedRankValues[CardRank.THREE] = 3;
		transformedRankValues[CardRank.FOUR] = 4;
		transformedRankValues[CardRank.FIVE] = 5;
		transformedRankValues[CardRank.SIX] = 6;
		transformedRankValues[CardRank.SEVEN] = 7;
		transformedRankValues[CardRank.EIGHT] = 8;
		transformedRankValues[CardRank.NINE] = 9;
		transformedRankValues[CardRank.TEN] = 10;
		transformedRankValues[CardRank.JACK] = 11;
		transformedRankValues[CardRank.QUEEN] = 12;
	}

	return {
		red_king_value: backendRules.red_king_value ?? 0,
		black_king_value: backendRules.black_king_value ?? 13,
		hand_size: backendRules.hand_size ?? 4,
		nb_of_starting_draw: backendRules.nb_of_starting_draw ?? 2,
		eligible_threshold: backendRules.eligible_threshold ?? 7,
		min_players: backendRules.min_players ?? 2,
		max_players: backendRules.max_players ?? 5,
		perjury_penalty: backendRules.perjury_penalty ?? 25,
		duel_loss_penalty: backendRules.duel_loss_penalty ?? 50,
		false_cross_testimony_penalty: backendRules.false_cross_testimony_penalty ?? 25,
		plea_penalty: backendRules.plea_penalty ?? 25,
		renaissance_thresholds: backendRules.renaissance_thresholds ?? { 50: 25, 100: 50 },
		game_over_score: backendRules.game_over_score ?? 120,
		rank_values: transformedRankValues
	};
}

export function getDefaultRules(): Rules {
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