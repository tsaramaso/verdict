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

<div
	class={`discard-zone ${isClickable ? 'discard-zone--clickable' : ''} ${isHovered ? 'discard-zone--hovered' : ''}`}
	role="button"
	tabindex={isClickable ? 0 : -1}
	onclick={onClick}
	onmouseenter={() => (isHovered = true)}
	onmouseleave={() => (isHovered = false)}
>
	{#if $gameState.discard_pile.visible_cards.length > 0}
		{@const topCard = $gameState.discard_pile.visible_cards[0]}
		<div class="discard-card" style="--suit-color: {SUIT_COLORS[topCard.suit]}">
			<div class="card-rank">{topCard.rank}</div>
			<div class="card-suit">{getSuitSymbol(topCard.suit)}</div>
		</div>
	{:else}
		<div class="discard-empty">
			<div class="discard-pattern"></div>
		</div>
	{/if}

	<div class="discard-count">{$gameState.discard_pile.count}</div>
</div>

<style>
	.discard-zone {
		position: relative;
		width: 100%;
		aspect-ratio: 2.5 / 3.5;
		background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: default;
		transition: all 0.2s ease;
		border: 2px solid transparent;
	}

	.discard-zone--clickable {
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

	.discard-card {
		width: 85%;
		height: 85%;
		background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%);
		border-radius: var(--radius-sm);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		color: var(--suit-color);
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

	.discard-empty {
		width: 85%;
		height: 85%;
		border: 2px dashed rgba(100, 100, 100, 0.3);
		border-radius: var(--radius-sm);
		display: flex;
		align-items: center;
		justify-content: center;
		color: var(--color-text-lighter);
		font-size: var(--font-size-sm);
	}

	.discard-pattern {
		width: 100%;
		height: 100%;
		background: repeating-linear-gradient(
			45deg,
			transparent,
			transparent 10px,
			rgba(100, 100, 100, 0.05) 10px,
			rgba(100, 100, 100, 0.05) 20px
		);
	}

	.discard-count {
		position: absolute;
		bottom: clamp(4px, 3%, 12px);
		right: clamp(4px, 3%, 12px);
		background: rgba(0, 0, 0, 0.2);
		color: var(--color-text);
		padding: clamp(2px, 1.5%, 6px) clamp(4px, 2%, 8px);
		border-radius: var(--radius-sm);
		font-size: clamp(0.65rem, 1.5vw, 0.875rem);
		font-weight: var(--font-weight-bold);
		font-family: monospace;
	}
</style>