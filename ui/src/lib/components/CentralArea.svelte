<!-- src/lib/components/CentralArea.svelte -->
<script lang="ts">
  import DeckZone from './DeckZone.svelte';
  import DiscardZone from './DiscardZone.svelte';
  import { gameState, isActivePlayer } from '$lib/stores/gameState';
  import { GAME_PHASES } from '$lib/config';
  import CardSlot from './CardSlot.svelte';

  interface Props {
    onDeckClick?: () => void;
    onDiscardClick?: () => void;
  }

  let { onDeckClick, onDiscardClick }: Props = $props();

  const isDeckClickable = $derived(
    $isActivePlayer && $gameState.phase === GAME_PHASES.DRAWING
  );

  const isDiscardClickable = $derived(
    $isActivePlayer &&
      ($gameState.phase === GAME_PHASES.DRAWING || $gameState.phase === GAME_PHASES.AWAITING_ACTION)
  );
</script>

<div class="central-area">
  <div class="central-cards-container">
    <DeckZone isClickable={isDeckClickable} onClick={onDeckClick} />
    <DiscardZone isClickable={isDiscardClickable} onClick={onDiscardClick} />
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
    gap: clamp(0.75rem, 2vw, 2rem);
    justify-content: center;
    align-items: center;
    height: 100%;
    min-height: 0;
    /* Two cards side-by-side, each with aspect-ratio 2.5/3.5 */
    /* Width: (height × 2.5/3.5) × 2 + gap */
    max-width: 100%;
    overflow: hidden;
  }

  .central-cards-container > :global(*) {
    /* Each card fills zone height, width from aspect-ratio */
    height: 100%;
    aspect-ratio: 2.5 / 3.5;
    flex: 0 0 auto;
  }
</style>