// src/utils/websocketService.ts

import store from '../store/store';
import { SystemMetric } from '../types/metrics';
import { updateMetrics } from '../store/slices/metricsSlice';
import { checkBackendAvailability } from './api';

// Sir Hawkington's Distinguished Type Definitions

// Raw metrics data from WebSocket as sent by the backend
// Sir Hawkington's Distinguished Raw Metric Interface
interface RawMetricData {
    // Backend sends these properties
    cpu: number;        // CPU usage percentage (0-100)
    memory: number;     // Memory usage percentage (0-100)
    disk: number;       // Disk usage percentage (0-100)
    timestamp: string;  // ISO timestamp
    connection_id: string; // WebSocket connection ID
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
    }

    public static getInstance(): WebSocketService {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService();
        }
        return WebSocketService.instance;
    }

    public async connect(): Promise<void> {
        console.log("🔌 ATTEMPTING WEBSOCKET CONNECTION...");
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

        // Check if backend is available before attempting WebSocket connection
        try {
            const backendAvailable = await checkBackendAvailability();
            if (!backendAvailable) {
                console.log("⚠️ Backend is not available, skipping WebSocket connection");
                return Promise.reject(new Error("Backend unavailable"));
            }
        } catch (error) {
            console.log("⚠️ Backend availability check failed, skipping WebSocket connection");
            return Promise.reject(error);
        }

        this.connectionPromise = new Promise((resolve, reject) => {
            try {
                if (this.socket?.readyState === WebSocket.OPEN) {
                    console.log("✅ WebSocket already connected!");
                    resolve();
                    return;
                }

                // Sir Hawkington's Distinguished WebSocket URL Determination Protocol
                const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
                // Use the same host as the current page for both production and development
                // This leverages the proxy configured in vite.config.ts - The Quantum Shadow People's suggestion
                const host = window.location.host;
                
                // The Hamsters insist on using the proxy path for WebSocket connections
                this.wsUrl = `${protocol}//${host}/ws/metrics/`;
                console.log(`🧐 Sir Hawkington has determined the WebSocket URL with aristocratic precision: ${this.wsUrl}`);
                console.log(`🐌 The Meth Snail is preparing the WebSocket pipes...`);
                
                this.socket = new WebSocket(this.wsUrl);
                
                this.socket.onopen = () => {
                    console.log('🎩 Sir Hawkington announces: WebSocket connection established with distinguished elegance! 🎉');
                    console.log(`🔍 WebSocket readyState: ${this.socket?.readyState}`);
                    console.log(`🐹 The Hamsters report successful WebSocket tunneling`);
                    this.reconnectAttempts = 0;
                    this.clearConnectionTimeout();
                    resolve();
                };
                
                this.socket.onmessage = (event) => {
                    console.log(`📨 Raw message received: ${event.data}`);
                    console.log(`🐌 The Meth Snail is processing data at ludicrous speed`);
                    this.handleMessage(event);
                };
                
                this.socket.onerror = (event) => {
                    console.error("🚨 WebSocket error detected!");
                    console.error("🧐 Sir Hawkington adjusts his monocle in distress:", event);
                    console.error("🪄 The Stick is attempting to manage the anxiety...");
                    this.handleError(event);
                    if (!this.isIntentionalDisconnect) {
                        reject(new Error("WebSocket connection error - The Hamsters have failed us"));
                    }
                };
                
                this.socket.onclose = (event) => {
                    console.log(`💔 WebSocket closed with code: ${event.code}, reason: ${event.reason}`);
                    console.log(`🧐 Sir Hawkington laments: "A most unfortunate disconnection, old chap!"`); 
                    console.log(`🐹 The Hamsters scurry to assess the damage...`);
                    this.handleClose();
                    if (!this.isIntentionalDisconnect) {
                        reject(new Error(`WebSocket closed: ${event.reason || 'Unknown reason - The VIC-20 is confused'}`));
                    }
                };
                
                // Add a timeout to detect connection issues
                this.setConnectionTimeout();
                
            } catch (error) {
                console.error("🔥 WEBSOCKET CREATION FAILED:", error);
                this.connectionPromise = null;
                reject(error);
            }
        });
        
        return this.connectionPromise;
    }

    private setConnectionTimeout(): void {
        this.clearConnectionTimeout();
        this.connectionTimeoutId = window.setTimeout(() => {
            if (this.socket?.readyState !== WebSocket.OPEN) {
                console.error(`⏰ WebSocket connection timeout. Current state: ${this.getConnectionState()}`);
                if (this.socket) {
                    this.socket.close();
                }
                this.connectionPromise = null;
            }
        }, 5000);
    }

    private clearConnectionTimeout(): void {
        if (this.connectionTimeoutId !== null) {
            window.clearTimeout(this.connectionTimeoutId);
            this.connectionTimeoutId = null;
        }
    }

    private handleMessage(event: MessageEvent): void {
        try {
            const data = JSON.parse(event.data) as WebSocketMessage;
            console.log("📨 WebSocket message received:", data);
            
            if (data.type === 'metrics_update' && data.data) {
                // Sir Hawkington's Distinguished Data Transformation Protocol
                console.log("🧐 Sir Hawkington is examining the raw metrics data with his monocle...");
                console.log("🔍 Raw data from the Hamsters' WebSocket tubes:", data.data);
                
                // Transform the raw WebSocket data into the format expected by our components
                const metricData: SystemMetric = {
                    // Transform backend properties to match frontend expectations
                    cpu_usage: data.data.cpu,
                    memory_usage: data.data.memory,
                    disk_usage: data.data.disk,
                    network_usage: 0, // The Quantum Shadow People suggest a default value
                    process_count: 0, // The VIC-20 provides 8-bit wisdom on process counting
                    timestamp: data.data.timestamp,
                    additional_metrics: {}
                };
                
                console.log("✨ The Meth Snail has processed the metrics data at ludicrous speed:", metricData);
                
                // Dispatch the transformed data to Redux
                store.dispatch(updateMetrics(metricData));
                console.log("🐹 The Hamsters have delivered the metrics to Sir Hawkington's Redux store");
                
                // Then call callback if set
                if (this.messageCallback) {
                    this.messageCallback({
                        type: data.type,
                        data: metricData as any // Type cast to satisfy the callback
                    });
                }
            }
        } catch (error) {
            console.error("💩 Error parsing metric data:", error);
        }
    }

    private handleError(error: Event): void {
        console.error("🚨 WebSocket error occurred:", error);
        this.connectionPromise = null;
    }

    private handleClose(): void {
        console.log("💔 WebSocket connection closed");
        console.log("🧐 Sir Hawkington adjusts his monocle and reaches for the emergency teacup...");
        this.connectionPromise = null;
        
        if (!this.isIntentionalDisconnect) {
            console.log("🐹 The Hamsters are preparing the reconnection apparatus...");
            this.handleReconnect();
        } else {
            console.log("🪄 The Stick confirms this was an intentional disconnection. No anxiety detected.");
        }
    }

    private handleReconnect(): void {
        this.clearReconnectTimeout();
        
        if (this.reconnectAttempts < this.MAX_ATTEMPTS) {
            this.reconnectAttempts++;
            console.log(`🔄 Attempting reconnection #${this.reconnectAttempts} of ${this.MAX_ATTEMPTS}`);
            console.log(`🧐 Sir Hawkington declares: "We shall not surrender! Prepare for reconnection!"`); 
            console.log(`🐌 The Meth Snail is injecting more methamphetamine to power the reconnection...`);
            
            // The Quantum Shadow People suggested this exponential backoff algorithm
            const delay = 1000 * Math.min(30, Math.pow(2, this.reconnectAttempts - 1)); // Exponential backoff
            this.reconnectTimeoutId = window.setTimeout(async () => {
                try {
                    // Check backend availability before reconnecting
                    const backendAvailable = await checkBackendAvailability();
                    if (backendAvailable) {
                        this.connect();
                    } else {
                        console.log("⚠️ Backend still unavailable, skipping reconnection attempt");
                        console.log("🪄 The Stick's anxiety levels are increasing...");
                        // Still count as an attempt
                        if (this.reconnectAttempts < this.MAX_ATTEMPTS) {
                            console.log("🐹 The Hamsters suggest trying again with more duct tape...");
                            this.handleReconnect();
                        } else {
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