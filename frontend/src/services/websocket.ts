// services/websocket.ts
import { WS_BASE_URL, WS_RECONNECT_INTERVAL, WS_MAX_RECONNECT_ATTEMPTS, API_ENDPOINTS } from '../config/constants';

type WebSocketCallback = (data: any) => void;

export class WebSocketService {
  private socket: WebSocket | null = null;
  private basePath: string; // plain path, no host, no token
  private messageCallbacks: Set<WebSocketCallback> = new Set();
  private reconnectAttempts = 0;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private _connected = false;

  onopen?: () => void;
  onmessage?: (event: any) => void;
  onerror?: (error: any) => void;
  onclose?: (closeEvent: CloseEvent) => void;

  constructor(path: string) {
    // DO NOT include token here. DO include /api prefix.
    this.basePath = path;
    this.connect();
  }

  private buildUrl(): string {
    // Ensure leading slash
    const path = this.basePath.startsWith('/') ? this.basePath : `/${this.basePath}`;

    // Strip any existing token from the incoming path to avoid duplication
    const [pathname, qs = ''] = path.split('?');
    const params = new URLSearchParams(qs);
    params.delete('token');

    const token = localStorage.getItem('access_token') || '';
    if (token) params.set('token', token);

    const url = `${WS_BASE_URL}${pathname}?${params.toString()}`;
    return url;
  }

  private connect(): void {
    try {
      const url = this.buildUrl();
      console.log('[WebSocketService] Attempting connection to:', url.replace(/token=[^&]+/, 'token=***'));
      this.socket = new WebSocket(url);
      this.setupEventListeners();
    } catch (error) {
      console.error('[WebSocketService] Connection build failed:', error);
      this.handleReconnect();
    }
  }

  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.onopen = () => {
      this._connected = true;
      this.reconnectAttempts = 0;
      if (this.reconnectTimeout) {
        clearTimeout(this.reconnectTimeout);
        this.reconnectTimeout = null;
      }
      this.onopen?.();
      console.log('WebSocket connected');
    };

    this.socket.onmessage = (event: MessageEvent) => {
      let data: any = null;
      try {
        data = JSON.parse(event.data);
      } catch {
        data = event.data;
      }
      // fan-out to subscribers
      this.messageCallbacks.forEach(cb => {
        try { cb(data); } catch (e) { console.error('Error in WebSocket callback:', e); }
      });
      // optional per-instance handler
      this.onmessage?.(data);
    };

    this.socket.onclose = (evt: CloseEvent) => {
      this._connected = false;
      this.onclose?.(evt);
      console.log('WebSocket closed', `code=${evt.code}`, `reason=${evt.reason || '(none)'}`);
      this.handleReconnect();
    };

    this.socket.onerror = (error: Event) => {
      this.onerror?.(error);
      console.error('WebSocket error:', error);
      // Let onclose drive the reconnect to avoid double-closing
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

  public subscribe(callback: WebSocketCallback): () => void {
    this.messageCallbacks.add(callback);
    return () => this.unsubscribe(callback);
  }

  public unsubscribe(callback: WebSocketCallback): void {
    this.messageCallbacks.delete(callback);
  }

  public ensureConnected(): void {
    const ready = this.socket?.readyState;
    if (ready === WebSocket.OPEN || ready === WebSocket.CONNECTING) return;
    this.connect();
  }

  public waitUntilOpen(timeoutMs = 5000): Promise<boolean> {
    const ready = this.socket?.readyState;
    if (ready === WebSocket.OPEN) return Promise.resolve(true);

    return new Promise<boolean>((resolve) => {
      let done = false;
      const finish = (ok: boolean) => {
        if (done) return;
        done = true;
        cleanup();
        resolve(ok);
      };
      const timeout = setTimeout(() => finish(false), timeoutMs);

      const s = this.socket;
      if (!s) {
        this.connect();
      }
      const sock = this.socket;
      if (!sock) {
        clearTimeout(timeout);
        return resolve(false);
      }

      const handleOpen = () => finish(true);
      const handleClose = () => finish(false);
      const handleError = () => finish(false);

      const cleanup = () => {
        clearTimeout(timeout);
        sock.removeEventListener('open', handleOpen);
        sock.removeEventListener('close', handleClose);
        sock.removeEventListener('error', handleError);
      };

      sock.addEventListener('open', handleOpen);
      sock.addEventListener('close', handleClose);
      sock.addEventListener('error', handleError);
    });
  }

  public send(data: any): void {
    if (!this.socket || !this._connected) {
      console.warn('[WebSocketService] Cannot send - not connected', {
        hasSocket: !!this.socket,
        readyState: this.socket?.readyState,
      });
      return;
    }
    try {
      const payload = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(payload);
    } catch (e) {
      console.error('Error sending WebSocket message:', e);
    }
  }

  public reconnectNow(): void {
    this.close();
    this.reconnectAttempts = 0;
    this.connect();
  }

  public close(): void {
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.socket) {
      try { this.socket.close(); } catch {}
      this.socket = null;
    }
    this._connected = false;
    this.messageCallbacks.clear();
  }

  public get connected(): boolean {
    return this._connected;
  }
}

// Singleton instance for system metrics
let systemMetricsWebSocket: WebSocketService | null = null;

export const getSystemMetricsWebSocket = (): WebSocketService => {
  if (!systemMetricsWebSocket) {
    // Pass a PLAIN path; service will add token
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
