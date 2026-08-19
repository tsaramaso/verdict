/**
 * WebSocket utilities for real-time lobby/game updates
 */

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
}

export interface PlayerDisconnectedMessage {
  type: 'player_disconnected';
  player_id: string;
}

export interface GameStartedMessage {
  type: 'game_started';
  game_id: string;
}

export type WebSocketMessage =
  | PlayerConnectedMessage
  | PlayerReadyMessage
  | PlayerDisconnectedMessage
  | GameStartedMessage
  | { type: 'ping' | 'pong' };

export interface WebSocketOptions {
  url: string;
  token: string;
  onMessage: (message: WebSocketMessage) => void;
  onError: (error: string) => void;
  onClose: () => void;
  reconnectDelay?: number;
  maxReconnectAttempts?: number;
}

export class WebSocketClient {
  private ws: WebSocket | null = null;
  private options: WebSocketOptions;
  private reconnectAttempts = 0;
  private maxReconnectAttempts: number;
  private reconnectDelay: number;
  private pingInterval: NodeJS.Timeout | null = null;

  constructor(options: WebSocketOptions) {
    this.options = options;
    this.maxReconnectAttempts = options.maxReconnectAttempts ?? 5;
    this.reconnectDelay = options.reconnectDelay ?? 5000;
  }

  connect(): void {
    try {
      const wsUrl = `${this.options.url}?token=${encodeURIComponent(this.options.token)}`;
      this.ws = new WebSocket(wsUrl);

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
        this.startPingInterval();
      };

      this.ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          this.options.onMessage(message);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      this.ws.onerror = () => {
        this.options.onError('WebSocket connection error');
      };

      this.ws.onclose = () => {
        this.stopPingInterval();
        this.attemptReconnect();
      };
    } catch (err) {
      this.options.onError(err instanceof Error ? err.message : 'Failed to connect');
    }
  }

  private startPingInterval(): void {
    this.pingInterval = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000);
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * this.reconnectAttempts;
      console.log(`Reconnecting in ${delay}ms... (attempt ${this.reconnectAttempts})`);
      setTimeout(() => this.connect(), delay);
    } else {
      this.options.onError('Max reconnection attempts reached');
      this.options.onClose();
    }
  }

  send(message: Partial<WebSocketMessage>): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected');
    }
  }

  disconnect(): void {
    this.stopPingInterval();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}