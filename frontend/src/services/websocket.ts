// services/websocket.ts
import { CircuitBreaker } from './circuitBreaker';
import { BackpressureHandler } from './backpressure';

type ConnectionState = "idle" | "connecting" | "open" | "closed" | "error";
type MessageHandler = (data: any) => void;

export const DEFAULT_PATH = "ws://localhost:8000/api/ws/system-metrics";

export class WebSocketService {
  private static instance: WebSocketService | null = null;

  private urlBase: string;
  private socket: WebSocket | null = null;
  private state: ConnectionState = "idle";
  private subscribers: Set<MessageHandler> = new Set();
  private openWaiter: Promise<void> | null = null;
  private currentPath: string = DEFAULT_PATH;
  
  // Resilience components
  private circuitBreaker: CircuitBreaker;
  private backpressure: BackpressureHandler<any>;
  private messageProcessor: number | null = null;
  private keepAliveInterval: number | null = null;

  // Optional external callbacks
  onError?: (evt: Event) => void;
  onClose?: (event?: CloseEvent) => void;

  private constructor(wsBaseUrl: string) {
    this.urlBase = wsBaseUrl.replace(/\/$/, "");
    
    this.circuitBreaker = new CircuitBreaker({
      name: 'websocket',
      maxFailures: 5,
      resetTimeout: 60,
      halfOpenMaxTrials: 3,
      exponentialBackoffFactor: 2.0
    });
    
    this.backpressure = new BackpressureHandler({
      maxBufferSize: 1000,
      throttleThreshold: 0.75,
      minSleepMs: 50,
      maxSleepMs: 1200
    });
    
    // Start message processor
    this.startMessageProcessor();
  }

  private startMessageProcessor(): void {
    const processMessages = () => {
      // Check if we should throttle
      if (this.backpressure.shouldThrottle()) {
        const waitTime = this.backpressure.getWaitTime();
        console.log(`🚨 Backpressure active, waiting ${(waitTime * 1000).toFixed(0)}ms`);
        this.messageProcessor = window.setTimeout(() => processMessages(), waitTime * 1000);
        return;
      }

      // Process a batch of messages
      const messages = this.backpressure.getItems(10);
      messages.forEach(msg => this.notifySubscribers(msg));

      // Schedule next processing
      this.messageProcessor = window.setTimeout(() => processMessages(), 100);
    };

    processMessages();
  }

  private startKeepAlive(): void {
    if (this.keepAliveInterval !== null) {
      return;
    }

    const sendHeartbeat = () => {
      if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
        return;
      }

      try {
        this.socket.send(JSON.stringify({ type: "ping", timestamp: Date.now() }));
      } catch (error) {
        console.warn("Failed to send websocket ping", error);
      }
    };

