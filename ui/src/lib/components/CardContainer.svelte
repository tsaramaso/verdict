<!-- src/lib/components/CardContainer.svelte -->
<script lang="ts">
  import CardSlot, { type CardData} from './CardSlot.svelte';
  import { getOpponentsThatKnowSlot, myOpponentKnowledge } from '$lib/stores/gameState';

  interface Props {
    cards?: (CardData | undefined)[];
    isYourCards?: boolean;
    onCardClick?: (slotIndex: number) => void;
    showKnowledge?: boolean;
  }

  let { 
    cards = [undefined, undefined, undefined, undefined],
    isYourCards = false,
    onCardClick,
    showKnowledge = true
  }: Props = $props();
</script>

<div class="card-container">
  {#each [0, 1, 2, 3] as slotIdx}
    {@const card = cards[slotIdx]}
    {@const oppsWhoKnow = isYourCards ? getOpponentsThatKnowSlot($myOpponentKnowledge, slotIdx) : []}
    {@const anyOpponentKnows = showKnowledge && oppsWhoKnow.length > 0}
    <CardSlot
      {card}
      slotIndex={slotIdx}
      isYourCard={isYourCards}
      isClickable={isYourCards}
      opponentKnowsSlot={anyOpponentKnows}
      opponentsWhoKnow={oppsWhoKnow}
      onClick={() => isYourCards && onCardClick?.(slotIdx)}
    />
  {/each}
</div>

<style>
  .card-container {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: clamp(0.5rem, 1.5vw, 1rem);
    width: 100%;
    height: 100%;
    min-height: 0;
    min-width: 0;
  }
</style>