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
  <DeckZone isClickable={isDeckClickable} onClick={onDeckClick} />

  <DiscardZone isClickable={isDiscardClickable} onClick={onDiscardClick} />
</div>

<style>
  .central-area {
    display: flex;
    gap: var(--spacing-xl);
    justify-content: center;
    align-items: center;
    padding: var(--spacing-lg);
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    flex-shrink: 0;
    width: 100%;
    height: 100%;
    max-width: 400px;
    max-height: 250px;
  }

  @media (max-width: 768px) {
    .central-area {
      gap: var(--spacing-lg);
      padding: var(--spacing-md);
      max-width: 100%;
      max-height: 200px;
    }
  }
</style>
