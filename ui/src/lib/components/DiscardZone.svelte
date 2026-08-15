<!-- src/lib/components/DiscardZone.svelte -->
<script lang="ts">
	import { gameState } from '$lib/stores/gameState';
	import { getSuitSymbol } from '$lib/config';
	import { SUIT_COLORS } from '$lib/constants/cards';

	interface Props {
		isClickable?: boolean;
		onClick?: () => void;
	}

	let { isClickable = false, onClick }: Props = $props();

	let isHovered = $state(false);
</script>

<button
	class={`discard-zone ${isClickable ? 'discard-zone--clickable' : ''} ${isHovered ? 'discard-zone--hovered' : ''}`}
	disabled={!isClickable}
	onclick={onClick}
	onmouseenter={() => (isHovered = true)}
	onmouseleave={() => (isHovered = false)}
	title={$gameState.discard_pile.visible_cards.length > 0 ? `${$gameState.discard_pile.visible_cards[0].rank}${getSuitSymbol($gameState.discard_pile.visible_cards[0].suit)}` : 'Empty discard pile'}
>
	{#if $gameState.discard_pile.visible_cards.length > 0}
		{@const topCard = $gameState.discard_pile.visible_cards[0]}
		<div class="card-display" style="--suit-color: {SUIT_COLORS[topCard.suit]}">
			<div class="card-rank">{topCard.rank}</div>
			<div class="card-suit">{getSuitSymbol(topCard.suit)}</div>
		</div>
	{:else}
		<div class="empty-label">No card</div>
	{/if}
	<div class="discard-count">{$gameState.discard_pile.count}</div>
</button>

<style>
	.discard-zone {
		position: relative;
		height: 100%;
		aspect-ratio: 2.5 / 3.5;
		background: linear-gradient(135deg, #2a2a3e 0%, #1a1a2e 100%);
		background-image: 
			repeating-linear-gradient(
				45deg,
				transparent,
				transparent 10px,
				rgba(255, 255, 255, 0.03) 10px,
				rgba(255, 255, 255, 0.03) 20px
			);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: default;
		transition: all 0.2s ease;
		border: 2px solid transparent;
	}

	.discard-zone:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.discard-zone:not(:disabled) {
		cursor: pointer;
	}

	.discard-zone--clickable:hover {
		border-color: var(--color-primary);
		box-shadow:
			0 0 0 2px rgba(0, 123, 255, 0.2),
			var(--shadow-md);
	}

	.discard-zone--hovered {
		transform: scale(1.05);
	}

	.card-display {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		color: var(--suit-color);
		width: 85%;
		height: 85%;
		background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%);
		border-radius: clamp(2px, 3%, 4px);
	}

	.card-rank {
		font-size: clamp(0.875rem, 2.5vw, 1.5rem);
		font-weight: var(--font-weight-bold);
		line-height: 1;
	}

	.card-suit {
		font-size: clamp(0.75rem, 2vw, 1.25rem);
		margin-top: clamp(2px, 1.5%, 6px);
	}

	.empty-label {
		font-size: clamp(0.75rem, 1.5vw, 1rem);
		color: #8892b0;
		font-weight: var(--font-weight-bold);
	}

	.discard-count {
		position: absolute;
		bottom: clamp(2px, 3%, 8px);
		right: clamp(2px, 3%, 8px);
		background: rgba(0, 0, 0, 0.3);
		color: white;
		padding: clamp(1px, 1.5%, 4px) clamp(2px, 2%, 6px);
		border-radius: clamp(2px, 3%, 4px);
		font-size: clamp(0.65rem, 1.5vw, 0.875rem);
		font-weight: var(--font-weight-bold);
		font-family: monospace;
	}
</style>