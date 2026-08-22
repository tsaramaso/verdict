<script lang="ts">
	import { onMount } from 'svelte';
	import { gameState, setCurrentPlayerId } from '$lib/stores/gameState';
	import RightPanel from './RightPanel.svelte';
	import BottomBar from './BottomBar.svelte';
	import PlayArea from './PlayArea.svelte';
	import SpellInvocationModal from './SpellInvocationModal.svelte';
	import RoundOverModal from './RoundOverModal.svelte';
	import GameOverModal from './GameOverModal.svelte';
	import { transformCardList, transformRank, transformSuit } from '$lib/utils/cardTransform';
	import { GAME_PHASES } from '$lib/config';
	import * as gameActions from '$lib/actions/gameActions';
	import { getHardcodedBaseRules } from '$lib/utils/baseRules';

	interface Props {
		playerId: string;
		gameId: string;
	}

	let { playerId, gameId }: Props = $props();

	let drawnCard: { rank: string; suit: string } | null = $state(null);
	let drawnCardSource: 'deck' | 'discard' | null = $state(null);
	let ws: WebSocket | null = $state(null);

	onMount(() => {
		setCurrentPlayerId(playerId);
		initWebSocket();
	});

	function initWebSocket() {
		const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
		const token = getTokenFromStorage();
		const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
		const apiHost = new URL(apiUrl).host;
		const url = `${protocol}//${apiHost}/ws/games/${gameId}?token=${token}`;

		console.log('[WS] Connecting to:', url);
		ws = new WebSocket(url);

		ws.onopen = () => console.log('[WS] Connected');
		ws.onmessage = (event) => handleWebSocketMessage(event.data);
		ws.onerror = (error) => console.error('[WS] Error:', error);
		ws.onclose = () => console.log('[WS] Closed, will auto-reconnect');
	}

	function handleWebSocketMessage(data: string) {
		console.log('[GamePage] WS message received:', data.substring(0, 200) + '...');
		const message = JSON.parse(data);

		if (message.type === 'game_state' || message.type === 'game_state_update') {
			console.log('[GamePage] Game state update, phase:', message.game.phase);
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

			const phaseUppercase = message.game.phase.toUpperCase();

			gameState.set({
				game_id: message.game.game_id,
				phase: phaseUppercase,
				current_player: message.game.current_player,
				round_number: message.game.round_number,
				self: transformedSelf,
				opponents: transformedOpponents,
				my_opponent_knowledge: message.my_opponent_knowledge,
				trial: message.trial,
				discard_pile: transformedDiscard,
				rules: message.rules || getHardcodedBaseRules()
			});

			if (phaseUppercase === GAME_PHASES.TURN_START) {
				setTimeout(async () => {
					await gameActions.advancePhase(gameId);
				}, 3000);
			}
		}
	}

	function getTokenFromStorage(): string {
		const token = localStorage.getItem('auth_token');
		if (!token) throw new Error('No auth token found');
		return token;
	}

	async function handleDrawDeck() {
		console.log('[GamePage] Deck clicked, gameId:', gameId);
		const result = await gameActions.drawFromDeck(gameId);
		console.log('[GamePage] Deck draw result:', result);
		if (result?.drawn_card) {
			console.log('[GamePage] Card drawn:', result.drawn_card);
			drawnCard = result.drawn_card;
			drawnCardSource = 'deck';
		} else {
			console.error('[GamePage] No card drawn from deck');
		}
	}

	async function handleDrawDiscard() {
		console.log('[GamePage] Discard clicked, gameId:', gameId);
		const result = await gameActions.drawFromDiscard(gameId);
		console.log('[GamePage] Discard draw result:', result);
		if (result?.drawn_card) {
			console.log('[GamePage] Card drawn:', result.drawn_card);
			drawnCard = result.drawn_card;
			drawnCardSource = 'discard';
		} else {
			console.error('[GamePage] No card drawn from discard');
		}
	}

	async function handleAction(choice: 'discard_immediate' | 'swap' | 'pass_back', slotIndex?: number) {
		if (choice === 'discard_immediate') {
			await gameActions.discardImmediate(gameId, drawnCardSource || 'deck');
		} else if (choice === 'swap' && slotIndex !== undefined) {
			await gameActions.swapCard(gameId, slotIndex, drawnCardSource || 'deck');
		} else if (choice === 'pass_back') {
			await gameActions.passBack(gameId);
		}
		clearDrawnCard();
	}

	async function handlePowerInvoke(
		ownSlotIndex?: number,
		targetOwner?: string,
		targetIndex?: number
	) {
		await gameActions.invokePower(gameId, ownSlotIndex, targetOwner, targetIndex);
		clearDrawnCard();
	}

	async function handlePowerDecline() {
		await gameActions.declinePower(gameId);
		clearDrawnCard();
	}

	async function handlePowerDecreeSwap(swap: boolean, ownSlotIndex?: number) {
		await gameActions.decreeSwap(gameId, swap, ownSlotIndex);
		if (swap) clearDrawnCard();
	}

	async function handleQuickDiscard(slotIndex: number) {
		await gameActions.quickDiscard(gameId, slotIndex);
	}

	async function handleTestifyFirst() {
		await gameActions.testifyFirst(gameId);
	}

	async function handleTestifyCross() {
		await gameActions.testifyCross(gameId);
	}

	async function handleChallenge() {
		await gameActions.challenge(gameId);
	}

	async function handlePlea() {
		await gameActions.takePlea(gameId);
	}

	async function handlePleaDecline() {
		await gameActions.declinePlea(gameId);
	}

	function clearDrawnCard() {
		drawnCard = null;
		drawnCardSource = null;
	}

	// ============================================
	// TIMEOUT FALLBACK HANDLERS
	// ============================================

	async function handleTimeoutDrawing() {
		await gameActions.timeoutDrawing(gameId);
	}

	async function handleTimeoutAction() {
		await gameActions.timeoutAction(gameId, drawnCardSource || 'deck');
		clearDrawnCard();
	}

	async function handleTimeoutSpell() {
		await gameActions.timeoutSpell(gameId);
		clearDrawnCard();
	}

	function getTimeoutHandler() {
		switch ($gameState.phase) {
			case GAME_PHASES.DRAWING:
				return handleTimeoutDrawing;
			case GAME_PHASES.AWAITING_ACTION:
				return handleTimeoutAction;
			case GAME_PHASES.AWAITING_SPELL_INVOCATION:
				return handleTimeoutSpell;
			default:
				return undefined;
		}
	}
