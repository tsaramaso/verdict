<!-- src/lib/components/BottomBar.svelte -->
<script lang="ts">
	import {
		gameState,
		canTestifyFirst,
		canTestifyCross,
		canChallenge,
		canPlea
	} from '$lib/stores/gameState';
	import { GAME_PHASES } from '$lib/config';

	interface Props {
		onSkip?: () => void;
		onTestifyFirst?: () => void;
		onTestifyCross?: () => void;
		onChallenge?: () => void;
		onPlea?: () => void;
	}

	let { onSkip, onTestifyFirst, onTestifyCross, onChallenge, onPlea }: Props = $props();

	// Button enabled logic based on phase and trial state
	const canTestifyFirstEnabled = $derived(
		$canTestifyFirst && $gameState.phase === GAME_PHASES.AWAITING_CALL_WINDOW
	);

	const canTestifyCrossEnabled = $derived(
		$canTestifyCross && $gameState.phase === GAME_PHASES.AWAITING_MATCH_WINDOW
	);

	const canChallengeEnabled = $derived(
		$canChallenge && $gameState.phase === GAME_PHASES.AWAITING_DUEL_WINDOW
	);

	const canPleaEnabled = $derived(
		$canPlea && $gameState.phase === GAME_PHASES.AWAITING_FINAL_PLEA_WINDOW
	);

	const canSkipEnabled = $derived(
		([
			GAME_PHASES.AWAITING_CALL_WINDOW,
			GAME_PHASES.AWAITING_MATCH_WINDOW,
			GAME_PHASES.AWAITING_DUEL_WINDOW,
			GAME_PHASES.AWAITING_FINAL_PLEA_WINDOW,
			GAME_PHASES.AWAITING_ACTION,
			GAME_PHASES.AWAITING_QUICK_DISCARD
		] as const).includes($gameState.phase as any)
	);

	// Context-aware TESTIMONY handler
	function handleTestimony() {
		if ($gameState.phase === GAME_PHASES.AWAITING_CALL_WINDOW) {
			onTestifyFirst?.();
		} else if ($gameState.phase === GAME_PHASES.AWAITING_MATCH_WINDOW) {
			onTestifyCross?.();
		}
	}

	const testifyButtonEnabled = $derived(
		canTestifyFirstEnabled || canTestifyCrossEnabled
	);
</script>

<div class="bottom-bar">
	<button class="btn btn--primary" onclick={handleTestimony} disabled={!testifyButtonEnabled}>
		TESTIMONY
	</button>

	<button class="btn btn--primary" onclick={onChallenge} disabled={!canChallengeEnabled}>
		CHALLENGE
	</button>

	<button class="btn btn--primary" onclick={onPlea} disabled={!canPleaEnabled}> TAKE PLEA </button>

	<button class="btn btn--secondary" onclick={onSkip} disabled={!canSkipEnabled}>
		SKIP / PASS
	</button>
</div>

<style>
	.bottom-bar {
		display: flex;
		gap: var(--spacing-md);
		padding: var(--spacing-md) var(--spacing-lg);
		background: var(--color-bg-card);
		border-top: 1px solid var(--color-border);
		box-shadow: var(--shadow-sm);
		justify-content: center;
		align-items: center;
		flex-shrink: 0;
		flex-wrap: wrap;
	}

	.btn {
		padding: var(--spacing-sm) var(--spacing-lg);
		border: none;
		border-radius: var(--radius-sm);
		font-size: var(--font-size-sm);
		font-weight: var(--font-weight-bold);
		cursor: pointer;
		transition: all 0.2s ease;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		min-width: 120px;
	}

	.btn--primary {
		background: var(--color-primary);
		color: white;
		box-shadow: var(--shadow-md);
	}

	.btn--primary:hover:not(:disabled) {
		background: var(--color-primary-dark);
		transform: translateY(-2px);
		box-shadow: 0 6px 12px rgba(0, 123, 255, 0.3);
	}

	.btn--primary:active:not(:disabled) {
		transform: translateY(0);
	}

	.btn--primary:disabled {
		background: #6b7280;
		opacity: 0.6;
		box-shadow: none;
	}

	.btn--secondary {
		background: var(--color-bg);
		color: var(--color-text);
		border: 1px solid var(--color-border);
	}

	.btn--secondary:hover:not(:disabled) {
		background: var(--color-border-light);
		border-color: var(--color-text-light);
	}

	.btn--secondary:active:not(:disabled) {
		background: var(--color-border);
	}

	.btn--secondary:disabled {
		background: var(--color-bg);
		color: #9ca3af;
		border-color: #d1d5db;
		opacity: 0.5;
	}

	.btn:disabled {
		cursor: not-allowed;
		transform: none !important;
	}

	.btn:disabled:hover {
		transform: none !important;
	}

	@media (max-width: 768px) {
		.bottom-bar {
			flex-direction: column;
			gap: var(--spacing-sm);
			padding: var(--spacing-md);
		}

		.btn {
			min-width: 100%;
		}
	}
</style>