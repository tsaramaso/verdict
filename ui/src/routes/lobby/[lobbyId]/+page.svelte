<script lang="ts">
	import { onMount } from 'svelte';
	import type { LobbyState, PlayerInfo } from '$lib/types/lobby';

	interface Props {
		data: {
			lobbyId: string;
			lobbyData: {
				host_player_id: string;
				players: Record<string, any>;
				player_count: number;
			};
		};
	}

	let { data } = $props();

	// Reactive state
	let lobbyState = $state({
		lobby_id: data.lobbyId,
		host_player_id: data.lobbyData.host_player_id,
		players: Object.values(data.lobbyData.players || {}).map((p: any) => ({
			player_id: p.id || '',
			player_name: p.name,
			ready: p.ready || false,
			connected: true
		})),
		player_count: data.lobbyData.player_count || 0
	});

	let allPlayers = $state<(PlayerInfo & { uuid: string; joined: boolean })[]>([]);
	let isReady = $state(false);
	let isLoading = $state(false);
	let errorMessage = $state('');
	let successMessage = $state('');

	// Derived state
	let connectedPlayers = $derived(lobbyState.players.filter(p => p.connected).length);
	let readyPlayers = $derived(lobbyState.players.filter(p => p.ready && p.connected).length);
	let isHost = $derived(lobbyState.host_player_id === data.data?.playerId);
	let allReady = $derived(
		lobbyState.players.length > 0 &&
		lobbyState.players.every(p => p.connected && p.ready)
	);

	// Non-reactive references
	let ws: WebSocket | null = null;
	const API_URL = 'http://localhost:8000';

	function getToken(): string | null {
		const cookieString = document.cookie;
		const cookies = cookieString.split(';');
		for (const cookie of cookies) {
			const [name, value] = cookie.trim().split('=');
			if (name === 'auth_token') return decodeURIComponent(value);
		}
		return null;
	}

	function connectWebSocket() {
		const token = getToken();
		if (!token) {
			errorMessage = 'Authentication token not found';
			return;
		}

		// Lobbies don't use WebSocket - they're ephemeral in-memory
		// Real-time updates will be added in Phase 2
		console.log('Lobby: WebSocket disabled - lobbies are ephemeral');
		return;

		// WebSocket disabled for ephemeral lobbies
	}

	function handleWebSocketMessage(message: any) {
		if (message.type === 'player_connected') {
			const player = allPlayers.find(p => p.player_id === message.player_id);
			if (player) {
				player.connected = true;
				player.joined = true;
			}
		} else if (message.type === 'player_ready') {
			const player = allPlayers.find(p => p.player_id === message.player_id);
			if (player) {
				player.ready = true;
			}
		} else if (message.type === 'player_not_ready') {
			const player = allPlayers.find(p => p.player_id === message.player_id);
			if (player) {
				player.ready = false;
			}
		} else if (message.type === 'player_disconnected') {
			const player = allPlayers.find(p => p.player_id === message.player_id);
			if (player) {
				player.connected = false;
			}
		} else if (message.game_id) {
			updateLobbyFromGameState(message);
		} else if (message.type === 'game_started') {
			successMessage = 'Game starting!';
		}
	}

	function updateLobbyFromGameState(gameState: any) {
		if (gameState.game_id) {
			lobbyState.game_id = gameState.game_id;
		}

		if (gameState.phase) {
			lobbyState.phase = gameState.phase;
		}

		// Initialize allPlayers from game creation (all invited players)
		if (gameState.player_order) {
			allPlayers = gameState.player_order.map((playerId: string) => {
				const existing = allPlayers.find(p => p.player_id === playerId);
				return {
					player_id: playerId,
					uuid: playerId,
					player_name: gameState.players?.[playerId]?.player_name || playerId,
					ready: gameState.players?.[playerId]?.ready || false,
					connected: gameState.players?.[playerId]?.connected || false,
					joined: !!gameState.players?.[playerId]
				};
			});
		}

		// Update lobbyState with currently connected players
		if (gameState.opponents) {
			lobbyState.players = gameState.opponents.map((opp: any) => ({
				player_id: opp.player_id,
				player_name: opp.player_name,
				ready: false,
				connected: true
			}));
		}

		if (gameState.self) {
			if (!lobbyState.players.some(p => p.player_id === gameState.self.player_id)) {
				lobbyState.players.unshift({
					player_id: gameState.self.player_id,
					player_name: gameState.self.player_name,
					ready: false,
					connected: true
				});
			}
		}

		if (gameState.host_player_id) {
			lobbyState.host_player_id = gameState.host_player_id;
		}
	}

	async function toggleReady() {
		isLoading = true;
		errorMessage = '';

		try {
			const token = getToken();
			if (!token) throw new Error('No auth token');

			const response = await fetch(`${API_URL}/lobbies/${data.lobbyId}/player/ready`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`,
					'Content-Type': 'application/json'
				},
				body: JSON.stringify({ ready: !isReady })
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.detail || 'Failed to update ready status');
			}

			isReady = !isReady;
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'Failed to update status';
		} finally {
			isLoading = false;
		}
	}

	async function startGame() {
		if (!isHost) {
			errorMessage = 'Only the host can start the game';
			return;
		}

		if (!allReady) {
			errorMessage = 'Not all players are ready';
			return;
		}

		isLoading = true;
		errorMessage = '';

		try {
			const token = getToken();
			if (!token) throw new Error('No auth token');

			const response = await fetch(`${API_URL}/lobbies/${data.lobbyId}/start`, {
				method: 'POST',
				headers: {
					Authorization: `Bearer ${token}`
				}
			});

			if (!response.ok) {
				const error = await response.json();
				throw new Error(error.detail || 'Failed to start game');
			}

			successMessage = 'Game started! Redirecting...';
			setTimeout(() => {
				window.location.href = `/game/${response.game_id}/play`;
			}, 500);
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'Failed to start game';
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		connectWebSocket();
	});
</script>

<div class="lobby-wrapper">
	<div class="lobby-container">
		<div class="lobby-header">
			<h1>Game Lobby</h1>
			<p class="game-id">Lobby ID: {data.lobbyId}</p>
		</div>

		{#if errorMessage}
			<div class="alert alert-danger">
				{errorMessage}
			</div>
		{/if}

		{#if successMessage}
			<div class="alert alert-success">
				{successMessage}
			</div>
		{/if}

		<div class="players-table-wrapper">
			<table class="players-table">
				<thead>
					<tr>
						<th>Player</th>
						<th>UUID</th>
						<th>Status</th>
						<th>Ready</th>
					</tr>
				</thead>
				<tbody>
					{#each allPlayers as player (player.uuid)}
						<tr class="player-row" class:not-joined={!player.joined} class:joined={player.joined} class:ready={player.ready && player.joined}>
							<td class="player-name-cell">
								{player.player_name}
								{#if player.player_id === data.playerId}
									<span class="badge badge-info">You</span>
								{/if}
								{#if player.player_id === lobbyState.host_player_id}
									<span class="badge badge-warning">Host</span>
								{/if}
							</td>
							<td class="uuid-cell">{player.uuid.slice(0, 8)}...</td>
							<td class="status-cell">
								{#if !player.joined}
									<span class="status-label pending">Not joined</span>
								{:else if !player.connected}
									<span class="status-label disconnected">Disconnected</span>
								{:else if player.ready}
									<span class="status-label ready">✓ Ready</span>
								{:else}
									<span class="status-label waiting">Waiting</span>
								{/if}
							</td>
							<td class="ready-indicator">
								{#if player.ready && player.joined}
									<div class="ready-badge">✓</div>
								{:else if player.joined}
									<div class="not-ready-badge">−</div>
								{/if}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="ready-counter">
			<p>
				{#if allReady}
					<span class="counter-badge success">✓</span>
					All players ready
				{:else}
					<span class="counter-badge waiting">⏱</span>
					{readyPlayers}/{connectedPlayers} ready
				{/if}
			</p>
		</div>

		<div class="button-group">
			{#if isHost}
				<button class="btn btn-primary btn-lg" disabled={!allReady || isLoading} onclick={() => startGame()}>
					{#if isLoading}
						Starting...
					{:else}
						Start Game
					{/if}
				</button>
			{:else}
				<button
					class="btn btn-primary btn-lg"
					class:active={isReady}
					disabled={isLoading}
					onclick={() => toggleReady()}
				>
					{#if isLoading}
						Updating...
					{:else if isReady}
						✓ Ready
					{:else}
						Mark Ready
					{/if}
				</button>
			{/if}
			<button class="btn btn-secondary" disabled={isLoading} onclick={() => window.location.href = '/home'}>
				Return Home
			</button>
		</div>
	</div>
</div>

<style>
	.lobby-wrapper {
		min-height: 100vh;
		background-color: var(--color-bg);
		padding: var(--spacing-xl);
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.lobby-container {
		width: 100%;
		max-width: 800px;
		background-color: var(--color-bg-card);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		padding: var(--spacing-2xl);
	}

	.lobby-header {
		text-align: center;
		margin-bottom: var(--spacing-2xl);
	}

	.lobby-header h1 {
		font-size: var(--font-size-2xl);
		font-weight: var(--font-weight-bold);
		color: var(--color-text);
		margin-bottom: var(--spacing-sm);
	}

	.game-id {
		font-size: var(--font-size-sm);
		color: var(--color-text-lighter);
		font-family: var(--font-family-mono);
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

	.alert-success {
		background-color: var(--color-success-light);
		color: var(--color-success);
		border: 1px solid var(--color-success);
	}

	.players-table-wrapper {
		margin-bottom: var(--spacing-2xl);
		border-radius: var(--radius-md);
		overflow: hidden;
		border: 1px solid var(--color-border);
	}

	.players-table {
		width: 100%;
		border-collapse: collapse;
		background-color: var(--color-bg-card);
	}

	.players-table thead {
		background-color: var(--color-bg);
	}

	.players-table th {
		padding: var(--spacing-md);
		text-align: left;
		font-weight: var(--font-weight-semibold);
		font-size: var(--font-size-sm);
		color: var(--color-text);
		border-bottom: 1px solid var(--color-border);
	}

	.players-table td {
		padding: var(--spacing-md);
		border-bottom: 1px solid var(--color-border-light);
		font-size: var(--font-size-sm);
	}

	.player-row {
		background-color: var(--color-bg-card);
		transition: all var(--transition-base);
	}

	/* Stage 1: Not joined (grey, disabled) */
	.player-row.not-joined {
		background-color: #f9f9f9;
		opacity: 0.6;
	}

	.player-row.not-joined td {
		color: var(--color-text-lighter);
	}

	/* Stage 2: Joined but not ready (white/normal) */
	.player-row.joined:not(.ready) {
		background-color: var(--color-bg-card);
	}

	.player-row.joined:not(.ready):hover {
		background-color: #fafafa;
	}

	/* Stage 3: Ready (light success) */
	.player-row.ready {
		background-color: rgba(76, 175, 80, 0.05);
	}

	.player-row.ready:hover {
		background-color: rgba(76, 175, 80, 0.08);
	}

	.player-name-cell {
		font-weight: var(--font-weight-semibold);
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		flex-wrap: wrap;
	}

	.uuid-cell {
		font-family: var(--font-family-mono);
		color: var(--color-text-lighter);
		font-size: var(--font-size-xs);
	}

	.status-cell {
		text-align: center;
	}

	.status-label {
		display: inline-block;
		padding: 2px 8px;
		border-radius: var(--radius-sm);
		font-size: var(--font-size-xs);
		font-weight: var(--font-weight-semibold);
	}

	.status-label.pending {
		background-color: #f0f0f0;
		color: #999;
	}

	.status-label.waiting {
		background-color: var(--color-warning-light);
		color: var(--color-warning);
	}

	.status-label.ready {
		background-color: var(--color-success-light);
		color: var(--color-success);
	}

	.status-label.disconnected {
		background-color: var(--color-danger-light);
		color: var(--color-danger);
	}

	.ready-indicator {
		text-align: center;
		font-weight: var(--font-weight-bold);
	}

	.ready-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background-color: var(--color-success);
		color: white;
		font-size: var(--font-size-sm);
	}

	.not-ready-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 28px;
		height: 28px;
		border-radius: 50%;
		background-color: var(--color-border);
		color: var(--color-text-lighter);
		font-size: var(--font-size-lg);
	}

	.ready-counter {
		background-color: var(--color-bg);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: var(--spacing-md);
		margin-bottom: var(--spacing-xl);
		text-align: center;
	}

	.ready-counter p {
		margin: 0;
		font-size: var(--font-size-base);
		font-weight: var(--font-weight-medium);
		color: var(--color-text);
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--spacing-sm);
	}

	.counter-badge {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 24px;
		height: 24px;
		border-radius: 50%;
		font-weight: var(--font-weight-bold);
		font-size: var(--font-size-sm);
	}

	.counter-badge.success {
		background-color: var(--color-success-light);
		color: var(--color-success);
	}

	.counter-badge.waiting {
		background-color: var(--color-warning-light);
		color: var(--color-warning);
		animation: pulse 1s infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; }
		50% { opacity: 0.5; }
	}

	.button-group {
		display: flex;
		gap: var(--spacing-md);
		flex-wrap: wrap;
		justify-content: center;
	}

	.btn {
		padding: var(--spacing-md) var(--spacing-lg);
		border: none;
		border-radius: var(--radius-md);
		font-size: var(--font-size-base);
		font-weight: var(--font-weight-semibold);
		cursor: pointer;
		transition: all var(--transition-base);
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

	.btn-primary.active {
		background-color: var(--color-success);
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
		padding: var(--spacing-md) var(--spacing-xl);
		font-size: var(--font-size-lg);
		min-width: 150px;
	}

	@media (max-width: 640px) {
		.lobby-container {
			padding: var(--spacing-lg);
		}
		.players-grid {
			grid-template-columns: 1fr;
		}
		.button-group {
			flex-direction: column;
		}
		.btn {
			width: 100%;
		}
	}
</style>