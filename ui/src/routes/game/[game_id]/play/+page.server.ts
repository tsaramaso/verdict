// ui/src/routes/game/[game_id]/play/+page.server.js
import { redirect } from '@sveltejs/kit';
import { getCurrentUser, getGameStatus } from '$lib/api';

export async function load({ params, cookies }) {
	const token = cookies.get('auth_token');
	const gameId = params.game_id;

	if (!token) {
		throw redirect(303, '/login');
	}

	try {
		// Fetch current user to get player ID
		const user = await getCurrentUser(token);

		// Fetch game status
		const gameStatus = await getGameStatus(gameId, token);

		return {
			gameId,
			playerId: user.uuid,
			gameStatus
		};
	} catch (err) {
		if (err instanceof Error && (err as any).status === 303) throw err;
		return {
			gameId,
			error: err instanceof Error ? err.message : 'Failed to load game'
		};
	}
}