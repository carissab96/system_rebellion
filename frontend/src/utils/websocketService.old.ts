// src/utils/websocketService.ts

import store from '../store/store';
import { SystemMetric } from '../types/metrics';
import { updateMetrics } from '../store/slices/metricsSlice';
import { checkBackendAvailability } from './api';

// Sir Hawkington's Distinguished Type Definitions

// Raw metrics data from WebSocket as sent by the backend
// Sir Hawkington's Distinguished Raw Metric Interface
interface RawMetricData {
    // Backend sends these properties - support both naming conventions
    cpu?: number;                // CPU usage percentage (0-100)
    cpu_usage?: number;         // Alternative property name
    memory?: number;            // Memory usage percentage (0-100)
    memory_usage?: number;      // Alternative property name
    disk?: number;              // Disk usage percentage (0-100)
    disk_usage?: number;        // Alternative property name
    network_io?: {
        sent: number;           // Bytes sent
        recv: number;           // Bytes received
    };
    sent?: number;              // Alternative property name
    recv?: number;              // Alternative property name
    process_count?: number;     // Number of running processes
    timestamp: string;          // ISO timestamp
    connection_id?: string;     // WebSocket connection ID
}

// WebSocket message structure
type WebSocketMessage = {
    type: string;
    data?: RawMetricData;
};

// The Quantum Shadow People's Interface Definition
interface IWebSocketService {
    connect(): Promise<void>;
    disconnect(): void;
    sendMessage(message: WebSocketMessage): void;
    isConnected(): boolean;
    getConnectionState(): string;
    setMessageCallback(callback: (data: WebSocketMessage) => void): void;
    resetReconnectAttempts(): void;
    on(event: string, callback: (...args: any[]) => void): void;
    off(event: string, callback: (...args: any[]) => void): void;
    connectWithRetry(): Promise<boolean>;
    clearConnectionTimeout(): void;
    setConnectionTimeout(): void;
    handleReconnect(): Promise<void>;
}

class WebSocketService implements IWebSocketService {
    private static instance: WebSocketService;
    private socket: WebSocket | null = null;
    private reconnectAttempts = 0;
    private readonly MAX_ATTEMPTS = 3; // Reduced from 5 to 3
    private permanentlyFailed = false; // New flag to track permanent failure
    private messageCallback: ((data: WebSocketMessage) => void) | null = null; // Updated to match interface
    private connectionPromise: Promise<void> | null = null;
    private wsUrl: string = '';
    private connectionTimeoutId: number | null = null;
    // Removed unused reconnectTimeoutId
    private isIntentionalDisconnect: boolean = false;

    private getStateName(state: number): string {
        switch (state) {
            case WebSocket.CONNECTING: return 'CONNECTING';
            case WebSocket.OPEN: return 'OPEN';
            case WebSocket.CLOSING: return 'CLOSING';
            case WebSocket.CLOSED: return 'CLOSED';
            default: return 'UNKNOWN';
        }
    }

    private constructor() {
        console.log("🎭 [WebSocketService] Constructor Called");
        
        try {
            // Use the WebSocket proxy path defined in vite.config.ts
            // Check if we're in development or production
            const isDev = import.meta.env.DEV;
            // Removed unused baseUrl
            
            // Use the correct WebSocket protocol based on the current protocol
            const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const host = window.location.host;
            
            // Try direct WebSocket connection first, then fallback to proxy
            this.wsUrl = isDev 
                ? `${wsProtocol}//${host}/ws/system-metrics`  // Use proxy in dev
                : `${wsProtocol}//${host}/api/ws/system-metrics`; // Direct in production
                
            console.log("🔗 [WebSocketService] Using WebSocket URL:", this.wsUrl);
            
            // Log environment for debugging
            console.log("🌍 [WebSocketService] Environment:", {
                NODE_ENV: import.meta.env.MODE,
                VITE_BACKEND_URL: import.meta.env.VITE_BACKEND_URL,
                PROD: import.meta.env.PROD,
                DEV: import.meta.env.DEV,
                location: window.location.href,
                wsUrl: this.wsUrl
            });
        } catch (error) {
            console.error("❌ [WebSocketService] Error configuring WebSocket URL:", error);
            // Fallback to WebSocket proxy path
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            this.wsUrl = `${protocol}//${window.location.host}/ws/system-metrics`;
            console.log("🔄 [WebSocketService] Falling back to WebSocket URL:", this.wsUrl);
        }
    }
    
