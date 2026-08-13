<!-- ui/src/routes/home/+page.svelte -->
<script lang="ts">
	import { goto } from '$app/navigation';
	import { enhance, type ActionResult, applyAction } from '$app/forms';
	import { onMount } from 'svelte';

	let { data } = $props();

	let user = $derived(data?.user);
	let games = $derived(data?.games || []);
	let error = $derived(data?.error);
	let availableUsers = $derived(data?.users || []);

	function getGameStatusLabel(status: string): string {
		const labels: Record<string, string> = {
			WAITING_FOR_PLAYERS: 'Waiting',
			IN_PROGRESS: 'Active',
			FINISHED: 'Finished'
		};
		return labels[status] || status;
	}

	function getStatusColor(status: string): string {
		if (status === 'IN_PROGRESS') return 'var(--color-success)';
		if (status === 'FINISHED') return 'var(--color-text-light)';
		return 'var(--color-warning)';
	}

	let selectedUsers = $state(
		new Map<string, { uuid: string; name: string | null; isCreator: boolean }>()
	);

	$effect(() => {
		if (user && selectedUsers.size === 0) {
			selectedUsers.set(user.uuid, {
				uuid: user.uuid,
				name: user.name,
				isCreator: true
			});
		}
	});
	let selectedUserId = $state('');
	let createGameError = $state('');
	let isCreatingGame = $state(false);
	let cancellingGameIds = $state(new Set<string>());

	let selectedPlayers = $derived(Array.from(selectedUsers.values()));
	let filteredGames = $derived(games.filter((g) => !cancellingGameIds.has(g.game_id)));

	onMount(() => {
		// Pre-add current user to selected players
		if (user) {
			const newMap = new Map(selectedUsers);
			newMap.set(user.uuid, {
				uuid: user.uuid,
				name: user.name,
				isCreator: true
			});
			selectedUsers = newMap;
		}
	});

	function addPlayer() {
		if (!selectedUserId || selectedUsers.has(selectedUserId)) return;

		const userToAdd = availableUsers.find((u: any) => u.uuid === selectedUserId);
		if (!userToAdd) return;

		const newMap = new Map(selectedUsers);
		newMap.set(selectedUserId, {
			uuid: selectedUserId,
			name: userToAdd.name,
			isCreator: false
		});
		selectedUsers = newMap;
		selectedUserId = '';
	}

	function removePlayer(uuid: string) {
		const newMap = new Map(selectedUsers);
		newMap.delete(uuid);
		selectedUsers = newMap;
	}

	function handleCancelGame(result: ActionResult) {
		if (result.type === 'success' && 'gameId' in result.data) {
			// Keep the game in cancellingGameIds to prevent it from reappearing
			// It's already hidden from the UI via filteredGames
		} else if (result.type === 'error' && result.error) {
			// Remove from cancelling set if there was an error so user can retry
			const gameId = new FormData(result as any).get('gameId') as string;
			if (gameId) {
				cancellingGameIds.delete(gameId);
			}
		}
	}

	function onCancelClick(e: Event, gameId: string) {
		e.stopPropagation();
		// Mark game as being cancelled
		cancellingGameIds.add(gameId);
	}
</script>

