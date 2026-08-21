<script lang="ts">
	import CardContainer from './CardContainer.svelte';
	import { gameState } from '$lib/stores/gameState';

	interface Props {
		onCardClick?: (slotIndex: number) => void;
		onQuickDiscard?: (slotIndex: number) => void;
	}

	let { onCardClick, onQuickDiscard }: Props = $props();

	const yourCards = $derived($gameState.self.hand);
</script>

<div class="your-cards-zone">
	<CardContainer
		cards={yourCards}
		isYourCards={true}
		{onCardClick}
		{onQuickDiscard}
		showKnowledge={true}
	/>
</div>

<style>
	.your-cards-zone {
		display: flex;
		flex-direction: column;
		gap: clamp(0.25rem, 0.8vw, 0.5rem);
		align-items: center;
		padding: 0;
		background: transparent;
		border-radius: 0;
		border: none;
		width: 100%;
		height: 100%;
		min-height: 0;
		margin-top: 5%;
		margin-right: 10%;
	}
</style>
