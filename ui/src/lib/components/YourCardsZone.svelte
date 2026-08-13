<!-- src/lib/components/YourCardsZone.svelte -->
<script lang="ts">
	import CardSlot from './CardSlot.svelte';
	import { gameState, getOpponentsThatKnowSlot, myOpponentKnowledge } from '$lib/stores/gameState';

	interface Props {
		onCardClick?: (slotIndex: number) => void;
	}

	let { onCardClick }: Props = $props();
</script>

<div class="your-cards-zone">
	<div class="cards-container">
		{#each [0, 1, 2, 3] as slotIdx}
			{@const card = $gameState.self.hand[slotIdx]}
			{@const oppsWhoKnow = getOpponentsThatKnowSlot($myOpponentKnowledge, slotIdx)}
			{@const anyOpponentKnows = oppsWhoKnow.length > 0}
			<CardSlot
				{card}
				slotIndex={slotIdx}
				isYourCard={true}
				isClickable={true}
				opponentKnowsSlot={anyOpponentKnows}
				opponentsWhoKnow={oppsWhoKnow}
				onClick={() => onCardClick?.(slotIdx)}
			/>
		{/each}
	</div>
</div>

<style>
	.your-cards-zone {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
		align-items: center;
		padding: var(--spacing-lg);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
	}

	.cards-container {
		display: grid;
		grid-template-columns: repeat(2, minmax(100px, 1fr));
		gap: var(--spacing-md);
		width: 100%;
		max-width: 600px;
	}

	@media (max-width: 768px) {
		.cards-container {
			max-width: 100%;
		}
	}
</style>
