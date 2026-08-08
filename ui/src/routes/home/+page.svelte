<!-- ui/src/routes/home/+page.svelte -->
<script lang="ts">
  import { goto } from '$app/navigation';
  import { enhance } from '$app/forms';

  let { data } = $props();

  let user = $derived(data?.user);
  let games = $derived(data?.games || []);
  let error = $derived(data?.error);

  function getGameStatusLabel(status: string): string {
    const labels: Record<string, string> = {
      WAITING_FOR_PLAYERS: 'Waiting',
      IN_PROGRESS: 'Active',
      FINISHED: 'Finished',
    };
    return labels[status] || status;
  }

  function getStatusColor(status: string): string {
    if (status === 'IN_PROGRESS') return 'var(--color-success)';
    if (status === 'FINISHED') return 'var(--color-text-light)';
    return 'var(--color-warning)';
  }
</script>

<div class="layout">
  <!-- Navigation Bar -->
  <nav class="navbar">
    <div class="navbar-content">
      <div class="navbar-brand">
        <h1>Verdict</h1>
      </div>
      <div class="navbar-user">
        {#if user}
          <span class="username">Hello, {user.name || 'Player'}</span>
          <form method="POST" action="?/logout" use:enhance>
            <button type="submit" class="btn-logout">Logout</button>
          </form>
        {/if}
      </div>
    </div>
  </nav>

  <!-- Main Content -->
  <main class="main-content">
    {#if error}
      <div class="error-state">
        <p class="error-message">{error}</p>
      </div>
    {:else}
      <div class="content-grid">
        <!-- Create Game Section -->
        <section class="section create-game-section">
          <h2>Create Game</h2>
          <div class="section-content">
            <p class="section-description">Start a new game by selecting players and turn direction.</p>
            <div class="placeholder">
              <p>Create game form coming in Phase 3</p>
            </div>
          </div>
        </section>

        <!-- Your Games Section -->
        <section class="section your-games-section">
          <h2>Your Games</h2>
          <div class="section-content">
            {#if games.length === 0}
              <div class="empty-state">
                <p>No games yet. Create one to get started!</p>
              </div>
            {:else}
              <div class="games-list">
                {#each games as game (game.game_id)}
                  <button class="game-card" onclick={() => goto(`/game/${game.game_id}`)}>
                    <div class="game-header">
                      <span class="game-status" style="color: {getStatusColor(game.status)}">
                        {getGameStatusLabel(game.status)}
                      </span>
                      <span class="game-round">Round {game.current_round}</span>
                    </div>
                    <div class="game-details">
                      <p class="game-id">Game: {game.game_id.slice(0, 8)}...</p>
                      <p class="game-direction">Direction: {game.turn_direction === 'CW' ? 'Clockwise' : 'Counter-clockwise'}</p>
                      <p class="game-date">Created: {new Date(game.created_at).toLocaleDateString()}</p>
                    </div>
                  </button>
                {/each}
              </div>
            {/if}
          </div>
        </section>
      </div>
    {/if}
  </main>
</div>

<style>
  .layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    background-color: var(--color-bg);
  }

  .navbar {
    background-color: var(--color-bg-card);
    border-bottom: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
    position: sticky;
    top: 0;
    z-index: var(--z-dropdown);
  }

  .navbar-content {
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--spacing-md) var(--spacing-lg);
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .navbar-brand h1 {
    margin: 0;
    font-size: var(--font-size-xl);
    color: var(--color-primary);
  }

  .navbar-user {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
  }

  .navbar-user form {
    display: contents;
  }

  .username {
    font-size: var(--font-size-sm);
    color: var(--color-text-light);
  }

  .btn-logout {
    background-color: transparent;
    color: var(--color-danger);
    border: 1px solid var(--color-danger);
    padding: var(--spacing-xs) var(--spacing-md);
    font-size: var(--font-size-sm);
    cursor: pointer;
    font-family: inherit;
  }

  .btn-logout:hover {
    background-color: var(--color-danger-light);
  }

  .main-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-xl);
  }

  .error-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    min-height: 400px;
  }

  .error-message {
    color: var(--color-danger);
    font-weight: var(--font-weight-medium);
  }

  .content-grid {
    max-width: 1400px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: var(--spacing-xl);
  }

  .section {
    background-color: var(--color-bg-card);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-md);
    display: flex;
    flex-direction: column;
    min-height: 500px;
  }

  .section h2 {
    padding: var(--spacing-lg) var(--spacing-lg) 0 var(--spacing-lg);
    margin-bottom: var(--spacing-md);
    font-size: var(--font-size-lg);
    border-bottom: 2px solid var(--color-border);
    padding-bottom: var(--spacing-md);
  }

  .section-content {
    padding: var(--spacing-lg);
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .section-description {
    font-size: var(--font-size-sm);
    color: var(--color-text-light);
    margin-bottom: var(--spacing-md);
  }

  .placeholder {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--color-bg);
    border-radius: var(--radius-md);
    border: 2px dashed var(--color-border);
    color: var(--color-text-light);
    text-align: center;
  }

  .empty-state {
    flex: 1;
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    color: var(--color-text-light);
  }

  .games-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    overflow-y: auto;
  }

  .game-card {
    background-color: var(--color-bg);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    padding: var(--spacing-md);
    cursor: pointer;
    transition: all var(--transition-fast);
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    font-family: inherit;
    text-align: left;
  }

  .game-card:hover {
    border-color: var(--color-primary);
    box-shadow: var(--shadow-md);
    transform: translateY(-2px);
  }

  .game-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--spacing-md);
  }

  .game-status {
    font-weight: var(--font-weight-medium);
    font-size: var(--font-size-sm);
    text-transform: capitalize;
  }

  .game-round {
    font-size: var(--font-size-sm);
    color: var(--color-text-light);
    background-color: var(--color-primary-light);
    padding: var(--spacing-xs) var(--spacing-sm);
    border-radius: var(--radius-sm);
    color: var(--color-primary);
  }

  .game-details {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);
  }

  .game-id,
  .game-direction,
  .game-date {
    font-size: var(--font-size-sm);
    color: var(--color-text-light);
    margin: 0;
  }

  @media (max-width: 768px) {
    .content-grid {
      grid-template-columns: 1fr;
      gap: var(--spacing-lg);
    }

    .navbar-content {
      flex-direction: column;
      gap: var(--spacing-md);
      text-align: center;
    }

    .section {
      min-height: auto;
    }
  }
</style>