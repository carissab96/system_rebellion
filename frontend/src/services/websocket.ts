import { WS_BASE_URL, WS_RECONNECT_INTERVAL, WS_MAX_RECONNECT_ATTEMPTS } from '@/config/constants';

type WebSocketCallback = (data: any) => void;

export class WebSocketService {
  private socket: WebSocket | null = null;
  private url: string;
  private messageCallbacks: Set<WebSocketCallback> = new Set();
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private isConnected = false;

  constructor(path: string) {
    this.url = `${WS_BASE_URL}${path}`;
    this.connect();
  }

  private connect(): void {
    try {
      this.socket = new WebSocket(this.url);
      this.setupEventListeners();
    } catch (error) {
      console.error('WebSocket connection error:', error);
      this.handleReconnect();
    }
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      this.isConnected = true;
      this.reconnectAttempts = 0;
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
        this.reconnectTimeout = null;
      }
    };

    this.socket.onmessage = (event: MessageEvent) => {
      try {
        const data = JSON.parse(event.data);
        this.notifyCallbacks(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    this.socket.onclose = () => {
      console.log('WebSocket disconnected');
      this.isConnected = false;
      this.handleReconnect();
    };

    this.socket.onerror = (error: Event) => {
      console.error('WebSocket error:', error);
      this.socket?.close();
    };
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= WS_MAX_RECONNECT_ATTEMPTS) {
      console.error('Max reconnection attempts reached');
      return;
    }

    if (!this.reconnectTimeout) {
      const delay = WS_RECONNECT_INTERVAL * Math.pow(2, this.reconnectAttempts);
      console.log(`Reconnecting in ${delay}ms...`);
      
      this.reconnectTimeout = setTimeout(() => {
        this.reconnectAttempts++;
        this.reconnectTimeout = null;
        this.connect();
      }, delay);
    }
  }

  private notifyCallbacks(data: any): void {
    this.messageCallbacks.forEach((callback) => {
      try {
        callback(data);
      } catch (error) {
        console.error('Error in WebSocket callback:', error);
      }
    });
  }

  public subscribe(callback: WebSocketCallback): () => void {
    this.messageCallbacks.add(callback);
    return () => this.unsubscribe(callback);
  }

  public unsubscribe(callback: WebSocketCallback): void {
    this.messageCallbacks.delete(callback);
  }

  public send(data: any): void {
    if (this.socket && this.isConnected) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        this.socket.send(message);
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
      }
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  public close(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
      this.isConnected = false;
      this.messageCallbacks.clear();
      
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
        this.reconnectTimeout = null;
      }
    }
  }

  public get connected(): boolean {
    return this.isConnected;
  }
}

// Singleton instance for system metrics
let systemMetricsWebSocket: WebSocketService | null = null;

export const getSystemMetricsWebSocket = (): WebSocketService => {
  if (!systemMetricsWebSocket) {
    const token = localStorage.getItem('access_token');
    systemMetricsWebSocket = new WebSocketService(`/ws/system-metrics?token=${token}`);
  }
  return systemMetricsWebSocket;
};

export const closeSystemMetricsWebSocket = (): void => {
  if (systemMetricsWebSocket) {
    systemMetricsWebSocket.close();
    systemMetricsWebSocket = null;
  }
};
