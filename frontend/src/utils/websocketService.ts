// src/utils/websocketService.ts
class WebSocketService {
  private socket: WebSocket | null = null;
  private reconnectAttempts = 0;
  private readonly MAX_ATTEMPTS = 5;
  private listeners: { [event: string]: Array<(...args: any[]) => void> } = {};
  private url: string = '';
  private connectionTimeoutId: number | null = null;
  private authenticated: boolean = false;
  private preventLogout: boolean = true; // Add this flag to control logout behavior
 
  
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

  private static get WS_URL(): string {
    return process.env.NODE_ENV === 'production' 
      ? `wss://${window.location.host}/api/ws` 
      : 'ws://localhost:8000/api/ws';
  }

  // Connect to the WebSocket server with authentication
  public connect(customUrl?: string): boolean {
    if (customUrl) this.url = customUrl;
    else this.url = WebSocketService.WS_URL;
    
    if (this.socket) {
      if (this.socket.readyState === WebSocket.OPEN) {
        console.log("✅ WebSocket already connected");
        return true;
      } else if (this.socket.readyState === WebSocket.CONNECTING) {
        console.log("⏳ WebSocket connection already in progress");
        return true;
      }
    }
    
    // Get authentication token from localStorage
    const token = localStorage.getItem('token');
    const hasAuth = !!token;
    
    // Append token to WebSocket URL if present
    let wsUrl = this.url;
    if (hasAuth) {
      wsUrl += (wsUrl.includes('?') ? '&' : '?') + `token=${encodeURIComponent(token!)}`;
      this.authenticated = true;
    } else {
      console.warn("🧙‍♂️ The Stick warns: Connecting to WebSocket without authentication");
      this.authenticated = false;
    }
    
    console.log("🔌 Connecting to WebSocket:", this.url);
    try {
      this.socket = new WebSocket(wsUrl);
      
      // Add a connection timeout
      this.connectionTimeoutId = window.setTimeout(() => {
        if (this.socket && this.socket.readyState === WebSocket.CONNECTING) {
          console.error("⏱️ WebSocket connection timed out");
          this.socket.close();
          // FIXED: Don't trigger error event that might cause logout
          console.log("🛡️ Connection timeout suppressed to prevent logout");
        }
      }, 5000); // 5 second connection timeout
      
      this.socket.onopen = () => {
        console.log("✅ WebSocket connected");
        if (this.connectionTimeoutId) {
          clearTimeout(this.connectionTimeoutId);
          this.connectionTimeoutId = null;
        }
        this.reconnectAttempts = 0;
        this.emit('open'); // Emit open event for hooks
        this.emit('connected'); // Emit connected event for slice
        
        // Send authentication message if needed
        if (hasAuth) {
          this.sendMessage({
            type: 'authenticate',
            token: token
          });
        }
      };
      
      this.socket.onclose = (event) => {
        console.log("👋 WebSocket closed:", event);
        
        // FIXED: Only emit standard close event, not auth errors
        // Prevent emitting 'close' from triggering reauth or logout
        this.emit('disconnected'); // Emit disconnected event for slice
        
        // Only log the close, don't emit to avoid logout
        console.log(`WebSocket closed with code ${event.code}: ${event.reason || 'No reason'}`);
        
        // Handle reconnect
        this.handleReconnect();
      };
      
      this.socket.onerror = (event) => {
        console.error("❌ WebSocket error:", event);
        
        // FIXED: Don't emit error events that might cause logout
        if (this.preventLogout) {
          console.log("🛡️ WebSocket error suppressed to prevent logout");
        } else {
          this.emit('error', event);
        }
      };
      
      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          // Handle authentication response
          if (data.type === 'auth_response') {
            this.authenticated = data.success;
            if (!data.success) {
              console.error("🚨 WebSocket authentication failed:", data.message);
              
              // FIXED: Don't emit auth_failed if we're preventing logout
              if (!this.preventLogout) {
                this.emit('auth_failed', data.message);
              } else {
                console.log("🛡️ Auth failure suppressed to prevent logout");
              }
            } else {
              console.log("✅ WebSocket authenticated successfully");
              this.emit('auth_success');
            }
          } else {
            // FIXED: Check for nethogs errors and suppress them
            if (data.error && typeof data.error === 'string' && 
                data.error.toLowerCase().includes('nethogs')) {
              console.warn("⚠️ Nethogs error detected and suppressed:", data.error);
              return; // Don't pass nethogs errors to listeners
            }
            
            // Pass other messages to listeners
            this.emit('message', data);
          }
        } catch (err) {
          console.error("❌ Error parsing message:", err);
        }
      };
      
