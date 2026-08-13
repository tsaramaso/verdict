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

<div
	class={`deck-zone ${isClickable ? 'deck-zone--clickable' : ''} ${isHovered ? 'deck-zone--hovered' : ''}`}
	role="button"
	tabindex={isClickable ? 0 : -1}
	onclick={onClick}
	onmouseenter={() => (isHovered = true)}
	onmouseleave={() => (isHovered = false)}
>
	<div class="deck-back">
		<div class="deck-pattern"></div>
	</div>
	<div class="deck-count">{$deckSize}</div>
</div>

<style>
	.deck-zone {
		position: relative;
		width: 120px;
		height: 180px;
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

	.deck-zone--clickable {
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

	.deck-back {
		width: 100%;
		height: 100%;
		border: 2px solid rgba(255, 255, 255, 0.2);
		border-radius: var(--radius-sm);
		position: relative;
		overflow: hidden;
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

	.deck-count {
		position: absolute;
		bottom: 8px;
		right: 8px;
		background: rgba(0, 0, 0, 0.3);
		color: white;
		padding: 4px 8px;
		border-radius: var(--radius-sm);
		font-size: var(--font-size-sm);
		font-weight: var(--font-weight-bold);
		font-family: monospace;
	}
</style>
