// ui/src/routes/game/[game_id]/lobby/+page.server.js
import { redirect } from '@sveltejs/kit';

const API_URL = 'http://localhost:8000';

export async function load({ params, cookies }) {
	const token = cookies.get('auth_token');
	const gameId = params.game_id;

	if (!token) {
		throw redirect(303, '/login');
	}

	try {
		const headers = {
			'Content-Type': 'application/json',
			Authorization: `Bearer ${token}`
		};

		// Fetch current user to get player ID
		const userResponse = await fetch(`${API_URL}/users/me`, {
			headers
		});

		if (!userResponse.ok) {
			throw redirect(303, '/login');
		}

		const user = await userResponse.json();

		// Fetch game status to check it exists and get initial state
		const statusResponse = await fetch(`${API_URL}/games/${gameId}/status`, {
			headers
		});

		if (!statusResponse.ok) {
			if (statusResponse.status === 404) {
				throw redirect(303, '/home');
			}
			throw new Error('Failed to fetch game status');
		}

		const gameStatus = await statusResponse.json();

		return {
			gameId,
			playerId: user.uuid,
			playerName: user.name || user.uuid,
			gameStatus
		};
	} catch (err) {
		if (err.status === 303) throw err;
		return {
			gameId: params.game_id,
			error: err instanceof Error ? err.message : 'Failed to load game'
		};
	}
}

export const actions = {
	startGame: async ({ params, cookies }) => {
		const token = cookies.get('auth_token');
		const gameId = params.game_id;

		if (!token) {
			return { error: 'Not authenticated' };
		}

		try {
			const response = await fetch(`${API_URL}/games/${gameId}/start`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!response.ok) {
				const error = await response.json();
				return { error: error.detail || 'Failed to start game' };
			}

			// Success - redirect to play page
			throw redirect(303, `/game/${gameId}/play`);
		} catch (err) {
			// Re-throw redirect errors
			if (err.status === 303) throw err;
			return { error: err instanceof Error ? err.message : 'Failed to start game' };
		}
	},

	returnHome: async () => {
		throw redirect(303, '/home');
	}
};