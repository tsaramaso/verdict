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
	import { CardRank, type CardSuit } from '$lib/constants/cards';
	import * as gameActions from '$lib/actions/gameActions';
	import { getHardcodedBaseRules } from '$lib/utils/baseRules';
	import { getLogger } from '$lib/utils/logger';

	const log = getLogger('game');

	interface Props {
		playerId: string;
		gameId: string;
	}

	let { playerId, gameId }: Props = $props();

	let drawnCard: { rank: CardRank; suit: CardSuit } | null = $state(null);
	let drawnCardSource: 'deck' | 'discard_pile' | null = $state(null);
	let ws: WebSocket | null = $state(null);

	// Spell state for coordinating between modal and opponent zone clicks
	let spellSelectedOwnSlot: number | null = $state(null);
	let spellSelectedTargetId: string | undefined = $state(undefined);
	let spellSelectedTargetSlot: number | null = $state(null);
	let spellDecreeStage: 'peek' | 'swap' = $state('peek');

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

		ws = new WebSocket(url);

		ws.onopen = () => log.info('ws_connected');
		ws.onmessage = (event) => handleWebSocketMessage(event.data);
		ws.onerror = (error) => log.error('ws_error', { error: String(error) });
		ws.onclose = () => log.info('ws_closed');
	}

	function handleWebSocketMessage(data: string) {
		const message = JSON.parse(data);

		if (message.type === 'game_state' || message.type === 'game_state_update') {
			// Handle both old (top-level) and new (wrapped in game object) formats
			const gameInfo = message.game || {
				game_id: message.game_id,
				phase: message.phase,
				current_player: message.current_player,
				round_number: message.round_number
			};

			log.debug('Game state update, phase:', gameInfo.phase);

			// Extract draw_source from message (if present)
			if (message.draw_source) {
				drawnCardSource = message.draw_source === 'DrawSource.DECK' ? 'deck' : 'discard_pile';
				log.debug('Set drawnCardSource:', { drawnCardSource });
			}

			// Extract drawn card from events if present
			if (message.events && message.events.length > 0) {
				const cardDrawnEvent = message.events.find((e: any) => e.type === 'card_drawn');
				if (cardDrawnEvent && cardDrawnEvent.scoped_fields?.true_card) {
					const card = cardDrawnEvent.scoped_fields.true_card;
					drawnCard = {
						rank: transformRank(card.rank),
						suit: transformSuit(card.suit)
					};
					log.debug('Extracted drawn card from event:', drawnCard);
				}
			}

			// Check for Last Turn (deck empty)
			const deckEmpty = message.deck?.card_count === 0;
			if (deckEmpty) {
				log.warn('LAST TURN: Deck is empty');
			}

			// Debug: log what self data arrived
			log.debug('Self data from WS:', message.self);

			const transformedSelf = {
				...message.self,
				hand: [...transformCardList(message.self.hand)] // Spread to create new array reference
			};

			// Debug: log raw server data first
			log.debug('RAW message.self.hand from server:', message.self.hand);

			// Debug: log hand changes with detail
			log.debug('hand_updated', {
				slot_count: transformedSelf.hand.length,
				known_slots: transformedSelf.hand.filter((c: any) => c?.known).length
			});

			const transformedOpponents = [
				...message.opponents.map((opp: any) => ({
					...opp,
					known_cards: opp.known_cards.map((card: any) => ({
						slot: card.slot,
						rank: transformRank(card.rank),
						suit: transformSuit(card.suit)
					}))
				}))
			];

			// Log discard pile state
			log.debug('Discard pile:', {
				count: message.discard_pile?.count,
				total_visible: message.discard_pile?.visible_cards?.length,
				last_card:
					message.discard_pile?.visible_cards?.[message.discard_pile.visible_cards.length - 1],
				all_cards: message.discard_pile?.visible_cards
			});

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
						log.debug('Active player advancing phase');
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
		spellSelectedOwnSlot = null;
		spellSelectedTargetId = undefined;
		spellSelectedTargetSlot = null;
		spellDecreeStage = 'peek';
	}

	function getPowerType(): string {
		if (!drawnCard) return '';
		const rank = drawnCard.rank;
		if (rank === CardRank.SEVEN || rank === CardRank.EIGHT) return 'glance';
		if (rank === CardRank.NINE || rank === CardRank.TEN) return 'spy';
		if (rank === CardRank.JACK) return 'smuggle';
		if (rank === CardRank.QUEEN) return 'decree';
		return '';
	}

	async function handleOpponentZoneClick(opponentId: string, slotIndex: number) {
		const power = getPowerType();
		log.debug('opponent_card_clicked', { power, opponentId, slotIndex, spellSelectedOwnSlot });

		if (power === 'spy') {
			await gameActions.invokePower(gameId, undefined, opponentId, slotIndex);
			clearDrawnCard();
		} else if (power === 'smuggle') {
			if (spellSelectedOwnSlot === null) {
				spellSelectedTargetId = opponentId;
				spellSelectedTargetSlot = slotIndex;
				log.debug('smuggle_target_selected', { opponentId, slotIndex });
			} else {
				await gameActions.invokePower(gameId, spellSelectedOwnSlot, opponentId, slotIndex);
				clearDrawnCard();
			}
		} else if (power === 'decree' && spellDecreeStage === 'peek') {
			spellSelectedTargetId = opponentId;
			spellSelectedTargetSlot = slotIndex;
			spellDecreeStage = 'swap';
			log.debug('decree_peeked', { opponentId, slotIndex });
		}
	}

	async function handleDrawDeck() {
		log.debug('Deck clicked, gameId:', { gameId });
		const result = await gameActions.drawFromDeck(gameId);
		log.debug('draw_deck_result', { success: !!result });
		// Card info comes via WebSocket in game_state_update, not API response
		// The drawnCard will be populated when the WS message updates gameState
		if (!result) {
			log.error('draw_action_failed', { source: 'deck' });
		}
	}

	async function handleDrawDiscard() {
		log.debug('draw_discard_clicked', { gameId });
		const result = await gameActions.drawFromDiscard(gameId);
		log.debug('draw_discard_result', { success: !!result });
		// Card info comes via WebSocket in game_state_update, not API response
		// The drawnCard will be populated when the WS message updates gameState
		if (!result) {
			log.error('draw_action_failed', { source: 'discard_pile' });
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
		log.debug('Timer expired for phase:', { phase });

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
		onOpponentCardClick={handleOpponentZoneClick}
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
			onInvoke={(ownSlot, targetId, targetSlot) => {
				spellSelectedOwnSlot = ownSlot ?? null;
				spellSelectedTargetId = targetId;
				spellSelectedTargetSlot = targetSlot ?? null;
				handlePowerInvoke(ownSlot, targetId, targetSlot);
			}}
			onDecline={handlePowerDecline}
			onDecreeSwap={(swap, ownSlot) => {
				if (!swap) {
					spellDecreeStage = 'swap';
				}
				handlePowerDecreeSwap(swap, ownSlot);
			}}
			onStateChange={(state) => {
				if (state.selectedOwnSlot !== undefined) {
					spellSelectedOwnSlot = state.selectedOwnSlot;
					log.debug('modal_spell_state_updated', { selectedOwnSlot: spellSelectedOwnSlot });
				}
				if (state.decreeStage !== undefined) {
					spellDecreeStage = state.decreeStage;
					log.debug('modal_spell_state_updated', { decreeStage: spellDecreeStage });
				}
			}}
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
