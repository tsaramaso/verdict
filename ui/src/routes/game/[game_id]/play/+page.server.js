// ui/src/routes/game/[game_id]/play/+page.server.js
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
      'Authorization': `Bearer ${token}`,
    };

    // Fetch current user to get player ID
    const userResponse = await fetch(`${API_URL}/users/me`, {
      headers,
    });

    if (!userResponse.ok) {
      throw redirect(303, '/login');
    }

    const user = await userResponse.json();

    // Fetch game status
    const statusResponse = await fetch(`${API_URL}/games/${gameId}/status`, {
      headers,
    });

    if (!statusResponse.ok) {
      if (statusResponse.status === 404) {
        throw redirect(303, '/home');
      }
      throw new Error('Failed to fetch game status');
    }

    return {
      gameId,
      playerId: user.uuid,
      gameStatus: await statusResponse.json(),
    };
  } catch (err) {
    if (err.status === 303) throw err;
    return {
      gameId,
      error: err instanceof Error ? err.message : 'Failed to load game',
    };
  }
}