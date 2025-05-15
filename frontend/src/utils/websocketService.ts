// src/utils/websocketService.ts
class WebSocketService {
    private socket: WebSocket | null = null;
    private reconnectAttempts = 0;
    private readonly MAX_ATTEMPTS = 5;
    private listeners: { [event: string]: Array<(...args: any[]) => void> } = {};
    private url: string = '';
    private connectionTimeoutId: number | null = null;
    
    constructor() {
      // Initialize with default URL, but don't connect yet
      this.updateUrl();
      console.log("🚀 WebSocketService initialized");
    }
    
    // Update the WebSocket URL based on current location
    private updateUrl(): void {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const host = window.location.host;
      this.url = `${protocol}//${host}/ws/system-metrics`;
      console.log("🔗 WebSocket URL set to:", this.url);
    }
  
    // Connect to the WebSocket server
    public connect(customUrl?: string): boolean {
      if (customUrl) this.url = customUrl;
      
      if (this.socket) {
        if (this.socket.readyState === WebSocket.OPEN) {
          console.log("✅ WebSocket already connected");
          return true;
        } else if (this.socket.readyState === WebSocket.CONNECTING) {
          console.log("⏳ WebSocket connection already in progress");
          return true;
        }
      }
      
      console.log("🔌 Connecting to WebSocket:", this.url);
      try {
        this.socket = new WebSocket(this.url);
        
        // Add a connection timeout
        setTimeout(() => {
          if (this.socket && this.socket.readyState === WebSocket.CONNECTING) {
            console.error("⏱️ WebSocket connection timed out");
            this.socket.close();
            this.emit('error', new Error('Connection timeout'));
          }
        }, 5000); // 5 second connection timeout
        
        this.socket.onopen = () => {
          console.log("✅ WebSocket connected");
          this.reconnectAttempts = 0;
          this.emit('open'); // Emit open event for hooks
          this.emit('connected'); // Emit connected event for slice
        };
        
        this.socket.onclose = (event) => {
          console.log("👋 WebSocket closed:", event);
          this.emit('close'); // Emit close event for hooks
          this.emit('disconnected'); // Emit disconnected event for slice
          this.handleReconnect();
        };
        
        this.socket.onerror = (event) => {
          console.error("❌ WebSocket error:", event);
          this.emit('error', event);
        };
        
        this.socket.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.emit('message', data);
          } catch (err) {
            console.error("❌ Error parsing message:", err);
          }
        };
        
        return true;
      } catch (error) {
        console.error("❌ Error connecting to WebSocket:", error);
        this.emit('error', error);
        return false;
      }
    }
  
    // Disconnect from the WebSocket server
    public disconnect(): void {
      if (this.socket) {
        this.socket.close();
        this.socket = null;
      }
      if (this.connectionTimeoutId) {
        clearTimeout(this.connectionTimeoutId);
        this.connectionTimeoutId = null;
      }
      console.log("🔌 WebSocket disconnected");
    }
  
    // Check if websocket is connected
    public isConnected(): boolean {
      return this.socket?.readyState === WebSocket.OPEN;
    }
  
    // Send a message through the WebSocket
    public sendMessage(message: any): void {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.socket.send(typeof message === 'string' ? message : JSON.stringify(message));
      } else {
        console.error("❌ Cannot send message: WebSocket not connected");
      }
    }
  
    // Add an event listener
    public on(event: string, callback: (...args: any[]) => void): void {
      if (!this.listeners[event]) {
        this.listeners[event] = [];
      }
      this.listeners[event].push(callback);
    }
  
    // Remove an event listener
    public off(event: string, callback: (...args: any[]) => void): void {
      if (!this.listeners[event]) return;
      this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }
  
    // Emit an event to all listeners
    private emit(event: string, ...args: any[]): void {
      if (!this.listeners[event]) return;
      for (const callback of this.listeners[event]) {
        try {
          callback(...args);
        } catch (e) {
          console.error(`❌ Error in ${event} listener:`, e);
        }
      }
    }
  
    // Attempt to reconnect
    private handleReconnect(): void {
      if (this.reconnectAttempts >= this.MAX_ATTEMPTS) {
        console.error("❌ Max reconnection attempts reached");
        this.emit('error', new Error("Failed to reconnect after maximum attempts"));
        return;
      }
      
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      
      console.log(`🔄 Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.MAX_ATTEMPTS})...`);
      
      if (this.connectionTimeoutId) {
        clearTimeout(this.connectionTimeoutId);
      }
      
      this.connectionTimeoutId = window.setTimeout(() => {
        this.connect();
      }, delay);
    }
  }
  
  // Export a singleton instance
  const websocketService = new WebSocketService();
  export default websocketService;