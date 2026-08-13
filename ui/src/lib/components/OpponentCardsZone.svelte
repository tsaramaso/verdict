<!-- src/lib/components/OpponentCardsZone.svelte -->
<script lang="ts">
  import CardSlot from './CardSlot.svelte';
  import { getOpponentsThatKnowSlot, myOpponentKnowledge } from '$lib/stores/gameState';
  import type { OpponentInfo } from '$lib/stores/gameState';

  interface Props {
    opponent: OpponentInfo;
  }

  let { opponent }: Props = $props();
</script>

<div class="opponent-cards-zone">
  <div class="opponent-header">
    <div class="opponent-name">{opponent.player_name}</div>
    <div class="opponent-meta">
      <span class="hand-count">Hand: {opponent.hand_count}</span>
      <span class="score">Score: {opponent.score}</span>
    </div>
  </div>

  <div class="opponent-hand">
    {#each [0, 1, 2, 3] as slotIdx}
      {@const knownCard = opponent.known_cards.find((c) => c.slot === slotIdx)}
      {@const oppsWhoKnow = getOpponentsThatKnowSlot($myOpponentKnowledge, slotIdx)}
      {@const anyOpponentKnows = oppsWhoKnow.length > 0}
      <CardSlot
        card={knownCard
          ? { known: true, rank: knownCard.rank, suit: knownCard.suit }
          : { known: false }}
        slotIndex={slotIdx}
        isYourCard={false}
        opponentKnowsSlot={anyOpponentKnows}
        opponentsWhoKnow={oppsWhoKnow}
      />
    {/each}
  </div>
</div>

<style>
  .opponent-cards-zone {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    align-items: center;
    padding: var(--spacing-md);
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
  }

  .opponent-header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: var(--spacing-xs);
    width: 100%;
    text-align: center;
    border-bottom: 1px solid var(--color-border-light);
    padding-bottom: var(--spacing-sm);
    margin-bottom: var(--spacing-sm);
  }

  .opponent-name {
    font-weight: var(--font-weight-bold);
    font-size: var(--font-size-base);
    color: var(--color-text);
  }

  .opponent-meta {
    display: flex;
    gap: var(--spacing-md);
    font-size: var(--font-size-xs);
    color: var(--color-text-light);
  }

  .hand-count,
  .score {
    white-space: nowrap;
  }

  .opponent-hand {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-sm);
    width: 100%;
  }

  @media (max-width: 768px) {
    .opponent-meta {
      flex-direction: column;
      gap: var(--spacing-xs);
    }
  }
</style>
