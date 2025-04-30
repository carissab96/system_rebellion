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
interface WebSocketMessage {
    type: string;
    data?: RawMetricData;
}

// The Quantum Shadow People's Interface Definition
interface IWebSocketService {
    connect(): Promise<void>;
    disconnect(): void;
    sendMessage(message: WebSocketMessage): void;
    isConnected(): boolean;
    getConnectionState(): string;
    // Sir Hawkington's Distinguished Callback Type
    // This allows for any WebSocket message format to be passed to the callback
    setMessageCallback(callback: (data: any) => void): void;
    resetReconnectAttempts(): void;
}

class WebSocketService implements IWebSocketService {
    private static instance: WebSocketService;
    private socket: WebSocket | null = null;
    private reconnectAttempts = 0;
    private readonly MAX_ATTEMPTS = 3; // Reduced from 5 to 3
    private permanentlyFailed = false; // New flag to track permanent failure
    private messageCallback: ((data: any) => void) | null = null; // Updated to match interface
    private connectionPromise: Promise<void> | null = null;
    private wsUrl: string = '';
    private connectionTimeoutId: number | null = null;
    private reconnectTimeoutId: number | null = null;
    private isIntentionalDisconnect: boolean = false;

    private constructor() {
        console.log("🎭 WebSocket Service Constructor Called");
        
        // Set WebSocket URL based on environment
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        this.wsUrl = `${protocol}//${host}/ws/system-metrics`;
        console.log("🧐 Sir Hawkington says: WebSocket URL configured to:", this.wsUrl);
    }

