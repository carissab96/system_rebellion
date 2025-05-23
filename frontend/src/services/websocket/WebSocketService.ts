import { AppDispatch } from '../../store/store';

export interface CPUMetricsMessage {
  type: 'cpu';
  data: {
    usage_percent: number;
    temperature: number;
    cores: number[];
    frequency_mhz: number;
    physical_cores: number;
    logical_cores: number;
    top_processes: {
      pid: number;
      name: string;
      cpu_percent: number;
      memory_percent: number;
    }[];
  };
}

export class WebSocketService {
  private socket: WebSocket | null = null;
  private retryCount = 0;
  private maxRetries = 3;
  private retryDelay = 2000; // 2 seconds
  private retryTimeout: NodeJS.Timeout | null = null;

  public onMessage: (message: CPUMetricsMessage) => void = () => {};
  public onError: (error: Error) => void = () => {};

  constructor(_dispatch: AppDispatch) {
    // dispatch is not used in this class
  }

  private getWebSocketUrl(): string {
    const token = localStorage.getItem('token');
    
    if (!token) {
      throw new Error('No authentication token found');
    }

    // Always connect directly to the backend in development
    const baseUrl = process.env.NODE_ENV === 'development' 
      ? 'ws://localhost:8000'
      : `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}`;

    // Always use /ws/system-metrics endpoint
    return `${baseUrl}/ws/system-metrics?token=${encodeURIComponent(token)}`;
  }

  private scheduleReconnect() {
    if (this.retryCount < this.maxRetries) {
      console.log(`🦉 Sir Hawkington scheduling reconnection attempt ${this.retryCount + 1}/${this.maxRetries}...`);
      this.retryTimeout = setTimeout(() => {
        this.connect();
      }, this.retryDelay);
    } else {
      console.error('🦉 Sir Hawkington exhausted all reconnection attempts');
      this.onError(new Error('Failed to establish WebSocket connection after multiple attempts'));
    }
  }

  public connect(): void {
    if (this.socket) {
      if (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING) {
        console.log('WebSocket connection already exists or is connecting');
        return;
      }
      // Clean up existing socket if it's in a closed/closing state
      this.socket.close();
      this.socket = null;
    }

    try {
      // Check for token first
      const token = localStorage.getItem('token');
      if (!token) {
        const error = new Error('No authentication token found');
        this.onError(error);
        return;
      }

      const url = this.getWebSocketUrl();
      console.log('🦔 Sir Hawkington: Connecting to WebSocket...');
      
      this.socket = new WebSocket(url);

      this.socket.onopen = () => {
        console.log('🦔 Sir Hawkington: WebSocket connection established');
        this.retryCount = 0;
      };

      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          if (message.type === 'error') {
            console.error('🚨 WebSocket error:', message.message);
            this.onError(new Error(message.message));
            return;
          }
          this.onMessage(message as CPUMetricsMessage);
        } catch (error) {
          console.error('🚨 Failed to parse WebSocket message:', error);
        }
      };

      this.socket.onerror = (event) => {
        console.error('🚨 WebSocket error:', event);
        this.onError(new Error('WebSocket connection error'));
      };

      this.socket.onclose = (event) => {
        console.log('🦔 Sir Hawkington: WebSocket closed:', event.code, event.reason);
        this.socket = null;

        if (event.code === 1008) {
          // Policy Violation (auth error) - don't retry
          console.error('🚨 Authentication failed');
          this.onError(new Error('Authentication failed'));
          return;
        }
        
        if (this.retryCount < this.maxRetries) {
          console.log(`🦔 Sir Hawkington: Attempting reconnect (${this.retryCount + 1}/${this.maxRetries})`);
          this.scheduleReconnect();
        } else {
          console.error('🚨 Maximum retry attempts reached');
          this.onError(new Error('Maximum retry attempts reached'));
        }
      };
    } catch (error) {
      console.error('🚨 Failed to establish WebSocket connection:', error);
      this.onError(error as Error);
    }  
  }

  public disconnect() {
    if (this.retryTimeout) {
      clearTimeout(this.retryTimeout);
      this.retryTimeout = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    this.retryCount = 0;
  }
}

export default WebSocketService;
