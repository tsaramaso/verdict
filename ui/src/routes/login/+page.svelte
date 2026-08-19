<!-- ui/src/routes/login/+page.svelte -->
<script lang="ts">
	import { enhance } from '$app/forms';
	import type { SubmitFunction } from '@sveltejs/kit';

	let isLoading = $state(false);
	let error = $state('');

	const handleSubmit: SubmitFunction = async () => {
		isLoading = true;
		error = '';

		return async ({ result }) => {
			isLoading = false;

			if (result.type === 'error') {
				error = result.data?.error || 'An error occurred';
			} else if (result.data?.error) {
				error = result.data.error;
			}
		};
	};
</script>

<main>
	<div class="card">
		<h1>Verdict</h1>
		<form method="POST" use:enhance={handleSubmit}>
			<label for="uuid">Login code</label>
			<input
				type="text"
				id="uuid"
				name="uuid"
				required
				disabled={isLoading}
				autocomplete="username"
				autocapitalize="off"
			/>
			<button type="submit" disabled={isLoading}>
				{isLoading ? 'Logging in...' : 'Log in'}
			</button>
			{#if error}
				<div class="error-message">{error}</div>
			{/if}
		</form>
	</div>
</main>

<style>
	main {
		display: flex;
		justify-content: center;
		align-items: center;
		height: 100vh;
		background-color: var(--color-bg);
	}

	.card {
		background-color: var(--color-bg-card);
		padding: var(--spacing-xl);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		width: 100%;
		max-width: 400px;
	}

	h1 {
		text-align: center;
		margin-bottom: var(--spacing-lg);
		font-size: var(--font-size-xl);
		font-weight: var(--font-weight-bold);
	}

	form {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
	}

	label {
		font-weight: var(--font-weight-medium);
	}

	input {
		padding: var(--spacing-sm);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		font-size: var(--font-size-base);
	}

	button {
		padding: var(--spacing-sm);
		background-color: var(--color-primary);
		color: white;
		border: none;
		border-radius: var(--radius-sm);
		font-weight: var(--font-weight-medium);
		cursor: pointer;
	}

	button:hover:not(:disabled) {
		background-color: var(--color-primary-dark);
	}

	button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.error-message {
		background-color: var(--color-danger-light);
		color: var(--color-danger);
		padding: var(--spacing-sm);
		border-radius: var(--radius-sm);
		font-size: var(--font-size-sm);
		border: 1px solid var(--color-danger);
	}
</style>
