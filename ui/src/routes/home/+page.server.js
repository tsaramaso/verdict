// ui/src/routes/home/+page.server.js
import { redirect } from '@sveltejs/kit';

const API_URL = 'http://localhost:8000';

export async function load({ cookies }) {
  const token = cookies.get('auth_token');

  // If no token, redirect to login
  if (!token) {
    throw redirect(303, '/login');
  }

  // Fetch user and games server-side
  try {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    };

    const [userResponse, gamesResponse] = await Promise.all([
      fetch(`${API_URL}/users/me`, { headers }),
      fetch(`${API_URL}/games`, { headers }),
    ]);

    if (!userResponse.ok) {
      throw new Error('Failed to fetch user');
    }

    if (!gamesResponse.ok) {
      throw new Error('Failed to fetch games');
    }

    const user = await userResponse.json();
    const gamesData = await gamesResponse.json();

    return {
      user,
      games: gamesData.games || [],
    };
  } catch (err) {
    // If API fails, return empty data (client can handle it)
    return {
      user: null,
      games: [],
      error: err instanceof Error ? err.message : 'Failed to load data',
    };
  }
}

export const actions = {
  logout: async ({ cookies }) => {
    cookies.delete('auth_token', { path: '/' });
    throw redirect(303, '/login');
  },
};