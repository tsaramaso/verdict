import { redirect } from '@sveltejs/kit';

const API_URL = 'http://localhost:8000';

export async function load({ cookies }) {
	const token = cookies.get('auth_token');

	if (!token) {
		throw redirect(303, '/login');
	}

	try {
		const headers = {
			Authorization: `Bearer ${token}`
		};

		// Fetch current user
		const userResponse = await fetch(`${API_URL}/users/me`, {
			headers
		});

		if (!userResponse.ok) {
			// Token is invalid, clear it and redirect to login
			cookies.delete('auth_token', { path: '/' });
			throw redirect(303, '/login');
		}

		const user = await userResponse.json();

		// Fetch active lobbies
		const lobbiesResponse = await fetch(`${API_URL}/lobbies`, {
			headers
		});

		const lobbiesData = lobbiesResponse.ok ? await lobbiesResponse.json() : { lobbies: [] };

		return {
			user,
			lobbies: lobbiesData.lobbies || []
		};
	} catch (err) {
		if (err.status === 303) throw err;
		throw redirect(303, '/login');
	}
}

export const actions = {
	logout: async ({ cookies }) => {
		cookies.delete('auth_token', { path: '/' });
		throw redirect(303, '/login');
	},

	createLobby: async ({ cookies }) => {
		const token = cookies.get('auth_token');

		if (!token) {
			return { error: 'Not authenticated' };
		}

		try {
			const response = await fetch(`${API_URL}/lobbies/create`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				}
			});

			if (!response.ok) {
				const error = await response.json();
				return { error: error.detail || 'Failed to create lobby' };
			}

			const data = await response.json();
			throw redirect(303, `/lobby/${data.lobby_id}`);
		} catch (err) {
			if (err.status === 303) throw err;
			return { error: err instanceof Error ? err.message : 'Failed to create lobby' };
		}
	},

	joinLobby: async ({ request, cookies }) => {
		const token = cookies.get('auth_token');
		const formData = await request.formData();
		const lobbyId = formData.get('lobby_id');

		if (!lobbyId || !token) {
			return { error: 'Invalid lobby or not authenticated' };
		}

		try {
			const response = await fetch(`${API_URL}/lobby/${lobbyId}`, {
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!response.ok) {
				return { error: 'Lobby not found' };
			}

			throw redirect(303, `/lobby/${lobbyId}`);
		} catch (err) {
			if (err.status === 303) throw err;
			return { error: err instanceof Error ? err.message : 'Failed to join lobby' };
		}
	}
};