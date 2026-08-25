<script lang="ts">
	import { calculateKnownSum, getPointsToRenaissance } from '$lib/config';
	import { gameState } from '$lib/stores/gameState';
	import YourCardsZone from './YourCardsZone.svelte';

	interface Props {
		onCardClick?: (slotIndex: number) => void;
		onQuickDiscard?: (slotIndex: number) => void;
	}

	let { onCardClick, onQuickDiscard }: Props = $props();

	const isYourTurn = $derived($gameState.current_player === $gameState.self.player_id);

	const knownSum = $derived(
		calculateKnownSum(
			$gameState.self.hand,
			$gameState.rules.black_king_value,
			$gameState.rules.red_king_value,
			$gameState.rules.rank_values
		)
	);

	const nextRenaissance = $derived(
		getPointsToRenaissance(
			$gameState.self.score,
			Object.keys($gameState.rules.renaissance_thresholds).map(Number)
		)
	);

	const knownSumColor = $derived(knownSum <= 7 ? '#4caf50' : '#f44336');
</script>

<div class="your-zones-row">
	<div class="your-zones-container" class:is-your-turn={isYourTurn}>
		<div class="player-info-label">
			<div class="player-name">{$gameState.self.player_name}<br /> (You)</div>
			<div class="player-meta">
				<span class="score">Score:<br />{$gameState.self.score}</span>
				<span class="score" style="color: {knownSumColor}">
					Known Sum:<br />{knownSum}
				</span>
				<span class="score">
					Next Renaissance:<br />{nextRenaissance}
				</span>
			</div>
		</div>
		<div class="your-zone">
			<YourCardsZone {onCardClick} {onQuickDiscard} />
		</div>
	</div>
</div>

<style>
	@keyframes turn-glow-self {
		0%,
		100% {
			box-shadow:
				0 0 12px rgba(0, 123, 255, 0.3),
				inset 0 0 8px rgba(0, 123, 255, 0.1);
		}
		50% {
			box-shadow:
				0 0 24px rgba(0, 123, 255, 0.6),
				inset 0 0 12px rgba(0, 123, 255, 0.2);
		}
	}

	.your-zones-row {
		display: flex;
		width: 100%;
		height: 100%;
		min-height: 0;
		min-width: 0;
		justify-content: center;
		align-items: center;
	}

	.your-zones-container {
		display: flex;
		gap: clamp(0.5rem, 1.5vw, 1.5rem);
		justify-content: center;
		align-items: center;
		height: 100%;
		min-height: 0;
		max-width: 100%;
		overflow: visible;
		border-radius: 5%;
		background-color: rgba(1, 160, 252, 0.345);
		transition: box-shadow 0.3s ease;
		border: 2px solid transparent;
		padding: clamp(0.25rem, 0.75vw, 0.5rem);
		box-sizing: border-box;
	}

	.your-zones-container.is-your-turn {
		animation: turn-glow-self 1.5s ease-in-out infinite;
		border-color: rgba(0, 123, 255, 0.5);
	}

	.your-zone {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 0;
		min-width: 0;
		aspect-ratio: 2.5 / 3.5;
		height: 100%;
		flex: 0 0 auto;
		margin-right: 5%

	}

	.player-info-label {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
		text-align: center;
		margin-left: 5%;
	}

	.player-name {
		font-weight: var(--font-weight-bold);
		font-size: clamp(0.75rem, 1vw, 1rem);
		color: var(--color-text);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		max-width: 100%;
	}

	.player-meta {
		display: flex;
		gap: clamp(0.5rem, 1vw, 1rem);
		font-size: clamp(0.65rem, 0.8vw, 0.875rem);
		color: var(--color-text-light);
	}

	.score {
		white-space: nowrap;
	}
</style>