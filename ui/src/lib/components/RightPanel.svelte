<!-- src/lib/components/RightPanel.svelte -->
<script lang="ts">
	import Timer from './Timer.svelte';
	import { PHASE_LABELS, UI, GAME_PHASES } from '$lib/config';
 
	interface GameState {
		phase: string;
		round_number: number;
		current_player: string;
		self: {
			player_id: string;
			player_name: string;
			score: number;
		};
		opponents: Array<{
			player_id: string;
			player_name: string;
			score: number;
		}>;
	}
 
	interface Props {
		gameState: GameState;
		onTimeOut?: () => void;
	}
 
	let { gameState, onTimeOut }: Props = $props();
 
	const phaseLabel = $derived(PHASE_LABELS[gameState.phase] || 'Unknown');
	const isAutoAdvance = $derived(UI.autoAdvancePhases.includes(gameState.phase));


	function getPhaseDescription(phase: string, currentPlayer: string, myPlayerId: string): string {
		const isMyTurn = currentPlayer === myPlayerId;
		switch (phase) {
			case GAME_PHASES.TURN_START:
				return 'Starting new round...';
			case GAME_PHASES.DRAWING:
				return isMyTurn ? 'Your turn to draw' : 'Waiting for draw...';
			case GAME_PHASES.AWAITING_ACTION:
				return isMyTurn ? 'Choose your action' : 'Waiting for action...';
			case GAME_PHASES.AWAITING_SPELL_INVOCATION:
				return isMyTurn ? 'Use power card?' : 'Waiting for power use...';
			case GAME_PHASES.AWAITING_QUICK_DISCARD:
				return 'Discard matching ranks...';
			case GAME_PHASES.AWAITING_CALL_WINDOW:
				return 'Call window open';
			case GAME_PHASES.AWAITING_MATCH_WINDOW:
				return 'Match window open';
			case GAME_PHASES.AWAITING_DUEL_WINDOW:
				return 'Duel happening...';
			case GAME_PHASES.AWAITING_FINAL_PLEA_WINDOW:
				return 'Final plea window...';
			case GAME_PHASES.ROUND_OVER:
				return 'Round ending...';
			case GAME_PHASES.GAME_OVER:
				return 'Game over!';
			default:
				return '';
		}
	}

	function getStandings() {
		const standings = [];

		// Add self
		standings.push({
			player_id: gameState.self.player_id,
			name: `${gameState.self.player_name}`,
			score: gameState.self.score,
			isYou: true
		});

		// Add opponents sorted by score
		for (const opponent of gameState.opponents) {
			standings.push({
				player_id: opponent.player_id,
				name: opponent.player_name,
				score: opponent.score,
				isYou: false
			});
		}

		return standings.sort((a, b) => b.score - a.score);
	}

	const description = $derived(
		getPhaseDescription(gameState.phase, gameState.current_player, gameState.self.player_id)
	);

	const standings = $derived(getStandings());
</script>

<aside class="right-panel">
	<div class="phase-card">
		<div class="phase-card__label">Round</div>
		<div class="phase-card__value">{gameState.round_number}</div>
	</div>

	<div class="phase-card">
		<div class="phase-card__label">Phase</div>
		<div class="phase-card__value phase-card__value--phase">{phaseLabel}</div>
	</div>

	<div class="timer-card">
		{#if !isAutoAdvance}
			<Timer phase={gameState.phase} {onTimeOut} />
		{:else}
			<div class="auto-advance-indicator">
				<span>Auto...</span>
			</div>
		{/if}
	</div>

	<div class="standings-card">
		<div class="standings-header">Score</div>
		<div class="standings-list">
			{#each standings as player, idx}
				<div class={`standing-row ${player.isYou ? 'standing-row--you' : ''}`}>
					<div class="standing-place">{idx + 1}</div>
					<div class="standing-name">{player.name}</div>
					<div class="standing-score">{player.score}</div>
				</div>
			{/each}
		</div>
	</div>
</aside>

<style>
	.right-panel {
		display: grid;
		grid-template-columns: 1fr;
		grid-template-rows: auto auto auto 1fr;
		gap: var(--spacing-sm);
		padding: var(--spacing-md);
		background: var(--color-bg);
		border-left: 1px solid var(--color-border);
		overflow-y: auto;
		flex-shrink: 0;
		min-width: 180px;
		max-width: 200px;
	}

	.phase-card {
		display: flex;
		flex-direction: column;
		gap: 4px;
		padding: var(--spacing-md);
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		text-align: center;
	}

	.phase-card__label {
		font-size: var(--font-size-xs);
		color: var(--color-text-light);
		text-transform: uppercase;
		letter-spacing: 0.5px;
		font-weight: var(--font-weight-bold);
	}

	.phase-card__value {
		font-size: var(--font-size-lg);
		font-weight: var(--font-weight-bold);
		color: var(--color-text);
	}

	.phase-card__value--phase {
		color: var(--color-primary);
	}

	.timer-card {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: var(--spacing-md);
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		min-height: 60px;
	}

	.auto-advance-indicator {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		color: var(--color-text-light);
		font-size: var(--font-size-sm);
		font-weight: var(--font-weight-bold);
	}

	.auto-advance-indicator::after {
		content: '';
		display: inline-block;
		width: 8px;
		height: 8px;
		background: var(--color-success);
		border-radius: 50%;
		animation: pulse 1.5s ease-in-out infinite;
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
			transform: scale(1);
		}
		50% {
			opacity: 0.5;
			transform: scale(1.2);
		}
	}

	.standings-card {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-sm);
		padding: var(--spacing-md);
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-sm);
		overflow-y: auto;
	}

	.standings-header {
		font-size: var(--font-size-xs);
		color: var(--color-text-light);
		text-transform: uppercase;
		letter-spacing: 0.5px;
		font-weight: var(--font-weight-bold);
		padding-bottom: var(--spacing-sm);
		border-bottom: 1px solid var(--color-border);
	}

	.standings-list {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-xs);
	}

	.standing-row {
		display: grid;
		grid-template-columns: 20px 1fr 25px;
		gap: var(--spacing-xs);
		align-items: center;
		font-size: var(--font-size-xs);
		padding: var(--spacing-xs);
		border-radius: var(--radius-sm);
		background: var(--color-bg);
		border: 1px solid var(--color-border-light);
		transition: all 0.2s ease;
	}

	.standing-row--you {
		background: linear-gradient(135deg, rgba(0, 123, 255, 0.08) 0%, rgba(0, 123, 255, 0.03) 100%);
		border-color: var(--color-primary);
		font-weight: var(--font-weight-bold);
	}

	.standing-place {
		text-align: center;
		color: var(--color-text-light);
		font-size: var(--font-size-xs);
		font-weight: var(--font-weight-bold);
	}

	.standing-name {
		color: var(--color-text);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		font-size: var(--font-size-xs);
	}

	.standing-score {
		text-align: right;
		color: var(--color-text);
		font-family: monospace;
		font-size: var(--font-size-xs);
		font-weight: var(--font-weight-bold);
	}
</style>