<script lang="ts">
	import OpponentZonesRow from './OpponentZonesRow.svelte';
	import CentralArea from './CentralArea.svelte';
	import YourZonesRow from './YourZonesRow.svelte';
	import type { CardRank, CardSuit } from '$lib/constants/cards';

	interface Props {
		drawnCard?: { rank: CardRank; suit: CardSuit } | null;
		drawnCardSource?: 'deck' | 'discard' | null;
		onDeckClick?: () => void;
		onDiscardDrawClick?: () => void;
		onAction?: (choice: 'discard_immediate' | 'swap' | 'pass_back', slotIndex?: number) => void;
		onQuickDiscard?: (slotIndex: number) => void;
	}

	let {
		drawnCard,
		drawnCardSource,
		onDeckClick,
		onDiscardDrawClick,
		onAction,
		onQuickDiscard
	}: Props = $props();
</script>

<div class="play-area">
	<div class="opponent-zones-row">
		<OpponentZonesRow />
	</div>

	<div class="central-section">
		<CentralArea {drawnCard} {drawnCardSource} {onDeckClick} {onDiscardDrawClick} {onAction} />
	</div>

	<div class="your-zones-row">
		<YourZonesRow onCardClick={(idx) => onAction?.('swap', idx)} {onQuickDiscard} />
	</div>
</div>

<style>
	.play-area {
		grid-column: 1;
		grid-row: 1;
		display: grid;
		grid-template-rows: 1fr 0.5fr 1fr;
		gap: clamp(0.25rem, 0.75vw, 0.75rem);
		padding: clamp(0.25rem, 0.75vw, 0.75rem);
		overflow: hidden;
		min-height: 0;
		min-width: 0;
	}

	.opponent-zones-row {
		grid-row: 1;
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 0;
		min-width: 0;
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: clamp(0.5rem, 1vw, 1rem);
		overflow: visible;
	}

	.central-section {
		grid-row: 2;
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 0;
		min-width: 0;
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		overflow: hidden;
	}

	.your-zones-row {
		grid-row: 3;
		display: flex;
		align-items: center;
		justify-content: center;
		min-height: 0;
		min-width: 0;
		background: var(--color-bg-card);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-md);
		padding: clamp(0.5rem, 1vw, 1rem);
		overflow: visible;
	}
</style>