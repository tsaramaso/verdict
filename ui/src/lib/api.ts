const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Get auth token from localStorage
 */
function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('auth_token');
}

export async function apiCall(
  endpoint: string,
  options: RequestInit = {}
) {
  const token = getAuthToken();
  
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
    throw new Error(`API error: ${response.statusText}`);
  }
  
  return response.json();
}

export async function login(uuid: string) {
  const response = await apiCall('/users/login', {
    method: 'POST',
    body: JSON.stringify({ uuid }),
  });
  
  // Store token in localStorage for subsequent requests
  if (response.token) {
    localStorage.setItem('auth_token', response.token);
  }
  
  return response;
}

// Types
export interface User {
  uuid: string;
  name: string;
  is_active: boolean;
  created_at: string;
}

export interface GameSummary {
  game_id: string;
  status: string;
  turn_direction: string;
  current_round: number;
  seat_order: string[];
  created_at: string;
  started_at: string | null;
  ended_at: string | null;
}

// API Functions
export async function getCurrentUser(): Promise<User> {
  return apiCall('/users/me');
}

export async function listUsers(): Promise<User[]> {
  const data = await apiCall('/users');
  const currentUser = await getCurrentUser();
  return (data.users || []).filter((u: User) => u.uuid !== currentUser.uuid);
}

export async function listGames(): Promise<GameSummary[]> {
  const data = await apiCall('/games');
  return data.games;
}

export async function getGameStatus(gameId: string) {
  return apiCall(`/games/${gameId}/status`);
}

export async function createGame(playerIds: string[]) {
  return apiCall('/games', {
    method: 'POST',
    body: JSON.stringify({
      player_ids: playerIds,
      rules_config: {},
    }),
  });
}

export async function getGameRecap(gameId: string) {
  return apiCall(`/games/${gameId}/recap`);
}