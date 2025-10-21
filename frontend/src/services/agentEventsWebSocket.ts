// services/agentEventsWebSocket.ts
// WebSocket service for /api/ws/agent-events endpoint
// Modeled after the working websocket.ts service

import { CircuitBreaker } from './circuitBreaker';
import { BackpressureHandler } from './backpressure';

type ConnectionState = "idle" | "connecting" | "open" | "closed" | "error";
type MessageHandler = (data: any) => void;

const DEFAULT_PATH = "ws://localhost:8000/api/ws/agent-events";

export class AgentEventsWebSocketService {
  private static instance: AgentEventsWebSocketService | null = null;

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

  // Optional external callbacks
  onError?: (evt: Event) => void;
  onClose?: () => void;

  private constructor(wsBaseUrl: string) {
    this.urlBase = wsBaseUrl.replace(/\/$/, "");
    
    this.circuitBreaker = new CircuitBreaker({
      name: 'agent-events-websocket',
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
        console.log(`🚨 Agent Events backpressure active, waiting ${(waitTime * 1000).toFixed(0)}ms`);
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

  /**
   * Singleton accessor
   */
  static getInstance(wsBaseUrl: string): AgentEventsWebSocketService {
    if (!AgentEventsWebSocketService.instance) {
      AgentEventsWebSocketService.instance = new AgentEventsWebSocketService(wsBaseUrl);
    }
    return AgentEventsWebSocketService.instance;
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
   */
  ensureConnected(path: string = DEFAULT_PATH): WebSocket {
    // Check circuit breaker before attempting connection
    if (!this.circuitBreaker.canAttemptConnection()) {
      const waitTime = this.circuitBreaker.getWaitTime();
      throw new Error(`Agent Events circuit breaker is open. Wait ${waitTime.toFixed(1)}s before retry`);
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
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      try {
        this.socket.close(1000, "switching-endpoint");
      } catch {
        // ignore
      }
    }

    const url = this.buildUrl(targetPath);
    console.log('🎭 Agent Events: Connecting to URL:', url);
    this.currentPath = targetPath;
    this.socket = new WebSocket(url);
    this.state = "connecting";
    
    // Prepare waiter promise for waitUntilOpen
    this.openWaiter = new Promise<void>((resolve, reject) => {
      const cleanup = () => {
        if (this.socket) {
          this.socket.removeEventListener("open", onOpen);
          this.socket.removeEventListener("error", onError);
          this.socket.removeEventListener("close", onClose);
        }
      };
      
      const onOpen = () => {
        this.state = "open";
        this.circuitBreaker.recordSuccess();
        cleanup();
        resolve();
      };
      
      const onError = (evt: Event) => {
        this.state = "error";
        this.circuitBreaker.recordFailure();
        cleanup();
        reject(new Error("Agent Events WebSocket error"));
        this.onError?.(evt);
      };
      
      const onClose = () => {
        this.state = "closed";
        cleanup();
        reject(new Error("Agent Events WebSocket closed"));
        this.onClose?.();
      };
    
      this.socket!.addEventListener("open", onOpen);
      this.socket!.addEventListener("error", onError);
      this.socket!.addEventListener("close", onClose);
    
      // Enhanced message handler with backpressure
      this.socket!.addEventListener("message", (ev: MessageEvent) => {
        try {
          const payload = this.parseMessage(ev.data);
          
          // Add to backpressure buffer instead of direct notification
          const added = this.backpressure.addItem(payload);
          if (!added) {
            console.warn('🚨 Agent Events message dropped due to backpressure');
          }
        } catch (e) {
          console.error("Error processing Agent Events WebSocket message:", e);
          const errorPayload = { 
            type: "error", 
            message: "message_processing_error",
            error: String(e)
          };
          this.backpressure.addItem(errorPayload);
        }
      });
    });
    
    return this.socket;
  }

  private parseMessage(data: any): any {
    let payload: any;
    
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
        console.log("Agent Events parsed payload:", payload);
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

  async waitUntilOpen(timeoutMs = 5000): Promise<void> {
    const waitTime = this.circuitBreaker.getWaitTime();
    if (waitTime > 0) {
      console.log(`Agent Events circuit breaker active, waiting ${waitTime.toFixed(1)}s before connection attempt`);
      await new Promise(resolve => setTimeout(resolve, waitTime * 1000));
    }

    if (this.socket?.readyState === WebSocket.OPEN && this.state === "open") {
      console.debug("Agent Events WebSocket already connected");
      return;
    }

    if (!this.openWaiter) {
      throw new Error("No connection in progress. Call ensureConnected() first.");
    }

    const waiter = this.openWaiter;
    let timeoutHandle: number | undefined;

    const timeoutPromise = new Promise<void>((_, reject) => {
      timeoutHandle = window.setTimeout(
        () => reject(new Error(`Agent Events WebSocket connection timed out after ${timeoutMs}ms`)),
        timeoutMs
      );
    });

    try {
      await Promise.race([waiter, timeoutPromise]);
      console.debug("Agent Events WebSocket connection established successfully");
    } catch (error) {
      this.circuitBreaker.recordFailure();
      throw error;
    } finally {
      if (timeoutHandle !== undefined) {
        window.clearTimeout(timeoutHandle);
      }
    }
  }

  send(msg: Record<string, unknown> | string): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error("Agent Events WebSocket is not open");
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

  close(code: number = 1000, reason: string = "client_close"): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      try {
        this.socket.close(code, reason);
      } finally {
        this.state = "closed";
      }
    }
  }

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
        console.error("Error in Agent Events WebSocket subscriber:", error);
      }
    }
  }

  resetCircuitBreaker(): void {
    this.circuitBreaker.reset();
    console.log('🔧 Agent Events circuit breaker reset');
  }

  getCircuitBreakerStatus() {
    return this.circuitBreaker.getDetailedState();
  }

  getBackpressureStatus() {
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
    console.log('🧹 Agent Events backpressure buffer cleared');
  }

  getSocket(): WebSocket | null {
    return this.socket;
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN && this.state === "open";
  }

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
