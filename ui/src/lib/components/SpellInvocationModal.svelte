<script lang="ts">
	import { gameState } from '$lib/stores/gameState';
	import { SUIT_LABELS, SUIT_COLORS, CardRank } from '$lib/constants/cards';
	import { getPowerName } from '$lib/config';

	interface Props {
		drawnCard: { rank: string; suit: string } | null;
		onInvoke?: (slotIndex?: number, targetId?: string, targetIndex?: number) => void;
		onDecline?: () => void;
		onDecreeSwap?: (swap: boolean, ownSlot?: number) => void;
	}

	let { drawnCard, onInvoke, onDecline, onDecreeSwap }: Props = $props();

	let selectedOwnSlot: number | null = $state(null);
	let selectedTargetSlot: number | null = $state(null);
	let selectedTargetId: string | null = $state(null);
	let decreeStage: 'peek' | 'swap' = $state('peek');

	function getPowerType(): string {
		if (!drawnCard) return '';
		const rank = drawnCard.rank;
		if (rank === '7' || rank === '8') return 'glance';
		if (rank === '9' || rank === '10') return 'spy';
		if (rank === 'J') return 'smuggle';
		if (rank === 'Q') return 'decree';
		return '';
	}

	function getSuitSymbol(suit: string): string {
		return SUIT_LABELS[suit as keyof typeof SUIT_LABELS];
	}

	function getSuitColor(suit: string): string {
		return SUIT_COLORS[suit as keyof typeof SUIT_COLORS];
	}

	function handleYourSlotClick(slotIndex: number) {
		const power = getPowerType();

		if (power === 'glance') {
			onInvoke?.(slotIndex);
		} else if (power === 'smuggle') {
			if (selectedOwnSlot === null) {
				selectedOwnSlot = slotIndex;
			} else {
				onInvoke?.(selectedOwnSlot, selectedTargetId, selectedTargetSlot);
				resetSelection();
			}
		} else if (power === 'decree' && decreeStage === 'swap') {
			onDecreeSwap?.(true, slotIndex);
		}
	}

	function handleOpponentSlotClick(targetId: string, slotIndex: number) {
		const power = getPowerType();

		if (power === 'spy') {
			onInvoke?.(undefined, targetId, slotIndex);
		} else if (power === 'smuggle') {
			if (selectedOwnSlot === null) {
				selectedTargetId = targetId;
				selectedTargetSlot = slotIndex;
			} else {
				onInvoke?.(selectedOwnSlot, targetId, slotIndex);
				resetSelection();
			}
		} else if (power === 'decree' && decreeStage === 'peek') {
			selectedTargetId = targetId;
			selectedTargetSlot = slotIndex;
			decreeStage = 'swap';
		}
	}

	function handleDecreeSwapDecline() {
		onDecreeSwap?.(false, undefined);
		resetSelection();
	}

	function resetSelection() {
		selectedOwnSlot = null;
		selectedTargetSlot = null;
		selectedTargetId = null;
		decreeStage = 'peek';
	}

	const powerType = $derived(getPowerType());
	const powerName = $derived(drawnCard ? getPowerName(drawnCard.rank as CardRank) : '');
</script>

