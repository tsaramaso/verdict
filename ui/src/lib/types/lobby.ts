/**
 * Lobby System Types
 * Used by: ui/src/routes/lobby/[lobbyId]/+page.svelte
 */

export interface PlayerInfo {
	player_id: string;
	player_name: string;
	ready: boolean;
	connected: boolean;
}

export interface LobbyState {
	lobby_id: string;
	host_player_id: string;
	players: PlayerInfo[];
}

export interface PlayerReadyRequest {
	ready: boolean;
}

export interface PlayerReadyResponse {
	player_id: string;
	ready: boolean;
}