    public static getInstance(): WebSocketService {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService();
        }
        return WebSocketService.instance;
    }

    // Implement missing interface methods
    public disconnect(): void {
        this.isIntentionalDisconnect = true;
        if (this.socket) {
            this.socket.close();
            this.socket = null;
        }
        this.clearConnectionTimeout();
    }

    public isConnected(): boolean {
        return this.socket?.readyState === WebSocket.OPEN;
    }

    public getConnectionState(): string {
        if (!this.socket) return 'disconnected';
        switch (this.socket.readyState) {
            case WebSocket.CONNECTING: return 'connecting';
            case WebSocket.OPEN: return 'connected';
            case WebSocket.CLOSING: return 'closing';
            case WebSocket.CLOSED: return 'disconnected';
            default: return 'disconnected';
        }
    }

    public resetReconnectAttempts(): void {
        this.reconnectAttempts = 0;
        this.permanentlyFailed = false;
    }

    public on(event: string, callback: (...args: any[]) => void): void {
        // Simple event emitter implementation
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    }

    public off(event: string, callback: (...args: any[]) => void): void {
        if (!this.listeners[event]) return;
        this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
    }

    private emit(event: string, ...args: any[]): void {
        if (!this.listeners[event]) return;
        for (const callback of this.listeners[event]) {
            try {
                callback(...args);
            } catch (e) {
                console.error(`Error in ${event} listener:`, e);
            }
        }
    }

    private listeners: { [event: string]: Array<(...args: any[]) => void> } = {};
    public async connect(): Promise<void> {
        console.log("🔌 [WebSocketService] ATTEMPTING WEBSOCKET CONNECTION to:", this.wsUrl);
        console.log(`🔍 [WebSocketService] Current time: ${new Date().toISOString()}`);
        
        // Reset the permanent failure state on each new connection attempt
        this.permanentlyFailed = false;
        
        // If we're already connected, don't try to connect again
        if (this.socket) {
            console.log(`🔌 [WebSocketService] Current WebSocket state: ${this.socket.readyState} (${this.getStateName(this.socket.readyState)})`);
            if (this.socket.readyState === WebSocket.OPEN) {
                console.log("🔌 [WebSocketService] WebSocket is already connected.");
                return Promise.resolve();
            }
        }
        
        // If we have a connection promise already, reuse it
        if (this.connectionPromise) {
          console.log("🔄 Connection already in progress, returning existing promise");
          return this.connectionPromise;
        }
    
        this.connectionPromise = new Promise((resolve, reject) => {
          try {
            // Check if backend is available before attempting WebSocket connection
            // FIXED: Added timeout to backend availability check
            const backendCheckWithTimeout = Promise.race([
              checkBackendAvailability(),
              new Promise<boolean>((_, reject) => 
                setTimeout(() => reject(new Error('Backend availability check timed out')), 5000)
              )
            ]);
            
            backendCheckWithTimeout.then(backendAvailable => {
              if (!backendAvailable) {
                console.error("🔌 Backend is not available, cannot establish WebSocket connection");
                this.connectionPromise = null;
                reject(new Error("Backend is not available"));
                return;
              }
              
              // Get and validate token
              let token = localStorage.getItem('token');
              
              if (!token) {
                console.log('🔑 No authentication token found, attempting to connect without token');
              }
              
              // Create WebSocket URL with token if available
              const wsUrlWithAuth = token ? `${this.wsUrl}?token=${token}` : this.wsUrl;
              console.log("🔌 Creating WebSocket with URL:", wsUrlWithAuth);
              
              // Actually use the URL with auth token here
              this.socket = new WebSocket(wsUrlWithAuth);
              
              // Set up connection timeout
              this.setConnectionTimeout();
              
              // Set up event handlers
              this.socket.onopen = () => {
                console.log("✅ WebSocket connection established!");
                console.log("🧐 Sir Hawkington adjusts his monocle in approval!");
                this.clearConnectionTimeout();
                this.reconnectAttempts = 0; // Reset reconnect attempts on successful connection
                resolve();
              };
              
              this.socket.onmessage = (event) => {
                this.handleMessage(event);
              };
              
              this.socket.onerror = (event) => {
                console.error("❌ WebSocket error:", event);
                this.handleError(event);
              };
              
              this.socket.onclose = (event) => {
                console.log("👋 WebSocket closed:", event);
                this.handleClose(event);
              };
            }).catch(error => {
              console.error("❌ Error checking backend availability:", error);
              this.connectionPromise = null;
              reject(error);
            });
          } catch (error) {
            console.error("❌ Error creating WebSocket:", error);
            this.connectionPromise = null;
            reject(error);
          }
        });
    
        return this.connectionPromise;
      }
    

    private setConnectionTimeout(): void {
        // Clear any existing timeout
        this.clearConnectionTimeout();
        
        // Set a new timeout - 10 seconds to establish connection
        // FIXED: Changed timeout from 10000000ms (≈115 days) to 10000ms (10 seconds)
        this.connectionTimeoutId = window.setTimeout(() => {
            console.error("⏱️ WebSocket connection timeout after 10 seconds");
            
            if (this.socket && this.socket.readyState === WebSocket.CONNECTING) {
                console.error("🔌 WebSocket still in CONNECTING state after timeout, closing");
                this.socket.close();
                this.socket = null;
            }
            

    private clearConnectionTimeout(): void {
        if (this.connectionTimeoutId) {
            clearTimeout(this.connectionTimeoutId);
            this.connectionTimeoutId = null;
        }
    }

    private clearReconnectTimeout(): void {
        // No-op since we removed reconnectTimeoutId
    }

    private handleMessage(event: MessageEvent): void {
        try {
            const message = JSON.parse(event.data);
            if (this.messageCallback) {
                this.messageCallback(message);
            }
        } catch (error) {
            console.error('Error handling WebSocket message:', error);
        }
    }

    public async connectWithRetry(): Promise<boolean> {
        if (this.permanentlyFailed) {
            console.error("WebSocket connection permanently failed. Please refresh the page to try again.");
            return false;
        }
        try {
            await this.connect();
            return true;
        } catch (error) {
            console.error("WebSocket connection failed:", error);
            return false;
        }
    }

    private async handleReconnect(): Promise<void> {
        // Don't try to reconnect if we've permanently failed
        if (this.permanentlyFailed) {
            console.log("WebSocket permanently disabled, not attempting reconnection");
            return;
        }

        if (this.reconnectAttempts >= this.MAX_ATTEMPTS) {
            console.error("Max reconnection attempts reached");
            console.error("Sir Hawkington removes his monocle in defeat: 'The WebSocket has fallen, and it cannot get up!'");
            console.error("The VIC-20 suggests turning it off and on again, but alas, it's too late.");
            this.permanentlyFailed = true;
            return;
        }

        const delay = this.getReconnectDelay();
        this.reconnectTimeoutId = window.setTimeout(async () => {
            try {
                const backendAvailable = await checkBackendAvailability();
                if (!backendAvailable) {
                    console.log("Backend is not available, will try again later");
                    this.reconnectAttempts++;
                    this.handleReconnect();
                } else {
                    this.connectWithRetry();
                }
            } catch (error) {
                console.error("Error checking backend availability during reconnect:", error);
                this.reconnectAttempts++;
                this.handleReconnect();
            }
        }, delay);

        console.log(`Will attempt reconnection in ${delay}ms`);
    }

    private setConnectionTimeout(): void {
        this.clearConnectionTimeout();
        this.connectionTimeoutId = window.setTimeout(async () => {
            if (this.socket && this.socket.readyState === WebSocket.CONNECTING) {
                this.socket.close();
                this.socket = null;
                await this.handleReconnect();
            }
        }, 10000); // 10 second timeout
    }

    public disconnect(): void {
        console.log("Starting WebSocket disconnect...");
        this.isIntentionalDisconnect = true;
        this.clearConnectionTimeout();
        this.clearReconnectTimeout();
        if (this.socket) {
            this.socket.onclose = null; // Prevent reconnect attempts during intentional disconnect
            this.socket.close();
            this.socket = null;
        }
        this.connectionPromise = null;
        console.log("WebSocket disconnected");
    }
}

// Make sure to create the singleton instance and export it
const websocketServiceInstance = WebSocketService.getInstance();
export const websocketService: IWebSocketService = websocketServiceInstance;

// Log that the service has been initialized
console.log("🚀 WebSocketService singleton instance created and exported");               