import { AppDispatch } from "@/store/store";
import { updateMetrics as updateCPUMetrics } from "@/store/slices/metrics/CPUSlice";
import { updateMetrics as updateMemoryMetrics } from "@/store/slices/metrics/MemorySlice";
import { updateMetrics as updateDiskMetrics } from "@/store/slices/metrics/DiskSlice";
import { updateMetrics as updateNetworkMetrics } from "@/store/slices/metrics/NetworkSlice";

// Message types
export interface CPUMetricsMessage {
  type: 'cpu_metrics';
  data: {
    usage_percent: number;
    temperature: number;
    cores: number[];
    frequency_mhz: number;
    physical_cores: number;
    logical_cores: number;
    top_processes: Array<{
      pid: number;
      name: string;
      cpu_percent: number;
      memory_percent: number;
    }>;
  };
}

export interface MemoryMetricsMessage {
  type: 'memory_metrics';
  data: {
    usage_percent: number;
    total: number;
    available: number;
    used: number;
    free: number;
    swap_total: number;
    swap_used: number;
    swap_free: number;
    swap_usage_percent: number;
  };
}

export interface DiskMetricsMessage {
  type: 'disk_metrics';
  data: {
    usage_percent: number;
    total: number;
    used: number;
    free: number;
    read_bytes: number;
    write_bytes: number;
    read_count: number;
    write_count: number;
    read_time: number;
    write_time: number;
  };
}

export interface NetworkMetricsMessage {
  type: 'network_metrics';
  data: {
    usage_percent: number;
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
    err_in: number;
    err_out: number;
    drop_in: number;
    drop_out: number;
  };
}

export type WebSocketMessage = 
  | CPUMetricsMessage 
  | MemoryMetricsMessage 
  | DiskMetricsMessage 
  | NetworkMetricsMessage;

// Circuit Breaker State
export interface CircuitBreakerState {
  status: 'closed' | 'open' | 'half-open';
  failures: number;
  lastFailureTime: number;
  nextAttemptTime: number;
}

// Rate Limiter
class RateLimiter {
  private requests: number[] = [];
  private readonly limit: number;
  private readonly windowMs: number;

  constructor(limit: number, windowMs: number) {
    this.limit = limit;
    this.windowMs = windowMs;
  }

  public checkLimit(): boolean {
    const now = Date.now();
    this.requests = this.requests.filter(timestamp => now - timestamp < this.windowMs);
    
    if (this.requests.length >= this.limit) {
      return false;
    }
    
    this.requests.push(now);
    return true;
  }
}

// Backpressure Handler
class BackpressureHandler {
  private queue: Array<() => Promise<void>> = [];
  private isProcessing = false;
  private readonly maxQueueSize: number;

  constructor(maxQueueSize = 100) {
    this.maxQueueSize = maxQueueSize;
  }

  public async addToQueue<T>(task: () => Promise<T>): Promise<T> {
    if (this.queue.length >= this.maxQueueSize) {
      throw new Error('Backpressure: Queue limit reached');
    }

    return new Promise((resolve, reject) => {
      const wrappedTask = async () => {
        try {
          const result = await task();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      };

      this.queue.push(wrappedTask);
      this.processQueue();
    });
  }

  private async processQueue(): Promise<void> {
    if (this.isProcessing || this.queue.length === 0) return;

    this.isProcessing = true;
    const task = this.queue.shift();

    if (task) {
      try {
        await task();
      } finally {
        this.isProcessing = false;
        setImmediate(() => this.processQueue());
      }
    } else {
      this.isProcessing = false;
    }
  }
}

// Circuit Breaker
class CircuitBreaker {
  private state: CircuitBreakerState = {
    status: 'closed',
    failures: 0,
    lastFailureTime: 0,
    nextAttemptTime: 0
  };

  constructor(
    private readonly maxFailures = 3,
    private readonly resetTimeout = 30000,
    private readonly exponentialBackoffFactor = 1.5
  ) {}

  public canAttemptConnection(): boolean {
    const now = Date.now();
    
    if (this.state.status === 'closed') return true;
    if (this.state.status === 'half-open') return true;
    if (now >= this.state.nextAttemptTime) {
      this.state.status = 'half-open';
      return true;
    }
    
    return false;
  }

  public recordSuccess(): void {
    if (this.state.status === 'half-open') {
      this.reset();
    }
  }

