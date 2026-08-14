<!-- src/lib/components/YourCardsZone.svelte (UPDATED) -->
<script lang="ts">
  import CardContainer from './CardContainer.svelte';
  import { gameState } from '$lib/stores/gameState';

  interface Props {
    onCardClick?: (slotIndex: number) => void;
  }

  let { onCardClick }: Props = $props();

  const yourCards = $derived($gameState.self.hand);
</script>

<div class="your-cards-zone">
  <CardContainer 
    cards={yourCards}
    isYourCards={true}
    {onCardClick}
    showKnowledge={true}
  />
</div>

<style>
  .your-cards-zone {
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0;
    background: transparent;
    width: 100%;
    height: 100%;
    min-height: 0;
    min-width: 0;
  }
</style>