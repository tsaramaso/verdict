<!-- src/lib/components/CentralArea.svelte -->
<script lang="ts">
  import DeckZone from './DeckZone.svelte';
  import DiscardZone from './DiscardZone.svelte';
  import { gameState, isActivePlayer } from '$lib/stores/gameState';
  import { GAME_PHASES } from '$lib/config';

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
  <div class="card-pair">
    <DeckZone isClickable={isDeckClickable} onClick={onDeckClick} />
    <DiscardZone isClickable={isDiscardClickable} onClick={onDiscardClick} />
  </div>
</div>

<style>
  .central-area {
    display: flex;
    gap: 0;
    justify-content: center;
    align-items: center;
    padding: 0;
    background: transparent;
    border-radius: 0;
    flex-shrink: 0;
    width: 100%;
    height: 100%;
  }

  .card-pair {
    display: flex;
    gap: clamp(0.75rem, 2vw, 2rem);
    justify-content: center;
    align-items: center;
    height: 100%;
    width: auto;
    max-width: 100%;
  }

  .card-pair > :global(*) {
    flex: 0 1 auto;
    max-width: 50%;
    max-height: 100%;
  }
</style>