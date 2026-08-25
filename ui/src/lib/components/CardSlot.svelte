<script lang="ts">
	import { type CardSuit, type CardRank, SUIT_COLORS } from '$lib/constants/cards';
	import { displayRank, displaySuit } from '$lib/utils/cardTransform';

	export interface CardData {
		known: boolean;
		rank?: CardRank;
		suit?: CardSuit;
	}

	interface Props {
		card?: CardData;
		slotIndex?: number;
		isYourCard?: boolean;
		isClickable?: boolean;
		isHighlighted?: boolean;
		opponentKnows?: Record<string, boolean>;
		onClick?: () => void;
		showRankBadge?: boolean;
	}

	let {
		card,
		slotIndex = 0,
		isYourCard = false,
		isClickable = false,
		isHighlighted = false,
		opponentKnows,
		onClick,
		showRankBadge = true
	}: Props = $props();

	let isHovered = $state(false);

	function hasOpponentKnowledge(): boolean {
		if (!opponentKnows) return false;
		return Object.values(opponentKnows).some((v) => v === true);
	}

	function getOpponentNames(): string[] {
		if (!opponentKnows) return [];
		return Object.keys(opponentKnows).filter((id) => opponentKnows![id]);
	}

	const opponentsWhoKnow = $derived(getOpponentNames());
</script>

<div
	class="card-slot"
	class:clickable={isClickable}
	class:highlighted={isHighlighted}
	class:hovered={isHovered}
	role={isClickable ? 'button' : 'region'}
	{...isClickable ? { tabindex: 0 } : {}}
	onclick={onClick}
	onkeydown={(e) => {
		if (isClickable && (e.key === 'Enter' || e.key === ' ')) {
			e.preventDefault();
			onClick?.();
		}
	}}
	onmouseenter={() => (isHovered = true)}
	onmouseleave={() => (isHovered = false)}
>
	{#if !card || !card.known}
		<div class="card-back"></div>
	{:else if card.known}
		<!-- Face-down but known: show badge only -->
		<div class="card-back"></div>
	{/if}

	{#if card?.known && showRankBadge && card.rank && card.suit}
		<div class="rank-badge" style="color: {SUIT_COLORS[card.suit]}">
			{displayRank(card.rank)}{displaySuit(card.suit)}
		</div>
	{/if}

	{#if hasOpponentKnowledge()}
		<div class="opponent-knows-icon" title={opponentsWhoKnow.join(', ')}>👁️</div>
	{/if}

	{#if isHovered && isYourCard && opponentsWhoKnow.length > 0}
		<div class="hover-tooltip">
			<div class="hover-tooltip__title">Known by:</div>
			<div class="hover-tooltip__list">
				{#each opponentsWhoKnow as oppId}
					<div class="hover-tooltip__item">{oppId.slice(0, 8)}</div>
				{/each}
			</div>
		</div>
	{/if}
</div>

<style>
	@import '$lib/styles/card.css';

	.card-slot {
		position: relative;
		width: 100%;
		display: flex;
		align-items: center;
		justify-content: center;
		transition: all 0.2s ease;
	}

	.card-slot.clickable {
		cursor: pointer;
	}

	.card-slot.clickable:hover {
		transform: translateY(-4px);
	}

	.card-slot.clickable:focus-visible {
		outline: 2px solid var(--color-primary, #007bff);
		outline-offset: 4px;
	}

	.card-slot.highlighted {
		background: linear-gradient(135deg, #ffeb3b, #ffc107);
		border-color: #ff9800;
		box-shadow: 0 0 0 3px rgba(255, 152, 0, 0.3);
	}

	.card-slot.hovered {
		box-shadow: var(--card-box-shadow-hover, 0 8px 16px rgba(0, 0, 0, 0.2));
	}
</style>