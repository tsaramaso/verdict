<script lang="ts">
	import { gameState } from '$lib/stores/gameState';

	interface Props {
		onAdvance?: () => void;
	}

	let { onAdvance }: Props = $props();

	let autoAdvanceTimer = $state(10);

	$effect(() => {
		if ($gameState.phase !== 'ROUND_OVER') return;

		const interval = setInterval(() => {
			autoAdvanceTimer -= 1;
			if (autoAdvanceTimer <= 0) {
				clearInterval(interval);
				onAdvance?.();
			}
		}, 1000);

		return () => clearInterval(interval);
	});
</script>

<div class="round-over-overlay">
	<div class="round-over-modal">
		<div class="modal-header">
			<h2>ROUND {$gameState.round_number} OVER</h2>
			<p class="timer">Auto-advance in {autoAdvanceTimer}s</p>
		</div>

		<div class="verdict-content">
			<div class="scores-grid">
				<div class="score-header">Player</div>
				<div class="score-header">Round Score</div>
				<div class="score-header">Total</div>

				{#each $gameState.opponents as opp}
					<div class="player-name">{opp.player_name}</div>
					<div class="round-score">+0</div>
					<div class="total-score">{opp.score}</div>
				{/each}
			</div>

			<div class="trial-summary">
				{#if $gameState.trial.perjury_removed.length > 0}
					<div class="summary-section perjury">
						<div class="section-title">⚠️ Perjury</div>
						<div class="summary-list">
							{#each $gameState.trial.perjury_removed as playerId}
								<div class="summary-item">
									{$gameState.opponents.find(o => o.player_id === playerId)?.player_name}
								</div>
							{/each}
						</div>
					</div>
				{/if}

				{#if $gameState.trial.duel_occurred}
					<div class="summary-section duel">
						<div class="section-title">⚔️ Duel Results</div>
						<div class="summary-list">
							{#each $gameState.trial.duel_winners as playerId}
								<div class="summary-item winner">
									{$gameState.opponents.find(o => o.player_id === playerId)?.player_name} (Winner)
								</div>
							{/each}
						</div>
					</div>
				{/if}

				{#if $gameState.trial.plea_taken.length > 0}
					<div class="summary-section plea">
						<div class="section-title">🙏 Plea Taken</div>
						<div class="summary-list">
							{#each $gameState.trial.plea_taken as playerId}
								<div class="summary-item">
									{$gameState.opponents.find(o => o.player_id === playerId)?.player_name}
								</div>
							{/each}
						</div>
					</div>
				{/if}
			</div>
		</div>

		<div class="modal-footer">
			<button class="btn btn--primary" onclick={onAdvance}>Continue</button>
		</div>
	</div>
</div>

<style>
	.round-over-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.6);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		animation: fadeIn 0.3s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.round-over-modal {
		background: var(--color-bg-card, #ffffff);
		border-radius: var(--radius-md, 8px);
		padding: 32px;
		max-width: 600px;
		width: 90vw;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 50px rgba(0, 0, 0, 0.3);
	}

	.modal-header {
		text-align: center;
		margin-bottom: 24px;
	}

	.modal-header h2 {
		font-size: 28px;
		font-weight: 700;
		margin: 0 0 8px;
		color: var(--color-text, #333);
	}

	.timer {
		font-size: 13px;
		color: var(--color-text-light, #666);
		margin: 0;
		font-weight: 500;
	}

	.verdict-content {
		margin-bottom: 24px;
	}

	.scores-grid {
		display: grid;
		grid-template-columns: 2fr 1fr 1fr;
		gap: 12px;
		margin-bottom: 20px;
		padding: 12px;
		background: var(--color-bg, #f5f5f5);
		border-radius: 6px;
	}

	.score-header {
		font-size: 12px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		color: var(--color-text-light, #666);
	}

	.player-name {
		font-weight: 600;
		color: var(--color-text, #333);
		font-size: 14px;
	}

	.round-score {
		text-align: center;
		font-size: 14px;
		color: var(--color-text, #333);
	}

	.total-score {
		text-align: center;
		font-weight: 600;
		font-size: 14px;
		color: var(--color-primary, #007bff);
	}

	.trial-summary {
		display: flex;
		flex-direction: column;
		gap: 12px;
	}

	.summary-section {
		padding: 12px;
		border-radius: 6px;
		border-left: 3px solid;
	}

	.summary-section.perjury {
		background: #ffebee;
		border-left-color: #f44336;
	}

	.summary-section.duel {
		background: #e8f5e9;
		border-left-color: #4caf50;
	}

	.summary-section.plea {
		background: #f3e5f5;
		border-left-color: #9c27b0;
	}

	.section-title {
		font-size: 12px;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		margin-bottom: 6px;
		color: var(--color-text, #333);
	}

	.summary-list {
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.summary-item {
		font-size: 13px;
		color: var(--color-text, #333);
		padding-left: 4px;
	}

	.summary-item.winner {
		font-weight: 600;
		color: #4caf50;
	}

	.modal-footer {
		display: flex;
		gap: 12px;
		justify-content: center;
	}

	.btn {
		padding: 10px 24px;
		border: none;
		border-radius: 4px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		font-size: 14px;
	}

	.btn--primary {
		background: var(--color-primary, #007bff);
		color: white;
	}

	.btn--primary:hover {
		background: var(--color-primary-dark, #0056b3);
	}
</style>