      return true;
    } catch (error) {
      console.error("❌ Error connecting to WebSocket:", error);
      
      // FIXED: Don't emit errors that might trigger logout
      if (!this.preventLogout) {
        this.emit('error', error);
      } else {
        console.log("🛡️ Connection error suppressed to prevent logout");
      }
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
  
  // Check if websocket is authenticated
  public isAuthenticated(): boolean {
    return this.isConnected() && this.authenticated;
  }

  // Send a message through the WebSocket
  public sendMessage(message: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
      this.socket.send(messageStr);
      console.log("📤 WebSocket message sent:", typeof message === 'object' ? {...message, token: '[REDACTED]'} : message);
    } else {
      console.error("❌ Cannot send message: WebSocket not connected");
      // Auto-connect if possible
      if (!this.socket || this.socket.readyState === WebSocket.CLOSED) {
        console.log("🔄 Auto-reconnecting WebSocket...");
        const connected = this.connect();
        if (connected) {
          // Queue message to be sent after connection
          this.once('open', () => {
            this.sendMessage(message);
          });
        }
      }
    }
  }

  // Add an event listener
  public on(event: string, callback: (...args: any[]) => void): void {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    this.listeners[event].push(callback);
  }
  
  // Add a one-time event listener
  public once(event: string, callback: (...args: any[]) => void): void {
    const onceWrapper = (...args: any[]) => {
      this.off(event, onceWrapper);
      callback(...args);
    };
    this.on(event, onceWrapper);
  }

  // Remove an event listener
  public off(event: string, callback: (...args: any[]) => void): void {
    if (!this.listeners[event]) return;
    this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
  }

  // Emit an event to all listeners
  private emit(event: string, ...args: any[]): void {
    // FIXED: Don't emit auth_failed or error events if preventLogout is true
    if (this.preventLogout && (event === 'auth_failed' || event === 'error')) {
      console.log(`🛡️ Prevented emitting ${event} event to avoid logout`);
      return;
    }
    
    if (!this.listeners[event]) return;
    for (const callback of this.listeners[event]) {
      try {
        callback(...args);
      } catch (e) {
        console.error(`❌ Error in ${event} listener:`, e);
      }
    }
  }

  // Reset connection state
  public reset(): void {
    this.disconnect();
    this.reconnectAttempts = 0;
    this.authenticated = false;
  }
  
  // Explicitly reconnect with fresh authentication
  public reconnect(): void {
    this.reset();
    this.connect();
  }

  // Attempt to reconnect with exponential backoff
  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.MAX_ATTEMPTS) {
      console.error("❌ Max reconnection attempts reached");
      
      // FIXED: Don't emit error that might trigger logout
      if (!this.preventLogout) {
        this.emit('error', new Error("Failed to reconnect after maximum attempts"));
      } else {
        console.log("🛡️ Max retries error suppressed to prevent logout");
      }
      
      this.emit('max_retries');
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
  
  // ADDED: Control logout prevention
  public setPreventLogout(value: boolean): void {
    this.preventLogout = value;
    console.log(`WebSocket logout prevention ${value ? 'enabled' : 'disabled'}`);
  }
}

// Export a singleton instance
const websocketService = new WebSocketService();

// FIXED: Enable logout prevention by default
websocketService.setPreventLogout(true);

export default websocketService;