<script lang="ts">
	import { displayRank, displaySuit } from '$lib/utils/cardTransform';
	import { SUIT_COLORS } from '$lib/constants/cards';
	import type { CardRank, CardSuit } from '$lib/constants/cards';

	interface Props {
		drawnCard?: { rank: CardRank; suit: CardSuit } | null;
		drawnCardSource?: 'deck' | 'discard' | null;
		isVisible?: boolean;
	}

	let {
		drawnCard,
		drawnCardSource,
		isVisible = false
	}: Props = $props();

	const sourceLabel = $derived(
		drawnCardSource === 'deck' ? 'From Deck' :
		drawnCardSource === 'discard' ? 'From Discard' :
		null
	);
</script>

{#if isVisible && drawnCard}
	<div class="peek-area">
		<div 
			class="peek-card"
			style="--suit-color: {SUIT_COLORS[drawnCard.suit]}"
		>
			<div class="peek-card__rank">{displayRank(drawnCard.rank)}</div>
			<div class="peek-card__suit">{displaySuit(drawnCard.suit)}</div>
		</div>
		{#if sourceLabel}
			<div class="source-badge">{sourceLabel}</div>
		{/if}
	</div>
{/if}

<style>
	@import '$lib/styles/card.css';

	.peek-area {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.75rem;
		padding: 0;
	}

	.peek-card {
		position: relative;
		width: 100%;
		height: 100%;
		aspect-ratio: 2.5 / 3.5;
		background: linear-gradient(135deg, #ffffff 0%, #f5f5f5 100%);
		border: 2px solid var(--suit-color);
		border-radius: var(--card-border-radius, 8px);
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
	}

	.peek-card__rank {
		font-size: clamp(2rem, 5vw, 3rem);
		font-weight: 700;
		color: var(--suit-color);
		line-height: 1;
	}

	.peek-card__suit {
		font-size: clamp(1.5rem, 4vw, 2.5rem);
		color: var(--suit-color);
		line-height: 1;
	}

	.source-badge {
		font-size: 0.875rem;
		font-weight: 600;
		color: var(--color-text-light, #666);
		text-transform: uppercase;
		letter-spacing: 0.5px;
		padding: 0.25rem 0.75rem;
		background: var(--color-bg-subtle, #f0f0f0);
		border-radius: 4px;
	}
</style>