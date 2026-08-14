<!-- src/lib/components/GamePage.svelte -->
<script lang="ts">
  import { onMount } from 'svelte';
  import { gameState, setCurrentPlayerId } from '$lib/stores/gameState';
  import TopBanner from './TopBanner.svelte';
  import OpponentZonesContainer from './OpponentZonesContainer.svelte';
  import CentralArea from './CentralArea.svelte';
  import YourCardsZone from './YourCardsZone.svelte';
  import RightPanel from './RightPanel.svelte';
	import { transformCardList, transformRank, transformSuit } from '$lib/utils/cardTransform';

  interface Props {
    playerId: string;
    gameId: string;
  }

  let { playerId, gameId }: Props = $props();

  onMount(() => {
    // Set current player ID for derived stores
    setCurrentPlayerId(playerId);

    // Initialize WebSocket connection
    initWebSocket();
  });

  function initWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const token = getTokenFromStorage();
  const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
  const apiHost = new URL(apiUrl).host;
  const url = `${protocol}//${apiHost}/ws/games/${gameId}?token=${token}`;

    console.log('WebSocket URL:', url);

  const ws = new WebSocket(url);

    ws.onopen = () => {
      console.log('[WS] Connected to game:', gameId);
    };


ws.onmessage = (event) => {
  const message = JSON.parse(event.data);

  if (message.type === 'game_state' || message.type === 'game_state_update') {
    // Transform card data from API strings to enums
    const transformedSelf = {
      ...message.self,
      hand: transformCardList(message.self.hand)
    };
    
    const transformedOpponents = message.opponents.map((opp: any) => ({
      ...opp,
      known_cards: opp.known_cards.map((card: any) => ({
        slot: card.slot,
        rank: transformRank(card.rank),
        suit: transformSuit(card.suit)
      }))
    }));
    
    const transformedDiscard = {
      ...message.discard_pile,
      visible_cards: message.discard_pile.visible_cards.map((card: any) => ({
        rank: transformRank(card.rank),
        suit: transformSuit(card.suit)
      }))
    };
    
    // Update store with transformed state
    gameState.set({
      game_id: message.game_id,
      phase: message.phase,
      current_player: message.current_player,
      round_number: message.round_number,
      self: transformedSelf,
      opponents: transformedOpponents,
      my_opponent_knowledge: message.my_opponent_knowledge,
      trial: message.trial,
      discard_pile: transformedDiscard,
      rules: message.rules
    });
  }
};

    ws.onerror = (error) => {
      console.error('[WS] Error:', error);
    };

    ws.onclose = () => {
      console.log('[WS] Disconnected');
      // TODO: Implement reconnection with exponential backoff
    };

    return ws;
  }

  function getTokenFromStorage(): string {
    if (typeof window === 'undefined') return '';
    return localStorage.getItem('auth_token') || '';
  }

  // Action handlers
  async function handleDeckClick() {
    try {
      const response = await fetch(`/api/games/${gameId}/draw`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) console.error('Draw failed');
    } catch (error) {
      console.error('Draw error:', error);
    }
  }

  async function handleDiscardClick() {
    try {
      const response = await fetch(`/api/games/${gameId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'discard' }),
      });
      if (!response.ok) console.error('Action failed');
    } catch (error) {
      console.error('Action error:', error);
    }
  }

  async function handleCardClick(slotIndex: number) {
    try {
      const response = await fetch(`/api/games/${gameId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'select_card', slot: slotIndex }),
      });
      if (!response.ok) console.error('Card selection failed');
    } catch (error) {
      console.error('Card selection error:', error);
    }
  }

  async function handleSkip() {
    try {
      const response = await fetch(`/api/games/${gameId}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'pass' }),
      });
      if (!response.ok) console.error('Skip failed');
    } catch (error) {
      console.error('Skip error:', error);
    }
  }

  async function handleTestifyFirst() {
    try {
      const response = await fetch(`/api/games/${gameId}/trial/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) console.error('Testimony failed');
    } catch (error) {
      console.error('Testimony error:', error);
    }
  }

  async function handleTestifyCross() {
    try {
      const response = await fetch(`/api/games/${gameId}/trial/match`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) console.error('Cross-examination failed');
    } catch (error) {
      console.error('Cross-examination error:', error);
    }
  }

  async function handleChallenge() {
    try {
      const response = await fetch(`/api/games/${gameId}/trial/duel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      if (!response.ok) console.error('Challenge failed');
    } catch (error) {
      console.error('Challenge error:', error);
    }
  }

  async function handlePlea() {
    try {
      const response = await fetch(`/api/games/${gameId}/trial/plea`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision: 'take' }),
      });
      if (!response.ok) console.error('Plea failed');
    } catch (error) {
      console.error('Plea error:', error);
    }
  }

  async function handlePleaDecline() {
    try {
      const response = await fetch(`/api/games/${gameId}/trial/plea`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ decision: 'decline' }),
      });
      if (!response.ok) console.error('Plea decline failed');
    } catch (error) {
      console.error('Plea decline error:', error);
    }
  }

  function handlePhaseTimeout() {
    // Auto-skip on timeout
    handleSkip();
  }
</script>

<div class="game-page">
  <TopBanner
    gameState={$gameState}
    onTimeOut={handlePhaseTimeout}
  />

  <div class="play-area">
    <div class="opponent-zones">
      <OpponentZonesContainer />
    </div>

    <div class="central-section">
      <CentralArea
        onDeckClick={handleDeckClick}
        onDiscardClick={handleDiscardClick}
      />
    </div>

    <div class="your-zone">
      <YourCardsZone onCardClick={handleCardClick} />
    </div>
  </div>

  <RightPanel
    onSkip={handleSkip}
    onTestifyFirst={handleTestifyFirst}
    onTestifyCross={handleTestifyCross}
    onChallenge={handleChallenge}
    onPlea={handlePlea}
    onPleaDecline={handlePleaDecline}
  />
</div>

<style>
  :global(html, body) {
    margin: 0;
    padding: 0;
    height: 100%;
    width: 100%;
  }

  :global(body) {
    background: var(--color-bg);
    overflow: hidden;
  }

  .game-page {
    display: grid;
    grid-template-columns: 1fr 320px;
    grid-template-rows: auto 1fr;
    height: 100vh;
    width: 100vw;
    background: var(--color-bg);
    overflow: hidden;
  }

  TopBanner {
    grid-column: 1 / -1;
    grid-row: 1;
    flex-shrink: 0;
  }

  .play-area {
    grid-column: 1;
    grid-row: 2;
    display: grid;
    grid-template-columns: 1fr;
    grid-template-rows: 2fr 1fr 1fr;
    gap: var(--spacing-lg);
    padding: var(--spacing-lg);
    overflow: hidden;
    min-height: 0;
    min-width: 0;
  }

  .opponent-zones {
    grid-column: 1;
    grid-row: 1;
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    grid-template-rows: repeat(2, 1fr);
    gap: var(--spacing-md);
    min-height: 0;
    min-width: 0;
  }

  .central-section {
    grid-column: 1;
    grid-row: 2;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 0;
    min-width: 0;
  }

  .your-zone {
    grid-column: 1;
    grid-row: 3;
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 0;
    min-width: 0;
  }

  :global(.right-panel) {
    grid-column: 2;
    grid-row: 2 / -1;
    overflow-y: auto;
    flex-shrink: 0;
  }

  @media (max-width: 1024px) {
    .game-page {
      grid-template-columns: 1fr;
      grid-template-rows: auto 1fr auto;
    }

    .play-area {
      grid-column: 1;
      grid-row: 2;
      grid-template-columns: 1fr;
      grid-template-rows: 2fr 1fr 1fr;
    }

    .opponent-zones {
      grid-column: 1;
      grid-row: 1;
      grid-template-columns: repeat(2, 1fr);
      grid-template-rows: repeat(2, 1fr);
    }

    .central-section {
      grid-column: 1;
      grid-row: 2;
    }

    .your-zone {
      grid-column: 1;
      grid-row: 3;
    }

    :global(.right-panel) {
      grid-column: 1;
      grid-row: 3;
      max-height: auto;
      overflow: visible;
      flex-direction: column;
    }
  }

  @media (max-width: 768px) {
    .play-area {
      padding: var(--spacing-md);
      gap: var(--spacing-md);
      grid-template-rows: 1.5fr 1fr 1fr;
    }

    .opponent-zones {
      gap: var(--spacing-sm);
    }
  }
</style>