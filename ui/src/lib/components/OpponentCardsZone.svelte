<!-- src/lib/components/OpponentCardsZone.svelte -->
<script lang="ts">
  import CardContainer from './CardContainer.svelte';
  import type { OpponentInfo } from '$lib/stores/gameState';

  interface Props {
    opponent: OpponentInfo;
  }

  let { opponent }: Props = $props();

  // Convert known_cards to card data format for CardContainer
  const opponentCards = $derived.by(() => {
    return [0, 1, 2, 3].map(slotIdx => {
      const knownCard = opponent.known_cards.find((c) => c.slot === slotIdx);
      return knownCard
        ? { known: true, rank: knownCard.rank, suit: knownCard.suit }
        : { known: false };
    });
  });
</script>

<div class="opponent-cards-zone">
  <div class="opponent-header">
    <div class="opponent-name">{opponent.player_name}</div>
    <div class="opponent-meta">
      <span class="score">Score: {opponent.score}</span>
    </div>
  </div>

  <CardContainer 
    cards={opponentCards}
    isYourCards={false}
    showKnowledge={false}
  />
</div>

<style>
  .opponent-cards-zone {
    display: flex;
    flex-direction: column;
    gap: clamp(0.25rem, 0.8vw, 0.5rem);
    align-items: center;
    padding: 0;
    background: transparent;
    border-radius: 0;
    border: none;
    width: 100%;
    height: 100%;
    min-height: 0;
  }

  .opponent-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
    width: 100%;
    text-align: center;
    border-bottom: 1px solid var(--color-border-light);
    padding-bottom: clamp(0.25rem, 0.5vw, 0.5rem);
    margin-bottom: clamp(0.25rem, 0.8vw, 0.5rem);
  }

  .opponent-name {
    font-weight: var(--font-weight-bold);
    font-size: clamp(0.75rem, 1vw, 1rem);
    color: var(--color-text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .opponent-meta {
    display: flex;
    gap: clamp(0.5rem, 1vw, 1rem);
    font-size: clamp(0.65rem, 0.8vw, 0.875rem);
    color: var(--color-text-light);
  }

  .score {
    white-space: nowrap;
  }
</style>