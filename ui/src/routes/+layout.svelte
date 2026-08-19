<script lang="ts">
	import '../app.css';
	import favicon from '$lib/assets/favicon.svg';
	import { onMount } from 'svelte';

	let { children } = $props();

	onMount(() => {
		// Sync auth token from cookie to localStorage (for WebSocket access)
		const name = 'auth_token=';
		const decodedCookie = decodeURIComponent(document.cookie);
		const cookieArray = decodedCookie.split(';');

		for (let cookie of cookieArray) {
			cookie = cookie.trim();
			if (cookie.indexOf(name) === 0) {
				const token = cookie.substring(name.length);
				localStorage.setItem('auth_token', token);
				break;
			}
		}
	});
</script>

<svelte:head>
	<link rel="icon" href={favicon} />
</svelte:head>

{@render children()}
