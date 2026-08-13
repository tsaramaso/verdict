<!-- src/lib/components/ButtonZone.svelte -->
<script lang="ts">
  import {
    gameState,
    canTestifyFirst,
    canTestifyCross,
    canChallenge,
    canPlea,
  } from '$lib/stores/gameState';
  import { GAME_PHASES } from '$lib/config';

  interface Props {
    onSkip?: () => void;
    onTestifyFirst?: () => void;
    onTestifyCross?: () => void;
    onChallenge?: () => void;
    onPlea?: () => void;
    onPleaDecline?: () => void;
  }

  let {
    onSkip,
    onTestifyFirst,
    onTestifyCross,
    onChallenge,
    onPlea,
    onPleaDecline,
  }: Props = $props();

  // Button visibility logic based on phase and trial state
  const showTestifyFirst = $derived(
    $canTestifyFirst && $gameState.phase === GAME_PHASES.AWAITING_CALL_WINDOW
  );

  const showTestifyCross = $derived(
    $canTestifyCross && $gameState.phase === GAME_PHASES.AWAITING_MATCH_WINDOW
  );

  const showChallenge = $derived(
    $canChallenge && $gameState.phase === GAME_PHASES.AWAITING_DUEL_WINDOW
  );

  const showPlea = $derived(
    $canPlea && $gameState.phase === GAME_PHASES.AWAITING_FINAL_PLEA_WINDOW
  );

  const showSkip = $derived(
    [
      GAME_PHASES.AWAITING_CALL_WINDOW,
      GAME_PHASES.AWAITING_MATCH_WINDOW,
      GAME_PHASES.AWAITING_DUEL_WINDOW,
      GAME_PHASES.AWAITING_FINAL_PLEA_WINDOW,
      GAME_PHASES.AWAITING_ACTION,
      GAME_PHASES.AWAITING_QUICK_DISCARD,
    ].includes($gameState.phase)
  );
</script>

<div class="button-zone">
  {#if showTestifyFirst}
    <button class="btn btn--primary" onclick={onTestifyFirst}>
      🎤 TESTIMONY
    </button>
    <button class="btn btn--secondary" onclick={onSkip}>
      PASS
    </button>
  {:else if showTestifyCross}
    <button class="btn btn--primary" onclick={onTestifyCross}>
      🎤 CROSS-EXAMINE
    </button>
    <button class="btn btn--secondary" onclick={onSkip}>
      PASS
    </button>
  {:else if showChallenge}
    <button class="btn btn--primary" onclick={onChallenge}>
      ⚔️ CHALLENGE
    </button>
    <button class="btn btn--secondary" onclick={onSkip}>
      PASS
    </button>
  {:else if showPlea}
    <button class="btn btn--primary" onclick={onPlea}>
      🙏 TAKE PLEA
    </button>
    <button class="btn btn--secondary" onclick={onPleaDecline}>
      DECLINE
    </button>
  {:else if showSkip}
    <button class="btn btn--secondary" onclick={onSkip}>
      SKIP / PASS
    </button>
  {/if}
</div>

<style>
  .button-zone {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
    padding: var(--spacing-md);
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
  }

  .btn {
    padding: var(--spacing-sm) var(--spacing-md);
    border: none;
    border-radius: var(--radius-sm);
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-bold);
    cursor: pointer;
    transition: all 0.2s ease;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  .btn--primary {
    background: var(--color-primary);
    color: white;
    box-shadow: var(--shadow-md);
  }

  .btn--primary:hover {
    background: var(--color-primary-dark);
    transform: translateY(-2px);
    box-shadow: 0 6px 12px rgba(0, 123, 255, 0.3);
  }

  .btn--primary:active {
    transform: translateY(0);
  }

  .btn--secondary {
    background: var(--color-bg);
    color: var(--color-text);
    border: 1px solid var(--color-border);
  }

  .btn--secondary:hover {
    background: var(--color-border-light);
    border-color: var(--color-text-light);
  }

  .btn--secondary:active {
    background: var(--color-border);
  }

  .btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none !important;
  }

  .btn:disabled:hover {
    background: inherit;
    box-shadow: none;
  }
</style>
