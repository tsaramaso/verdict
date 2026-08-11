<script lang="ts">
  import { goto } from '$app/navigation';

  let { data } = $props();

  let recap = $derived(data?.recap);
  let error = $derived(data?.error);
  let game_id = $derived(data?.game_id);

  let finalRankings = $derived(recap?.final_rankings || []);
  let scoreProgression = $derived(recap?.score_progression || {});

  function getRankBadge(rank: number): string {
    if (rank === 1) return '🥇';
    if (rank === 2) return '🥈';
    if (rank === 3) return '🥉';
    return '•';
  }

  function getPlayerName(uuid: string): string {
    const ranking = finalRankings.find((r) => r.user_uuid === uuid);
    return ranking?.player_name || uuid.slice(0, 8);
  }

  let playerUuids = $derived(Object.keys(scoreProgression).sort());
  let roundCount = $derived(
    Math.max(...playerUuids.map((uuid) => scoreProgression[uuid]?.length || 0))
  );
</script>

<div class="layout">
  <!-- Navigation Bar -->
  <nav class="navbar">
    <div class="navbar-content">
      <div class="navbar-brand">
        <h1>Verdict</h1>
      </div>
      <button class="btn-back" onclick={() => goto('/home')}>← Back to Home</button>
    </div>
  </nav>

  <!-- Main Content -->
  <main class="main-content">
    {#if error}
      <div class="error-state">
        <p class="error-message">{error}</p>
      </div>
    {:else}
      <div class="recap-container">
        <!-- Final Rankings Table -->
        <section class="section">
          <h2>Final Rankings</h2>
          <div class="section-content">
            <table class="rankings-table">
              <thead>
                <tr>
                  <th class="col-rank">#</th>
                  <th class="col-player">Player</th>
                  <th class="col-score">Score</th>
                </tr>
              </thead>
              <tbody>
                {#each finalRankings as ranking (ranking.user_uuid)}
                  <tr>
                    <td class="col-rank">
                      <span class="badge">{getRankBadge(ranking.rank)}</span>
                      <span class="rank-num">{ranking.rank}</span>
                    </td>
                    <td class="col-player">{ranking.player_name}</td>
                    <td class="col-score">{ranking.final_score}</td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        </section>

        <!-- Score Progression Table -->
        <section class="section">
          <h2>Score Progression</h2>
          <div class="section-content">
            <div class="table-wrapper">
              <table class="progression-table">
                <thead>
                  <tr>
                    <th class="col-player">Player</th>
                    {#each Array(roundCount) as _, round}
                      <th class="col-round">R{round + 1}</th>
                    {/each}
                  </tr>
                </thead>
                <tbody>
                  {#each playerUuids as uuid (uuid)}
                    <tr>
                      <td class="col-player">{getPlayerName(uuid)}</td>
                      {#each scoreProgression[uuid] || [] as score}
                        <td class="col-score">{score}</td>
                      {/each}
                    </tr>
                  {/each}
                </tbody>
              </table>
            </div>
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

  .btn-back {
    background-color: transparent;
    color: var(--color-primary);
    border: 1px solid var(--color-primary);
    padding: var(--spacing-xs) var(--spacing-md);
    font-size: var(--font-size-sm);
    cursor: pointer;
    font-family: inherit;
    border-radius: var(--radius-sm);
    transition: all var(--transition-fast);
  }

  .btn-back:hover {
    background-color: var(--color-primary-light);
  }

  .main-content {
    flex: 1;
    overflow-y: auto;
    padding: var(--spacing-lg);
  }

  .recap-container {
    max-width: 1400px;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }

  .section {
    background-color: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    overflow: hidden;
  }

  .section h2 {
    margin: 0;
    padding: var(--spacing-lg);
    font-size: var(--font-size-lg);
    border-bottom: 2px solid var(--color-border);
    background-color: var(--color-bg);
  }

  .section-content {
    padding: var(--spacing-lg);
  }

  .rankings-table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--font-size-sm);
  }

  .rankings-table thead {
    background-color: var(--color-bg);
  }

  .rankings-table th {
    padding: var(--spacing-md);
    text-align: left;
    font-weight: var(--font-weight-bold);
    color: var(--color-text-light);
    border-bottom: 1px solid var(--color-border);
  }

  .rankings-table td {
    padding: var(--spacing-md);
    border-bottom: 1px solid var(--color-border);
  }

  .rankings-table tbody tr:last-child td {
    border-bottom: none;
  }

  .col-rank {
    width: 80px;
  }

  .col-player {
    flex: 1;
  }

  .col-score {
    width: 100px;
    text-align: right;
    font-weight: var(--font-weight-medium);
  }

  .col-round {
    width: 60px;
    text-align: center;
  }

  .badge {
    font-size: var(--font-size-lg);
    margin-right: var(--spacing-xs);
  }

  .rank-num {
    font-weight: var(--font-weight-bold);
    color: var(--color-text-light);
  }

  .table-wrapper {
    overflow-x: auto;
  }

  .progression-table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--font-size-sm);
    min-width: 500px;
  }

  .progression-table thead {
    background-color: var(--color-bg);
  }

  .progression-table th {
    padding: var(--spacing-md);
    text-align: center;
    font-weight: var(--font-weight-bold);
    color: var(--color-text-light);
    border-bottom: 1px solid var(--color-border);
  }

  .progression-table th.col-player {
    text-align: left;
  }

  .progression-table td {
    padding: var(--spacing-md);
    text-align: center;
    border-bottom: 1px solid var(--color-border);
  }

  .progression-table td.col-player {
    text-align: left;
    font-weight: var(--font-weight-medium);
  }

  .progression-table tbody tr:last-child td {
    border-bottom: none;
  }

  .error-state {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 100%;
    text-align: center;
  }

  .error-message {
    color: var(--color-danger);
    font-size: var(--font-size-base);
  }
</style>