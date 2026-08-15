<!-- src/lib/components/DeckZone.svelte (FINAL) -->
<script lang="ts">
  interface Props {
    isClickable?: boolean;
    onClick?: () => void;
  }

  let { isClickable = false, onClick }: Props = $props();

  import { deckSize } from '$lib/stores/gameState';

  const deckCount = $derived(deckSize);
</script>

<button
  class="deck-zone"
  disabled={!isClickable}
  onclick={onClick}
  title="Draw a card from the deck"
>
  <div class="deck-pattern">
    <div class="deck-label">Deck</div>
  </div>
</button>

<style>
	.deck-zone {
		position: relative;
		height: 100%;
		aspect-ratio: 2.5 / 3.5;
		background: linear-gradient(135deg, #2a2a3e 0%, #1a1a2e 100%);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: default;
		transition: all 0.2s ease;
		border: 2px solid transparent;
	}

	.deck-zone:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.deck-zone:not(:disabled) {
		cursor: pointer;
	}

	.deck-zone:not(:disabled):hover {
		border-color: #4a9eff;
		transform: translateY(-2px);
		box-shadow: var(--shadow-lg), 0 0 12px rgba(74, 158, 255, 0.3);
	}

	.deck-zone:not(:disabled):active {
		transform: translateY(0);
	}
		.deck-pattern {
		width: 100%;
		height: 100%;
		background: repeating-linear-gradient(
			45deg,
			transparent,
			transparent 10px,
			rgba(255, 255, 255, 0.05) 10px,
			rgba(255, 255, 255, 0.05) 20px
		);
	}

	.deck-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
				background: repeating-linear-gradient(
			45deg,
			transparent,
			transparent 10px,
			rgba(255, 255, 255, 0.05) 10px,
			rgba(255, 255, 255, 0.05) 20px
		);
		font-size: clamp(0.875rem, 2.5vw, 1.5rem);
		font-weight: var(--font-weight-bold);
	}

	.deck-label {
		letter-spacing: 2px;
	}

	.deck-count {
		position: absolute;
		bottom: clamp(4px, 3%, 12px);
		right: clamp(4px, 3%, 12px);
		background: rgba(0, 0, 0, 0.3);
		color: white;
		padding: clamp(2px, 1.5%, 6px) clamp(4px, 2%, 8px);
		border-radius: var(--radius-sm);
		font-size: clamp(0.65rem, 1.5vw, 0.875rem);
		font-weight: var(--font-weight-bold);
		font-family: monospace;
	}
	
</style>