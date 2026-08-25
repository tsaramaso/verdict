<script lang="ts">
	import { gameState } from '$lib/stores/gameState';
	import { displayRank, displaySuit } from '$lib/utils/cardTransform';
	import { SUIT_COLORS } from '$lib/constants/cards';

	interface Props {
		isClickable?: boolean;
		onClick?: () => void;
	}

	let { isClickable = false, onClick }: Props = $props();

	let isHovered = $state(false);
</script>

<button
	class="discard-zone"
	class:clickable={isClickable}
	class:clickable-glow={isClickable}
	class:hovered={isHovered}
	disabled={!isClickable}
	onclick={onClick}
	onmouseenter={() => (isHovered = true)}
	onmouseleave={() => (isHovered = false)}
	title={$gameState.discard_pile.visible_cards.length > 0
		? `${displayRank($gameState.discard_pile.visible_cards[0].rank)}${displaySuit($gameState.discard_pile.visible_cards[0].suit)}`
		: 'Empty discard pile'}
>
	{#if $gameState.discard_pile.visible_cards.length > 0}
		{@const topCard = $gameState.discard_pile.visible_cards[0]}
		<div class="card-face" style="--suit-color: {SUIT_COLORS[topCard.suit]}">
			<div class="card-face__rank">{displayRank(topCard.rank)}</div>
			<div class="card-face__suit">{displaySuit(topCard.suit)}</div>
		</div>
	{:else}
		<div class="empty-label">-</div>
	{/if}
	<div class="card-count">{$gameState.discard_pile.count}</div>
</button>

<style>
	@import '$lib/styles/card.css';
	@import '$lib/styles/clickable.css';

	.discard-zone {
		position: relative;
		padding: 0;
		background: transparent;
		border: none;
		cursor: default;
		transition: all 0.2s ease;
		display: grid;
		grid-template-columns: auto 1fr;
		grid-template-rows: 1fr;
		align-items: center;
		gap: 0.5rem;
		height: 100%;
		max-height: 100%;
	}

	.discard-zone:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.discard-zone.clickable {
		cursor: pointer;
	}

	.discard-zone.clickable:hover {
		transform: translateY(-4px);
	}

	.discard-zone.clickable:focus-visible {
		outline: 2px solid var(--color-primary, #007bff);
		outline-offset: 4px;
	}

	.discard-zone.hovered .card-face {
		box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
	}

	.card-face {
		width: auto !important;
		height: 100%;
		max-height: 100%;
	}

	.empty-label {
		font-size: 32px;
		color: var(--color-text-light, #999);
		display: flex;
		align-items: center;
		justify-content: center;
		width: auto;
		height: 100%;
		max-height: 100%;
	}

	.card-count {
		font-weight: var(--font-weight-bold);
		font-size: clamp(0.75rem, 1.2vw, 1rem);
		color: var(--color-text);
		text-align: center;
		min-width: 2rem;
		white-space: nowrap;
		position: static !important;
		bottom: auto !important;
		right: auto !important;
	}
</style>