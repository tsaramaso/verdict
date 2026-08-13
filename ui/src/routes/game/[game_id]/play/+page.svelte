<!-- ui/src/routes/game/[game_id]/play/+page.svelte -->
<script lang="ts">
  import { goto } from '$app/navigation';
  import GamePage from '$lib/components/GamePage.svelte';

  let { data } = $props();

  let gameId = $derived(data?.gameId);
  let playerId = $derived(data?.playerId);
  let error = $derived(data?.error);

  // If no playerId, show error
  $effect(() => {
    if (!playerId && !error) {
      console.warn('No playerId in route data');
    }
  });
</script>

{#if error}
  <div class="error-container">
    <div class="error-box">
      <h2>Error Loading Game</h2>
      <p>{error}</p>
      <button onclick={() => goto('/home')} class="btn-back">Return to Home</button>
    </div>
  </div>
{:else if !gameId || !playerId}
  <div class="loading-container">
    <div class="loading-box">
      <p>Loading game...</p>
    </div>
  </div>
{:else}
  <GamePage {gameId} {playerId} />
{/if}

<style>
  .error-container,
  .loading-container {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100vh;
    background: var(--color-bg);
  }

  .error-box,
  .loading-box {
    text-align: center;
    padding: var(--spacing-xl);
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
  }

  .error-box h2 {
    margin-top: 0;
    color: var(--color-danger);
  }

  .error-box p {
    color: var(--color-text-light);
    margin: var(--spacing-md) 0;
  }

  .btn-back {
    padding: var(--spacing-sm) var(--spacing-lg);
    background: var(--color-primary);
    color: white;
    border: none;
    border-radius: var(--radius-sm);
    cursor: pointer;
    font-weight: var(--font-weight-bold);
    transition: all 0.2s ease;
  }

  .btn-back:hover {
    background: var(--color-primary-dark);
    transform: translateY(-2px);
  }

  .loading-box p {
    color: var(--color-text-light);
  }
</style>