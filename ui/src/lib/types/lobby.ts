/**
 * Lobby System Types
 * Used by: ui/src/routes/game/[game_id]/lobby/+page.svelte
 */

export interface PlayerInfo {
  player_id: string;
  player_name: string;
  ready: boolean;
  connected: boolean;
}

export interface LobbyState {
  game_id: string;
  host_player_id: string;
  players: PlayerInfo[];
  phase: string;
}

export type WebSocketMessageType =
  | 'player_connected'
  | 'player_ready'
  | 'player_not_ready'
  | 'player_disconnected'
  | 'game_started'
  | 'ping'
  | 'pong';

export interface PlayerConnectedMessage {
  type: 'player_connected';
  player_id: string;
  player_name: string;
}

export interface PlayerReadyMessage {
  type: 'player_ready' | 'player_not_ready';
  player_id: string;
  player_name: string;
}

export interface PlayerDisconnectedMessage {
  type: 'player_disconnected';
  player_id: string;
}

export interface GameStartedMessage {
  type: 'game_started';
  phase: string;
  current_player: string;
}

export type WebSocketMessage =
  | PlayerConnectedMessage
  | PlayerReadyMessage
  | PlayerDisconnectedMessage
  | GameStartedMessage
  | { type: 'pong' };

export interface PlayerReadyRequest {
  ready: boolean;
}

export interface PlayerReadyResponse {
  player_id: string;
  ready: boolean;
}