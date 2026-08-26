import { redirect } from '@sveltejs/kit';
import type { PageServerLoad, Actions } from './$types';
import { getCurrentUser, listLobbies, createLobby } from '$lib/api';

export const load: PageServerLoad = async ({ cookies }) => {
	const token = cookies.get('auth_token');

	if (!token) {
		throw redirect(303, '/login');
	}

	try {
		// Fetch current user
		const user = await getCurrentUser(token);

		// Fetch active lobbies
		const lobbiesData = await listLobbies(token);

		return {
			user,
			lobbies: lobbiesData.lobbies || []
		};
	} catch (err) {
		// Check if it's a redirect error
		if (err instanceof Error && (err as any).status === 303) {
			throw err;
		}
		// If getCurrentUser fails, token is invalid
		cookies.delete('auth_token', { path: '/' });
		throw redirect(303, '/login');
	}
};

export const actions: Actions = {
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
			const data = await createLobby(token);
			throw redirect(303, `/lobby/${data.lobby_id}`);
		} catch (err) {
			// Check if it's a redirect error
			if (err instanceof Error && (err as any).status === 303) {
				throw err;
			}
			return { error: err instanceof Error ? err.message : 'Failed to create lobby' };
		}
	}
};