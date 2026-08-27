<script lang="ts">
	import { onMount } from 'svelte';
	import { gameState, setCurrentPlayerId, isActivePlayer, type Rules } from '$lib/stores/gameState';
	import RightPanel from './RightPanel.svelte';
	import BottomBar from './BottomBar.svelte';
	import PlayArea from './PlayArea.svelte';
	import SpellInvocationModal from './SpellInvocationModal.svelte';
	import RoundOverModal from './RoundOverModal.svelte';
	import GameOverModal from './GameOverModal.svelte';
	import { transformCardList, transformRank, transformSuit } from '$lib/utils/cardTransform';
	import { transformRules } from '$lib/utils/rulesTransform';
	import { GAME_PHASES } from '$lib/config';
	import type { CardRank, CardSuit } from '$lib/constants/cards';
	import * as gameActions from '$lib/actions/gameActions';
	import { getHardcodedBaseRules } from '$lib/utils/baseRules';

	interface Props {
		playerId: string;
		gameId: string;
	}

	let { playerId, gameId }: Props = $props();

	let drawnCard: { rank: CardRank; suit: CardSuit } | null = $state(null);
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
		console.log('[GamePage] WS message received:', data);
		const message = JSON.parse(data);

		if (message.type === 'game_state' || message.type === 'game_state_update') {
			// Handle both old (top-level) and new (wrapped in game object) formats
			const gameInfo = message.game || {
				game_id: message.game_id,
				phase: message.phase,
				current_player: message.current_player,
				round_number: message.round_number
			};
			
			console.log('[GamePage] Game state update, phase:', gameInfo.phase);

			// Extract drawn card from events if present
			if (message.events && message.events.length > 0) {
				const cardDrawnEvent = message.events.find((e: any) => e.type === 'card_drawn');
				if (cardDrawnEvent && cardDrawnEvent.scoped_fields?.true_card) {
					const card = cardDrawnEvent.scoped_fields.true_card;
					drawnCard = {
						rank: transformRank(card.rank),
						suit: transformSuit(card.suit)
					};
					console.log('[GamePage] Extracted drawn card from event:', drawnCard);
				}
			}

			// Check for Last Turn (deck empty)
			const deckEmpty = message.deck?.card_count === 0;
			if (deckEmpty) {
				console.warn('[GamePage] LAST TURN: Deck is empty');
			}

			// Debug: log what self data arrived
			console.log('[GamePage] Self data from WS:', message.self);
			
			const transformedSelf = {
				...message.self,
				hand: [...transformCardList(message.self.hand)]  // Spread to create new array reference
			};
			
			// Debug: log hand changes with detail
			console.log('[GamePage] Hand updated:', transformedSelf.hand);
			transformedSelf.hand.forEach((c, i) => {
				console.log(`  [Slot ${i}]`, {
					known: c?.known,
					rank: c?.rank,
					suit: c?.suit,
					displayRank: c?.rank !== undefined ? c.rank : 'N/A',
					displaySuit: c?.suit !== undefined ? c.suit : 'N/A'
				});
			});

			const transformedOpponents = [...message.opponents.map((opp: any) => ({
				...opp,
				known_cards: opp.known_cards.map((card: any) => ({
					slot: card.slot,
					rank: transformRank(card.rank),
					suit: transformSuit(card.suit)
				}))
			}))];

			const transformedDiscard = {
				...message.discard_pile,
				visible_cards: message.discard_pile.visible_cards.map((card: any) => ({
					rank: transformRank(card.rank),
					suit: transformSuit(card.suit)
				}))
			};

			const phaseUppercase = gameInfo.phase.toUpperCase();

			gameState.set({
				game_id: gameInfo.game_id,
				phase: phaseUppercase,
				current_player: gameInfo.current_player,
				round_number: gameInfo.round_number,
				self: transformedSelf,
				opponents: transformedOpponents,
				my_opponent_knowledge: message.my_opponent_knowledge,
				trial: message.trial,
				discard_pile: transformedDiscard,
				rules: transformRules(message.rules || getHardcodedBaseRules())
			});

			if (phaseUppercase === GAME_PHASES.TURN_START) {
				// Only active player should advance phase after animation delay
				const isActive = $isActivePlayer;
				if (isActive) {
					setTimeout(async () => {
						console.log('[GamePage] Active player advancing phase');
						await gameActions.advancePhase(gameId);
					}, 3000);
				}
			}
		}
	}

	function getTokenFromStorage(): string {
		const token = localStorage.getItem('auth_token');
		if (!token) throw new Error('No auth token found');
		return token;
	}

	function clearDrawnCard() {
		drawnCard = null;
		drawnCardSource = null;
	}

	async function handleDrawDeck() {
		console.log('[GamePage] Deck clicked, gameId:', gameId);
		const result = await gameActions.drawFromDeck(gameId);
		console.log('[GamePage] Deck draw result:', result);
		// Card info comes via WebSocket in game_state_update, not API response
		// The drawnCard will be populated when the WS message updates gameState
		if (!result) {
			console.error('[GamePage] Draw action failed');
		}
	}

	async function handleDrawDiscard() {
		console.log('[GamePage] Discard clicked, gameId:', gameId);
		const result = await gameActions.drawFromDiscard(gameId);
		console.log('[GamePage] Discard draw result:', result);
		// Card info comes via WebSocket in game_state_update, not API response
		// The drawnCard will be populated when the WS message updates gameState
		if (!result) {
			console.error('[GamePage] Draw action failed');
		}
	}

	async function handleAction(
		choice: 'discard_immediate' | 'swap' | 'pass_back',
		slotIndex?: number
	) {
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

	async function handleSkip() {
		// Skip/Pass button handler - different logic per phase
		if ($gameState.phase === GAME_PHASES.AWAITING_SPELL_INVOCATION) {
			await gameActions.declinePower(gameId);
			clearDrawnCard();
		} else if ($gameState.phase === GAME_PHASES.AWAITING_QUICK_DISCARD) {
			// No action, player passes quick discard
			return;
		} else if ($gameState.phase === GAME_PHASES.AWAITING_CALL_WINDOW) {
			// No explicit API call, player just passes
			return;
		} else if ($gameState.phase === GAME_PHASES.AWAITING_MATCH_WINDOW) {
			// No explicit API call, player just passes
			return;
		} else if ($gameState.phase === GAME_PHASES.AWAITING_DUEL_WINDOW) {
			// No explicit API call, player just doesn't challenge
			return;
		} else if ($gameState.phase === GAME_PHASES.AWAITING_FINAL_PLEA_WINDOW) {
			await gameActions.declinePlea(gameId);
		}
	}

	// ============================================
	// SINGLE TIMEOUT DISPATCHER
	// ============================================

	async function handleTimeout() {
		const phase = $gameState.phase;
		console.log('[GamePage] Timer expired for phase:', phase);

		if (phase === GAME_PHASES.DRAWING) {
			await gameActions.timeoutDrawing(gameId);
		} else if (phase === GAME_PHASES.AWAITING_ACTION) {
			await gameActions.timeoutAction(gameId, drawnCardSource || 'deck');
			clearDrawnCard();
		} else if (phase === GAME_PHASES.AWAITING_SPELL_INVOCATION) {
			await gameActions.timeoutSpell(gameId);
			clearDrawnCard();
		} else if (phase === GAME_PHASES.AWAITING_QUICK_DISCARD) {
			await gameActions.timeoutQuickDiscard(gameId);
		} else if (phase === GAME_PHASES.AWAITING_CALL_WINDOW) {
			await gameActions.timeoutTestifyWindow(gameId);
		} else if (phase === GAME_PHASES.AWAITING_MATCH_WINDOW) {
			await gameActions.timeoutTestifyWindow(gameId);
		} else if (phase === GAME_PHASES.AWAITING_DUEL_WINDOW) {
			await gameActions.timeoutDuelWindow(gameId);
		} else if (phase === GAME_PHASES.AWAITING_FINAL_PLEA_WINDOW) {
			await gameActions.timeoutPleaWindow(gameId);
		}
	}
</script>

<div class="game-page">
	<PlayArea
		{drawnCard}
		{drawnCardSource}
		onDeckClick={handleDrawDeck}
		onDiscardDrawClick={handleDrawDiscard}
		onAction={handleAction}
		onQuickDiscard={handleQuickDiscard}
	/>

	<RightPanel gameState={$gameState} onTimeOut={handleTimeout} />

	<BottomBar
		onSkip={handleSkip}
		onTestifyFirst={handleTestifyFirst}
		onTestifyCross={handleTestifyCross}
		onChallenge={handleChallenge}
		onPlea={handlePlea}
	/>

	{#if $gameState.phase === GAME_PHASES.AWAITING_SPELL_INVOCATION && drawnCard}
		<SpellInvocationModal
			{drawnCard}
			{drawnCardSource}
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
