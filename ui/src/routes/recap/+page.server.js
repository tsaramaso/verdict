import { redirect } from '@sveltejs/kit';

const API_URL = 'http://localhost:8000';

export async function load({ params, cookies }) {
	const token = cookies.get('auth_token');

	if (!token) {
		throw redirect(303, '/login');
	}

	const { game_id } = params;

	try {
		const response = await fetch(`${API_URL}/games/${game_id}/recap`, {
			headers: {
				Authorization: `Bearer ${token}`,
				'Content-Type': 'application/json'
			}
		});

		if (!response.ok) {
			throw new Error('Failed to fetch recap');
		}

		const recap = await response.json();

		return {
			game_id,
			recap
		};
	} catch (err) {
		return {
			game_id,
			error: err instanceof Error ? err.message : 'Failed to load recap'
		};
	}
}
