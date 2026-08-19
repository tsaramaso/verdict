<script lang="ts">
	import type { PageData } from './$types';

	interface Props {
		data: {
			user?: { name: string; uuid: string };
			lobbies: any[];
		};
	}

	let { data } = $props<Props>();

	let isJoining = $state(false);
	let errorMessage = $state('');
</script>

<div class="home-wrapper">
	<div class="home-container">
		<div class="user-header">
			<div class="user-info">
				<span class="greeting">Welcome, <strong>{data.user?.name || 'Player'}</strong></span>
			</div>
			<form method="POST" action="?/logout" style="display: inline;">
				<button type="submit" class="btn btn-logout">Logout</button>
			</form>
		</div>

		<div class="home-header">
			<h1>Verdict</h1>
			<p class="tagline">Card game of truth and deception</p>
		</div>

		{#if errorMessage}
			<div class="alert alert-danger">
				{errorMessage}
			</div>
		{/if}

		<!-- Create Lobby Section -->
		<section class="section">
			<h2>Start Playing</h2>
			<form method="POST" action="?/createLobby" class="create-lobby-form">
				<button type="submit" class="btn btn-primary btn-lg">
					Create New Lobby
				</button>
			</form>
			<p class="section-hint">Create a lobby and invite your friends to play</p>
		</section>

		<!-- Join Lobby Section -->
		<section class="section">
			<h2>Join Lobby</h2>
			<form method="POST" action="?/joinLobby" class="join-lobby-form">
				<input
					type="text"
					name="lobby_id"
					placeholder="Enter lobby ID (e.g., ABC123)"
					class="lobby-input"
					disabled={isJoining}
					required
				/>
				<button
					type="submit"
					class="btn btn-secondary"
					disabled={isJoining}
				>
					{#if isJoining}
						Joining...
					{:else}
						Join
					{/if}
				</button>
			</form>
		</section>

		<!-- Active Lobbies Section -->
		{#if data.lobbies && data.lobbies.length > 0}
			<section class="section">
				<h2>Active Lobbies</h2>
				<div class="lobbies-list">
					{#each data.lobbies as lobby}
						<div class="lobby-card">
							<div class="lobby-header-row">
								<div class="lobby-id-badge">{lobby.lobby_id}</div>
								<div class="lobby-host">{lobby.host}</div>
							</div>
							<div class="lobby-info">
								<span class="player-count">👥 {lobby.player_count} player{lobby.player_count !== 1 ? 's' : ''}</span>
								<span class="created-time">{new Date(lobby.created_at).toLocaleTimeString()}</span>
							</div>
							<button
								class="btn btn-secondary btn-sm"
								onclick={() => window.location.href = `/lobby/${lobby.lobby_id}`}
							>
								Join Lobby
							</button>
						</div>
					{/each}
				</div>
			</section>
		{:else}
			<section class="section">
				<p class="empty-state">No active lobbies. Create one to get started!</p>
			</section>
		{/if}

		<!-- Game Recaps Section -->
		<section class="section">
			<h2>Game Recaps</h2>
			<p class="section-hint">Previous games will appear here</p>
			<div class="empty-state">No completed games yet</div>
		</section>
	</div>
</div>

<style>
	.home-wrapper {
		min-height: 100vh;
		background-color: var(--color-bg);
		padding: var(--spacing-xl);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.home-container {
		width: 100%;
		max-width: 900px;
		background-color: var(--color-bg-card);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		padding: var(--spacing-2xl);
	}

	.user-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		margin-bottom: var(--spacing-2xl);
		padding-bottom: var(--spacing-lg);
		border-bottom: 1px solid var(--color-border-light);
	}

	.user-info {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
	}

	.greeting {
		font-size: var(--font-size-base);
		color: var(--color-text);
	}

	.btn-logout {
		background-color: transparent;
		color: var(--color-danger);
		border: 1px solid var(--color-danger);
		padding: var(--spacing-sm) var(--spacing-md);
		font-size: var(--font-size-sm);
	}

	.btn-logout:not(:disabled):hover {
		background-color: var(--color-danger-light);
		border-color: var(--color-danger);
	}

	.home-header {
		text-align: center;
		margin-bottom: var(--spacing-2xl);
	}

	.home-header h1 {
		font-size: 3rem;
		font-weight: var(--font-weight-bold);
		color: var(--color-primary);
		margin: 0 0 var(--spacing-sm) 0;
		letter-spacing: -0.02em;
	}

	.tagline {
		font-size: var(--font-size-lg);
		color: var(--color-text-light);
		margin: 0;
		font-weight: var(--font-weight-medium);
	}

	.alert {
		padding: var(--spacing-md);
		border-radius: var(--radius-md);
		margin-bottom: var(--spacing-lg);
		font-size: var(--font-size-sm);
	}

	.alert-danger {
		background-color: var(--color-danger-light);
		color: var(--color-danger);
		border: 1px solid var(--color-danger);
	}

	.section {
		margin-bottom: var(--spacing-2xl);
		padding-bottom: var(--spacing-2xl);
		border-bottom: 1px solid var(--color-border-light);
	}

	.section:last-child {
		margin-bottom: 0;
		padding-bottom: 0;
		border-bottom: none;
	}

	.section h2 {
		font-size: var(--font-size-xl);
		font-weight: var(--font-weight-semibold);
		color: var(--color-text);
		margin: 0 0 var(--spacing-lg) 0;
	}

	.section-hint {
		font-size: var(--font-size-sm);
		color: var(--color-text-lighter);
		margin: var(--spacing-md) 0 0 0;
	}

	.create-lobby-form {
		display: flex;
		justify-content: center;
		margin-bottom: var(--spacing-md);
	}

	.btn {
		padding: var(--spacing-md) var(--spacing-lg);
		border: none;
		border-radius: var(--radius-md);
		font-size: var(--font-size-base);
		font-weight: var(--font-weight-semibold);
		cursor: pointer;
		transition: all var(--transition-base);
		font-family: var(--font-family-base);
	}

	.btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-primary {
		background-color: var(--color-primary);
		color: white;
	}

	.btn-primary:not(:disabled):hover {
		background-color: var(--color-primary-dark);
		box-shadow: var(--shadow-md);
	}

	.btn-secondary {
		background-color: transparent;
		color: var(--color-primary);
		border: 1px solid var(--color-primary);
	}

	.btn-secondary:not(:disabled):hover {
		background-color: var(--color-primary-light);
	}

	.btn-lg {
		padding: var(--spacing-lg) var(--spacing-2xl);
		font-size: var(--font-size-lg);
		min-width: 200px;
	}

	.btn-sm {
		padding: var(--spacing-sm) var(--spacing-md);
		font-size: var(--font-size-sm);
	}

	.join-lobby-form {
		display: flex;
		gap: var(--spacing-md);
		margin-bottom: var(--spacing-md);
	}

	.lobby-input {
		flex: 1;
		padding: var(--spacing-md);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		font-size: var(--font-size-base);
		font-family: var(--font-family-mono);
		text-transform: uppercase;
	}

	.lobby-input:focus {
		outline: none;
		border-color: var(--color-primary);
		box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.1);
	}

	.lobbies-list {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: var(--spacing-md);
	}

	.lobby-card {
		background-color: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: var(--spacing-md);
		transition: all var(--transition-base);
	}

	.lobby-card:hover {
		border-color: var(--color-primary);
		box-shadow: var(--shadow-md);
	}

	.lobby-header-row {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
		margin-bottom: var(--spacing-md);
	}

	.lobby-id-badge {
		background-color: var(--color-primary);
		color: white;
		padding: var(--spacing-sm) var(--spacing-md);
		border-radius: var(--radius-sm);
		font-family: var(--font-family-mono);
		font-weight: var(--font-weight-bold);
		font-size: var(--font-size-sm);
	}

	.lobby-host {
		font-weight: var(--font-weight-semibold);
		color: var(--color-text);
		flex: 1;
	}

	.lobby-info {
		display: flex;
		gap: var(--spacing-md);
		font-size: var(--font-size-sm);
		color: var(--color-text-lighter);
		margin-bottom: var(--spacing-md);
	}

	.player-count {
		font-weight: var(--font-weight-medium);
	}

	.empty-state {
		text-align: center;
		padding: var(--spacing-lg);
		color: var(--color-text-lighter);
		font-size: var(--font-size-sm);
		background-color: var(--color-bg);
		border-radius: var(--radius-md);
	}

	@media (max-width: 640px) {
		.home-container {
			padding: var(--spacing-lg);
		}

		.home-header h1 {
			font-size: 2rem;
		}

		.join-lobby-form {
			flex-direction: column;
		}

		.lobbies-list {
			grid-template-columns: 1fr;
		}

		.lobby-header-row {
			flex-direction: column;
			align-items: flex-start;
		}

		.btn-lg {
			width: 100%;
		}
	}
</style>