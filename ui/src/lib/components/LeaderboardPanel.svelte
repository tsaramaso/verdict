<!-- src/lib/components/LeaderboardPanel.svelte -->
<script lang="ts">
	interface PlayerStanding {
		player_id: string;
		name: string;
		score: number;
		isYou?: boolean;
	}

	interface Props {
		standings?: PlayerStanding[];
	}

	let { standings = [] }: Props = $props();
</script>

<div class="leaderboard-panel">
	<div class="leaderboard-header">
		<h3>Standings</h3>
	</div>

	<div class="leaderboard-table">
		{#each standings as player, idx}
			<div class={`leaderboard-row ${player.isYou ? 'leaderboard-row--you' : ''}`}>
				<div class="place">#{idx + 1}</div>
				<div class="player-name">{player.name}</div>
				<div class="score">
					<span class="score-value">{player.score}</span>
				</div>
			</div>
		{/each}
	</div>
</div>

<style>
	.leaderboard-panel {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-md);
		padding: var(--spacing-md);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
	}

	.leaderboard-header {
		display: flex;
		align-items: center;
		justify-content: space-between;
		border-bottom: 1px solid var(--color-border);
		padding-bottom: var(--spacing-sm);
	}

	.leaderboard-header h3 {
		margin: 0;
		font-size: var(--font-size-base);
		font-weight: var(--font-weight-bold);
		color: var(--color-text);
	}

	.leaderboard-table {
		display: flex;
		flex-direction: column;
		gap: var(--spacing-xs);
	}

	.leaderboard-row {
		display: grid;
		grid-template-columns: 30px 1fr auto;
		gap: var(--spacing-sm);
		align-items: center;
		padding: var(--spacing-sm);
		border-radius: var(--radius-sm);
		background: var(--color-bg);
		border: 1px solid var(--color-border-light);
		transition: all 0.2s ease;
	}

	.leaderboard-row--you {
		background: linear-gradient(135deg, rgba(0, 123, 255, 0.05) 0%, rgba(0, 123, 255, 0.02) 100%);
		border-color: var(--color-primary);
		font-weight: var(--font-weight-bold);
	}

	.place {
		font-size: var(--font-size-sm);
		color: var(--color-text-light);
		font-weight: var(--font-weight-bold);
		text-align: center;
	}

	.player-name {
		font-size: var(--font-size-sm);
		color: var(--color-text);
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.score {
		display: flex;
		gap: var(--spacing-sm);
		align-items: center;
		font-size: var(--font-size-sm);
	}

	.score-value {
		font-weight: var(--font-weight-bold);
		color: var(--color-text);
		min-width: 30px;
		text-align: right;
		font-family: monospace;
	}

	.points-to-next {
		font-weight: var(--font-weight-bold);
		font-size: var(--font-size-xs);
		min-width: 35px;
		text-align: right;
		font-family: monospace;
	}

	.legend-item {
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
	}

	.legend-color {
		width: 12px;
		height: 12px;
		border-radius: 2px;
		flex-shrink: 0;
	}

	.legend-text {
		white-space: nowrap;
	}
</style>