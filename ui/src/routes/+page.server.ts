import { redirect } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';

export const load: PageServerLoad = ({ cookies }) => {
	const token = cookies.get('auth_token');

	if (!token) {
		throw redirect(303, '/login');
	}

	// Token exists, redirect to home
	throw redirect(303, '/home');
};