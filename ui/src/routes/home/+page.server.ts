import { redirect } from '@sveltejs/kit';
import { getLobby, createGame } from '$lib/api';

export async function load({ params, cookies }) {
	const token = cookies.get('auth_token');
	const lobbyId = params.lobbyId;

	if (!token) {
		throw redirect(303, '/login');
	}

	try {
		const lobbyData = await getLobby(lobbyId, token);

		return {
			lobbyId,
			lobbyData
		};
	} catch (err) {
		if (err instanceof Error && (err as any).status === 303) throw err;
		throw redirect(303, '/home');
	}
}

export const actions = {
	startGame: async ({ params, cookies }) => {
		const token = cookies.get('auth_token');
		const lobbyId = params.lobbyId;

		if (!token) {
			return { error: 'Not authenticated' };
		}

		try {
			// Get lobby players first
			const lobbyData = await getLobby(lobbyId, token);
			const playerIds = Object.keys(lobbyData.players);

			// Create game with lobby players
			const gameData = await createGame(playerIds, undefined, token);
			throw redirect(303, `/game/${gameData.game_id}/play`);
		} catch (err) {
			if (err instanceof Error && (err as any).status === 303) throw err;
			return { error: err instanceof Error ? err.message : 'Failed to start game' };
		}
	},

	returnHome: async () => {
		throw redirect(303, '/home');
	}
};