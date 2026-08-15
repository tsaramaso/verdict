<!-- src/lib/components/YourZonesRow.svelte -->
<script lang="ts">
	import { calculateKnownSum, getPointsToRenaissance } from '$lib/config';
  import { gameState } from '$lib/stores/gameState';
  import YourCardsZone from './YourCardsZone.svelte';

  interface Props {
    onCardClick?: (slotIndex: number) => void;
  }

  let { onCardClick }: Props = $props();
</script>

<div class="your-zones-row">

  <div class="your-zones-container">
    <div class="player-info-label">
  <div class="player-name">{$gameState.self.player_name}<br/> (You)</div>
  <div class="player-meta">
    <span class="score">Score:<br/>{$gameState.self.score}</span>
    <span class="score">Known Sum:<br/>{calculateKnownSum($gameState.self.hand, $gameState.rules.black_king_value, $gameState.rules.red_king_value, $gameState.rules.rank_values )}</span>
    <span class="score">Next Renaissance:<br/>{getPointsToRenaissance($gameState.self.score, Object.keys($gameState.rules.renaissance_thresholds).map(Number))}</span>
  </div>
</div>
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
    border-radius: 5%;
    background-color: rgba(1, 160, 252, 0.345);

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

    .player-info-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
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

</style>