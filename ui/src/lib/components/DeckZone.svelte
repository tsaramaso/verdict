<!-- src/lib/components/DeckZone.svelte -->
<script lang="ts">
	import { deckSize } from '$lib/stores/gameState';

	interface Props {
		isClickable?: boolean;
		onClick?: () => void;
	}

	let { isClickable = false, onClick }: Props = $props();

	let isHovered = $state(false);
</script>

<button
	class={`deck-zone ${isClickable ? 'deck-zone--clickable' : ''} ${isHovered ? 'deck-zone--hovered' : ''}`}
	disabled={!isClickable}
	onclick={onClick}
	onmouseenter={() => (isHovered = true)}
	onmouseleave={() => (isHovered = false)}
	title="Draw a card from the deck"
>
	<div class="deck-content">
		<div class="deck-label">DECK</div>
	</div>
	<div class="deck-count">{$deckSize}</div>
</button>

<style>
	.deck-zone {
		position: relative;
		height: 100%;
		aspect-ratio: 2.5 / 3.5;
		background: linear-gradient(135deg, #2a2a3e 0%, #1a1a2e 100%);
		background-image: 
			repeating-linear-gradient(
				45deg,
				transparent,
				transparent 10px,
				rgba(12, 196, 233, 0.05) 10px,
				rgba(255, 255, 255, 0.05) 20px
			);
		border: 2px solid rgba(255, 255, 255, 0.1);
		border-radius: var(--radius-md);
		box-shadow: var(--shadow-md);
		display: flex;
		align-items: center;
		justify-content: center;
		cursor: default;
		transition: all 0.2s ease;
	}

	.deck-zone:disabled {
		cursor: not-allowed;
		opacity: 0.6;
	}

	.deck-zone:not(:disabled) {
		cursor: pointer;
	}

	.deck-zone--clickable:hover {
		border-color: var(--color-primary);
		box-shadow:
			0 0 0 2px rgba(0, 123, 255, 0.2),
			var(--shadow-md);
	}

	.deck-zone--hovered {
		transform: scale(1.05);
	}

	.deck-content {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		color: #8892b0;
		font-size: clamp(0.75rem, 2.5vw, 1.25rem);
		font-weight: var(--font-weight-bold);
	}

	.deck-label {
		letter-spacing: clamp(1px, 1vw, 2px);
	}

	.deck-count {
		position: absolute;
		bottom: clamp(2px, 3%, 8px);
		right: clamp(2px, 3%, 8px);
		background: rgba(0, 0, 0, 0.3);
		color: white;
		padding: clamp(1px, 1.5%, 4px) clamp(2px, 2%, 6px);
		border-radius: clamp(2px, 3%, 4px);
		font-size: clamp(0.65rem, 1.5vw, 0.875rem);
		font-weight: var(--font-weight-bold);
		font-family: monospace;
	}
</style>