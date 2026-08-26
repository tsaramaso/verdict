// ui/src/routes/login/+page.server.js
import { redirect } from '@sveltejs/kit';
import { login } from '$lib/api';

export function load({ cookies }) {
	const token = cookies.get('auth_token');

	// If already logged in, redirect to home
	if (token) {
		throw redirect(303, '/home');
	}
}

export const actions = {
	default: async ({ request, cookies }) => {
		const data = await request.formData();
		const uuid = data.get('uuid');

		if (!uuid) {
			return { error: 'UUID required' };
		}

		try {
			const response = await login(uuid as string);

			// Set token in non-httpOnly cookie so client-side JS can access it
			cookies.set('auth_token', response.token, {
				path: '/',
				maxAge: 60 * 60 * 24 * 100, // 100 days
				httpOnly: false // Allow client-side JS access (for WebSocket)
			});

			// Redirect to home
			throw redirect(303, '/home');
		} catch (err) {
			// Re-throw redirect errors
			if (err instanceof Error && (err as any).status === 303) throw err;
			return { error: 'Login failed' };
		}
	}
};
