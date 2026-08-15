<!-- src/lib/components/YourZonesRow.svelte -->
<script lang="ts">
  import YourCardsZone from './YourCardsZone.svelte';

  interface Props {
    onCardClick?: (slotIndex: number) => void;
  }

  let { onCardClick }: Props = $props();
</script>

<div class="your-zones-row">
  <div class="your-zones-container">
    <div class="your-zone">
      <YourCardsZone {onCardClick} />
    </div>
  </div>
</div>

<style>
  .your-zones-row {
    display: flex;
    width: 100%;
    height: 100%;
    min-height: 0;
    min-width: 0;
    justify-content: center;
    align-items: center;
  }

  .your-zones-container {
    display: flex;
    gap: clamp(0.5rem, 1.5vw, 1.5rem);
    justify-content: center;
    align-items: center;
    height: 100%;
    min-height: 0;
    /* Single zone with fixed aspect ratio */
    max-width: 100%;
    overflow: hidden;
  }

  .your-zone {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 0;
    min-width: 0;
    /* Fixed width derived from height via aspect-ratio */
    /* Height 100% comes from parent */
    /* Width is calculated as: 100% height × (2.5/3.5) aspect */
    aspect-ratio: 2.5 / 3.5;
    height: 100%;
    /* Zone is fixed size - doesn't shrink/grow individually */
    flex: 0 0 auto;
  }
</style>