<div class="layout">
	<!-- Navigation Bar -->
	<nav class="navbar">
		<div class="navbar-content">
			<div class="navbar-brand">
				<h1>Verdict</h1>
			</div>
			<div class="navbar-user">
				{#if user}
					<span class="username">Hello, {user.name || 'Player'}</span>
					<form method="POST" action="?/logout" use:enhance>
						<button type="submit" class="btn-logout">Logout</button>
					</form>
				{/if}
			</div>
		</div>
	</nav>

	<!-- Main Content -->
	<main class="main-content">
		{#if error}
			<div class="error-state">
				<p class="error-message">{error}</p>
			</div>
		{:else}
			<div class="content-grid">
				<!-- Create Game Section -->
				<section class="section create-game-section">
					<h2>Create Game</h2>
					<div class="section-content">
						<form method="POST" action="?/createGame" use:enhance>
							{#if createGameError}
								<div class="error-banner">{createGameError}</div>
							{/if}

							<!-- Players Selection -->
							<div class="form-group">
								<label for="player-select">Add Players</label>
								<div class="player-select-row">
									<select id="player-select" bind:value={selectedUserId} disabled={isCreatingGame}>
										<option value="">Select a player...</option>
										{#each availableUsers as availUser (availUser.uuid)}
											{#if availUser.uuid !== user?.uuid}
												<option value={availUser.uuid}>
													{availUser.name || 'Unnamed'} ({availUser.uuid.slice(0, 8)})
												</option>
											{/if}
										{/each}
									</select>
									<button
										type="button"
										class="btn-add-player"
										onclick={addPlayer}
										disabled={!selectedUserId || isCreatingGame}
									>
										Add
									</button>
								</div>
							</div>

							<!-- Selected Players List -->
							<div class="form-group">
								<div class="form-header">Selected Players ({selectedPlayers.length})</div>
								<p class="form-note">
									You are automatically included as creator and cannot be removed
								</p>
								<div class="selected-players">
									{#if selectedPlayers.length === 0}
										<div class="empty-players">No players selected yet</div>
									{:else}
										<div class="players-list">
											{#each selectedPlayers as player (player.uuid)}
												<div class="player-tag">
													<span class="player-info">
														{#if player.uuid === user?.uuid}
															You (creator)
														{:else}
															{player.name || 'Unnamed'}
															{#if player.isCreator}
																<span class="creator-badge">creator</span>
															{/if}
														{/if}
													</span>
													{#if !player.isCreator}
														<button
															type="button"
															class="btn-remove-player"
															onclick={() => removePlayer(player.uuid)}
															disabled={isCreatingGame}
														>
															✕
														</button>
													{/if}
												</div>
											{/each}
										</div>
									{/if}
								</div>
							</div>

							<!-- Hidden input to send player IDs -->
							<div style="display: none;">
								{#each selectedPlayers as player (player.uuid)}
									<input type="hidden" name="playerIds" value={player.uuid} />
								{/each}
							</div>

							<!-- Submit Button -->
							<button
								type="submit"
								class="btn-create-game"
								disabled={selectedPlayers.length < 2 || isCreatingGame}
							>
								{isCreatingGame ? 'Creating...' : 'Create Game'}
							</button>

							<p class="form-hint">
								{#if selectedPlayers.length < 2}
									Select at least 2 players to create a game
								{:else}
									Ready to create game with {selectedPlayers.length} players
								{/if}
							</p>
						</form>
					</div>
				</section>

				<!-- Games Section -->
				<section class="section your-games-section">
					<h2>Games</h2>
					<div class="section-content">
						{#if games.length === 0}
							<div class="empty-state">
								<p>No games yet. Create one to get started!</p>
							</div>
						{:else}
							<div class="games-list">
								{#each filteredGames as game (game.game_id)}
									<div class="game-card-wrapper">
										<button class="game-card" onclick={() => goto(`/game/${game.game_id}/play`)}>
											<div class="game-header">
												<span class="game-status" style="color: {getStatusColor(game.status)}">
													{getGameStatusLabel(game.status)}
												</span>
												<span class="game-round">Round {game.current_round}</span>
											</div>
											<div class="game-details">
												<p class="game-id">Game: {game.game_id.slice(0, 8)}...</p>
												<p class="game-date">
													Created: {new Date(game.created_at).toLocaleDateString()}
												</p>
											</div>
										</button>
										<form
											method="POST"
											action="?/cancelGame"
											use:enhance={() => {
												onCancelClick(new Event('click'), game.game_id);
												return async ({ result }) => {
													handleCancelGame(result);
													await applyAction(result);
												};
											}}
											class="cancel-form"
										>
											<input type="hidden" name="gameId" value={game.game_id} />
											<button
												type="submit"
												class="btn-close-game"
												title="Cancel this game"
												disabled={cancellingGameIds.has(game.game_id)}
											>
												✕
											</button>
										</form>
									</div>
								{/each}
							</div>
						{/if}
					</div>
				</section>
			</div>
		{/if}
	</main>
</div>

<style>
	.layout {
		display: flex;
		flex-direction: column;
		height: 100vh;
		background-color: var(--color-bg);
	}

	.navbar {
		background-color: var(--color-bg-card);
		border-bottom: 1px solid var(--color-border);
		box-shadow: var(--shadow-sm);
		position: sticky;
		top: 0;
		z-index: var(--z-dropdown);
	}

	.navbar-content {
		max-width: 1400px;
		margin: 0 auto;
		padding: var(--spacing-md) var(--spacing-lg);
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.navbar-brand h1 {
		margin: 0;
		font-size: var(--font-size-xl);
		color: var(--color-primary);
	}

	.navbar-user {
		display: flex;
		align-items: center;
		gap: var(--spacing-md);
	}

	.navbar-user form {
		display: contents;
	}

	.username {
		font-size: var(--font-size-sm);
		color: var(--color-text-light);
	}

	.btn-logout {
		background-color: transparent;
		color: var(--color-danger);
		border: 1px solid var(--color-danger);
		padding: var(--spacing-xs) var(--spacing-md);
		font-size: var(--font-size-sm);
		cursor: pointer;
		font-family: inherit;
	}

	.btn-logout:hover {
		background-color: var(--color-danger-light);
	}

	.main-content {
		flex: 1;
		overflow-y: auto;
		padding: var(--spacing-xl);
	}

	.error-state {
		display: flex;
		align-items: center;
		justify-content: center;
		height: 100%;
		min-height: 400px;
	}

	.error-message {
		color: var(--color-danger);
		font-weight: var(--font-weight-medium);
	}

	.content-grid {
		max-width: 1400px;
		margin: 0 auto;
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: var(--spacing-xl);
	}

	.section {
		background-color: var(--color-bg-card);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		display: flex;
		flex-direction: column;
		min-height: 500px;
	}

	.section h2 {
		padding: var(--spacing-lg) var(--spacing-lg) 0 var(--spacing-lg);
		margin-bottom: var(--spacing-md);
		font-size: var(--font-size-lg);
		border-bottom: 2px solid var(--color-border);
		padding-bottom: var(--spacing-md);
	}

	.section-content {
		padding: var(--spacing-lg);
		flex: 1;
		display: flex;
		flex-direction: column;
	}

	.empty-state {
		flex: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		text-align: center;
		color: var(--color-text-light);
	}

	/* Create Game Form Styles */
	.player-select-row {
		display: flex;
		gap: var(--spacing-sm);
		margin-bottom: var(--spacing-md);
	}

	select {
		font-family: inherit;
	}

	select {
		flex: 1;
		padding: var(--spacing-sm);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		font-size: var(--font-size-base);
		background-color: var(--color-bg);
		color: var(--color-text);
	}

	select:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-add-player {
		padding: var(--spacing-sm) var(--spacing-md);
		background-color: var(--color-primary);
		color: white;
		border: none;
		border-radius: var(--radius-sm);
		cursor: pointer;
		font-weight: var(--font-weight-medium);
		white-space: nowrap;
	}

	.btn-add-player:hover:not(:disabled) {
		background-color: var(--color-primary-dark);
	}

	.btn-add-player:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.form-group {
		margin-bottom: var(--spacing-lg);
	}

	.form-group label {
		display: block;
		margin-bottom: var(--spacing-sm);
		font-weight: var(--font-weight-medium);
		font-size: var(--font-size-sm);
	}

	.form-header {
		display: block;
		margin-bottom: var(--spacing-sm);
		font-weight: var(--font-weight-medium);
		font-size: var(--font-size-sm);
	}

	.form-note {
		font-size: var(--font-size-xs, 0.75rem);
		color: var(--color-text-light);
		margin: 0 0 var(--spacing-sm) 0;
		font-style: italic;
	}

	.selected-players {
		background-color: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		padding: var(--spacing-md);
		min-height: 80px;
	}

	.empty-players {
		text-align: center;
		color: var(--color-text-light);
		padding: var(--spacing-md) 0;
	}

	.players-list {
		display: flex;
		flex-wrap: wrap;
		gap: var(--spacing-sm);
	}

	.player-tag {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		background-color: var(--color-primary-light);
		color: var(--color-primary);
		padding: var(--spacing-xs) var(--spacing-sm);
		border-radius: var(--radius-sm);
		font-size: var(--font-size-sm);
	}

	.player-info {
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
	}

	.creator-badge {
		font-size: 0.75rem;
		opacity: 0.7;
		font-style: italic;
	}

	.btn-remove-player {
		background-color: transparent;
		border: none;
		color: var(--color-primary);
		cursor: pointer;
		padding: 0;
		font-size: var(--font-size-base);
		font-weight: bold;
	}

	.btn-remove-player:hover:not(:disabled) {
		color: var(--color-danger);
	}

	.btn-remove-player:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-create-game {
		width: 100%;
		padding: var(--spacing-md);
		background-color: var(--color-success);
		color: white;
		border: none;
		border-radius: var(--radius-sm);
		font-size: var(--font-size-base);
		font-weight: var(--font-weight-bold);
		cursor: pointer;
		margin-bottom: var(--spacing-sm);
	}

	.btn-create-game:hover:not(:disabled) {
		background-color: var(--color-success-dark);
	}

	.btn-create-game:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.form-hint {
		text-align: center;
		font-size: var(--font-size-sm);
		color: var(--color-text-light);
		margin: 0;
	}

	.error-banner {
		background-color: var(--color-danger-light);
		color: var(--color-danger);
		padding: var(--spacing-md);
		border-radius: var(--radius-sm);
		margin-bottom: var(--spacing-md);
		font-size: var(--font-size-sm);
		border-left: 3px solid var(--color-danger);
	}

	.games-list {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
		overflow-y: auto;
	}

	.game-card-wrapper {
		display: flex;
		gap: var(--spacing-sm);
		align-items: flex-start;
	}

	.game-card {
		flex: 1;
		background-color: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: var(--spacing-md);
		cursor: pointer;
		transition: all var(--transition-fast);
		display: flex;
		flex-direction: column;
		gap: var(--spacing-sm);
		font-family: inherit;
		text-align: left;
	}

	.game-card:hover {
		border-color: var(--color-primary);
		box-shadow: var(--shadow-md);
		transform: translateY(-2px);
	}

	.cancel-form {
		display: flex;
		align-items: flex-start;
		padding-top: var(--spacing-xs);
	}

	.btn-close-game {
		background-color: transparent;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		width: 40px;
		height: 40px;
		min-width: 40px;
		cursor: pointer;
		color: var(--color-text-light);
		font-size: var(--font-size-lg);
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all var(--transition-fast);
		padding: 0;
	}

	.btn-close-game:hover:not(:disabled) {
		border-color: var(--color-danger);
		color: var(--color-danger);
		background-color: var(--color-danger-light);
	}

	.btn-close-game:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.btn-close-game:active:not(:disabled) {
		transform: scale(0.95);
	}

	.game-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: var(--spacing-md);
	}

	.game-status {
		font-weight: var(--font-weight-medium);
		font-size: var(--font-size-sm);
		text-transform: capitalize;
	}

	.game-round {
		font-size: var(--font-size-sm);
		color: var(--color-text-light);
		background-color: var(--color-primary-light);
		padding: var(--spacing-xs) var(--spacing-sm);
		border-radius: var(--radius-sm);
		color: var(--color-primary);
	}

	.game-details {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-xs);
	}

	.game-id,
	.game-direction,
	.game-date {
		font-size: var(--font-size-sm);
		color: var(--color-text-light);
		margin: 0;
	}

	@media (max-width: 768px) {
		.content-grid {
			grid-template-columns: 1fr;
			gap: var(--spacing-lg);
		}

		.navbar-content {
			flex-direction: column;
			gap: var(--spacing-md);
			text-align: center;
		}

		.section {
			min-height: auto;
		}
	}
</style>
