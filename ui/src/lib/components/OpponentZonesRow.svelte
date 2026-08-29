<!-- src/lib/components/OpponentZonesRow.svelte -->
<script lang="ts">
	import { gameState } from '$lib/stores/gameState';
	import OpponentCardsZone from './OpponentCardsZone.svelte';
	import type { OpponentInfo } from '$lib/stores/gameState';

	interface Props {
		opponents?: OpponentInfo[];
		currentPlayer?: string;
		onOpponentCardClick?: (opponentId: string, slotIndex: number) => void;
	}

	let {
		opponents = $gameState.opponents,
		currentPlayer = $gameState.current_player,
		onOpponentCardClick
	}: Props = $props();
</script>

<div class="opponent-zones-row">
	<div class="opponent-zones-container">
		{#each opponents as opponent (opponent.player_id)}
			{@const isCurrentTurn = currentPlayer === opponent.player_id}
			<div class="player-box" class:is-opponent-turn={isCurrentTurn}>
				<div class="player-info-label">
					<div class="player-name">{opponent.player_name}</div>
					<div class="player-meta">
						<span class="score">Score: {opponent.score}</span>
					</div>
				</div>
				<div class="opponent-zone">
					<OpponentCardsZone
						{opponent}
						onCardClick={(slotIdx) => onOpponentCardClick?.(opponent.player_id, slotIdx)}
					/>
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	@keyframes turn-glow-opponent {
		0%,
		100% {
			box-shadow:
				0 0 12px rgba(244, 67, 54, 0.3),
				inset 0 0 8px rgba(244, 67, 54, 0.1);
		}
		50% {
			box-shadow:
				0 0 24px rgba(244, 67, 54, 0.6),
				inset 0 0 12px rgba(244, 67, 54, 0.2);
		}
	}

	.opponent-zones-row {
		display: flex;
		width: 100%;
		height: 100%;
		min-height: 0;
		min-width: 0;
		justify-content: center;
		align-items: center;
	}

	.opponent-zones-container {
		display: flex;
		width: 100%;
		height: 100%;
		gap: clamp(0.75rem, 1.5vw, 1.5rem);
		justify-content: center;
		align-items: center;
		padding: 0;
		min-height: 0;
		min-width: 0;
	}

	.player-box {
		border-color: black;
		display: flex;
		gap: clamp(0.5rem, 1.5vw, 1.5rem);
		justify-content: center;
		align-items: center;
		height: 100%;
		min-height: 0;
		background-color: rgba(255, 42, 0, 0.371);
		border-radius: 5%;
		min-width: fit-content;
		max-width: 100%;
		overflow: visible;
		transition: box-shadow 0.3s ease;
		border: 2px solid transparent;
		padding: clamp(0.25rem, 0.75vw, 0.5rem);
		box-sizing: border-box;
	}

	.player-box.is-opponent-turn {
		animation: turn-glow-opponent 1.5s ease-in-out infinite;
		border-color: rgba(244, 67, 54, 0.5);
	}

	.player-info-label {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 2px;
		width: 100%;
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

	.opponent-zone {
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 0;
		min-width: 0;
		aspect-ratio: 2.5 / 3.5;
		height: 100%;
		flex: 0 0 auto;
		margin-right: 5%;
	}
</style>
