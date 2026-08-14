<!-- src/lib/components/RightPanel.svelte -->
<script lang="ts">
  import LeaderboardPanel from './LeaderboardPanel.svelte';
  import ButtonZone from './ButtonZone.svelte';

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
</script>

<aside class="right-panel">
  <LeaderboardPanel />

  <ButtonZone
    {onSkip}
    {onTestifyFirst}
    {onTestifyCross}
    {onChallenge}
    {onPlea}
    {onPleaDecline}
  />

  <!-- Tooltip panel placeholder for Phase 2 -->
  <div class="tooltip-panel">
    <div class="tooltip-placeholder">💡 Tips (Coming Soon)</div>
  </div>
</aside>

<style>
  .right-panel {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-md);
    padding: var(--spacing-md);
    background: var(--color-bg);
    border-radius: var(--radius-md);
    overflow-y: auto;
    overflow-x: hidden;
    flex-shrink: 0;
  }

  .tooltip-panel {
    padding: var(--spacing-md);
    background: var(--color-bg-card);
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border);
  }

  .tooltip-placeholder {
    text-align: center;
    color: var(--color-text-light);
    font-size: var(--font-size-xs);
    font-style: italic;
  }

  @media (max-width: 1024px) {
    .right-panel {
      flex-direction: row;
      gap: var(--spacing-lg);
      overflow: auto;
      align-items: center;
      justify-content: space-around;
    }

    .tooltip-panel {
      display: none;
    }
  }

  @media (max-width: 768px) {
    .right-panel {
      flex-direction: column;
      gap: var(--spacing-md);
    }
  }
</style>
