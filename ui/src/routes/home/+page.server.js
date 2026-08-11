// ui/src/routes/home/+page.server.js
import { redirect } from '@sveltejs/kit';

const API_URL = 'http://localhost:8000';

export async function load({ cookies }) {
  const token = cookies.get('auth_token');

  // If no token, redirect to login
  if (!token) {
    throw redirect(303, '/login');
  }

  // Fetch user, games, and users list server-side
  try {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };

    const [userResponse, gamesResponse, usersResponse] = await Promise.all([
      fetch(`${API_URL}/users/me`, { headers }),
      fetch(`${API_URL}/games`, { headers }),
      fetch(`${API_URL}/users`, { headers }),
    ]);

    if (!userResponse.ok) {
      throw new Error('Failed to fetch user');
    }

    if (!gamesResponse.ok) {
      throw new Error('Failed to fetch games');
    }

    const user = await userResponse.json();
    const gamesData = await gamesResponse.json();
    let users = [];

    if (usersResponse.ok) {
      const usersData = await usersResponse.json();
      users = usersData.users || [];
    }

    return {
      user,
      games: gamesData.games || [],
      users,
    };
  } catch (err) {
    // If API fails, return empty data (client can handle it)
    return {
      user: null,
      games: [],
      users: [],
      error: err instanceof Error ? err.message : 'Failed to load data',
    };
  }
}

export const actions = {
  createGame: async ({ request, cookies }) => {
    const token = cookies.get('auth_token');

    if (!token) {
      return { error: 'Not authenticated' };
    }

    try {
      const formData = await request.formData();
      const playerIds = formData.getAll('playerIds');

      // Validation
      if (!playerIds || playerIds.length < 2) {
        return { error: 'At least 2 players required' };
      }

      // Create game via API
      const response = await fetch(`${API_URL}/games`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          player_ids: playerIds,
          rules_config: {},
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        return { error: error.detail || 'Failed to create game' };
      }

      const game = await response.json();
      throw redirect(303, `/game/${game.game_id}/play`);
    } catch (err) {
      // Re-throw redirect errors
      if (err.status === 303) throw err;
      return { error: err instanceof Error ? err.message : 'Failed to create game' };
    }
  },

  cancelGame: async ({ request, cookies }) => {
    const token = cookies.get('auth_token');

    if (!token) {
      return { error: 'Not authenticated' };
    }

    try {
      const formData = await request.formData();
      const gameId = formData.get('gameId');

      if (!gameId) {
        return { error: 'Game ID required' };
      }

      const response = await fetch(`${API_URL}/games/${gameId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const error = await response.json();
        return { error: error.detail || 'Failed to cancel game' };
      }

      return { success: true, gameId };
    } catch (err) {
      return { error: err instanceof Error ? err.message : 'Failed to cancel game' };
    }
  },

  logout: async ({ cookies }) => {
    cookies.delete('auth_token', { path: '/' });
    throw redirect(303, '/login');
  },
};