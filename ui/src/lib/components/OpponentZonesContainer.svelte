<!-- src/lib/components/OpponentZonesContainer.svelte -->
<script lang="ts">
	import { gameState } from '$lib/stores/gameState';
	import OpponentCardsZone from './OpponentCardsZone.svelte';
	import { LAYOUT } from '$lib/config';

	interface Position {
		x: number;
		y: number;
		angle: number;
	}

	function getOpponentPositions(numOpponents: number): Position[] {
		const positions: Position[] = [];

		if (numOpponents === 0) return positions;

		// Get responsive radius based on viewport
		let radius = LAYOUT.circleRadius;
		if (typeof window !== 'undefined') {
			const width = window.innerWidth;
			if (width < 768) {
				radius = LAYOUT.circleRadiusMobile;
			} else if (width < 1024) {
				radius = LAYOUT.circleRadiusTablet;
			}
		}

		// Distribute opponents around circle, excluding player position (270° / bottom)
		// Start from top (0°) and go clockwise
		const availableAngles = 360 - 60; // Reserve 60° for player zone
		const angleStep = availableAngles / numOpponents;

		for (let i = 0; i < numOpponents; i++) {
			let angle = i * angleStep; // Start from top, 0°

			// Skip the bottom area (240° to 300°) reserved for player
			if (angle >= 240) {
				angle += 60;
			}

			const radians = (angle * Math.PI) / 180;
			const x = Math.cos(radians) * radius;
			const y = Math.sin(radians) * radius;

			positions.push({ x, y, angle });
		}

		return positions;
	}

	let windowWidth = $state(typeof window !== 'undefined' ? window.innerWidth : 1024);

	$effect(() => {
		if (typeof window === 'undefined') return;

		const handleResize = () => {
			windowWidth = window.innerWidth;
		};

		window.addEventListener('resize', handleResize);
		return () => window.removeEventListener('resize', handleResize);
	});

	const positions = $derived(getOpponentPositions($gameState.opponents.length));
</script>

<div class="opponent-zones-container">
	{#each $gameState.opponents as opponent, idx}
		{@const pos = positions[idx]}
		<div class="opponent-zone" style="--x: {pos.x}px; --y: {pos.y}px;">
			<OpponentCardsZone {opponent} />
		</div>
	{/each}
</div>

<style>
	.opponent-zones-container {
		position: relative;
		width: 100%;
		height: 500px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.opponent-zone {
		position: absolute;
		left: 50%;
		top: 50%;
		transform: translate(calc(-50% + var(--x)), calc(-50% + var(--y)));
		z-index: 10;
	}

	@media (max-width: 1024px) {
		.opponent-zones-container {
			height: 400px;
		}
	}

	@media (max-width: 768px) {
		.opponent-zones-container {
			height: 300px;
			display: grid;
			grid-template-columns: 1fr 1fr;
			gap: var(--spacing-md);
			position: relative;
		}

		.opponent-zone {
			position: static;
			transform: none;
			left: auto;
			top: auto;
		}
	}
</style>
