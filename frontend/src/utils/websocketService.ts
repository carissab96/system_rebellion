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
            this.wsUrl = `/api/ws/system-metrics`;
            console.log("🔗 [WebSocketService] Using relative WebSocket URL:", this.wsUrl);
            
            // Log environment for debugging
            console.log("🌍 [WebSocketService] Environment:", {
                NODE_ENV: import.meta.env.MODE,
                VITE_BACKEND_URL: import.meta.env.VITE_BACKEND_URL,
                PROD: import.meta.env.PROD,
                DEV: import.meta.env.DEV,
                location: window.location.href
            });
        } catch (error) {
            console.error("❌ [WebSocketService] Error configuring WebSocket URL:", error);
            // Fallback to WebSocket proxy path
            this.wsUrl = '/api/ws/system-metrics';
            console.log("🔄 [WebSocketService] Falling back to default WebSocket URL:", this.wsUrl);
        }
    }
    
    public static getInstance(): WebSocketService {
        if (!WebSocketService.instance) {
            WebSocketService.instance = new WebSocketService();
        }
        return WebSocketService.instance;
    }
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
            
            this.connectionPromise = null;
        }, 10000); // 10 second timeout - FIXED from 10000000
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
                const networkIo = message.data.network_io || {};
                const networkUsage = message.data.network_io ? 
                    (networkIo.sent + networkIo.recv) / 1024 / 1024 : 
                    ((message.data.sent || 0) + (message.data.recv || 0)) / 1024 / 1024;

                // Create a base metric with required fields
                const baseMetric: Partial<SystemMetric> = {
                    id: crypto.randomUUID ? crypto.randomUUID() : `metric-${Date.now()}`,
                    user_id: 'system',
                    timestamp: message.data.timestamp || new Date().toISOString(),
                    cpu_usage: message.data.cpu_usage || message.data.cpu || 0,
                    memory_usage: message.data.memory_usage || message.data.memory || 0,
                    disk_usage: message.data.disk_usage || message.data.disk || 0,
                    network_usage: networkUsage,
                    process_count: message.data.process_count || 0,
                    // Required fields with default values
                    memory_total: 0,
                    memory_available: 0,
                    memory_free: 0,
                    memory_buffer: 0,
                    memory_cache: 0,
                    memory_swap: 0,
                    memory_swap_total: 0,
                    memory_swap_free: 0,
                    memory_swap_used: 0,
                    memory_swap_percent: 0,
                    memory_percent: 0,
                    disk_total: 0,
                    disk_available: 0,
                    disk_free: 0,
                    disk_used: 0,
                    disk_percent: 0,
                    network_total: 0,
                    network_available: 0,
                    network_free: 0,
                    network_used: 0,
                    network_percent: 0,
                    cpu: {
                        name: message.data.cpu_model || 'Unknown CPU',
                        frequency: 0,
                        temp: {
                            current: 0,
                            min: 0,
                            max: 100,
                            critical: 90,
                            throttle_threshold: 80,
                            unit: 'C' as const
                        },
                        processes: [],
                        core_count: 0,
                        usage_percent: undefined,
                        overall_usage: message.data.cpu_usage || message.data.cpu || 0,
                        process_count: 0,
                        thread_count: 0,
                        physical_cores: 0,
                        logical_cores: 0,
                        model_name: message.data.cpu_model || 'Unknown',
                        frequency_mhz: 0,
                        temperature: {
                            current: 0,
                            min: 0,
                            max: 100,
                            critical: 90,
                            throttle_threshold: 80,
                            unit: 'C' as const
                        },
                        top_processes: [],
                        cores: []
                    },
                    additional_metrics: {}
                };

                // Merge with any additional data and ensure all required fields are set
                const metricData: SystemMetric = {
                    // Base fields with defaults
                    ...baseMetric,
                    // Override with any additional metrics from the message
                    ...(message.data.additional_metrics || {}),
                    // Ensure network data is properly set
                    network: message.data.network_io || message.data.network || {},
                    // Ensure timestamp is set
                    timestamp: message.data.timestamp || new Date().toISOString(),
                    // Ensure additional_metrics exists
                    additional_metrics: message.data.additional_metrics || {}
                } as SystemMetric;
                
                // Log the network data specifically
                console.log("🌐 Network data being preserved:", metricData.network);
                
                // If we have network data in the message but it's not in the expected format,
                // add it to additional.network_details for backward compatibility
                if (message.data.network && !metricData.additional) {
                    metricData.additional = {
                        network_details: message.data.network
                    };
                }
                
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
                    // FIXED: Added timeout to backend availability check during reconnection
                    const backendCheckWithTimeout = Promise.race([
                      checkBackendAvailability(),
                      new Promise<boolean>((_, reject) => 
                        setTimeout(() => reject(new Error('Backend availability check timed out')), 5000)
                      )
                    ]);
                    
                    const backendAvailable = await backendCheckWithTimeout;
                    
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