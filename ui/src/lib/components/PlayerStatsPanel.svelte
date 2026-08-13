<script lang="ts">
  import { gameState } from '$lib/stores/gameState';
  import { getPointsToRenaissance, COLORS, calculateKnownSum } from '$lib/config';

  const knownSum = $derived(calculateKnownSum($gameState.self.hand, $gameState.rules.black_king_value, $gameState.rules.red_king_value, $gameState.rules.rank_values));
  const pointsToNext = $derived(getPointsToRenaissance($gameState.self.score, Object.keys($gameState.rules.eligible_thresholds));
  const sumColor = $derived(knownSum <= 7 ? COLORS.success : COLORS.danger);
</script>

<div class="stats-panel">
	<div class="stat">
		<span class="stat-label">Known Sum:</span>
		<span class="stat-value" style="color: {sumColor}">{knownSum}</span>
	</div>
	<div class="stat">
		<span class="stat-label">Renaissance:</span>
		<span class="stat-value">{pointsToNext}</span>
	</div>
</div>

<style>
	.stats-panel {
		display: flex;
		gap: var(--spacing-lg);
		padding: var(--spacing-md);
		background: var(--color-bg-card);
		border-radius: var(--radius-md);
		border: 1px solid var(--color-border);
	}

	.stat {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
	}

	.stat-label {
		font-size: var(--font-size-sm);
		color: var(--color-text-light);
		font-weight: var(--font-weight-medium);
	}

	.stat-value {
		font-size: var(--font-size-base);
		font-weight: var(--font-weight-bold);
		font-family: monospace;
	}
</style>