  public recordFailure(): void {
    const now = Date.now();
    this.state.failures++;
    this.state.lastFailureTime = now;
    
    if (this.state.status === 'half-open' || this.state.failures >= this.maxFailures) {
      this.state.status = 'open';
      const backoffMultiplier = Math.pow(
        this.exponentialBackoffFactor,
        Math.min(this.state.failures - this.maxFailures, 5)
      );
      this.state.nextAttemptTime = now + Math.min(
        this.resetTimeout * backoffMultiplier,
        300000 // 5 minutes max
      );
    }
  }

  public getState(): CircuitBreakerState {
    return { ...this.state };
  }

  public getWaitTimeSeconds(): number {
    const now = Date.now();
    return Math.ceil(Math.max(0, this.state.nextAttemptTime - now) / 1000);
  }

  public reset(): void {
    this.state = {
      status: 'closed',
      failures: 0,
      lastFailureTime: 0,
      nextAttemptTime: 0
    };
  }
}

// Main WebSocket Service
export class WebSocketService {
  resetCircuitBreaker() {
    throw new Error('Method not implemented.');
  }
  getCircuitBreakerState(): import("react").SetStateAction<CircuitBreakerState | null> {
    throw new Error('Method not implemented.');
  }
  private socket: WebSocket | null = null;
  private dispatch: AppDispatch;
  private retryCount = 0;
  private maxRetries = 5;
  private retryDelay = 3000;
  private retryTimeout: NodeJS.Timeout | null = null;
  private circuitBreaker: CircuitBreaker;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private lastMessageTime = 0;
  private heartbeatTimeout = 20000;
  private isConnected = false;
  private isProcessingQueue = false;
  private messageQueue: Array<() => void> = [];
  private backpressureHandler: BackpressureHandler;
  private rateLimiter: RateLimiter;

  // Event handlers
  public onMessage: (message: WebSocketMessage) => void = () => {};
  public onError: (error: Error) => void = () => {};
  public onConnectionStatusChange: (
    status: 'connecting' | 'connected' | 'disconnected' | 'error' | 'circuit-open'
  ) => void = () => {};

  constructor(dispatch: AppDispatch) {
    this.dispatch = dispatch;
    this.circuitBreaker = new CircuitBreaker();
    this.backpressureHandler = new BackpressureHandler(100);
    this.rateLimiter = new RateLimiter(10, 1000); // 10 messages per second
  }

