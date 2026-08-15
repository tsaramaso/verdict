<!-- src/lib/components/YourCardsZone.svelte -->
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
  <div class="your-zone-container">
    <CardContainer 
      cards={yourCards}
      isYourCards={true}
      {onCardClick}
      showKnowledge={true}
    />
  </div>
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

  .your-zone-container {
    display: flex;
    align-items: center;
    justify-content: center;
    /* Fixed size matching opponent zones */
    aspect-ratio: 2.5 / 3.5;
    height: 100%;
    width: auto;
    min-height: 0;
    min-width: 0;
  }
</style>