    sendHeartbeat();
    this.keepAliveInterval = window.setInterval(sendHeartbeat, 15000);
  }

  private stopKeepAlive(): void {
    if (this.keepAliveInterval !== null) {
      window.clearInterval(this.keepAliveInterval);
      this.keepAliveInterval = null;
    }
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
    const token = localStorage.getItem("access_token") || localStorage.getItem("token");
    if (!token) throw new Error("No access token");
    
    // If path is already a full URL (starts with ws:// or wss://), use it directly
    if (path.startsWith('ws://') || path.startsWith('wss://')) {
        const sep = path.includes("?") ? "&" : "?";
        return `${path}${sep}token=${encodeURIComponent(token)}`;
    }
    
    // Otherwise build from urlBase
    const noLeading = path.startsWith("/") ? path : `/${path}`;
    const sep = noLeading.includes("?") ? "&" : "?";
    return `${this.urlBase}${noLeading}${sep}token=${encodeURIComponent(token)}`;
  }

  /**
   * Ensure a single open connection to the given path.
   * Does NOT auto close on component unmounts.
   */
  ensureConnected(path: string = DEFAULT_PATH): WebSocket {
    // Check circuit breaker before attempting connection
    if (!this.circuitBreaker.canAttemptConnection()) {
      const waitTime = this.circuitBreaker.getWaitTime();
      throw new Error(`Circuit breaker is open. Wait ${waitTime.toFixed(1)}s before retry`);
    }

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
    if (this.socket) {
      try {
        if (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING) {
          this.socket.close(1000, "switching-endpoint");
        }
      } catch (err) {
        console.warn("Error closing previous socket:", err);
      }
      this.socket = null;
    }

    // Build URL with error handling
    let url: string;
    try {
      url = this.buildUrl(targetPath);
    } catch (err) {
      this.state = "error";
      throw err;
    }

    this.currentPath = targetPath;
    this.socket = new WebSocket(url);
    this.state = "connecting";
    
    // Setup event handlers outside the promise to avoid memory leaks
    const onOpen = () => {
      this.state = "open";
      this.circuitBreaker.recordSuccess();
      this.startKeepAlive();
    };
    
    const onError = (evt: Event) => {
      this.state = "error";
      this.circuitBreaker.recordFailure();
      this.onError?.(evt);
    };
    
    const onClose = (event: CloseEvent) => {
      this.state = "closed";
      this.stopKeepAlive();
      this.onClose?.(event);
    };
    
    const onMessage = (ev: MessageEvent) => {
      try {
        const payload = this.parseMessage(ev.data);
        
        // Add to backpressure buffer instead of direct notification
        const added = this.backpressure.addItem(payload);
        if (!added) {
          console.warn('🚨 Message dropped due to backpressure');
        }
      } catch (e) {
        console.error("Error processing WebSocket message:", e);
        // Still try to add error messages to buffer
        const errorPayload = { 
          type: "error", 
          message: "message_processing_error",
          error: String(e)
        };
        this.backpressure.addItem(errorPayload);
      }
    };
    
    // Add all event listeners
    this.socket.addEventListener("open", onOpen);
    this.socket.addEventListener("error", onError);
    this.socket.addEventListener("close", onClose);
    this.socket.addEventListener("message", onMessage);
    
    // Prepare waiter promise for waitUntilOpen
    this.openWaiter = new Promise<void>((resolve, reject) => {
      const socket = this.socket;
      if (!socket) {
        reject(new Error("Socket was cleared during connection setup"));
        return;
      }
      
      const cleanup = () => {
        socket.removeEventListener("open", promiseOnOpen);
        socket.removeEventListener("error", promiseOnError);
        socket.removeEventListener("close", promiseOnClose);
      };
      
      const promiseOnOpen = () => {
        cleanup();
        resolve();
      };
      
      const promiseOnError = () => {
        cleanup();
        reject(new Error("WebSocket error"));
      };
      
      const promiseOnClose = () => {
        cleanup();
        reject(new Error("WebSocket closed"));
      };
      
      // Add temporary listeners just for the promise
      socket.addEventListener("open", promiseOnOpen, { once: true });
      socket.addEventListener("error", promiseOnError, { once: true });
      socket.addEventListener("close", promiseOnClose, { once: true });
    });
    
    return this.socket;
  }

  private parseMessage(data: any): any {
    let payload: any;
    
    // Handle different message data types
    if (data instanceof Blob || data instanceof ArrayBuffer) {
      payload = { 
        type: "error", 
        message: "binary_message_not_supported",
        dataType: data.constructor.name
      };
    } 
    else if (typeof data === 'object' && data !== null) {
      payload = data;
    } 
    else if (typeof data === 'string') {
      try {
        payload = JSON.parse(data);
        console.log("Parsed payload:", payload);
      } catch (e) {
        console.warn("Received non-JSON string message:", data);
        payload = { 
          type: "message", 
          data: data 
        };
      }
    } 
    else {
      console.warn("Received message with unexpected format:", data);
      payload = { 
        type: "unknown", 
        message: "unhandled_message_format",
        data: String(data)
      };
    }
    
    return payload;
  }

  /**
   * Wait for the WebSocket connection to be established with retry logic.
   */
  async waitUntilOpen(
    timeoutMs = 5000,
    _maxRetries = 3,
    _initialDelayMs = 1000
  ): Promise<void> {
    // Circuit breaker will handle retry logic
    const waitTime = this.circuitBreaker.getWaitTime();
    if (waitTime > 0) {
      console.log(`Circuit breaker active, waiting ${waitTime.toFixed(1)}s before connection attempt`);
      await new Promise(resolve => setTimeout(resolve, waitTime * 1000));
    }

    // If already open, fast-path
    if (this.socket?.readyState === WebSocket.OPEN && this.state === "open") {
      console.debug("WebSocket already connected");
      return;
    }

    if (!this.openWaiter) {
      throw new Error("No connection in progress. Call ensureConnected() first.");
    }

    const waiter = this.openWaiter;
    let timeoutHandle: number | undefined;

    const timeoutPromise = new Promise<void>((_, reject) => {
      timeoutHandle = window.setTimeout(
        () => reject(new Error(`WebSocket connection timed out after ${timeoutMs}ms`)),
        timeoutMs
      );
    });

    try {
      await Promise.race([waiter, timeoutPromise]);
      console.debug("WebSocket connection established successfully");
    } catch (error) {
      this.circuitBreaker.recordFailure();
      throw error;
    } finally {
      if (timeoutHandle !== undefined) {
        window.clearTimeout(timeoutHandle);
      }
    }
  }

  /**
   * Send a message. The server expects JSON objects with a "type".
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
   * Close the socket explicitly.
   */
  close(code: number = 1000, reason: string = "client_close"): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      try {
        this.stopKeepAlive();
        this.socket.close(code, reason);
      } finally {
        this.state = "closed";
      }
    }
  }

  /**
   * Subscribe to all incoming WS messages (already JSON-parsed).
   */
  subscribe(handler: MessageHandler): () => void {
    this.subscribers.add(handler);
    return () => this.unsubscribe(handler);
  }

  unsubscribe(handler: MessageHandler): void {
    this.subscribers.delete(handler);
  }

  private notifySubscribers(payload: any): void {
    const subscribers = Array.from(this.subscribers);
    for (const fn of subscribers) {
      try {
        fn(payload);
      } catch (error) {
        console.error("Error in WebSocket subscriber:", error);
        // Continue to other subscribers even if one fails
      }
    }
  }

  // Circuit breaker controls
  resetCircuitBreaker(): void {
    this.circuitBreaker.reset();
    console.log('🔧 Circuit breaker reset');
  }

  getCircuitBreakerStatus(): {
    state: string;
    failures: number;
    waitTime: number;
  } {
    return this.circuitBreaker.getDetailedState();
  }

  // Backpressure controls
  getBackpressureStatus(): {
    bufferSize: number;
    pressure: number;
    droppedMessages: number;
    incomingRate: number;
    processingRate: number;
  } {
    const stats = this.backpressure.getStats();
    return {
      bufferSize: stats.bufferSize,
      pressure: stats.pressure,
      droppedMessages: stats.droppedMessages,
      incomingRate: stats.incomingRate,
      processingRate: stats.processingRate
    };
  }

  clearBackpressureBuffer(): void {
    this.backpressure.clear();
    console.log('🧹 Backpressure buffer cleared');
  }

  /**
   * Static helpers for older call sites that used class-level subscribe/unsubscribe.
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

  // Cleanup
  destroy(): void {
    if (this.messageProcessor) {
      clearTimeout(this.messageProcessor);
      this.messageProcessor = null;
    }
    this.close();
    this.subscribers.clear();
    this.backpressure.clear();
  }
}