  // Get WebSocket URL with authentication token
  private getWebSocketUrl(): string {
    const token = localStorage.getItem('token');
    if (!token) {
      throw new Error('No authentication token found');
    }

    let baseUrl: string;
    if (process.env.NODE_ENV === 'development') {
      // Try proxy first, fall back to direct connection
      baseUrl = this.retryCount > 0 
        ? 'ws://localhost:8000'  // Fallback to direct connection
        : 'ws://localhost:5173'; // First try Vite proxy
    } else {
      baseUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`;
    }

    return `${baseUrl}/ws/system-metrics?token=${encodeURIComponent(token)}`;
  }

  // Connection management
  public connect(): void {
    if (this.isConnected || (this.socket && (
      this.socket.readyState === WebSocket.OPEN || 
      this.socket.readyState === WebSocket.CONNECTING
    ))) {
      return;
    }

    if (!this.circuitBreaker.canAttemptConnection()) {
      const waitTime = this.circuitBreaker.getWaitTimeSeconds();
      console.log(`🚨 Circuit breaker is open, cannot connect for ${waitTime}s`);
      this.onError(new Error(`Connection attempts are blocked for ${waitTime} seconds due to previous failures`));
      this.onConnectionStatusChange('circuit-open');
      this.scheduleReconnect();
      return;
    }

    try {
      const url = this.getWebSocketUrl();
      console.log('🦔 Sir Hawkington: Connecting to WebSocket...', url);
      
      this.socket = new WebSocket(url);
      this.setupEventListeners();
      this.onConnectionStatusChange('connecting');
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      this.onError(error as Error);
      this.circuitBreaker.recordFailure();
      this.onConnectionStatusChange('error');
      this.scheduleReconnect();
    }
  }

  public disconnect(): void {
    this.isConnected = false;
    
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
      this.retryTimeout = null;
    }
    
    this.stopHeartbeatMonitoring();
    
    if (this.socket) {
      try {
        if (this.socket.readyState === WebSocket.OPEN || 
            this.socket.readyState === WebSocket.CONNECTING) {
          this.socket.close(1000, 'Client disconnected');
        }
      } catch (error) {
        console.error('Error closing WebSocket:', error);
      } finally {
        this.socket = null;
      }
    }
    
    this.onConnectionStatusChange('disconnected');
  }

  public reconnect(): void {
    console.log('🔄 Attempting to reconnect...');
    this.disconnect();
    this.connect();
  }

  // Message handling
  public sendMessage(message: unknown): boolean {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.warn('⚠️ Cannot send message, WebSocket is not open');
      // Queue the message if not connected
      this.messageQueue.push(() => this.sendMessage(message));
      if (!this.isConnected) {
        this.reconnect();
      }
      return false;
    }

    try {
      if (!this.rateLimiter.checkLimit()) {
        console.warn('⚠️ Rate limit exceeded, message queued');
        this.messageQueue.push(() => this.sendMessage(message));
        return false;
      }

      const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
      this.socket.send(messageStr);
      return true;
    } catch (error) {
      console.error('🚨 Error sending WebSocket message:', error);
      this.messageQueue.push(() => this.sendMessage(message));
      return false;
    }
  }

  // Event listeners
  private setupEventListeners(): void {
    if (!this.socket) return;

    this.socket.onopen = (_event: Event) => {
      console.log('🦔 Sir Hawkington: WebSocket connection established');
      this.isConnected = true;
      this.retryCount = 0;
      this.circuitBreaker.recordSuccess();
      this.onConnectionStatusChange('connected');
      this.startHeartbeatMonitoring();
      
      // Process any queued messages
      this.processMessageQueue();
      
      // Request system info with a reasonable update interval (5 seconds)
      this.sendMessage({
        type: 'request_system_info',
        interval: 5000
      });
    };

    this.socket.onmessage = (event: MessageEvent) => {
      try {
        const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data;
        console.log('📨 WebSocket message received:', data);

        // Update last message time for heartbeat
        this.lastMessageTime = Date.now();

        // Process message based on type
        if (data && data.type) {
          switch (data.type) {
            case 'cpu_metrics':
              this.dispatch(updateCPUMetrics(data.payload));
              break;
            case 'memory_metrics':
              this.dispatch(updateMemoryMetrics(data.payload));
              break;
            case 'disk_metrics':
              this.dispatch(updateDiskMetrics(data.payload));
              break;
            case 'network_metrics':
              this.dispatch(updateNetworkMetrics(data.payload));
              break;
            case 'rate_limit':
              this.handleRateLimit(
                data.retry_after || 5,
                data.message || 'Rate limit exceeded'
              );
              break;
            case 'connection_established':
              console.log('🦔 Connection established:', data.message);
              break;
            case 'heartbeat':
              return; // Don't log heartbeats to reduce noise
            case 'circuit_status':
              console.log('🔌 Circuit status:', data.status);
              this.onConnectionStatusChange('circuit-open');
              break;
            default:
              console.warn('⚠️ Unhandled message type:', data.type);
          }
        } else {
          console.warn('⚠️ Received message without type:', data);
        }
      } catch (error) {
        console.error('🚨 Failed to handle WebSocket message:', error);
        this.onError(error as Error);
      }
    };

    this.socket.onerror = (error: Event) => {
      console.error('🚨 WebSocket error:', error);
      const errorMessage = 'WebSocket connection error';
      this.onError(new Error(errorMessage));
      this.circuitBreaker.recordFailure();
      this.onConnectionStatusChange('error');
      
      // Schedule reconnection with exponential backoff
      if (this.retryCount < this.maxRetries) {
        const delay = Math.min(1000 * Math.pow(2, this.retryCount), 30000);
        console.log(`⏳ Scheduling reconnection attempt in ${delay}ms...`);
        
        if (this.retryTimeout) {
          clearTimeout(this.retryTimeout);
        }
        
        this.retryTimeout = setTimeout(() => {
          console.log('🔄 Attempting to reconnect...');
          this.reconnect();
        }, delay);
      }
    };

    this.socket.onclose = (event: CloseEvent) => {
      console.log('🦔 Sir Hawkington: WebSocket closed:', event.code, event.reason);
      this.isConnected = false;
      this.socket = null;
      this.stopHeartbeatMonitoring();
      this.onConnectionStatusChange('disconnected');
      
      if (event.code === 1000) {
        console.log('🦔 WebSocket closed normally');
      } else if (event.code === 1008) {
        // Authentication error
        this.circuitBreaker.recordFailure();
        const error = new Error(`Authentication error: ${event.reason || 'Invalid token'}`);
        console.error('🔒', error.message);
        this.onError(error);
      } else if (event.code === 1013) {
        // Server overload or rate limited
        this.circuitBreaker.recordFailure();
        
        // Extract retry time from message if available
        const retryMatch = event.reason?.match(/try again in (\d+) seconds?/i);
        const retryAfter = retryMatch ? parseInt(retryMatch[1], 10) * 1000 : 5000;
        
        this.handleRateLimit(
          retryAfter / 1000, // Convert to seconds
          event.reason || 'Server is currently overloaded'
        );
      } else {
        // Other errors - use exponential backoff
        this.scheduleReconnect();
      }
    };
  }

  // Heartbeat monitoring
  private startHeartbeatMonitoring(): void {
    this.stopHeartbeatMonitoring();
    this.lastMessageTime = Date.now();
    
    this.heartbeatInterval = setInterval(() => {
      if (!this.isConnected || !this.socket) return;
      
      const timeSinceLastMessage = Date.now() - this.lastMessageTime;
      if (timeSinceLastMessage > this.heartbeatTimeout) {
        console.warn('⚠️ No message received, reconnecting...');
        this.reconnect();
      }
    }, 5000);
  }

  private stopHeartbeatMonitoring(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  // Rate limiting
  private handleRateLimit(retryAfter: number, message: string): void {
    console.warn(`⚠️ Rate limited by server. ${message}`);
    
    // Reset retry count to prevent exponential backoff
    this.retryCount = 0;
    
    // Clear any existing timeout
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }
    
    // Add some jitter to prevent thundering herd
    const jitter = Math.random() * 2000; // Up to 2 seconds of jitter
    const delay = Math.max(1000, retryAfter * 1000 + jitter); // At least 1 second
    
    console.log(`⏳ Server requested delay: ${retryAfter}s (with jitter: ${Math.round(delay/1000)}s)`);
    
    this.retryTimeout = setTimeout(() => {
      console.log('🔄 Retrying after rate limit...');
      this.reconnect();
    }, delay);
    
    // Notify consumers about the rate limit
    this.onError(new Error(`Rate limited: ${message}`));
    this.onConnectionStatusChange('connecting');
  }

  // Message queue processing
  private async processMessageQueue(): Promise<void> {
    if (this.isProcessingQueue || this.messageQueue.length === 0) return;
    
    this.isProcessingQueue = true;
    
    try {
      // Process messages with backpressure handling
      await this.backpressureHandler.addToQueue(async () => {
        while (this.messageQueue.length > 0) {
          const message = this.messageQueue.shift();
          if (message) {
            try {
              message();
            } catch (error) {
              console.error('Error processing queued message:', error);
            }
          }
          
          // Small delay to prevent UI freezing
          if (this.messageQueue.length > 0) {
            await new Promise(resolve => setTimeout(resolve, 5));
          }
        }
      });
    } catch (error) {
      console.error('Backpressure error:', error);
      // If we hit backpressure, try again after a delay
      setTimeout(() => this.processMessageQueue(), 1000);
    } finally {
      this.isProcessingQueue = false;
    }
  }

  // Schedule a reconnection attempt with exponential backoff
  private scheduleReconnect(): void {
    if (this.retryCount >= this.maxRetries) {
      console.error('🦉 Sir Hawkington exhausted all reconnection attempts');
      this.onError(new Error('Failed to establish WebSocket connection after multiple attempts'));
      this.onConnectionStatusChange('error');
      
      // Reset retry count after a while to allow future reconnection attempts
      setTimeout(() => {
        this.retryCount = 0;
      }, 60000); // Reset after 60 seconds
      return;
    }

    this.retryCount++;
    const baseDelay = Math.min(this.retryDelay * Math.pow(2, this.retryCount - 1), 30000);
    const jitter = Math.random() * 1000; // Add up to 1s of jitter
    const delay = Math.min(baseDelay + jitter, 30000); // Cap at 30s
    
    console.log(`⏳ Scheduling reconnection attempt ${this.retryCount}/${this.maxRetries} in ${Math.round(delay/1000)}s...`);
    
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
    }
    
    this.retryTimeout = setTimeout(() => {
      if (!this.isConnected) {
        console.log('🔄 Attempting to reconnect...');
        this.connect();
      }
    }, delay);
    
    this.onConnectionStatusChange('connecting');
  }
}
// Create a single instance of WebSocketService
let webSocketService: WebSocketService | null = null;

export const initWebSocket = (dispatch: AppDispatch): WebSocketService => {
  if (!webSocketService) {
    webSocketService = new WebSocketService(dispatch);
    
    // Set up event handlers
    webSocketService.onError = (error) => {
      console.error('WebSocket error:', error);
    };

    webSocketService.onConnectionStatusChange = (status) => {
      console.log('WebSocket connection status:', status);
    };

    // Connect to the WebSocket server
    webSocketService.connect();
  }
  
  return webSocketService;
};

export const getWebSocketService = (): WebSocketService => {
  if (!webSocketService) {
    throw new Error('WebSocketService has not been initialized. Call initWebSocket first.');
  }
  return webSocketService;
};

export default WebSocketService;

