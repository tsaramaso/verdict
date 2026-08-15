<!-- src/lib/components/DiscardZone.svelte (FINAL) -->
<script lang="ts">
  interface Props {
    isClickable?: boolean;
    onClick?: () => void;
  }

  let { isClickable = false, onClick }: Props = $props();

  import { gameState } from '$lib/stores/gameState';

  const topCard = $derived($gameState.discard_pile.visible_cards[0]);
  const discardCount = $derived($gameState.discard_pile.count ?? 0);
</script>

<button
  class="discard-zone"
  disabled={!isClickable}
  onclick={onClick}
  title={topCard ? `${topCard.rank}${topCard.suit}` : 'Empty discard pile'}
>
  {#if topCard}
    <div class="card-display">
      <div class="card-rank">{topCard.rank}</div>
      <div class="card-suit">{topCard.suit}</div>
    </div>
  {:else}
    <div class="card-display">
      <div class="empty-text">No card</div>
    </div>
  {/if}
  <div class="discard-count">{discardCount}</div>
</button>

<style>
	.discard-zone {
		position: relative;
		height: 100%;
		aspect-ratio: 2.5 / 3.5;
		background: linear-gradient(135deg, #f5f5f5 0%, #e8e8e8 100%);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: default;
		transition: all 0.2s ease;
		border: 2px solid transparent;
	}

	.discard-zone:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.discard-zone:not(:disabled) {
		cursor: pointer;
	}

	.discard-zone:not(:disabled):hover {
		border-color: #4a9eff;
		transform: translateY(-2px);
		box-shadow: var(--shadow-lg), 0 0 12px rgba(74, 158, 255, 0.3);
	}

	.discard-zone:not(:disabled):active {
		transform: translateY(0);
	}

	.card-display {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		color: var(--color-text);
	}

	.card-rank {
		font-size: clamp(0.875rem, 2.5vw, 1.5rem);
		font-weight: var(--font-weight-bold);
		line-height: 1;
	}

	.card-suit {
		font-size: clamp(0.75rem, 2vw, 1.25rem);
		margin-top: clamp(2px, 1.5%, 6px);
	}

	.empty-text {
		font-size: clamp(0.75rem, 1.5vw, 1rem);
		color: var(--color-text-light);
	}

	.discard-count {
		position: absolute;
		bottom: clamp(4px, 3%, 12px);
		right: clamp(4px, 3%, 12px);
		background: rgba(0, 0, 0, 0.2);
		color: var(--color-text);
		padding: clamp(2px, 1.5%, 6px) clamp(4px, 2%, 8px);
		border-radius: var(--radius-sm);
		font-size: clamp(0.65rem, 1.5vw, 0.875rem);
		font-weight: var(--font-weight-bold);
		font-family: monospace;
	}
</style>