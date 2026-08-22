<script lang="ts">
	import type { CardRank, CardSuit } from '$lib/constants/cards';
	import { SUIT_LABELS, RANK_LABELS, SUIT_COLORS } from '$lib/constants/cards';

	interface Props {
		card: { rank: CardRank; suit: CardSuit } | null;
		isVisible: boolean;
		isActivePlayer: boolean;
	}

	let { card, isVisible, isActivePlayer }: Props = $props();

	function getSuitColor(suit: CardSuit): string {
		return SUIT_COLORS[suit];
	}

	function getSuitSymbol(suit: CardSuit): string {
		return SUIT_LABELS[suit];
	}
</script>

<div class="peek-area" class:visible={isVisible && isActivePlayer}>
	{#if isVisible && isActivePlayer && card}
		<div class="peek-card card-face" style="color: {getSuitColor(card.suit)}">
			<div class="card-face__rank">{RANK_LABELS[card.rank]}</div>
			<div class="card-face__suit">{getSuitSymbol(card.suit)}</div>
		</div>
		<div class="peek-label">Drawn Card</div>
	{:else}
		<div class="peek-empty">-</div>
	{/if}
</div>

<style>
	.peek-area {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 8px;
		padding: 16px;
		min-width: 150px;
		opacity: 0.3;
		transition: opacity 0.3s ease;
	}

	.peek-area.visible {
		opacity: 1;
	}

	.peek-card {
		width: 120px;
		height: 168px;
	}

	.peek-empty {
		width: 120px;
		height: 168px;
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 32px;
		color: var(--color-text-light, #999);
	}

	.peek-label {
		font-size: 0.875rem;
		font-weight: 500;
		color: var(--color-text, #333);
		text-transform: uppercase;
		letter-spacing: 0.5px;
	}
</style>