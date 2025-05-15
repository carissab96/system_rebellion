// src/utils/websocketService.ts

// Simple event emitter implementation for browser compatibility
class EventEmitter {
  private events: { [key: string]: Function[] } = {};

  on(event: string, listener: (...args: any[]) => void): this {
    if (!this.events[event]) {
      this.events[event] = [];
    }
    this.events[event].push(listener);
    return this;
  }

  off(event: string, listener: (...args: any[]) => void): this {
    if (!this.events[event]) return this;
    this.events[event] = this.events[event].filter(l => l !== listener);
    return this;
  }

  emit(event: string, ...args: any[]): boolean {
    if (!this.events[event]) return false;
    // Create a copy of the listeners array to handle cases where listeners are removed during iteration
    const listeners = [...this.events[event]];
    listeners.forEach(listener => {
      try {
        listener(...args);
      } catch (error) {
        console.error(`Error in event listener for '${event}':`, error);
      }
    });
    return true;
  }

  once(event: string, listener: (...args: any[]) => void): this {
    const onceWrapper = (...args: any[]) => {
      this.off(event, onceWrapper);
      listener(...args);
    };
    return this.on(event, onceWrapper);
  }

  removeAllListeners(event?: string): this {
    if (event) {
      delete this.events[event];
    } else {
      this.events = {};
    }
    return this;
  }
}

type WebSocketMessage = {
  type: string;
  data?: any;
  error?: string;
  timestamp?: number;
};

// Sir Hawkington's Distinguished Type Definitions
type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

class WebSocketService {
    private static instance: WebSocketService;
    private socket: WebSocket | null = null;
    private reconnectAttempts = 0;
    private readonly MAX_ATTEMPTS = 5; 
    private reconnectDelay = 1000;
    private maxReconnectDelay = 30000;
    private isConnecting = false;
    private baseUrl: string = '';
    private connectionStatus: ConnectionStatus = 'disconnected';
    private messageCallback: ((data: WebSocketMessage) => void) | null = null;
    private eventEmitter = new EventEmitter();
    private reconnectTimeoutId: ReturnType<typeof setTimeout> | null = null;
    private heartbeatInterval: ReturnType<typeof setInterval> | null = null;
    private lastHeartbeat: number = 0;
    private readonly HEARTBEAT_INTERVAL = 30000; 
    private readonly HEARTBEAT_TIMEOUT = 10000; 

    // Sir Hawkington's Distinguished Private Constructor
    private constructor() {
        console.log("🎭 [WebSocketService] Sir Hawkington's Distinguished WebSocket Service Initialized");
        // Don't connect here, wait for explicit connect() call with URL
    }

