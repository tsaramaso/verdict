<!-- src/lib/components/OpponentZonesContainer.svelte -->
<script lang="ts">
  import { gameState } from '$lib/stores/gameState';
  import OpponentCardsZone from './OpponentCardsZone.svelte';

  // Map to ensure opponents are positioned correctly by index
  // Even with fewer opponents, maintain their grid positions
  function getGridPosition(index: number): { col: number; row: number } {
    const positions = [
      { col: 1, row: 1 }, // Top-left (opponent 0 / position 1)
      { col: 2, row: 1 }, // Top-right (opponent 1 / position 2)
      { col: 1, row: 2 }, // Bottom-left (opponent 2 / position 3)
      { col: 2, row: 2 }, // Bottom-right (opponent 3 / position 0, wraps)
    ];
    return positions[index] || positions[0];
  }

  const numOpponents = $derived($gameState.opponents.length);
</script>

<div class="opponent-zones-container">
  {#each Array(numOpponents) as _, idx}
    {@const opponent = $gameState.opponents[idx]}
    {@const pos = getGridPosition(idx)}
    <div
      class="opponent-zone"
      style="--col: {pos.col}; --row: {pos.row};"
    >
      {#if opponent}
        <OpponentCardsZone {opponent} />
      {/if}
    </div>
  {/each}
</div>

<style>
  .opponent-zones-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 1fr);
    gap: var(--spacing-md);
    width: 100%;
    height: 100%;
    min-height: 0;
    min-width: 0;
  }

  .opponent-zone {
    grid-column: var(--col);
    grid-row: var(--row);
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 0;
    min-width: 0;
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    /* padding: var(--spacing-md); */
    overflow: auto;
  }

  @media (max-width: 768px) {
    .opponent-zones-container {
      gap: var(--spacing-sm);
    }

    .opponent-zone {
      padding: var(--spacing-sm);
      border-radius: var(--radius-sm);
    }
  }
</style>
