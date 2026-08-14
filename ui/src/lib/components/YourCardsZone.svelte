<!-- src/lib/components/YourCardsZone.svelte (UPDATED) -->
<script lang="ts">
  import CardContainer from './CardContainer.svelte';
  import { gameState } from '$lib/stores/gameState';

  interface Props {
    onCardClick?: (slotIndex: number) => void;
  }

  let { onCardClick }: Props = $props();

  const yourCards = $derived($gameState.self.hand);
  const yourName = $derived($gameState.self.player_name);
</script>

<div class="your-cards-zone">
  <div class="your-header">
    <div class="your-name">{yourName}</div>
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
    .your-header {
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
  .your-name {
    font-weight: var(--font-weight-bold);
    font-size: clamp(0.75rem, 1vw, 1rem);
    color: var(--color-text);
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

</style>