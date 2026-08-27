<script lang="ts">
	import CardSlot from './CardSlot.svelte';
	import { gameState, getOpponentsThatKnowSlot, myOpponentKnowledge } from '$lib/stores/gameState';
	import { GAME_PHASES } from '$lib/config';
	import type { CardData } from '$lib/components/CardSlot.svelte';

	interface Props {
		cards?: (CardData | undefined)[];
		isYourCards?: boolean;
		onCardClick?: (slotIndex: number) => void;
		showKnowledge?: boolean;
		onQuickDiscard?: (slotIndex: number) => void;
	}

	let {
		cards = [undefined, undefined, undefined, undefined],
		isYourCards = false,
		onCardClick,
		showKnowledge = true,
		onQuickDiscard
	}: Props = $props();

	const discardTopCard = $derived($gameState.discard_pile.visible_cards[0]);
	const isQuickDiscardPhase = $derived($gameState.phase === GAME_PHASES.AWAITING_QUICK_DISCARD);

	function isSlotHighlighted(slotIdx: number): boolean {
		if (!isQuickDiscardPhase || !isYourCards) return false;

		const card = cards[slotIdx];
		if (!card || !card.known) return false;

		if (!discardTopCard) return false;

		// Highlight if card rank matches discard top card rank
		return card.rank === discardTopCard.rank;
	}

	function handleCardClick(slotIdx: number) {
		if (isQuickDiscardPhase && isYourCards) {
			// Quick discard phase: only allow clicking matching cards
			if (isSlotHighlighted(slotIdx)) {
				onQuickDiscard?.(slotIdx);
			}
		} else if (!isQuickDiscardPhase && isYourCards) {
			// Action phase: normal card selection
			onCardClick?.(slotIdx);
		}
	}

	function isClickableInPhase(slotIdx: number): boolean {
		if (!isYourCards) return false;

		if (isQuickDiscardPhase) {
			// Quick discard: only matching-rank cards clickable
			return isSlotHighlighted(slotIdx);
		}

		// Action phase: all cards clickable
		if ($gameState.phase === GAME_PHASES.AWAITING_ACTION) {
			return true;
		}

		return false;
	}
</script>

<div class="card-container">
	{#each [0, 1, 2, 3] as slotIdx}
		{@const card = cards[slotIdx]}
		{@const oppsWhoKnow = isYourCards
			? getOpponentsThatKnowSlot($myOpponentKnowledge, slotIdx)
			: []}
		{@const opponentKnowsRecord = oppsWhoKnow.reduce((acc, id) => {
			acc[id] = true;
			return acc;
		}, {})}
		<div style="order: {slotIdx < 2 ? slotIdx + 2 : slotIdx - 2}">
			<CardSlot
				{card}
				slotIndex={slotIdx}
				isYourCard={isYourCards}
				isClickable={isClickableInPhase(slotIdx)}
				isHighlighted={isSlotHighlighted(slotIdx)}
				opponentKnows={opponentKnowsRecord}
				showRankBadge={showKnowledge}
				onClick={() => handleCardClick(slotIdx)}
			/>
		</div>
	{/each}
</div>

<style>
	.card-container {
		display: grid;
		grid-template-columns: repeat(2, 1fr);
		gap: clamp(0.25rem, 0.5vw, 0.5rem);
		width: 100%;
		height: 100%;
		min-height: 0;
		min-width: 0;
	}

	.card-container > div {
		width: 100%;
		height: 100%;
		min-height: 0;
		min-width: 0;
	}
</style>