<div class="spell-modal-overlay">
	<div class="spell-modal">
		<div class="spell-header">
			<div class="spell-title">{powerName}</div>
			<div class="spell-card" style="color: {getSuitColor(drawnCard?.suit || '')}">
				<div class="spell-rank">{drawnCard?.rank[0]}</div>
				<div class="spell-suit">{getSuitSymbol(drawnCard?.suit || '')}</div>
			</div>
		</div>

		<div class="spell-instructions">
			{#if powerType === 'glance'}
				<p>Select one of your card slots to peek</p>
			{:else if powerType === 'spy'}
				<p>Select an opponent's card to peek</p>
			{:else if powerType === 'smuggle'}
				{#if selectedOwnSlot === null}
					<p>Click one of your card slots</p>
				{:else}
					<p>Click an opponent's card to swap</p>
				{/if}
			{:else if powerType === 'decree'}
				{#if decreeStage === 'peek'}
					<p>Click an opponent's card to peek</p>
				{:else}
					<p>Click one of your cards to swap, or decline</p>
				{/if}
			{/if}
		</div>

		{#if powerType === 'glance' || powerType === 'smuggle'}
			<div class="slots-container">
				<div class="your-slots">
					<div class="slots-label">Your Cards</div>
					<div class="slots-grid">
						{#each [0, 1, 2, 3] as idx}
							<button
								class="slot-btn"
								class:selected={selectedOwnSlot === idx}
								onclick={() => handleYourSlotClick(idx)}
							>
								Slot {idx + 1}
							</button>
						{/each}
					</div>
				</div>
			</div>
		{/if}

		{#if powerType === 'spy' || powerType === 'smuggle' || (powerType === 'decree' && decreeStage === 'peek')}
			<div class="opponent-slots">
				<div class="slots-label">Opponent Cards</div>
				{#each $gameState.opponents as opponent}
					<div class="opponent-group">
						<div class="opponent-name">{opponent.player_name}</div>
						<div class="slots-grid">
							{#each [0, 1, 2, 3] as idx}
								<button
									class="slot-btn"
									class:selected={selectedTargetId === opponent.player_id &&
										selectedTargetSlot === idx}
									onclick={() => handleOpponentSlotClick(opponent.player_id, idx)}
								>
									Slot {idx + 1}
								</button>
							{/each}
						</div>
					</div>
				{/each}
			</div>
		{/if}

		{#if powerType === 'decree' && decreeStage === 'swap'}
			<div class="your-slots">
				<div class="slots-label">Your Cards (to swap)</div>
				<div class="slots-grid">
					{#each [0, 1, 2, 3] as idx}
						<button class="slot-btn" onclick={() => handleYourSlotClick(idx)}>
							Slot {idx + 1}
						</button>
					{/each}
				</div>
			</div>
		{/if}

		<div class="spell-buttons">
			{#if powerType === 'decree' && decreeStage === 'swap'}
				<button class="btn btn-secondary" onclick={handleDecreeSwapDecline}> Decline Swap </button>
			{:else}
				<button class="btn btn-secondary" onclick={onDecline}> Skip Spell </button>
			{/if}
		</div>
	</div>
</div>

<style>
	.spell-modal-overlay {
		position: fixed;
		inset: 0;
		background: rgba(0, 0, 0, 0.5);
		display: flex;
		align-items: center;
		justify-content: center;
		z-index: 1000;
		animation: fadeIn 0.2s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	.spell-modal {
		background: var(--color-bg-card, #ffffff);
		border-radius: var(--radius-md, 8px);
		padding: 24px;
		max-width: 600px;
		width: 90vw;
		max-height: 90vh;
		overflow-y: auto;
		box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
	}

	.spell-header {
		display: flex;
		gap: 16px;
		align-items: center;
		margin-bottom: 24px;
	}

	.spell-title {
		font-size: 20px;
		font-weight: 700;
		color: var(--color-text, #333);
	}

	.spell-card {
		width: 80px;
		height: 112px;
		background: linear-gradient(135deg, #ffffff, #f3f4f6);
		border: 1px solid var(--color-border, #ddd);
		border-radius: 6px;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.spell-rank {
		font-size: 18px;
		font-weight: 700;
		line-height: 1;
	}

	.spell-suit {
		font-size: 16px;
		margin-top: 4px;
	}

	.spell-instructions {
		margin-bottom: 20px;
		padding: 12px;
		background: var(--color-bg, #f5f5f5);
		border-radius: 6px;
		border-left: 3px solid var(--color-primary, #007bff);
	}

	.spell-instructions p {
		margin: 0;
		font-size: 14px;
		color: var(--color-text, #333);
	}

	.slots-container {
		margin-bottom: 20px;
	}

	.your-slots,
	.opponent-slots {
		margin-bottom: 16px;
	}

	.slots-label {
		font-size: 13px;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.5px;
		color: var(--color-text-light, #666);
		margin-bottom: 8px;
	}

	.opponent-group {
		margin-bottom: 12px;
	}

	.opponent-name {
		font-size: 12px;
		font-weight: 600;
		color: var(--color-text-light, #666);
		margin-bottom: 6px;
		padding-left: 4px;
	}

	.slots-grid {
		display: grid;
		grid-template-columns: repeat(4, 1fr);
		gap: 8px;
	}

	.slot-btn {
		padding: 10px 12px;
		background: var(--color-bg, #f5f5f5);
		border: 1px solid var(--color-border, #ddd);
		border-radius: 4px;
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		color: var(--color-text, #333);
	}

	.slot-btn:hover {
		background: var(--color-primary-light, #e7f1ff);
		border-color: var(--color-primary, #007bff);
	}

	.slot-btn.selected {
		background: var(--color-primary, #007bff);
		color: white;
		border-color: var(--color-primary, #007bff);
	}

	.spell-buttons {
		display: flex;
		gap: 12px;
		margin-top: 24px;
	}

	.btn {
		flex: 1;
		padding: 10px 16px;
		border: none;
		border-radius: 4px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		font-size: 14px;
	}

	.btn-secondary {
		background: var(--color-text-light, #666);
		color: white;
	}

	.btn-secondary:hover {
		background: var(--color-text, #333);
	}
</style>
