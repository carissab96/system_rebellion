import { WS_BASE_URL, WS_RECONNECT_INTERVAL, WS_MAX_RECONNECT_ATTEMPTS, API_ENDPOINTS } from '../config/constants';

type WebSocketCallback = (data: any) => void;

export class WebSocketService {
  private socket: WebSocket | null = null;
  private url: string;
  private messageCallbacks: Set<WebSocketCallback> = new Set();
  private reconnectAttempts = 0;
  private reconnectTimeout: NodeJS.Timeout | null = null;
  private isConnected = false;
  onopen!: () => void;
  onmessage!: (event: any) => void;
  onerror!: (error: any) => void;
  onclose!: (closeEvent: CloseEvent) => void;

  constructor(path: string) {
    this.url = `${WS_BASE_URL}${path}`;
    this.connect();
  }

  private connect(): void {
    try {
      console.log(`[WebSocketService] Attempting connection to: ${this.url}`);
      this.socket = new WebSocket(this.url);
      this.setupEventListeners();
    } catch (error) {
      console.error(`[WebSocketService] Connection failed to ${this.url}:`, error);
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
        
        // Handle backend authentication flow
        if (data.type === 'connection_established') {
          console.log('WebSocket connection established, sending auth token...');
          const token = localStorage.getItem('access_token');
          if (token) {
            this.socket?.send(JSON.stringify({ token }));
          } else {
            console.error('No access token found for WebSocket authentication');
          }
          return;
        }
        
        if (data.type === 'authentication_success') {
          console.log('WebSocket authentication successful');
          this.isConnected = true;
        }
        
        // Backend doesn't send authentication_success, but system_info means auth worked
        if (data.type === 'system_info' || data.type === 'metrics_update') {
          if (!this.isConnected) {
            console.log('WebSocket authentication successful (inferred from data messages)');
            this.isConnected = true;
          }
        }
        
        if (data.type === 'error' || data.type === 'authentication_failed') {
          console.error('WebSocket authentication failed:', data.message);
          this.isConnected = false;
        }
        
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
    console.log('[WebSocketService] Send attempt:', {
      hasSocket: !!this.socket,
      isConnected: this.isConnected,
      readyState: this.socket?.readyState,
      data: data
    });
    
    if (this.socket && this.isConnected) {
      try {
        const message = typeof data === 'string' ? data : JSON.stringify(data);
        console.log('[WebSocketService] Sending message:', message);
        this.socket.send(message);
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
      }
    } else {
      console.warn('[WebSocketService] Cannot send - WebSocket not connected:', {
        hasSocket: !!this.socket,
        isConnected: this.isConnected,
        readyState: this.socket?.readyState
      });
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
    // Connect without token in URL - backend expects token via message
    systemMetricsWebSocket = new WebSocketService(API_ENDPOINTS.WEBSOCKET.SYSTEM_METRICS);
  }
  return systemMetricsWebSocket;
};

export const closeSystemMetricsWebSocket = (): void => {
  if (systemMetricsWebSocket) {
    systemMetricsWebSocket.close();
    systemMetricsWebSocket = null;
  }
};