    public static getInstance(): WebSocketService {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService();
        }
        return WebSocketService.instance;
    }

    // Initialize WebSocket connection with the provided URL
    public connect(url: string): void {
        // Clean up any existing connection
        this.cleanup();

        this.baseUrl = url;
        this.isConnecting = true;
        this.setConnectionStatus('connecting');
        
        console.log(`🔌 Connecting to WebSocket at: ${this.baseUrl}`);
        
        try {
            this.socket = new WebSocket(this.baseUrl);
            this.setupEventHandlers();
            
            // Set a connection timeout
            const connectionTimeout = setTimeout(() => {
                if (this.socket?.readyState === WebSocket.CONNECTING) {
                    console.error('❌ WebSocket connection timeout');
                    this.handleError(new Error('Connection timeout'));
                    this.cleanup();
                    this.attemptReconnect();
                }
            }, 10000); // 10 second timeout
            
            // Clean up timeout on successful connection or error
            const onConnectOrError = () => {
                clearTimeout(connectionTimeout);
                this.socket?.removeEventListener('open', onConnectOrError);
                this.socket?.removeEventListener('error', onConnectOrError);
            };
            
            this.socket.addEventListener('open', onConnectOrError);
            this.socket.addEventListener('error', onConnectOrError);
            
        } catch (err) {
            const error = err as Error;
            console.error('❌ Failed to create WebSocket:', error);
            this.handleError(error);
            this.attemptReconnect();
        }
    }

    // Setup WebSocket event handlers
    private setupEventHandlers(): void {
        if (!this.socket) return;
        
        this.socket.onopen = (event: Event) => {
            console.log('✅ WebSocket connection established');
            this.isConnecting = false;
            this.setConnectionStatus('connected');
            this.reconnectAttempts = 0;
            this.eventEmitter.emit('open', event);
            this.startHeartbeat();
        };
        
        this.socket.onmessage = (event: MessageEvent) => this.handleMessage(event);
        this.socket.onclose = (event: CloseEvent) => this.handleClose(event);
        this.socket.onerror = (event: Event) => this.handleError(event);
    }

    // Handle incoming WebSocket messages
    private handleMessage(event: MessageEvent): void {
        try {
            const message = JSON.parse(event.data as string) as WebSocketMessage;
            this.eventEmitter.emit('message', message);
            
            // Call the message callback if set
            if (this.messageCallback) {
                this.messageCallback(message);
            }
        } catch (error) {
            console.error('Error parsing WebSocket message:', error);
        }
    }

    // Handle WebSocket close events
    private handleClose(event: CloseEvent): void {
        console.log(`WebSocket connection closed: ${event.code} ${event.reason}`);
        this.cleanup();
        this.setConnectionStatus('disconnected');
        this.eventEmitter.emit('close', event);
        
        if (event.code !== 1000) { 
            this.attemptReconnect();
        }
    }
    
    // Handle WebSocket errors
    private handleError(error: Event | Error): void {
        console.error('WebSocket error:', error);
        this.setConnectionStatus('error');
        this.eventEmitter.emit('error', error);
        
        // Clean up and attempt to reconnect if this was a runtime error
        if (error instanceof Error) {
            this.cleanup();
            this.attemptReconnect();
        }
    }

    // Disconnect from WebSocket
    public disconnect(): void {
        console.log('🔌 Disconnecting WebSocket...');
        this.cleanup();
        this.setConnectionStatus('disconnected');
        this.eventEmitter.emit('close');
    }

    // Attempt to reconnect with exponential backoff
    private attemptReconnect(): void {
        if (this.reconnectAttempts >= this.MAX_ATTEMPTS) {
            console.error(`❌ Max reconnection attempts (${this.MAX_ATTEMPTS}) reached`);
            return;
        }
        
        // Calculate delay with exponential backoff
        const delay = Math.min(
            this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts),
            this.maxReconnectDelay
        );
        
        this.reconnectAttempts++;
        console.log(`🔄 Attempting to reconnect (${this.reconnectAttempts}/${this.MAX_ATTEMPTS}) in ${delay}ms...`);
        
        // Clear any existing timeout
        if (this.reconnectTimeoutId) {
            clearTimeout(this.reconnectTimeoutId);
        }
        
        // Set new timeout
        this.reconnectTimeoutId = setTimeout(() => {
            if (this.baseUrl) {
                this.connect(this.baseUrl);
            }
        }, delay) as unknown as NodeJS.Timeout;
    }

    // Clean up resources
    private cleanup(): void {
        // Clear heartbeat interval
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
            this.heartbeatInterval = null;
        }
        
        // Clear reconnect timeout
        if (this.reconnectTimeoutId) {
            clearTimeout(this.reconnectTimeoutId);
            this.reconnectTimeoutId = null;
        }
        
        // Clean up WebSocket
        if (this.socket) {
            // Remove all event listeners to prevent memory leaks
            this.socket.onopen = null;
            this.socket.onclose = null;
            this.socket.onerror = null;
            this.socket.onmessage = null;
            
            // Only close if not already closed
            if (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING) {
                this.socket.close();
            }
            this.socket = null;
        }
        
        this.isConnecting = false;
    }

    // Heartbeat management
    private startHeartbeat(): void {
        if (this.heartbeatInterval) {
            clearInterval(this.heartbeatInterval);
        }
        
        this.lastHeartbeat = Date.now();
        
        this.heartbeatInterval = setInterval(() => {
            if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
                console.warn('WebSocket not connected, skipping heartbeat');
                return;
            }
            
            try {
                this.socket.send(JSON.stringify({ type: 'ping' }));
                console.log('❤️ Heartbeat sent');
                
                // Check if we've missed too many heartbeats
                const timeSinceLastHeartbeat = Date.now() - this.lastHeartbeat;
                if (timeSinceLastHeartbeat > this.HEARTBEAT_TIMEOUT) {
                    console.error('💔 Heartbeat timeout, reconnecting...');
                    this.handleError(new Error('Heartbeat timeout'));
                    this.attemptReconnect();
                }
            } catch (error) {
                console.error('Error sending heartbeat:', error);
                this.handleError(error as Error);
            }
        }, this.HEARTBEAT_INTERVAL) as unknown as number;
    }

        
        // Clear any pending reconnection attempts
        this.cleanup();
        
        // Close the connection if it's open
        if (this.socket) {
            if (this.socket.readyState === WebSocket.OPEN) {
                this.socket.close(1000, 'User disconnected');
            } else if (this.socket.readyState === WebSocket.CONNECTING) {
                this.socket.close(1001, 'Connection aborted');
            }
            this.socket = null;
        }
        
        this.connectionStatus = 'disconnected';
        this.eventEmitter.emit('status', 'disconnected');
    }

    // Reconnect to WebSocket
    public reconnect(): void {
        if (this.socket) {
            this.socket.close();
        }
        this.cleanup();
        if (this.baseUrl) {
            this.connect(this.baseUrl);
        }
    }

    public sendMessage(message: WebSocketMessage): void {
        if (!this.isConnected()) {
            console.error("❌ Cannot send message: Not connected to WebSocket");
            console.error("🐹 The Hamsters are on strike! No connection available.");
            throw new Error('Not connected to WebSocket');
        }
        
        try {
            this.socket?.send(JSON.stringify(message));
            console.log("📤 Message sent:", message);
        } catch (error) {
            console.error("❌ Error sending message:", error);
            console.error("🐌 The Meth Snail dropped the message! How embarrassing...");
            throw error;
        }
    }

    public isConnected(): boolean {
        return this.socket?.readyState === WebSocket.OPEN;
    }

    public getConnectionState(): ConnectionStatus {
        return this.connectionStatus;
    }

    public setMessageCallback(callback: (data: WebSocketMessage) => void): void {
        console.log("🎭 Sir Hawkington is registering a distinguished message callback");
        this.messageCallback = callback;
        console.log("✅ Callback set with aristocratic precision:", !!this.messageCallback);
    }

    public resetReconnectAttempts(): void {
        console.log("🔄 Resetting reconnection attempts");
        this.reconnectAttempts = 0;
    }

    // Event emitter methods
    public on(event: string, listener: (...args: any[]) => void): void {
        this.eventEmitter.on(event, listener);
    }

    public off(event: string, listener: (...args: any[]) => void): void {
        this.eventEmitter.off(event, listener);
    }

    // Private helper methods
    private setConnectionStatus(status: ConnectionStatus): void {
        if (this.connectionStatus !== status) {
            this.connectionStatus = status;
            console.log(`🔌 Connection status: ${status}`);
            this.eventEmitter.emit('statusChange', status);
        }
    }
}

// Export a singleton instance as default
export default WebSocketService.getInstance();
