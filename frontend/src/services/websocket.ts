// frontend/src/services/WebSocketService.ts

type ConnectionState = "idle" | "connecting" | "open" | "closed" | "error";
type MessageHandler = (data: any) => void;

const DEFAULT_PATH = "/ws/system-metrics";

export class WebSocketService {
  private static instance: WebSocketService | null = null;

  private urlBase: string;
  private socket: WebSocket | null = null;
  private state: ConnectionState = "idle";
  private subscribers: Set<MessageHandler> = new Set();
  private openWaiter: Promise<void> | null = null;
  private currentPath: string = DEFAULT_PATH;

  // Optional external callbacks
  onError?: (evt: Event) => void;
  onClose?: () => void;

  private constructor(wsBaseUrl: string) {
    this.urlBase = wsBaseUrl.replace(/\/$/, "");
  }

  /**
   * Singleton accessor. Keeps the socket alive across view unmounts.
   */
  static getInstance(wsBaseUrl: string): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService(wsBaseUrl);
    }
    return WebSocketService.instance;
  }

  /**
   * Build WS URL and append ?token=... exactly once.
   */
  private buildUrl(path: string): string {
    const token = localStorage.getItem("access_token");
    if (!token) throw new Error("No access token");
    const noLeading = path.startsWith("/") ? path : `/${path}`;
    if (noLeading.includes("token=")) {
      throw new Error("Token must not be included in path; it is appended automatically");
    }
    const sep = noLeading.includes("?") ? "&" : "?";
    return `${this.urlBase}${noLeading}${sep}token=${encodeURIComponent(token)}`;
  }

  /**
   * Ensure a single open connection to the given path.
   * Does NOT auto close on component unmounts.
   */
  ensureConnected(path: string = DEFAULT_PATH): WebSocket {
    // If path changes, we intentionally re-open to the new endpoint
    const targetPath = path || DEFAULT_PATH;
    const needsNew =
      !this.socket ||
      this.state === "closed" ||
      this.state === "error" ||
      this.currentPath !== targetPath ||
      this.socket.readyState === WebSocket.CLOSING ||
      this.socket.readyState === WebSocket.CLOSED;

    if (!needsNew && this.socket && this.socket.readyState === WebSocket.OPEN) {
      return this.socket;
    }

    // Close any dangling socket without nuking subscribers
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      try {
        this.socket.close(1000, "switching-endpoint");
      } catch {
        // ignore
      }
    }

    const url = this.buildUrl(targetPath);
    this.currentPath = targetPath;
    this.socket = new WebSocket(url);
    this.state = "connecting";

    // Prepare waiter promise for waitUntilOpen
    this.openWaiter = new Promise<void>((resolve, reject) => {
      const onOpen = () => {
        this.state = "open";
        resolve();
      };
      const onError = (evt: Event) => {
        this.state = "error";
        reject(new Error("WebSocket error"));
        this.onError?.(evt);
      };
      const onClose = () => {
        this.state = "closed";
        this.onClose?.();
      };

      this.socket!.addEventListener("open", onOpen, { once: true });
      this.socket!.addEventListener("error", onError);
      this.socket!.addEventListener("close", onClose);

      // Message fan-out
      this.socket!.addEventListener("message", (ev: MessageEvent) => {
        let payload: any = null;
        try {
          payload = JSON.parse(ev.data);
        } catch {
          // Non-JSON payloads aren’t expected; surface as error-like shape
          payload = { type: "error", message: "non_json_message", raw: ev.data };
        }
        // Deliver to all subscribers
        this.subscribers.forEach(fn => {
          try {
            fn(payload);
          } catch {
            // Never let one bad handler kill distribution
          }
        });
      });
    });

    return this.socket;
  }

  /**
   * Await an open connection with a timeout.
   */
  async waitUntilOpen(timeoutMs = 5000): Promise<void> {
    // If already open, fast-path
    if (this.socket?.readyState === WebSocket.OPEN && this.state === "open") return;

    if (!this.openWaiter) {
      // If someone calls this before ensureConnected, try to connect to default path.
      this.ensureConnected(this.currentPath || DEFAULT_PATH);
    }

    const waiter = this.openWaiter!;
    let timeoutHandle: number | undefined;

    const timeoutPromise = new Promise<void>((_, reject) => {
      timeoutHandle = window.setTimeout(() => reject(new Error("WS open timeout")), timeoutMs);
    });

    try {
      await Promise.race([waiter, timeoutPromise]);
    } finally {
      if (timeoutHandle !== undefined) window.clearTimeout(timeoutHandle);
    }
  }

  /**
   * Send a message. The server expects JSON objects with a "type".
   * Never send tokens here. Auth is via URL query only.
   */
  send(msg: Record<string, unknown> | string): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket is not open");
    }
    if (typeof msg === "string") {
      this.socket.send(msg);
      return;
    }
    if (!("type" in msg)) {
      throw new Error("Outgoing WS message must include a 'type' field");
    }
    this.socket.send(JSON.stringify(msg));
  }

  /**
   * Close the socket explicitly. We do not auto-close on unmount elsewhere.
   */
  close(code: number = 1000, reason: string = "client_close"): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      try {
        this.socket.close(code, reason);
      } finally {
        this.state = "closed";
      }
    }
  }

  /**
   * Subscribe to all incoming WS messages (already JSON-parsed).
   * Returns an unsubscribe function for convenience.
   */
  subscribe(handler: MessageHandler): () => void {
    this.subscribers.add(handler);
    return () => this.unsubscribe(handler);
  }

  unsubscribe(handler: MessageHandler): void {
    this.subscribers.delete(handler);
  }

  /**
   * Static helpers for older call sites that used class-level subscribe/unsubscribe.
   * These require you to have called getInstance(...) at least once.
   */
  static subscribe(handler: MessageHandler): () => void {
    const svc = WebSocketService.instance;
    if (!svc) throw new Error("WebSocketService not initialized. Call getInstance(wsBaseUrl) first.");
    return svc.subscribe(handler);
  }

  static unsubscribe(handler: MessageHandler): void {
    const svc = WebSocketService.instance;
    if (!svc) return;
    svc.unsubscribe(handler);
  }

  getSocket(): WebSocket | null {
    return this.socket;
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN && this.state === "open";
  }
}
