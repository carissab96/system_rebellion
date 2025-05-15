import { EventEmitter } from 'events';

export type WebSocketMessage = {
  type: string;
  data?: any;
  error?: string;
  timestamp?: number;
};

export class WebSocketManager extends EventEmitter {
  private static instance: WebSocketManager;
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second
  private maxReconnectDelay = 30000; // Max 30 seconds
  private isConnected = false;
  private isConnecting = false;
  private url: string;
  private messageQueue: any[] = [];

  private constructor(url: string) {
    super();
    this.url = url;
  }

  public static getInstance(url: string): WebSocketManager {
    if (!WebSocketManager.instance) {
      WebSocketManager.instance = new WebSocketManager(url);
    }
    return WebSocketManager.instance;
  }

  public connect(): Promise<boolean> {
    if (this.isConnected || this.isConnecting) {
      console.log('WebSocket already connected or connecting');
      return Promise.resolve(this.isConnected);
    }

    this.isConnecting = true;

    return new Promise((resolve) => {
      try {
        console.log(`🌐 Connecting to WebSocket at ${this.url}`);
        this.socket = new WebSocket(this.url);

        this.socket.onopen = () => this.handleOpen(resolve);
        this.socket.onmessage = (event) => this.handleMessage(event);
        this.socket.onclose = () => this.handleClose();
        this.socket.onerror = (error) => this.handleError(error);
      } catch (error) {
        console.error('WebSocket connection error:', error);
        this.handleReconnect();
        resolve(false);
      }
    });
  }

  private handleOpen(resolve: (value: boolean) => void) {
    console.log('✅ WebSocket connected');
    this.isConnected = true;
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000; // Reset delay on successful connection
    
    // Process any queued messages
    this.processMessageQueue();
    
    this.emit('connected');
    resolve(true);
  }

  private handleMessage(event: MessageEvent) {
    try {
      const message = JSON.parse(event.data);
      this.emit('message', message);
      
      // Emit specific message types as their own events
      if (message.type) {
        this.emit(message.type, message);
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }

  private handleClose() {
    console.log('WebSocket connection closed');
    this.isConnected = false;
    this.isConnecting = false;
    this.socket = null;
    this.emit('disconnected');
    this.handleReconnect();
  }

  private handleError(error: Event) {
    console.error('WebSocket error:', error);
    this.emit('error', error);
  }

  private handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      this.emit('reconnect_failed');
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), this.maxReconnectDelay);
    
    console.log(`⏳ Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      this.connect().catch(console.error);
    }, delay);
  }

  public send(message: any): void {
    if (!this.isConnected) {
      console.log('WebSocket not connected, queueing message:', message);
      this.messageQueue.push(message);
      return;
    }

    try {
      const messageString = typeof message === 'string' ? message : JSON.stringify(message);
      this.socket?.send(messageString);
    } catch (error) {
      console.error('Error sending WebSocket message:', error);
      this.messageQueue.push(message); // Requeue failed message
    }
  }

  private processMessageQueue() {
    while (this.messageQueue.length > 0 && this.isConnected) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  public disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.isConnected = false;
    this.isConnecting = false;
    this.reconnectAttempts = 0;
    this.messageQueue = [];
    this.emit('disconnected');
  }

  public getConnectionStatus(): 'connected' | 'connecting' | 'disconnected' {
    if (this.isConnected) return 'connected';
    if (this.isConnecting) return 'connecting';
    return 'disconnected';
  }
}

// Create a singleton instance
export const webSocketManager = WebSocketManager.getInstance(
  window.location.protocol === 'https:' 
    ? `wss://${window.location.host}/ws/system-metrics`
    : `ws://${window.location.host}/ws/system-metrics`
);
