<script lang="ts">
	import DeckZone from './DeckZone.svelte';
	import DiscardZone from './DiscardZone.svelte';
	import PeekArea from './PeekArea.svelte';
	import { gameState, isActivePlayer } from '$lib/stores/gameState';
	import { GAME_PHASES } from '$lib/config';
	import type { CardRank, CardSuit } from '$lib/constants/cards';

	interface Props {
		drawnCard?: { rank: CardRank; suit: CardSuit } | null;
		drawnCardSource?: 'deck' | 'discard' | null;
		onDeckClick?: () => void;
		onAction?: (choice: 'discard_immediate' | 'swap' | 'pass_back', slotIndex?: number) => void;
	}

	let { 
		drawnCard,
		drawnCardSource,
		onDeckClick, 
		onAction
	}: Props = $props();

	const isDeckClickable = $derived.by(() => {
		const isActive = $isActivePlayer;
		const isDrawingPhase = $gameState.phase === GAME_PHASES.DRAWING;
		const clickable = isActive && isDrawingPhase;
		console.log('[CentralArea] isDeckClickable:', clickable, '| isActive:', isActive, '| phase:', $gameState.phase, '| DRAWING:', GAME_PHASES.DRAWING);
		return clickable;
	});

	const isDiscardClickable = $derived.by(() => {
		const clickable = $isActivePlayer &&
			($gameState.phase === GAME_PHASES.DRAWING || $gameState.phase === GAME_PHASES.AWAITING_ACTION);
		console.log('[CentralArea] isDiscardClickable:', clickable, 'isActive:', $isActivePlayer, 'phase:', $gameState.phase);
		return clickable;
	});

	const isPeekAreaVisible = $derived(
		$gameState.phase === GAME_PHASES.AWAITING_ACTION && !!drawnCard
	);

	function handleDiscardImmediateClick() {
		if (!isDiscardClickable) return;
		if ($gameState.phase === GAME_PHASES.AWAITING_ACTION) {
			onAction?.('discard_immediate');
		}
	}
</script>

<div class="central-area">
	<div class="central-cards-container">
		<DeckZone isClickable={isDeckClickable} onClick={onDeckClick} />
		<PeekArea 
			{drawnCard}
			{drawnCardSource}
			isVisible={isPeekAreaVisible}
		/>
		<DiscardZone isClickable={isDiscardClickable && $gameState.phase === GAME_PHASES.AWAITING_ACTION} onClick={handleDiscardImmediateClick} />
	</div>
</div>

<style>
	.central-area {
		display: flex;
		align-items: center;
		justify-content: center;
		padding: 0;
		background: transparent;
		width: 100%;
		height: 100%;
		min-height: 0;
		min-width: 0;
	}

	.central-cards-container {
		display: flex;
		gap: clamp(0.5rem, 1.5vw, 1.5rem);
		justify-content: center;
		align-items: center;
		height: 100%;
		width: 100%;
		min-height: 0;
		min-width: 0;
		padding: clamp(1rem, 2vh, 2rem) 0;
	}

	.central-cards-container > :global(*) {
		height: 100%;
		max-height: clamp(150px, 60vh, 400px);
		aspect-ratio: 2.5 / 3.5;
		flex: 0 0 auto;
	}
</style>