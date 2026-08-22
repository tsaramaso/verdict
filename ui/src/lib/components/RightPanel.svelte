<script lang="ts">
	import Timer from './Timer.svelte';
	import Leaderboard from './Leaderboard.svelte';
	import ButtonZone from './ButtonZone.svelte';
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

	const currentPlayerName = $derived.by(() => {
		if (gameState.current_player === gameState.self.player_id) {
			return gameState.self.player_name;
		}
		return gameState.opponents.find(o => o.player_id === gameState.current_player)?.player_name || 'Unknown';
	});

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
				return 'Round complete';
			case GAME_PHASES.GAME_OVER:
				return 'Game finished!';
			default:
				return 'Unknown phase';
		}
	}
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
		<Timer phase={gameState.phase} onTimeOut={onTimeOut} />
	</div>

	<div class="leaderboard-section">
		<Leaderboard {gameState} />
	</div>

	<div class="button-section">
		<ButtonZone />
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

	.button-section {
		padding-top: 8px;
		border-top: 1px solid var(--color-border, #ddd);
	}
</style>