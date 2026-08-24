<script lang="ts">
	import { gameState } from '$lib/stores/gameState';

	interface Props {
		isClickable: boolean;
		onClick?: () => void;
	}

	let { isClickable, onClick }: Props = $props();

	const deckCount = $derived($gameState.discard_pile?.count ?? 0);
	const cardCount = $derived(52 - deckCount);

	function handleClick() {
		console.log('[DeckZone] Clicked, isClickable:', isClickable);
		if (isClickable && onClick) {
			console.log('[DeckZone] Calling onClick handler');
			onClick();
		} else {
			console.warn('[DeckZone] Click ignored - not clickable or no handler');
		}
	}
</script>

<div
	class="deck-zone"
	class:clickable={isClickable}
	class:clickable-glow={isClickable}
	onclick={handleClick}
	role={isClickable ? 'button' : 'region'}
	{...isClickable ? { tabindex: 0 } : {}}
	aria-label="Draw from deck"
>
	<div class="card-stack">
		<div class="card-stack__layer card-back"></div>
		<div class="card-stack__layer card-back"></div>
		<div class="card-stack__layer card-back"></div>
	</div>
	<div class="card-count">{cardCount}</div>
</div>

<style>
	@import '$lib/styles/card.css';
	@import '$lib/styles/clickable.css';

	.deck-zone {
		position: relative;
		cursor: default;
		transition: all 0.2s ease;
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 0.5rem;
	}

	.deck-zone.clickable {
		cursor: pointer;
	}

	.deck-zone.clickable:hover {
		transform: translateY(-4px);
	}

	.deck-zone.clickable:focus-visible {
		outline: 2px solid var(--color-primary, #007bff);
		outline-offset: 4px;
		border-radius: var(--card-border-radius);
	}

	.card-count {
		font-weight: var(--font-weight-bold);
		font-size: clamp(0.75rem, 1.2vw, 1rem);
		color: var(--color-text);
		text-align: center;
		min-width: 2rem;
	}
</style>