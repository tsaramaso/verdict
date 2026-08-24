<!-- src/lib/components/Timer.svelte -->
<script lang="ts">
	import { TIMERS } from '$lib/config';
	import type { GamePhase } from '$lib/stores/gameState';

	interface Props {
		phase: GamePhase;
		onTimeOut?: () => void;
	}

	let { phase = 'TURN_START' as GamePhase, onTimeOut }: Props = $props();

	let remainingSeconds = $state(0);
	let timerInterval: ReturnType<typeof setInterval> | null = $state.snapshot(null);

	// Initialize timer whenever phase changes
	$effect(() => {
		// Clear existing timer
		if (timerInterval) {
			clearInterval(timerInterval);
			timerInterval = null;
		}

		// Get duration for this phase (default to 10s)
		const duration = (TIMERS as Record<string, number>)[phase] || 10;
		remainingSeconds = duration;

		// Start countdown
		timerInterval = setInterval(() => {
			remainingSeconds -= 1;

			if (remainingSeconds <= 0) {
				if (timerInterval) {
					clearInterval(timerInterval);
				}
				timerInterval = null;
				if (onTimeOut) {
					onTimeOut();
				}
			}
		}, 1000);

		// Cleanup on unmount
		return () => {
			if (timerInterval) {
				clearInterval(timerInterval);
			}
		};
	});

	function getTimerState() {
		if (remainingSeconds <= TIMERS.TIMER_CRITICAL_THRESHOLD) return 'critical';
		if (remainingSeconds <= TIMERS.TIMER_WARNING_THRESHOLD) return 'warning';
		return 'normal';
	}

	function formatTime(seconds: number): string {
		const mins = Math.floor(seconds / 60);
		const secs = seconds % 60;
		return `${mins}:${secs.toString().padStart(2, '0')}`;
	}

	const timerState = $derived(getTimerState());
	const maxDuration = (TIMERS as Record<string, number>)[phase] || 10;
</script>

<div class={`timer timer--${timerState}`}>
	<div class="timer__display">
		{formatTime(remainingSeconds)}
	</div>
	<div class="timer__bar" style="width: {(remainingSeconds / maxDuration) * 100}%"></div>
</div>

<style>
	.timer {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: var(--spacing-sm);
	}

	.timer__display {
		font-size: var(--font-size-lg);
		font-weight: var(--font-weight-bold);
		font-family: monospace;
		min-width: 60px;
		text-align: center;
	}

	.timer--normal .timer__display {
		color: var(--color-text);
	}

	.timer--warning .timer__display {
		color: var(--color-warning);
		animation: pulse 1s ease-in-out infinite;
	}

	.timer--critical .timer__display {
		color: var(--color-danger);
		animation: pulse 0.5s ease-in-out infinite;
	}

	.timer__bar {
		height: 4px;
		width: 100%;
		background: var(--color-primary);
		border-radius: 2px;
		transition:
			width 1s linear,
			background-color 0.2s ease;
	}

	.timer--warning .timer__bar {
		background-color: var(--color-warning);
	}

	.timer--critical .timer__bar {
		background-color: var(--color-danger);
	}

	@keyframes pulse {
		0%,
		100% {
			opacity: 1;
		}
		50% {
			opacity: 0.6;
		}
	}
</style>
