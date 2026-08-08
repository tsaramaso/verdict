const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Get auth token from cookie
 */
function getAuthToken(): string | null {
  const name = 'auth_token=';
  const decodedCookie = decodeURIComponent(document.cookie);
  const cookieArray = decodedCookie.split(';');
  
  for (let cookie of cookieArray) {
    cookie = cookie.trim();
    if (cookie.indexOf(name) === 0) {
      return cookie.substring(name.length);
    }
  }
  
  return null;
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
  return apiCall('/users/login', {
    method: 'POST',
    body: JSON.stringify({ uuid }),
  });
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
  return data.users;
}

export async function listGames(): Promise<GameSummary[]> {
  const data = await apiCall('/games');
  return data.games;
}

export async function getGameStatus(gameId: string) {
  return apiCall(`/games/${gameId}/status`);
}

export async function createGame(playerIds: string[], turnDirection: string) {
  return apiCall('/games', {
    method: 'POST',
    body: JSON.stringify({
      player_ids: playerIds,
      turn_direction: turnDirection,
      rules_config: {},
    }),
  });
}