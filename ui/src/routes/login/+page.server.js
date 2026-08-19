// ui/src/routes/login/+page.server.js
import { redirect } from '@sveltejs/kit';

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
			const response = await fetch('http://localhost:8000/users/login', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ uuid })
			});

			if (!response.ok) {
				return { error: 'Invalid UUID' };
			}

			const { token } = await response.json();

			// Set token in non-httpOnly cookie so client-side JS can access it
			cookies.set('auth_token', token, {
				path: '/',
				maxAge: 60 * 60 * 24 * 100, // 100 days
				httpOnly: false // Allow client-side JS access (for WebSocket)
			});

			// Redirect to home
			throw redirect(303, '/home');
		} catch (err) {
			// Re-throw redirect errors
			if (err.status === 303) throw err;
			return { error: 'Login failed' };
		}
	}
};
