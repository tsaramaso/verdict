<!-- src/lib/components/TopBanner.svelte -->
<script lang="ts">
  import Timer from './Timer.svelte';
  import { PHASE_LABELS, UI, GAME_PHASES } from '$lib/config';

  interface GameState {
    phase: string;
    round_number: number;
    current_player: string;
    self: {
      player_id: string;
    };
  }

  interface Props {
    gameState: GameState;
    onTimeOut?: () => void;
  }

  let { gameState, onTimeOut }: Props = $props();

  const phaseLabel = $derived(PHASE_LABELS[gameState.phase] || 'Unknown');
  const isAutoAdvance = $derived(UI.autoAdvancePhases.includes(gameState.phase));

  function getPhaseDescription(
    phase: string,
    currentPlayer: string,
    myPlayerId: string
  ): string {
    const isMyTurn = currentPlayer === myPlayerId;
    switch (phase) {
      case GAME_PHASES.TURN_START:
        return 'Starting new round...';
      case GAME_PHASES.DRAWING:
        return isMyTurn ? 'Your turn to draw' : 'Waiting for draw...';
      case GAME_PHASES.AWAITING_ACTION:
        return isMyTurn ? 'Choose your action' : 'Waiting for action...';
      case GAME_PHASES.AWAITING_SPELL_INVOCATION:
        return isMyTurn ? 'Use power card?' : 'Waiting for power use...';
      case GAME_PHASES.AWAITING_QUICK_DISCARD:
        return 'Discard matching ranks...';
      case GAME_PHASES.AWAITING_CALL_WINDOW:
        return 'Call window open';
      case GAME_PHASES.AWAITING_MATCH_WINDOW:
        return 'Match window open';
      case GAME_PHASES.AWAITING_DUEL_WINDOW:
        return 'Duel happening...';
      case GAME_PHASES.AWAITING_FINAL_PLEA_WINDOW:
        return 'Final plea window...';
      case GAME_PHASES.ROUND_OVER:
        return 'Round ending...';
      case GAME_PHASES.GAME_OVER:
        return 'Game over!';
      default:
        return '';
    }
  }

  const description = $derived(
    getPhaseDescription(gameState.phase, gameState.current_player, gameState.self.player_id)
  );
</script>

<div class="top-banner">
  <div class="top-banner__left">
    <div class="phase-info">
      <div class="phase-info__round">Round {gameState.round_number}</div>
      <div class="phase-info__phase">{phaseLabel}</div>
    </div>
  </div>

  <div class="top-banner__center">
    <div class="phase-description">{description}</div>
  </div>

  <div class="top-banner__right">
    {#if !isAutoAdvance}
      <Timer phase={gameState.phase} {onTimeOut} />
    {:else}
      <div class="auto-advance-indicator">
        <span>Auto-advancing...</span>
      </div>
    {/if}
  </div>
</div>

<style>
  .top-banner {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
    gap: var(--spacing-lg);
    align-items: center;
    padding: var(--spacing-md) var(--spacing-lg);
    background: var(--color-bg-card);
    border-bottom: 1px solid var(--color-border);
    box-shadow: var(--shadow-sm);
  }

  .top-banner__left,
  .top-banner__right {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .top-banner__center {
    text-align: center;
  }

  .phase-info {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }

  .phase-info__round {
    font-size: var(--font-size-sm);
    color: var(--color-text-light);
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .phase-info__phase {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
  }

  .phase-description {
    font-size: var(--font-size-base);
    color: var(--color-text);
    font-weight: var(--font-weight-medium);
  }

  .auto-advance-indicator {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    color: var(--color-text-light);
    font-size: var(--font-size-sm);
  }

  .auto-advance-indicator::after {
    content: '';
    display: inline-block;
    width: 8px;
    height: 8px;
    background: var(--color-success);
    border-radius: 50%;
    animation: pulse 1.5s ease-in-out infinite;
  }

  @keyframes pulse {
    0%, 100% {
      opacity: 1;
      transform: scale(1);
    }
    50% {
      opacity: 0.5;
      transform: scale(1.2);
    }
  }

  @media (max-width: 768px) {
    .top-banner {
      grid-template-columns: 1fr;
      gap: var(--spacing-md);
    }

    .top-banner__left,
    .top-banner__right {
      order: 2;
    }

    .top-banner__center {
      order: 1;
    }
  }
</style>
