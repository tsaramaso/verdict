<script lang="ts">
	import { onMount } from 'svelte';
	import { gameState, setCurrentPlayerId } from '$lib/stores/gameState';
	import RightPanel from './RightPanel.svelte';
	import BottomBar from './BottomBar.svelte';
	import PlayArea from './PlayArea.svelte';
	import SpellInvocationModal from './SpellInvocationModal.svelte';
	import { transformCardList, transformRank, transformSuit } from '$lib/utils/cardTransform';
	import { transformRules } from '$lib/utils/rulesTransform';
	import { API_ENDPOINTS, getFullUrl } from '$lib/constants/api';
	import { GAME_PHASES } from '$lib/config';

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
		const message = JSON.parse(data);

		if (message.type === 'game_state' || message.type === 'game_state_update') {
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

			gameState.set({
				game_id: message.game.game_id,
				phase: message.game.phase,
				current_player: message.game.current_player,
				round_number: message.game.round_number,
				self: transformedSelf,
				opponents: transformedOpponents,
				my_opponent_knowledge: message.my_opponent_knowledge,
				trial: message.trial,
				discard_pile: transformedDiscard
			});
		}
	}

	function getTokenFromStorage(): string {
		const token = localStorage.getItem('auth_token');
		if (!token) throw new Error('No auth token found');
		return token;
	}

	async function handleDeckClick() {
		try {
			const response = await fetch(getFullUrl(API_ENDPOINTS.draw(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ source: 'deck' })
			});

			if (!response.ok) {
				console.error('Draw from deck failed:', response.status);
				return;
			}

			const data = await response.json();
			if (data.drawn_card) {
				drawnCard = data.drawn_card;
				drawnCardSource = 'deck';
			}
		} catch (error) {
			console.error('Deck draw error:', error);
		}
	}

	async function handleDiscardClick() {
		try {
			const response = await fetch(getFullUrl(API_ENDPOINTS.draw(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ source: 'discard' })
			});

			if (!response.ok) {
				console.error('Draw from discard failed:', response.status);
				return;
			}

			const data = await response.json();
			if (data.drawn_card) {
				drawnCard = data.drawn_card;
				drawnCardSource = 'discard';
			}
		} catch (error) {
			console.error('Discard draw error:', error);
		}
	}

	async function handleAction(choice: 'discard_immediate' | 'swap' | 'pass_back', slotIndex?: number) {
		try {
			const response = await fetch(getFullUrl(API_ENDPOINTS.action(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					choice,
					slot_index: slotIndex,
					source: drawnCardSource
				})
			});

			if (!response.ok) console.error('Action failed:', response.status);
			clearDrawnCard();
		} catch (error) {
			console.error('Action error:', error);
		}
	}

	async function handlePowerInvoke(
		ownSlotIndex?: number,
		targetOwner?: string,
		targetIndex?: number
	) {
		try {
			const response = await fetch(getFullUrl(API_ENDPOINTS.power.invoke(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					own_slot_index: ownSlotIndex,
					target_owner: targetOwner,
					target_index: targetIndex
				})
			});

			if (!response.ok) console.error('Power invoke failed:', response.status);
			clearDrawnCard();
		} catch (error) {
			console.error('Power invoke error:', error);
		}
	}

	async function handlePowerDecline() {
		try {
			const response = await fetch(getFullUrl(API_ENDPOINTS.power.decline(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' }
			});

			if (!response.ok) console.error('Power decline failed:', response.status);
			clearDrawnCard();
		} catch (error) {
			console.error('Power decline error:', error);
		}
	}

	async function handlePowerDecreeSwap(swap: boolean, ownSlotIndex?: number) {
		try {
			const response = await fetch(getFullUrl(API_ENDPOINTS.power.decreeSwap(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ swap, own_slot_index: ownSlotIndex })
			});

			if (!response.ok) console.error('Decree swap failed:', response.status);
			if (swap) clearDrawnCard();
		} catch (error) {
			console.error('Decree swap error:', error);
		}
	}

	async function handleQuickDiscard(slotIndex: number) {
		try {
			const response = await fetch(getFullUrl(API_ENDPOINTS.quickDiscard(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ slot_index: slotIndex })
			});

			if (!response.ok) console.error('Quick discard failed:', response.status);
		} catch (error) {
			console.error('Quick discard error:', error);
		}
	}

	async function handleTestifyFirst() {
		try {
			await fetch(getFullUrl(API_ENDPOINTS.trial.testifyFirst(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' }
			});
		} catch (error) {
			console.error('Testify first error:', error);
		}
	}

	async function handleTestifyCross() {
		try {
			await fetch(getFullUrl(API_ENDPOINTS.trial.testifyCross(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' }
			});
		} catch (error) {
			console.error('Testify cross error:', error);
		}
	}

	async function handleChallenge() {
		try {
			await fetch(getFullUrl(API_ENDPOINTS.trial.challenge(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' }
			});
		} catch (error) {
			console.error('Challenge error:', error);
		}
	}

	async function handlePlea() {
		try {
			await fetch(getFullUrl(API_ENDPOINTS.trial.plea(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ plea: true })
			});
		} catch (error) {
			console.error('Plea error:', error);
		}
	}

	async function handlePleaDecline() {
		try {
			await fetch(getFullUrl(API_ENDPOINTS.trial.plea(gameId)), {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ plea: false })
			});
		} catch (error) {
			console.error('Plea decline error:', error);
		}
	}

	function clearDrawnCard() {
		drawnCard = null;
		drawnCardSource = null;
	}
</script>

<div class="game-page">
	<PlayArea
		{drawnCard}
		{drawnCardSource}
		{onDeckClick: handleDeckClick}
		{onDiscardClick: handleDiscardClick}
		{onAction: handleAction}
		{onQuickDiscard: handleQuickDiscard}
		{onTestifyFirst: handleTestifyFirst}
		{onTestifyCross: handleTestifyCross}
		{onChallenge: handleChallenge}
		{onPlea: handlePlea}
		{onPleaDecline: handlePleaDecline}
	/>

	<RightPanel
		{onTestifyFirst: handleTestifyFirst}
		{onTestifyCross: handleTestifyCross}
		{onChallenge: handleChallenge}
		{onPlea: handlePlea}
		{onPleaDecline: handlePleaDecline}
	/>

	<BottomBar />

	{#if $gameState.phase === GAME_PHASES.AWAITING_SPELL_INVOCATION && drawnCard}
		<SpellInvocationModal
			card={drawnCard}
			onInvoke={handlePowerInvoke}
			onDecline={handlePowerDecline}
			onDecreeSwap={handlePowerDecreeSwap}
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