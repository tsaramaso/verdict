<!-- ui/src/routes/game/[game_id]/play/+page.svelte -->
<script lang="ts">
  import { goto } from '$app/navigation';

  let { data } = $props();

  let gameId = $derived(data?.gameId);
  let gameStatus = $derived(data?.gameStatus);
  let error = $derived(data?.error);
</script>

<div class="game-layout">
  <!-- Header -->
  <header class="game-header">
    <div class="header-content">
      <div class="game-info">
        <h1>Game</h1>
        <p class="game-id">ID: {gameId?.slice(0, 8) || 'Unknown'}...</p>
      </div>

      {#if gameStatus}
        <div class="status-info">
          <div class="status-item">
            <span class="label">Phase</span>
            <span class="value">{gameStatus.phase}</span>
          </div>
          <div class="status-item">
            <span class="label">Round</span>
            <span class="value">{gameStatus.round_number}</span>
          </div>
          <div class="status-item">
            <span class="label">Current Player</span>
            <span class="value">{gameStatus.current_player?.slice(0, 8) || 'N/A'}...</span>
          </div>
          <div class="status-item">
            <span class="label">Game Over</span>
            <span class="value">{gameStatus.game_over ? 'Yes' : 'No'}</span>
          </div>
        </div>

        <div class="scores">
          <h3>Scores</h3>
          <div class="scores-list">
            {#each Object.entries(gameStatus.scores) as [playerId, score]}
              <div class="score-item">
                <span class="player-id">{playerId?.slice(0, 8) || 'Unknown'}...</span>
                <span class="score-value">{score}</span>
              </div>
            {/each}
          </div>
        </div>
      {/if}

      <button class="btn-back" onclick={() => goto('/home')}>
        Back to Home
      </button>
    </div>
  </header>

  <!-- Main Content -->
  <main class="game-board">
    {#if error}
      <div class="error-message">
        <p>{error}</p>
        <button onclick={() => goto('/home')}>Return to Home</button>
      </div>
    {:else if !gameStatus}
      <div class="loading">
        <p>Loading game...</p>
      </div>
    {:else}
      <div class="placeholder">
        <h2>Game Board</h2>
        <p>Game play UI coming soon</p>
        <p class="phase-indicator">
          Current Phase: <strong>{gameStatus.phase}</strong>
        </p>
        <p class="player-indicator">
          Current Player: <strong>{gameStatus.current_player?.slice(0, 8) || 'N/A'}...</strong>
        </p>
      </div>
    {/if}
  </main>
</div>

<style>
  .game-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: var(--color-bg);
  }

  .game-header {
    background-color: var(--color-bg-card);
    border-bottom: 1px solid var(--color-border);
    box-shadow: var(--shadow-md);
    padding: var(--spacing-lg);
  }

  .header-content {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 2fr 1fr 1fr;
    gap: var(--spacing-lg);
    align-items: start;
  }

  .game-info h1 {
    margin: 0 0 var(--spacing-xs) 0;
    font-size: var(--font-size-lg);
  }

  .game-id {
    margin: 0;
    font-size: var(--font-size-sm);
    color: var(--color-text-light);
    font-family: monospace;
  }

  .status-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .status-item {
    display: flex;
    justify-content: space-between;
    gap: var(--spacing-md);
    padding: var(--spacing-sm);
    background-color: var(--color-bg);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border);
  }

  .status-item .label {
    font-weight: var(--font-weight-medium);
    color: var(--color-text-light);
    font-size: var(--font-size-sm);
  }

  .status-item .value {
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
  }

  .scores {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
  }

  .scores h3 {
    margin: 0 0 var(--spacing-sm) 0;
    font-size: var(--font-size-base);
  }

  .scores-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .score-item {
    display: flex;
    justify-content: space-between;
    padding: var(--spacing-xs) var(--spacing-sm);
    background-color: var(--color-bg);
    border-radius: var(--radius-sm);
    border: 1px solid var(--color-border);
    font-size: var(--font-size-sm);
  }

  .score-item .player-id {
    font-family: monospace;
    color: var(--color-text-light);
  }

  .score-item .score-value {
    font-weight: var(--font-weight-bold);
    color: var(--color-success);
  }

  .btn-back {
    padding: var(--spacing-sm) var(--spacing-md);
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-size: var(--font-size-sm);
  }

  .btn-back:hover {
    background-color: var(--color-primary-dark);
  }

  .game-board {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: var(--spacing-xl);
    overflow-y: auto;
  }

  .error-message {
    text-align: center;
    color: var(--color-danger);
  }

  .error-message button {
    margin-top: var(--spacing-md);
    padding: var(--spacing-sm) var(--spacing-lg);
    background-color: var(--color-primary);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
  }

  .loading {
    text-align: center;
    color: var(--color-text-light);
  }

  .placeholder {
    text-align: center;
    padding: var(--spacing-xl);
    background-color: var(--color-bg-card);
    border-radius: var(--radius-md);
    border: 2px dashed var(--color-border);
    max-width: 600px;
  }

  .placeholder h2 {
    margin-top: 0;
    font-size: var(--font-size-lg);
  }

  .placeholder p {
    margin: var(--spacing-md) 0;
    color: var(--color-text-light);
  }

  .phase-indicator,
  .player-indicator {
    padding: var(--spacing-md);
    background-color: var(--color-bg);
    border-radius: var(--radius-sm);
    border-left: 3px solid var(--color-primary);
  }

  .phase-indicator strong,
  .player-indicator strong {
    color: var(--color-primary);
    font-family: monospace;
  }

  @media (max-width: 1024px) {
    .header-content {
      grid-template-columns: 1fr;
      gap: var(--spacing-md);
    }
  }
</style>