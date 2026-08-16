<script lang="ts">
	import { onMount } from 'svelte';
	import type { LobbyState, PlayerInfo } from '$lib/types/lobby';

	interface Props {
		data: {
			gameId: string;
			playerId: string;
			playerName: string;
		};
	}

	let { data } = $props();

	let lobbyState = $state<LobbyState>({
		game_id: data.gameId,
		host_player_id: '',
		players: [],
		phase: 'WAITING_FOR_PLAYERS'
	});

	let isReady = $state(false);
	let isLoading = $state(false);
	let errorMessage = $state('');
	let successMessage = $state('');
	
	let isHost = $derived(lobbyState.host_player_id === data.playerId);
	let allReady = $derived(
		lobbyState.players.length > 0 &&
		lobbyState.players.every(p => p.connected && p.ready)
	);
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

		const wsUrl = `ws://localhost:8000/ws/games/${data.gameId}?token=${encodeURIComponent(token)}`;

		ws = new WebSocket(wsUrl);

		ws.onopen = () => {
			console.log('WebSocket connected');
			// Send initial ping to keep connection alive
			setInterval(() => {
				if (ws && ws.readyState === WebSocket.OPEN) {
					ws.send(JSON.stringify({ type: 'ping' }));
				}
			}, 30000);
		};

		ws.onmessage = (event) => {
			try {
				const message = JSON.parse(event.data);
				handleWebSocketMessage(message);
			} catch (err) {
				console.error('Failed to parse WebSocket message:', err);
			}
		};

		ws.onerror = (error) => {
			console.error('WebSocket error:', error);
			errorMessage = 'Connection error. Retrying...';
			setTimeout(() => connectWebSocket(), 3000);
		};

		ws.onclose = () => {
			console.log('WebSocket disconnected');
			// Attempt reconnect after delay
			setTimeout(() => connectWebSocket(), 3000);
		};
	}

	function handleWebSocketMessage(message: any) {
		if (message.type === 'player_connected') {
			// Update player connection status
			const player = lobbyState.players.find(p => p.player_id === message.player_id);
			if (player) {
				player.connected = true;
			} else {
				// New player joining
				lobbyState.players.push({
					player_id: message.player_id,
					player_name: message.player_name || message.player_id,
					ready: false,
					connected: true
				});
			}
		} else if (message.type === 'player_ready') {
			const player = lobbyState.players.find(p => p.player_id === message.player_id);
			if (player) {
				player.ready = true;
			}
		} else if (message.type === 'player_not_ready') {
			const player = lobbyState.players.find(p => p.player_id === message.player_id);
			if (player) {
				player.ready = false;
			}
		} else if (message.type === 'player_disconnected') {
			const player = lobbyState.players.find(p => p.player_id === message.player_id);
			if (player) {
				player.connected = false;
			}
		} else if (message.game_id) {
			// This is the initial game state from the server
			updateLobbyFromGameState(message);
		} else if (message.type === 'game_started') {
			// Game is starting, redirect will happen via form action
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

		// Extract players and their readiness from the game state
		// The server sends player info through the scoped state
		if (gameState.opponents) {
			// Map opponents to lobby format
			lobbyState.players = gameState.opponents.map((opp: any) => ({
				player_id: opp.player_id,
				player_name: opp.player_name,
				ready: false, // Will be updated via WebSocket messages
				connected: true
			}));
		}

		if (gameState.self) {
			// Add self to players list at beginning
			if (!lobbyState.players.some(p => p.player_id === gameState.self.player_id)) {
				lobbyState.players.unshift({
					player_id: gameState.self.player_id,
					player_name: gameState.self.player_name,
					ready: false,
					connected: true
				});
			}
		}

		// Check if we're the host (typically first player or from state)
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

			const response = await fetch(`${API_URL}/games/${data.gameId}/player/ready`, {
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

			// Broadcast ready status to others via WebSocket
			if (ws && ws.readyState === WebSocket.OPEN) {
				ws.send(
					JSON.stringify({
						type: isReady ? 'ready' : 'not_ready'
					})
				);
			}
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

			const response = await fetch(`${API_URL}/games/${data.gameId}/start`, {
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
				window.location.href = `/game/${data.gameId}/play`;
			}, 500);
		} catch (err) {
			errorMessage = err instanceof Error ? err.message : 'Failed to start game';
		} finally {
			isLoading = false;
		}
	}

	function getPlayerStatus(player: PlayerInfo): string {
		if (!player.connected) return 'Disconnected';
		if (!player.ready) return 'Waiting';
		return 'Ready';
	}

	function getStatusColor(player: PlayerInfo): string {
		if (!player.connected) return '#ef4444';
		if (!player.ready) return '#f59e0b';
		return '#10b981';
	}

	onMount(() => {
		connectWebSocket();

		return () => {
			if (ws) {
				ws.close();
			}
		};
	});
</script>

<div class="lobby-container">
	<div class="lobby-header">
		<h1>Game Lobby</h1>
		<p class="game-id">Game ID: {data.gameId}</p>
	</div>

	{#if errorMessage}
		<div class="message error-message">
			{errorMessage}
		</div>
	{/if}

	{#if successMessage}
		<div class="message success-message">
			{successMessage}
		</div>
	{/if}

	<div class="players-section">
		<h2>Players</h2>
		<div class="players-list">
			{#each lobbyState.players as player (player.player_id)}
				<div class="player-card">
					<div class="player-info">
						<div class="player-name">
							{player.player_name}
							{#if player.player_id === data.playerId}
								<span class="badge">You</span>
							{/if}
							{#if player.player_id === lobbyState.host_player_id}
								<span class="badge host">Host</span>
							{/if}
						</div>
						<div
							class="player-status"
							style="color: {getStatusColor(player)}"
						>
							{getPlayerStatus(player)}
						</div>
					</div>
					<div class="status-indicator" style="background: {getStatusColor(player)}"></div>
				</div>
			{/each}
		</div>
	</div>

	<div class="controls-section">
		{#if data.playerId === lobbyState.host_player_id}
			<div class="host-controls">
				<p class="info-text">You are the host. Start the game when all players are ready.</p>
				<button
					class="start-button"
					disabled={!allReady || isLoading}
					onclick={startGame}
				>
					{#if isLoading}
						Starting...
					{:else}
						Start Game
					{/if}
				</button>
			</div>
		{:else}
			<div class="player-controls">
				<p class="info-text">
					{isReady ? 'You are ready to play.' : 'Ready up to start the game.'}
				</p>
				<button
					class="ready-button {isReady ? 'active' : ''}"
					disabled={isLoading}
					onclick={toggleReady}
				>
					{#if isLoading}
						Updating...
					{:else if isReady}
						✓ Ready
					{:else}
						Not Ready
					{/if}
				</button>
			</div>
		{/if}

		<button
			class="return-button"
			disabled={isLoading}
			onclick={() => window.location.href = '/home'}
		>
			Return to Home
		</button>
	</div>

	<div class="ready-status">
		<p>
			{#if allReady}
				<span class="ready-indicator">✓</span> All players ready - Host can launch!
			{:else}
				<span class="waiting-indicator">⏱</span>
				Waiting for players...
				({lobbyState.players.filter(p => p.ready && p.connected).length}/{lobbyState.players.filter(
					p => p.connected
				).length} ready)
			{/if}
		</p>
	</div>
</div>

<style>
	.lobby-container {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
		background: linear-gradient(135deg, #1e1b4b 0%, #1e3a8a 100%);
		color: #e5e7eb;
		padding: 2rem;
		font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu,
			Cantarell, sans-serif;
	}

	.lobby-header {
		text-align: center;
		margin-bottom: 2rem;
	}

	.lobby-header h1 {
		font-size: 2.5rem;
		font-weight: 700;
		margin: 0 0 0.5rem 0;
		color: #fff;
	}

	.game-id {
		color: #9ca3af;
		margin: 0;
		font-size: 0.875rem;
		font-family: 'Monaco', 'Courier New', monospace;
	}

	.message {
		padding: 1rem;
		border-radius: 0.5rem;
		margin-bottom: 1.5rem;
		text-align: center;
		font-weight: 500;
	}

	.error-message {
		background-color: rgba(239, 68, 68, 0.1);
		color: #fca5a5;
		border: 1px solid rgba(239, 68, 68, 0.3);
	}

	.success-message {
		background-color: rgba(16, 185, 129, 0.1);
		color: #86efac;
		border: 1px solid rgba(16, 185, 129, 0.3);
	}

	.players-section {
		background: rgba(30, 27, 75, 0.5);
		border: 1px solid rgba(229, 231, 235, 0.1);
		border-radius: 0.75rem;
		padding: 2rem;
		margin-bottom: 2rem;
		flex: 1;
	}

	.players-section h2 {
		margin: 0 0 1.5rem 0;
		font-size: 1.5rem;
		font-weight: 600;
	}

	.players-list {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 1.5rem;
	}

	.player-card {
		background: rgba(31, 41, 55, 0.6);
		border: 1px solid rgba(229, 231, 235, 0.15);
		border-radius: 0.5rem;
		padding: 1.5rem;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 1rem;
		transition: all 0.3s ease;
	}

	.player-card:hover {
		background: rgba(31, 41, 55, 0.8);
		border-color: rgba(229, 231, 235, 0.25);
	}

	.player-info {
		flex: 1;
	}

	.player-name {
		font-weight: 600;
		font-size: 1rem;
		margin-bottom: 0.5rem;
		display: flex;
		align-items: center;
		gap: 0.5rem;
		flex-wrap: wrap;
	}

	.badge {
		background: rgba(99, 102, 241, 0.2);
		border: 1px solid rgba(99, 102, 241, 0.4);
		color: #93c5fd;
		padding: 0.25rem 0.75rem;
		border-radius: 9999px;
		font-size: 0.75rem;
		font-weight: 500;
	}

	.badge.host {
		background: rgba(168, 85, 247, 0.2);
		border-color: rgba(168, 85, 247, 0.4);
		color: #d8b4fe;
	}

	.player-status {
		font-size: 0.875rem;
		font-weight: 500;
	}

	.status-indicator {
		width: 12px;
		height: 12px;
		border-radius: 50%;
		flex-shrink: 0;
		box-shadow: 0 0 8px currentColor;
	}

	.controls-section {
		background: rgba(30, 27, 75, 0.5);
		border: 1px solid rgba(229, 231, 235, 0.1);
		border-radius: 0.75rem;
		padding: 2rem;
		margin-bottom: 2rem;
	}

	.host-controls,
	.player-controls {
		text-align: center;
	}

	.info-text {
		margin: 0 0 1.5rem 0;
		color: #d1d5db;
		font-size: 1rem;
	}

	button {
		padding: 0.75rem 1.5rem;
		border: none;
		border-radius: 0.5rem;
		font-size: 1rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.3s ease;
		margin-right: 1rem;
	}

	button:last-child {
		margin-right: 0;
	}

	button:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.start-button {
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
		color: white;
		padding: 1rem 2rem;
		font-size: 1.125rem;
		min-width: 200px;
	}

	.start-button:not(:disabled):hover {
		background: linear-gradient(135deg, #059669 0%, #047857 100%);
		box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
	}

	.ready-button {
		background: rgba(107, 114, 128, 0.3);
		color: #e5e7eb;
		border: 2px solid rgba(107, 114, 128, 0.5);
		padding: 0.75rem 2rem;
		font-size: 1.125rem;
		min-width: 150px;
	}

	.ready-button:not(:disabled):hover {
		background: rgba(107, 114, 128, 0.5);
		border-color: rgba(107, 114, 128, 0.7);
	}

	.ready-button.active {
		background: rgba(16, 185, 129, 0.2);
		color: #86efac;
		border-color: rgba(16, 185, 129, 0.5);
	}

	.return-button {
		background: rgba(99, 102, 241, 0.1);
		color: #93c5fd;
		border: 1px solid rgba(99, 102, 241, 0.3);
	}

	.return-button:not(:disabled):hover {
		background: rgba(99, 102, 241, 0.2);
		border-color: rgba(99, 102, 241, 0.5);
	}

	.ready-status {
		background: rgba(30, 27, 75, 0.5);
		border: 1px solid rgba(229, 231, 235, 0.1);
		border-radius: 0.75rem;
		padding: 1.5rem;
		text-align: center;
	}

	.ready-status p {
		margin: 0;
		font-size: 1.125rem;
		font-weight: 500;
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 0.75rem;
	}

	.ready-indicator {
		color: #10b981;
		font-size: 1.5rem;
	}

	.waiting-indicator {
		color: #f59e0b;
		font-size: 1.5rem;
		animation: pulse 1s infinite;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}
</style>