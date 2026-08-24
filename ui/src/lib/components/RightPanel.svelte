<script lang="ts">
	import Timer from './Timer.svelte';
	import LeaderboardPanel from './LeaderboardPanel.svelte';
	import { PHASE_LABELS, UI, GAME_PHASES } from '$lib/config';
	import type { GameState, GamePhase } from '$lib/stores/gameState';

	interface PlayerStanding {
		player_id: string;
		name: string;
		score: number;
		isYou?: boolean;
	}

	interface Props {
		gameState: GameState;
		onTimeOut?: () => void;
	}

	let { gameState, onTimeOut }: Props = $props();

	const phaseLabel = $derived(PHASE_LABELS[gameState.phase] || 'Unknown');

	const currentPlayerName = $derived.by(() => {
		if (gameState.current_player === gameState.self.player_id) {
			console.log('[RightPanel] Current player is self:', gameState.self.player_name);
			return gameState.self.player_name;
		}
		const opponentName =
			gameState.opponents.find((o) => o.player_id === gameState.current_player)?.player_name ||
			'Unknown';
		console.log('[RightPanel] Current player is opponent:', opponentName);
		return opponentName;
	});

	const standings = $derived.by(() => {
		const all: PlayerStanding[] = [];

		// Add self
		all.push({
			player_id: gameState.self.player_id,
			name: `${gameState.self.player_name} (You)`,
			score: gameState.self.score,
			isYou: true
		});

		// Add opponents
		for (const opponent of gameState.opponents) {
			all.push({
				player_id: opponent.player_id,
				name: opponent.player_name,
				score: opponent.score,
				isYou: false
			});
		}

		return all.sort((a, b) => a.score - b.score);
	});
</script>

<div class="right-panel">
	<div class="info-section">
		<div class="phase-card">
			<div class="phase-card__label">Round</div>
			<div class="phase-card__value">{gameState.round_number}</div>
		</div>

		<div class="phase-card">
			<div class="phase-card__label">Phase</div>
			<div class="phase-card__value phase-card__value--phase">{phaseLabel}</div>
		</div>

		<div class="phase-card">
			<div class="phase-card__label">Current Turn</div>
			<div class="phase-card__value phase-card__value--player">{currentPlayerName}</div>
		</div>
	</div>

	<div class="timer-section">
		<Timer phase={gameState.phase as GamePhase} {onTimeOut} />
	</div>

	<div class="leaderboard-section">
		<LeaderboardPanel {standings} />
	</div>
</div>

<style>
	.right-panel {
		display: flex;
		flex-direction: column;
		gap: clamp(0.5rem, 1.5vw, 1rem);
		padding: clamp(1rem, 2vw, 1.5rem);
		background: var(--color-bg-card, #fafafa);
		border-radius: var(--radius-md, 8px);
		min-width: 200px;
		max-width: 280px;
		height: 100%;
		min-height: 0;
		overflow-y: auto;
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	.info-section {
		display: flex;
		flex-direction: column;
		gap: 8px;
	}

	.phase-card {
		display: flex;
		flex-direction: column;
		gap: 4px;
		padding: 12px;
		background: var(--color-bg, #f5f5f5);
		border-radius: 4px;
		border: 1px solid var(--color-border, #ddd);
	}

	.phase-card__label {
		font-size: 11px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		color: var(--color-text-light, #666);
	}

	.phase-card__value {
		font-size: 14px;
		font-weight: 600;
		color: var(--color-text, #333);
	}

	.phase-card__value--phase {
		color: var(--color-primary, #007bff);
		font-size: 15px;
	}

	.phase-card__value--player {
		color: var(--color-text, #333);
		font-weight: 600;
	}

	.timer-section {
		padding: clamp(0.5rem, 1vw, 1rem) 0;
		border-top: 1px solid var(--color-border, #ddd);
		border-bottom: 1px solid var(--color-border, #ddd);
	}

	.leaderboard-section {
		flex: 1;
		min-height: 0;
		overflow-y: auto;
	}
</style>