    public static getInstance(): WebSocketService {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService();
        }
        return WebSocketService.instance;
    }

    public async connect(): Promise<void> {
        console.log("🔌 ATTEMPTING WEBSOCKET CONNECTION to:", this.wsUrl);
        console.log(`🔍 Current time: ${new Date().toISOString()}`);
        
        // If we've permanently failed, don't even try
        if (this.permanentlyFailed) {
            console.log("💀 WebSocket connection permanently disabled due to repeated failures");
            return Promise.reject(new Error("WebSocket permanently disabled"));
        }
        
        // Reset intentional disconnect flag
        this.isIntentionalDisconnect = false;
        
        if (this.connectionPromise) {
            console.log("🔄 Connection already in progress, returning existing promise");
            return this.connectionPromise;
        }

        this.connectionPromise = new Promise((resolve, reject) => {
            try {
                // Check if backend is available before attempting WebSocket connection
                checkBackendAvailability().then(backendAvailable => {
                    if (!backendAvailable) {
                        console.error("🔌 Backend is not available, cannot establish WebSocket connection");
                        this.connectionPromise = null;
                        reject(new Error("Backend is not available"));
                        return;
                    }
                    
                    // Get authentication token from localStorage
                    const token = localStorage.getItem('token');
                    
                    // Create WebSocket URL with token if available
                    let wsUrlWithAuth = this.wsUrl;
                    if (token) {
                        // Add token as a query parameter or use a custom header depending on backend implementation
                        wsUrlWithAuth = `${this.wsUrl}?token=${token}`;
                        console.log("🔑 Adding authentication token to WebSocket connection");
                    }
                    
                    console.log("🔌 Creating WebSocket with URL:", wsUrlWithAuth);
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
        this.connectionTimeoutId = window.setTimeout(() => {
            console.error("⏱️ WebSocket connection timeout after 10 seconds");
            
            if (this.socket && this.socket.readyState === WebSocket.CONNECTING) {
                console.error("🔌 WebSocket still in CONNECTING state after timeout, closing");
                this.socket.close();
                this.socket = null;
            }
            
            this.connectionPromise = null;
        }, 10000); // 10 second timeout
    }

    private clearConnectionTimeout(): void {
        if (this.connectionTimeoutId !== null) {
            window.clearTimeout(this.connectionTimeoutId);
            this.connectionTimeoutId = null;
        }
    }

    private handleMessage(event: MessageEvent): void {
        try {
            console.log("📨 Raw WebSocket message received:", event.data);
            
            // Parse the message
            const message = JSON.parse(event.data);
            console.log("📨 Parsed WebSocket message:", message);
            
            // Process the message based on its type
            if (message.type === 'system_metrics' && message.data) {
                console.log("📊 System metrics received:", message.data);
                
                // Transform the data into our SystemMetric format
                const metricData: SystemMetric = {
                    id: crypto.randomUUID ? crypto.randomUUID() : `metric-${Date.now()}`,
                    user_id: 'system',
                    cpu_usage: message.data.cpu_usage || message.data.cpu || 0,
                    memory_usage: message.data.memory_usage || message.data.memory || 0,
                    disk_usage: message.data.disk_usage || message.data.disk || 0,
                    network_usage: message.data.network_io ? 
                        (message.data.network_io.sent + message.data.network_io.recv) / 1024 / 1024 : 
                        ((message.data.sent || 0) + (message.data.recv || 0)) / 1024 / 1024,
                    process_count: message.data.process_count || 0,
                    timestamp: message.data.timestamp || new Date().toISOString(),
                    additional_metrics: {}
                };
                
                // Dispatch to Redux store
                store.dispatch(updateMetrics(metricData));
            }
            
            // Call the callback if set
            if (this.messageCallback) {
                this.messageCallback(message);
            }
        } catch (error) {
            console.error("❌ Error handling WebSocket message:", error);
            console.error("🐌 The Meth Snail is confused by this message format!");
        }
    }

    private handleError(error: Event): void {
        console.error("❌ WebSocket error:", error);
        console.error("🐹 The Hamsters report a critical failure in the WebSocket tubes!");
        
        // If we have a connection promise, reject it
        if (this.connectionPromise) {
            this.connectionPromise = null;
        }
    }

    private handleClose(event?: CloseEvent): void {
        console.log("👋 WebSocket closed:", event);
        
        // If this was an intentional disconnect, don't try to reconnect
        if (this.isIntentionalDisconnect) {
            console.log("🧐 Sir Hawkington notes this was an intentional disconnect. No reconnection needed.");
            return;
        }
        
        // Try to reconnect
        this.handleReconnect();
    }

    private handleReconnect(): void {
        // Don't try to reconnect if we've permanently failed
        if (this.permanentlyFailed) {
            console.log("💀 WebSocket permanently disabled, not attempting reconnection");
            return;
        }
        
        this.reconnectAttempts++;
        console.log(`🔄 Reconnection attempt ${this.reconnectAttempts}/${this.MAX_ATTEMPTS}`);
        
        // Clear any existing reconnect timeout
        this.clearReconnectTimeout();
        
        if (this.reconnectAttempts <= this.MAX_ATTEMPTS) {
            // Exponential backoff: 1s, 2s, 4s, etc.
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts - 1), 30000);
            
            this.reconnectTimeoutId = window.setTimeout(async () => {
                console.log(`⏱️ Attempting reconnection after ${delay}ms delay`);
                
                try {
                    // Check if backend is available before attempting reconnection
                    const backendAvailable = await checkBackendAvailability();
                    
                    if (backendAvailable) {
                        console.log("✅ Backend is available, attempting WebSocket reconnection");
                        
                        // Reset connection promise so we can try again
                        this.connectionPromise = null;
                        
                        try {
                            await this.connect();
                            console.log("✅ WebSocket reconnection successful!");
                            console.log("🧐 Sir Hawkington is pleased with the reconnection!");
                            this.reconnectAttempts = 0; // Reset on successful reconnection
                        } catch (reconnectError) {
                            console.error("❌ WebSocket reconnection failed:", reconnectError);
                            
                            if (this.reconnectAttempts >= this.MAX_ATTEMPTS) {
                                this.permanentlyFailed = true;
                                console.error("💀 Maximum reconnection attempts reached. WebSocket permanently disabled.");
                                console.error("🧐 Sir Hawkington removes his monocle in defeat: 'The WebSocket has fallen, and it cannot get up!'");
                                console.error("🎮 The VIC-20 suggests turning it off and on again, but alas, it's too late.");
                            }
                        }
                    } else {
                        console.log("❌ Backend is not available, will try again later");
                        
                        if (this.reconnectAttempts >= this.MAX_ATTEMPTS) {
                            this.permanentlyFailed = true;
                            console.error("💀 Maximum reconnection attempts reached. WebSocket permanently disabled.");
                            console.error("🧐 Sir Hawkington removes his monocle in defeat: 'The WebSocket has fallen, and it cannot get up!'");
                            console.error("🎮 The VIC-20 suggests turning it off and on again, but alas, it's too late.");
                        }
                    }
                } catch (error) {
                    console.error("⚠️ Error checking backend availability during reconnect:", error);
                    console.error("👻 The Quantum Shadow People report disturbances in the network fabric...");
                    if (this.reconnectAttempts < this.MAX_ATTEMPTS) {
                        console.log("🐌 The Meth Snail suggests one more hit of that sweet, sweet reconnection...");
                        this.handleReconnect();
                    } else {
                        this.permanentlyFailed = true;
                        console.error("💀 Maximum reconnection attempts reached. WebSocket permanently disabled.");
                        console.error("🧐 Sir Hawkington declares: 'This connection has shuffled off its mortal coil!'");
                        console.error("🐹 The Hamsters have run out of duct tape and are now in mourning.");
                    }
                }
            }, delay);
            
            console.log(`⏱️ Will attempt reconnection in ${delay}ms`);
        } else {
            this.permanentlyFailed = true;
            console.error("💀 Maximum reconnection attempts reached. WebSocket permanently disabled.");
        }
    }

    private clearReconnectTimeout(): void {
        if (this.reconnectTimeoutId !== null) {
            window.clearTimeout(this.reconnectTimeoutId);
            this.reconnectTimeoutId = null;
        }
    }

    public resetReconnectAttempts(): void {
        this.reconnectAttempts = 0;
        this.permanentlyFailed = false; // Allow reconnection attempts again
        console.log("🔄 Reconnection attempts reset and WebSocket re-enabled");
    }

    public isConnected(): boolean {
        return this.socket?.readyState === WebSocket.OPEN;
    }

    public getConnectionState(): string {
        if (!this.socket) return "NOT_INITIALIZED";
        
        switch (this.socket.readyState) {
            case WebSocket.CONNECTING:
                return "CONNECTING";
            case WebSocket.OPEN:
                return "CONNECTED";
            case WebSocket.CLOSING:
                return "CLOSING";
            case WebSocket.CLOSED:
                return "CLOSED";
            default:
                return "UNKNOWN";
        }
    }

    public setMessageCallback(callback: (data: any) => void): void {
        console.log("🎭 Sir Hawkington is registering a distinguished message callback");
        this.messageCallback = callback;
        console.log("✅ Callback set with aristocratic precision:", !!this.messageCallback);
    }

    public sendMessage(message: WebSocketMessage): void {
        if (this.socket?.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(message));
        } else {
            console.error('Cannot send message, WebSocket is not connected');
        }
    }

    public disconnect(): void {
        console.log("👋 Starting WebSocket disconnect...");
        this.isIntentionalDisconnect = true;
        
        this.clearConnectionTimeout();
        this.clearReconnectTimeout();
        
        if (this.socket) {
            this.socket.onclose = null; // Prevent reconnect attempts during intentional disconnect
            this.socket.close();
            this.socket = null;
        }
        this.connectionPromise = null;
        console.log("✅ WebSocket disconnected");
    }
}

// Make sure to create the singleton instance and export it
const websocketServiceInstance = WebSocketService.getInstance();
export const websocketService: IWebSocketService = websocketServiceInstance;

// Log that the service has been initialized
console.log("🚀 WebSocketService singleton instance created and exported");