</script>

<div class="game-page">
	<PlayArea
		{drawnCard}
		{drawnCardSource}
		onDeckClick={handleDrawDeck}
		onDiscardClick={handleDrawDiscard}
		onAction={handleAction}
		onQuickDiscard={handleQuickDiscard}
		onTestifyFirst={handleTestifyFirst}
		onTestifyCross={handleTestifyCross}
		onChallenge={handleChallenge}
		onPlea={handlePlea}
		onPleaDecline={handlePleaDecline}
	/>

	<RightPanel gameState={$gameState} onTimeOut={getTimeoutHandler()} />

	<BottomBar />

	{#if $gameState.phase === GAME_PHASES.AWAITING_SPELL_INVOCATION && drawnCard}
		<SpellInvocationModal
			{drawnCard}
			onInvoke={handlePowerInvoke}
			onDecline={handlePowerDecline}
			onDecreeSwap={handlePowerDecreeSwap}
		/>
	{/if}

	{#if $gameState.phase === GAME_PHASES.ROUND_OVER}
		<RoundOverModal 
			onAdvance={() => {
				// Auto-advance triggered, game continues via WebSocket
			}}	
		/>
	{/if}

	{#if $gameState.phase === GAME_PHASES.GAME_OVER}
		<GameOverModal 
			onReturnLobby={() => (window.location.href = '/')}
			onPlayAgain={() => (window.location.href = '/lobbies')}
		/>
	{/if}
</div>

<style>
	.game-page {
		display: grid;
		grid-template-columns: 1fr auto;
		grid-template-rows: 1fr;
		gap: 16px;
		padding: 16px;
		height: 100vh;
		background: var(--color-bg, #f5f5f5);
	}
</style>