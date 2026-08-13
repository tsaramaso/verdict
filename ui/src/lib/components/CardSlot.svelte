<!-- src/lib/components/CardSlot.svelte -->
<script lang="ts">
	import { type CardSuit, type CardRank, SUIT_LABELS, RANK_LABELS } from '$lib/constants/cards';

  interface CardData {
    known: boolean;
    rank?: CardRank;
    suit?: CardSuit;
  }

  interface Props {
    card?: CardData;
    slotIndex?: number;
    isYourCard?: boolean;
    isClickable?: boolean;
    opponentKnowsSlot?: boolean;
    opponentsWhoKnow?: string[];
    onClick?: () => void;
    showRankBadge?: boolean;
  }

  let {
    card,
    slotIndex = 0,
    isYourCard = false,
    isClickable = false,
    opponentKnowsSlot = false,
    opponentsWhoKnow = [],
    onClick,
    showRankBadge = true,
  }: Props = $props();

  let isHovered = $state(false);

  function getKnowledgeTooltip(opponents: string[]): string {
    if (opponents.length === 0) return 'No one knows';
    return `${opponents.length} opponent(s) know`;
  }
</script>

<div
  class={`card-slot ${isYourCard ? 'card-slot--your' : 'card-slot--opponent'} ${isClickable ? 'card-slot--clickable' : ''} ${isHovered ? 'card-slot--hovered' : ''}`}
  role="button"
  tabindex={isClickable ? 0 : -1}
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
  <!-- Card Back Visual (Geometric Rectangle) -->
  {#if !card || !card.known}
    <div class="card-back">
      <div class="card-back__pattern"></div>
    </div>
  {/if}
  <!-- Rank Badge (if known) -->
  {#if card?.known && showRankBadge && card.rank && card.suit}
    <div class="rank-badge">
      <span class="badge__text">{card.rank}<br/>{card.suit}</span>
    </div>
  {/if}

  <!-- Opponent Knows Icon (Unified 👁️) -->
  {#if opponentKnowsSlot}
    <div class="opponent-knows-icon" title={getKnowledgeTooltip(opponentsWhoKnow)}>
      👁️
    </div>
  {/if}

  <!-- Hover Tooltip (who knows this card) -->
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
  .card-slot {
    position: relative;
    width: 100%;
    aspect-ratio: 2.5 / 3.5;
    border-radius: var(--radius-md);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    cursor: default;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .card-slot--clickable {
    cursor: pointer;
  }

  .card-slot--clickable:hover {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
  }

  .card-slot--hovered {
    transform: translateY(-4px);
    box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
  }

  /* Card Back Visual (Face Down) */
  .card-back {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #2a2a3e 0%, #1a1a2e 100%);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
  }

  .card-back__pattern {
    width: 80%;
    height: 80%;
    border: 2px solid rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    background: repeating-linear-gradient(
      45deg,
      transparent,
      transparent 10px,
      rgba(255, 255, 255, 0.05) 10px,
      rgba(255, 255, 255, 0.05) 20px
    );
  }

  /* Card Face (Known Card) */
  .card-face {
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, #ffffff 0%, #f3f4f6 100%);
    border-radius: var(--radius-md);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    color: var(--suit-color, #dc2626);
  }

  .card-face__rank {
    font-size: clamp(16px, 4vw, 24px);
    font-weight: var(--font-weight-bold);
    line-height: 1;
  }

  .card-face__suit {
    font-size: clamp(14px, 3vw, 20px);
    margin-top: 4px;
  }

  /* Rank Badge (for known opponent cards) */
  .rank-badge {
    position: absolute;
    top: 4px;
    right: 4px;
    background: var(--color-primary);
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: var(--font-weight-bold);
    pointer-events: none;
    z-index: 10;
  }

  .badge__text {
    font-family: monospace;
    color: var(--suit-color)
  }


  /* Opponent Knows Icon (Unified 👁️) */
  .opponent-knows-icon {
    position: absolute;
    bottom: 4px;
    right: 4px;
    font-size: 18px;
    filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.3));
    pointer-events: none;
    z-index: 10;
  }

  /* Hover Tooltip */
  .hover-tooltip {
    position: absolute;
    bottom: 100%;
    left: 50%;
    transform: translateX(-50%);
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-sm);
    padding: var(--spacing-sm);
    margin-bottom: var(--spacing-xs);
    z-index: 20;
    white-space: nowrap;
    box-shadow: var(--shadow-lg);
  }

  .hover-tooltip__title {
    font-size: var(--font-size-xs);
    font-weight: var(--font-weight-bold);
    color: var(--color-text-light);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }

  .hover-tooltip__list {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }

  .hover-tooltip__item {
    font-size: var(--font-size-sm);
    color: var(--color-text);
    font-family: monospace;
  }

  /* Your Cards styling */
  .card-slot--your {
    min-width: 100px;
  }

  /* Opponent Cards styling (smaller) */
  .card-slot--opponent {
    min-width: 80px;
  }
</style>