/**
 * API client for Verdict game
 * Handles all communication with the FastAPI backend
 * Base URL defaults to localhost:8000 in dev, uses VITE_API_URL env var in production
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

interface ApiError {
  detail: string;
}

interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
}

/**
 * Base fetch wrapper that handles auth and error handling
 */
async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<any> {
  const token = localStorage.getItem('auth_token');

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API error: ${response.statusText}`);
  }

  // Handle 204 No Content responses (like DELETE)
  if (response.status === 204) {
    return null;
  }

  return response.json();
}

// ============================================================================
// User Endpoints
// ============================================================================

export interface User {
  uuid: string;
  name: string | null;
  is_active: boolean;
  created_at: string;
}

export interface UserListResponse {
  users: User[];
}

/**
 * Login with UUID to get JWT token
 */
export async function login(uuid: string): Promise<{ token: string; uuid: string }> {
  return apiFetch('/users/login', {
    method: 'POST',
    body: JSON.stringify({ uuid }),
  });
}

/**
 * Get current user's profile
 */
export async function getCurrentUser(): Promise<User> {
  return apiFetch('/users/me');
}

/**
 * List all active users (for selecting players in game creation)
 */
export async function listUsers(): Promise<User[]> {
  const response = await apiFetch('/users');
  return response.users;
}

/**
 * Soft-delete current user (deactivate account)
 * Status: 204 No Content on success
 */
export async function deleteCurrentUser(uuid: string): Promise<void> {
  return apiFetch(`/users/${uuid}`, {
    method: 'DELETE',
  });
}

// ============================================================================
// Game Endpoints
// ============================================================================

export interface GameSummary {
  game_id: string;
  status: 'WAITING_FOR_PLAYERS' | 'IN_PROGRESS' | 'FINISHED';
  turn_direction: 'CW' | 'CCW';
  current_round: number;
  seat_order: number;
  created_at: string;
  started_at: string | null;
  ended_at: string | null;
}

export interface GameListResponse {
  games: GameSummary[];
}

export interface GameStatus {
  game_id: string;
  phase: string;
  current_player: string;
  round_number: number;
  scores: Record<string, number>;
  is_last_turn: boolean;
  game_over: boolean;
}

export interface GameCreateRequest {
  player_ids: string[];
  turn_direction: 'CW' | 'CCW';
  rules_config?: Record<string, any>;
}

export interface GameCreateResponse {
  game_id: string;
  phase: string;
  events: any[]; // Event type, not needed for MVP
}

/**
 * Create a new game
 * Creator must be included in player_ids
 * Player count: 2-5
 */
export async function createGame(request: GameCreateRequest): Promise<GameCreateResponse> {
  return apiFetch('/games', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * List all games the current user is seated in
 */
export async function listGames(): Promise<GameSummary[]> {
  const response = await apiFetch('/games');
  return response.games;
}

/**
 * Get live status snapshot of a game
 * Only works if game is currently loaded in API process
 */
export async function getGameStatus(gameId: string): Promise<GameStatus> {
  return apiFetch(`/games/${gameId}/status`);
}

/**
 * Get full event log for a game (scoped to current player)
 */
export async function getGameEvents(gameId: string): Promise<any> {
  const response = await apiFetch(`/games/${gameId}/events`);
  return response.events;
}

// ============================================================================
// Gameplay Endpoints (Actions)
// ============================================================================

export interface ActionResult {
  phase: string;
  events: any[];
}

/**
 * Draw a card from deck or discard pile
 */
export async function draw(
  gameId: string,
  source: 'deck' | 'discard'
): Promise<ActionResult> {
  return apiFetch(`/games/${gameId}/draw`, {
    method: 'POST',
    body: JSON.stringify({ source }),
  });
}

/**
 * Take an action (discard or swap)
 */
export async function takeAction(
  gameId: string,
  choice: string,
  slotIndex?: number
): Promise<ActionResult> {
  return apiFetch(`/games/${gameId}/action`, {
    method: 'POST',
    body: JSON.stringify({ choice, slot_index: slotIndex }),
  });
}

// Note: Power card endpoints (power/decline, power/glance, etc.) and
// Trial endpoints (trial/testify, trial/challenge, etc.) can be added
// as needed when building the game board UI.