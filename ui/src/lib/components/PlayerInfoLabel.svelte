<!-- src/lib/components/PlayerInfoLabel.svelte -->
<script lang="ts">
  import { gameState } from '$lib/stores/gameState';

  const yourName = $derived($gameState.self.player_name);
  const yourScore = $derived($gameState.self.score);
</script>

<div class="player-info-label">
  <div class="player-name">{yourName}</div>
  <div class="player-meta">
    <span class="score">Score: {yourScore}</span>
  </div>
</div>

<style>
  .player-info-label {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    width: 100%;
    text-align: center;
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