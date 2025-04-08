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
        console.log("🔌 WebSocket URL set to:", this.wsUrl);
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
                        console.log("❌ Backend server is not available");
                        this.permanentlyFailed = true;
                        return reject(new Error("Backend server is not available"));
                    }

                    // Create WebSocket connection
                    this.socket = new WebSocket(this.wsUrl);

                    // Set up event handlers
                    this.socket.onopen = () => {
                        console.log("✅ WebSocket connection established");
                        this.reconnectAttempts = 0;
                        this.permanentlyFailed = false;
                        this.clearConnectionTimeout();
                        this.clearReconnectTimeout();
                        resolve();
                    };

                    this.socket.onmessage = (event) => {
                        this.handleMessage(event);
                    };

                    this.socket.onerror = (event) => {
                        console.error("🚨 WebSocket error detected!", event);
                        this.handleError(event);
                        reject(event);
                    };

                    this.socket.onclose = (event) => {
                        console.log("🚪 WebSocket connection closed", event);
                        this.handleClose(event);
                        reject(event);
                    };

                    // Set connection timeout
                    this.setConnectionTimeout();
                });
            } catch (error) {
                console.error("❌ Error creating WebSocket connection:", error);
                reject(error);
            }
        });

        return this.connectionPromise;
    }

    private setConnectionTimeout(): void {
        this.clearConnectionTimeout();
        this.connectionTimeoutId = window.setTimeout(() => {
            if (this.socket && this.socket.readyState !== WebSocket.OPEN) {
                const stateNames = {
                    [WebSocket.CONNECTING]: 'CONNECTING',
                    [WebSocket.OPEN]: 'OPEN',
                    [WebSocket.CLOSING]: 'CLOSING',
                    [WebSocket.CLOSED]: 'CLOSED'
                };
                console.error("⏰ WebSocket connection timeout. Current state:", stateNames[this.socket.readyState]);
                this.handleClose();
            }
        }, 5000); // 5 second timeout
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
            
            if (data.type === 'system_metrics' && data.data) {
                // Sir Hawkington's Distinguished Data Transformation Protocol
                console.log("🧐 Sir Hawkington is examining the raw metrics data with his monocle...");
                console.log("🔍 Raw data from the Hamsters' WebSocket tubes:", data.data);
                
                // Transform the raw WebSocket data into the format expected by our components
                console.log('🔬 Detailed data inspection:', JSON.stringify(data));
                
                // Extract the actual metrics from the nested data structure
                const rawMetrics = data.data;
                
                const metricData: SystemMetric = {
                    // Required fields for SystemMetric interface
                    id: crypto.randomUUID ? crypto.randomUUID() : `metric-${Date.now()}`,
                    user_id: 'system', // System-generated metrics don't have a specific user
                    // Transform backend properties to match frontend expectations
                    cpu_usage: rawMetrics.cpu_usage || 0,
                    memory_usage: rawMetrics.memory_usage || 0,
                    disk_usage: rawMetrics.disk_usage || 0,
                    network_usage: rawMetrics.network_io ? 
                        (rawMetrics.network_io.sent + rawMetrics.network_io.recv) / 1024 / 1024 : 0, // Convert to MB
                    process_count: rawMetrics.process_count || 0,
                    timestamp: rawMetrics.timestamp || new Date().toISOString(),
                    additional_metrics: {}
                };
                
                console.log('🧪 Transformed metric data:', metricData);
                
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
        
        if (this.reconnectAttempts < this.MAX_ATTEMPTS) {
            this.handleReconnect();
        } else {
            this.permanentlyFailed = true;
            console.error("💀 Maximum reconnection attempts reached. WebSocket permanently disabled.");
        }
    }

    private handleClose(event?: CloseEvent): void {
        console.log("🚪 WebSocket connection closed", event);
        
        if (!this.isIntentionalDisconnect && !this.permanentlyFailed) {
            if (this.reconnectAttempts < this.MAX_ATTEMPTS) {
                this.handleReconnect();
            } else {
                this.permanentlyFailed = true;
                console.error("💀 Maximum reconnection attempts reached. WebSocket permanently disabled.");
            }
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