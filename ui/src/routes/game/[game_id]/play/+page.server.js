// ui/src/routes/game/[game_id]/play/+page.server.js
import { redirect } from '@sveltejs/kit';

const API_URL = 'http://localhost:8000';

export async function load({ params, cookies }) {
  const token = cookies.get('auth_token');
  const gameId = params.game_id;

  // If no token, redirect to login
  if (!token) {
    throw redirect(303, '/login');
  }

  try {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };

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

    const gameStatus = await statusResponse.json();

    return {
      gameId,
      gameStatus,
    };
  } catch (err) {
    if (err.status === 303) throw err; // Re-throw redirects
    return {
      gameId,
      gameStatus: null,
      error: err instanceof Error ? err.message : 'Failed to load game',
    };
  }
}