<!-- src/lib/components/PlayArea.svelte -->
<script lang="ts">
  import OpponentZonesRow from './OpponentZonesRow.svelte';
  import CentralArea from './CentralArea.svelte';
  import YourZonesRow from './YourZonesRow.svelte';

  interface Props {
    onDeckClick?: () => void;
    onDiscardClick?: () => void;
    onCardClick?: (slotIndex: number) => void;
  }

  let { onDeckClick, onDiscardClick, onCardClick }: Props = $props();
</script>

<div class="play-area">
  <div class="opponent-zones-row">
    <OpponentZonesRow />
  </div>

  <div class="central-section">
    <CentralArea {onDeckClick} {onDiscardClick} />
  </div>

  <div class="your-zones-row">
    <YourZonesRow {onCardClick} />
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
    overflow: hidden;
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
    padding: clamp(0.5rem, 1vw, 1rem);
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
    overflow: hidden;
  }
</style>