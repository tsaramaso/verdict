<!-- src/lib/components/OpponentCardsZone.svelte -->
<script lang="ts">
	import CardContainer from './CardContainer.svelte';
	import type { OpponentInfo } from '$lib/stores/gameState';

	interface Props {
		opponent: OpponentInfo;
	}

	let { opponent }: Props = $props();

	// Convert known_cards to card data format for CardContainer
	const opponentCards = $derived.by(() => {
		return [0, 1, 2, 3].map((slotIdx) => {
			const knownCard = opponent.known_cards.find((c) => c.slot === slotIdx);
			return knownCard
				? { known: true, rank: knownCard.rank, suit: knownCard.suit }
				: { known: false };
		});
	});
</script>

<div class="opponent-cards-zone">
	<CardContainer cards={opponentCards} isYourCards={false} showKnowledge={false} />
</div>

<style>
	.opponent-cards-zone {
		display: flex;
		flex-direction: column;
		gap: clamp(0.25rem, 0.8vw, 0.5rem);
		align-items: center;
		justify-content: center;
		padding: 0;
		background: transparent;
		border-radius: 0;
		border: none;
		width: 100%;
		height: 100%;
		min-height: 0;
		min-width: 0;
	}
</style>