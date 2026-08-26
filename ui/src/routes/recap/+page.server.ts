import { redirect } from '@sveltejs/kit';
import { getGameRecap } from '$lib/api';
import type { PageServerLoad } from './$types';

export async function load({ params, cookies }) {
	const token = cookies.get('auth_token');

	if (!token) {
		throw redirect(303, '/login');
	}

	const { game_id } = params as { game_id: string };

	try {
		const recap = await getGameRecap(game_id, token);

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
