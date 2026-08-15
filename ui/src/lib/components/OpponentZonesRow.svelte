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
    <div class="player-box">
    <div class="player-info-label">
  <div class="player-name">{opponent.player_name}</div>
  <div class="player-meta">
    <span class="score">Score: {opponent.score}</span>
  </div>
</div>
<div class="opponent-zone">
  {#if opponent}
  <OpponentCardsZone {opponent} />
  {/if}
</div>
</div>
    {/each}
  </div>
</div>


<style>
  .player-box {
    border-color: black;
    display: flex;
    gap: clamp(0.5rem, 1.5vw, 1.5rem);
    justify-content: center;
    align-items: center;
    height: 100%;
    min-height: 0;
    background-color: rgba(255, 42, 0, 0.371);
    border-radius: 5%;
    /* Base size calculated from zone height via aspect-ratio */
    /* Width = height × (2.5/3.5) for card aspect ratio */
    /* Minimum width based on zone height */
    min-width: fit-content;
    /* If all zones overflow, scale down uniformly */
    max-width: 100%;
    overflow: hidden;
    
  }
    .player-info-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    width: 100%;
    text-align: center;
    margin-left: 5%;
  }


  .player-name {
    font-weight: var(--font-weight-bold);
    font-size: clamp(0.75rem, 1vw, 1rem);
    color: var(--color-text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 100%;
  }

  .player-meta {
    display: flex;
    gap: clamp(0.5rem, 1vw, 1rem);
    font-size: clamp(0.65rem, 0.8vw, 0.875rem);
    color: var(--color-text-light);
  }

  .score {
    white-space: nowrap;
  }


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
    border-color: black;
    display: flex;
    gap: clamp(0.5rem, 1.5vw, 1.5rem);
    justify-content: center;
    align-items: center;
    height: 100%;
    min-height: 0;
    border-radius: 5%;
    /* Base size calculated from zone height via aspect-ratio */
    /* Width = height × (2.5/3.5) for card aspect ratio */
    /* Minimum width based on zone height */
    min-width: fit-content;
    /* If all zones overflow, scale down uniformly */
    max-width: 100%;
    overflow: hidden;
    padding: 0.5%;
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