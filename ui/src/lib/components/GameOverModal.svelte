<script lang="ts">
	import { gameState } from '$lib/stores/gameState';

	interface Props {
		onReturnLobby?: () => void;
		onPlayAgain?: () => void;
	}

	let { onReturnLobby, onPlayAgain }: Props = $props();

	// Sort players by score (lowest wins)
	const finalRankings = $derived.by(() => {
		const allPlayers = [
			{ id: $gameState.self.player_id, name: $gameState.self.player_name, score: $gameState.self.score },
			...$gameState.opponents.map(o => ({ id: o.player_id, name: o.player_name, score: o.score }))
		];

		return allPlayers.sort((a, b) => a.score - b.score);
	});

	function getRankLabel(index: number): string {
		const ranks = ['🥇 1st', '🥈 2nd', '🥉 3rd', '4th', '5th'];
		return ranks[index] || `${index + 1}th`;
	}
</script>

<div class="game-over-overlay">
	<div class="game-over-modal">
		<div class="modal-header">
			<h1>GAME OVER</h1>
			<p class="subtitle">Final Rankings</p>
		</div>

		<div class="rankings">
			{#each finalRankings as player, idx}
				<div class="ranking-row" class:winner={idx === 0}>
					<div class="rank">
						{getRankLabel(idx)}
					</div>
					<div class="player-info">
						<div class="player-name">{player.name}</div>
						<div class="player-score">{player.score} points</div>
					</div>
					{#if idx === 0}
						<div class="crown">👑</div>
					{/if}
				</div>
			{/each}
		</div>

		<div class="modal-footer">
			<button class="btn btn--secondary" onclick={onReturnLobby}>Return to Lobby</button>
			<button class="btn btn--primary" onclick={onPlayAgain}>Play Again</button>
		</div>
	</div>
</div>

<style>
	.game-over-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.7);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		animation: fadeIn 0.3s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
			transform: scale(0.95);
		}
		to {
			opacity: 1;
			transform: scale(1);
		}
	}

	.game-over-modal {
		background: var(--color-bg-card, #ffffff);
		border-radius: var(--radius-md, 8px);
		padding: 40px;
		max-width: 500px;
		width: 90vw;
		box-shadow: 0 25px 60px rgba(0, 0, 0, 0.4);
	}

	.modal-header {
		text-align: center;
		margin-bottom: 32px;
	}

	.modal-header h1 {
		font-size: 40px;
		font-weight: 800;
		margin: 0 0 8px;
		color: var(--color-text, #333);
		letter-spacing: 2px;
	}

	.subtitle {
		font-size: 14px;
		color: var(--color-text-light, #666);
		margin: 0;
		text-transform: uppercase;
		letter-spacing: 1px;
		font-weight: 600;
	}

	.rankings {
		display: flex;
		flex-direction: column;
		gap: 12px;
		margin-bottom: 32px;
	}

	.ranking-row {
		display: flex;
		align-items: center;
		gap: 16px;
		padding: 16px;
		background: var(--color-bg, #f5f5f5);
		border-radius: 6px;
		transition: all 0.2s ease;
	}

	.ranking-row.winner {
		background: linear-gradient(135deg, #fff9e6 0%, #ffe6b3 100%);
		border: 2px solid #ffc107;
	}

	.rank {
		font-size: 16px;
		font-weight: 700;
		min-width: 60px;
		color: var(--color-text, #333);
	}

	.player-info {
		flex: 1;
	}

	.player-name {
		font-weight: 600;
		font-size: 15px;
		color: var(--color-text, #333);
		margin-bottom: 4px;
	}

	.player-score {
		font-size: 12px;
		color: var(--color-text-light, #666);
	}

	.crown {
		font-size: 24px;
		animation: bounce 1s infinite;
	}

	@keyframes bounce {
		0%,
		100% {
			transform: translateY(0);
		}
		50% {
			transform: translateY(-4px);
		}
	}

	.modal-footer {
		display: flex;
		gap: 12px;
	}

	.btn {
		flex: 1;
		padding: 12px 16px;
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

	.btn--secondary {
		background: var(--color-border, #ddd);
		color: var(--color-text, #333);
	}

	.btn--secondary:hover {
		background: var(--color-text-light, #999);
		color: white;
	}
</style>