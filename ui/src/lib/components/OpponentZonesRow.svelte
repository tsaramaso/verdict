<!-- src/lib/components/OpponentZonesRow.svelte -->
<script lang="ts">
  import { gameState } from '$lib/stores/gameState';
  import OpponentCardsZone from './OpponentCardsZone.svelte';

  const numOpponents = $derived($gameState.opponents.length);
</script>

<div class="opponent-zones-row">
  <div class="opponent-zones-container">
    {#each Array(numOpponents) as _, idx (idx)}
      {@const opponent = $gameState.opponents[idx]}
      <div class="opponent-zone">
        {#if opponent}
          <OpponentCardsZone {opponent} />
        {/if}
      </div>
    {/each}
  </div>
</div>

<style>
  .opponent-zones-row {
    display: flex;
    width: 100%;
    height: 100%;
    min-height: 0;
    min-width: 0;
    justify-content: center;
    align-items: center;
  }

  .opponent-zones-container {
    display: flex;
    gap: clamp(0.5rem, 1.5vw, 1.5rem);
    justify-content: center;
    align-items: center;
    height: 100%;
    min-height: 0;
    /* Base size calculated from zone height via aspect-ratio */
    /* Width = height × (2.5/3.5) for card aspect ratio */
    /* Minimum width based on zone height */
    min-width: fit-content;
    /* If all zones overflow, scale down uniformly */
    max-width: 100%;
    overflow: hidden;
  }

  .opponent-zone {
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
    /* All zones are identical size - shrink together if needed */
    flex: 0 0 auto;
  }
</style>