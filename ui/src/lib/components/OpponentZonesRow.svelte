<!-- src/lib/components/OpponentZonesRow.svelte -->
<script lang="ts">
  import { gameState } from '$lib/stores/gameState';
  import OpponentCardsZone from './OpponentCardsZone.svelte';

  const numOpponents = $derived($gameState.opponents.length);
</script>

<div class="opponent-zones-row">
  {#each Array(numOpponents) as _, idx (idx)}
    {@const opponent = $gameState.opponents[idx]}
    <div class="opponent-zone" style="--opponent-index: {idx};">
      {#if opponent}
        <OpponentCardsZone {opponent} />
      {/if}
    </div>
  {/each}
</div>

<style>
  .opponent-zones-row {
    display: flex;
    gap: clamp(0.5rem, 1.5vw, 1.5rem);
    width: 100%;
    height: 100%;
    min-height: 0;
    min-width: 0;
    justify-content: center;
    align-items: center;
  }

  .opponent-zone {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 0;
    min-width: 0;
    flex: 1;
    height: 100%;
  }
</style>