import { redirect } from '@sveltejs/kit';

const API_URL = 'http://localhost:8000';

export async function load({ params, cookies }) {
	const token = cookies.get('auth_token');
	const lobbyId = params.lobbyId;

	if (!token) {
		throw redirect(303, '/login');
	}

	try {
		const headers = {
			Authorization: `Bearer ${token}`
		};

		const response = await fetch(`${API_URL}/lobbies/${lobbyId}`, {
			headers
		});

		if (!response.ok) {
			throw redirect(303, '/home');
		}

		const lobbyData = await response.json();

		return {
			lobbyId,
			lobbyData
		};
	} catch (err) {
		if (err.status === 303) throw err;
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
			const lobbyResponse = await fetch(`${API_URL}/lobbies/${lobbyId}`, {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!lobbyResponse.ok) {
				return { error: 'Lobby not found' };
			}

			const lobbyData = await lobbyResponse.json();
			const playerIds = Object.keys(lobbyData.players);

			// Create game with lobby players
			const gameResponse = await fetch(`${API_URL}/games`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({
					player_ids: playerIds
				})
			});

			if (!gameResponse.ok) {
				const error = await gameResponse.json();
				return { error: error.detail || 'Failed to create game' };
			}

			const gameData = await gameResponse.json();
			throw redirect(303, `/game/${gameData.game_id}/play`);
		} catch (err) {
			if (err.status === 303) throw err;
			return { error: err instanceof Error ? err.message : 'Failed to start game' };
		}
	},

	returnHome: async () => {
		throw redirect(303, '/home');
	}
};