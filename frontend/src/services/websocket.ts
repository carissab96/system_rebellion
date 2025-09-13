// services/websocket.ts
import { WS_BASE_URL, API_ENDPOINTS} from '../config/constants';

type WebSocketCallback = (data: any) => void;

export class WebSocketService {
  [x: string]: () => void | undefined;
  private socket: WebSocket | null = null;
  private basePath: string; // plain path, no host, no token
  private messageCallbacks: Set<WebSocketCallback> = new Set();
  private reconnectAttempts = 0;
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null;
  private isConnected = false;
  onError: (evt: Event) => void | undefined;

  constructor(path: string) {
    this.basePath = path;
    this.connect();
  }

  private buildUrl(): string {
    // normalize leading slash
    let path = this.basePath.startsWith('/') ? this.basePath : `/${this.basePath}`;

    // normalize to /api/ws/... if someone passed /ws/...
    if (path.startsWith('/ws/')) path = `/api${path}`;

    // split path & query, scrub any existing token
    const [pathname, rawQs = ''] = path.split('?');
    const params = new URLSearchParams(rawQs);
    params.delete('token');

    // append the current access token once
    const token = localStorage.getItem('access_token') || '';
    if (token) params.set('token', token);

    const qs = params.toString();
    return `${WS_BASE_URL}${pathname}${qs ? `?${qs}` : ''}`;
  }

  private connect(): void {
    try {
      const url = this.buildUrl();
      console.log(`[WebSocketService] Attempting connection to: ${url}`);
      this.socket = new WebSocket(url);
      this.setupEventListeners();
    } catch (err) {
      console.error('[WebSocketService] Connection failed:', err);
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
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
      }
    };

    this.socket.onclose = (ev: CloseEvent) => {
      console.log(`WebSocket closed code=${ev.code} reason=${ev.reason || '(none)'}`);
      this.isConnected = false;
      this.handleReconnect();
    };

    this.socket.onerror = (error: Event) => {
      console.error('WebSocket error:', error);
      // Let onclose drive the reconnect if the server shuts it
    };
  }

  private handleReconnect(): void {
    const MAX = 5; // or import from constants
    const BASE = 3000;

    if (this.reconnectAttempts >= MAX) {
      console.error('Max reconnection attempts reached');
      return;
    }
    if (!this.reconnectTimeout) {
      const delay = BASE * Math.pow(2, this.reconnectAttempts);
      console.log(`Reconnecting in ${delay}ms...`);
      this.reconnectTimeout = setTimeout(() => {
        this.reconnectAttempts++;
        this.reconnectTimeout = null;
        this.connect();
      }, delay);
    }
  }

  private notifyCallbacks(data: any): void {
    this.messageCallbacks.forEach(cb => {
      try { cb(data); } catch (e) { console.error('WS callback error:', e); }
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
      const message = typeof data === 'string' ? data : JSON.stringify(data);
      this.socket.send(message);
    } else {
      console.warn('[WebSocketService] Cannot send - WebSocket not connected');
    }
  }

  // --- helpers you added; keep them ---
  public ensureConnected(): void {
    const ready = this.socket?.readyState;
    const isOpen = ready === WebSocket.OPEN;
    const isConnecting = ready === WebSocket.CONNECTING;
    if (isOpen || isConnecting) return;
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

      const s = this.socket;
      if (!s) {
        this.connect();
      }
      const target = this.socket;
      if (!target) return finish(false);

      const handleOpen = () => finish(true);
      const handleClose = () => finish(false);
      const handleError = () => finish(false);

      const timeout = setTimeout(() => finish(false), timeoutMs);
      const cleanup = () => {
        clearTimeout(timeout);
        target.removeEventListener('open', handleOpen);
        target.removeEventListener('close', handleClose);
        target.removeEventListener('error', handleError);
      };

      target.addEventListener('open', handleOpen);
      target.addEventListener('close', handleClose);
      target.addEventListener('error', handleError);
    });
  }

  public close(): void {
    if (this.socket) {
      try { this.socket.close(); } catch {}
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
