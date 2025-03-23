import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { SystemMetric, MetricsState, MetricThresholds, MetricAlert, MetricsApiResponse } from '../../types/metrics';
import { websocketService } from '../../utils/websocketService';
import { apiMethods } from '../../utils/api';

// Extended state interface to match our actual implementation
interface ExtendedMetricsState extends MetricsState {
  current: SystemMetric | null;
  historical: SystemMetric[];
  alerts: MetricAlert[];
  thresholds: MetricThresholds;
}

const initialState: ExtendedMetricsState = {
  metrics: [], // From base MetricsState
  current: null,
  historical: [],
  alerts: [],
  loading: false,
  thresholds: {
    cpu: 0,
    memory: 0,
    disk: 0,
    network: 0,
  },
  error: null,
  lastUpdated: null,
  websocketService: null
};

interface WebSocketInitStatus {
  status: 'connected' | 'failed';
  error?: string;
}

interface WebSocketMessage {
  type: string;
  data?: SystemMetric;
}

export const initializeWebSocket = createAsyncThunk(
  'metrics/initializeWebSocket',
  async (_, { dispatch }) => {
    console.log("🚀 Initializing WebSocket connection...");
    
    try {
      websocketService.setMessageCallback((data: WebSocketMessage) => {
        console.log('🎩 Sir Hawkington received WebSocket message:', data);
        if (data.type === 'system_metrics' && data.data) {
          console.log('🐹 The Hamsters are processing metrics data:', data.data);
          dispatch(updateMetrics(data.data));
        }
      });

      try {
        await websocketService.connect();
        return { 
          status: 'connected' 
        } as WebSocketInitStatus;
      } catch (wsError) {
        console.warn('WebSocket connection failed, falling back to REST API:', wsError);
        
        // Fallback to REST API if WebSocket connection fails
        try {
          console.log('💾 Falling back to REST API for metrics...');
          const response = await fetch('http://localhost:8000/api/metrics/system');
          
          if (!response.ok) {
            throw new Error(`API returned ${response.status}: ${response.statusText}`);
          }
          
          const data = await response.json();
          console.log('💾 REST API metrics data:', data);
          
          // Transform the data to match the expected format
          const metricData: SystemMetric = {
            id: crypto.randomUUID ? crypto.randomUUID() : `metric-${Date.now()}`,
            user_id: 'system',
            cpu_usage: data.cpu_usage || 0,
            memory_usage: data.memory_usage || 0,
            disk_usage: data.disk_usage || 0,
            network_usage: data.network_io ? 
              (data.network_io.sent + data.network_io.recv) / 1024 / 1024 : 0,
            process_count: data.process_count || 0,
            timestamp: data.timestamp || new Date().toISOString(),
            additional_metrics: {}
          };
          
          // Update metrics with the REST API data
          dispatch(updateMetrics(metricData));
          
          // Set up a polling interval to fetch metrics regularly
          // Store the interval ID in a variable that we can access for cleanup
          const pollInterval = setInterval(async () => {
            try {
              const pollResponse = await fetch('http://localhost:8000/api/metrics/system');
              if (!pollResponse.ok) throw new Error('API poll failed');
              
              const pollData = await pollResponse.json();
              const updatedMetric = {
                ...metricData,
                id: crypto.randomUUID ? crypto.randomUUID() : `metric-${Date.now()}`,
                cpu_usage: pollData.cpu_usage || 0,
                memory_usage: pollData.memory_usage || 0,
                disk_usage: pollData.disk_usage || 0,
                network_usage: pollData.network_io ? 
                  (pollData.network_io.sent + pollData.network_io.recv) / 1024 / 1024 : 0,
                process_count: pollData.process_count || 0,
                timestamp: pollData.timestamp || new Date().toISOString(),
              };
              
              dispatch(updateMetrics(updatedMetric));
            } catch (pollError) {
              console.error('Metrics polling failed:', pollError);
            }
          }, 5000); // Poll every 5 seconds
          
          // Store the interval ID in window for cleanup on unmount
          // @ts-ignore - Adding custom property to window
          window.metricsPollingInterval = pollInterval;
          
          // Add cleanup on page unload
          window.addEventListener('beforeunload', () => {
            // @ts-ignore - Accessing custom property from window
            if (window.metricsPollingInterval) {
              // @ts-ignore - Accessing custom property from window
              clearInterval(window.metricsPollingInterval);
            }
          });
          
          // Return success status with REST API fallback
          return { 
            status: 'connected' 
          } as WebSocketInitStatus;
        } catch (apiError) {
          console.error('REST API fallback failed:', apiError);
          return {
            status: 'failed',
            error: apiError instanceof Error ? apiError.message : 'REST API fallback failed'
          } as WebSocketInitStatus;
        }
      }
    } catch (error) {
      return {
        status: 'failed',
        error: error instanceof Error ? error.message : 'Unknown WebSocket fuckup'
      } as WebSocketInitStatus;
    }
  }
);

export const fetchSystemMetrics = createAsyncThunk<
  MetricsApiResponse,
  void,
  { rejectValue: string }
>(
  'metrics/fetch',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiMethods.get('/api/metrics/');
      return response as MetricsApiResponse;
    } catch (error) {
      const fuckups = [
        "The API is having a fucking existential crisis",
        "TypeScript ate our metrics and left a strongly-typed note",
        "The quantum shadow people finally got to the router",
        "The Meth Snail's tin foil hat interfered with the signal",
        "Sir Hawkington knocked over the server with his monocle",
        "The Stick fainted from improper type definitions again"
      ];
      
      const randomFuckup = fuckups[Math.floor(Math.random() * fuckups.length)];
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      
      return rejectWithValue(
        `Failed to fetch metrics: ${errorMessage}. ` +
        `Additional Info: ${randomFuckup}`
      );
    }
  }
);

export const createMetric = createAsyncThunk<
  SystemMetric,
  Omit<SystemMetric, 'id'>,
  { rejectValue: string }
>(
  'metrics/create',
  async (metricData, { rejectWithValue }) => {
    try {
      const response = await apiMethods.post('/api/metrics/', metricData);
      return response as SystemMetric;
    } catch (error) {
      return rejectWithValue(error instanceof Error ? error.message : 'Unknown error');
    }
  }
);

export const metricsSlice = createSlice({
  name: 'metrics',
  initialState,
  reducers: {
    updateMetrics: (state, action: PayloadAction<SystemMetric>) => {
      console.log('🔍 Redux: updateMetrics action received with payload:', action.payload);
      state.current = action.payload;
      state.historical = [...state.historical.slice(-19), action.payload];
      state.metrics = [...state.metrics, action.payload];
      state.lastUpdated = new Date().toISOString();
      console.log('💾 Redux: State updated with new metrics data');
    },
    clearMetrics: (state) => {
      state.current = null;
      state.historical = [];
      state.metrics = [];
      state.alerts = [];
      state.thresholds = {
        cpu: 0,
        memory: 0,
        disk: 0,
        network: 0,
      };
      state.lastUpdated = null;
    },
    setThresholds: (state, action: PayloadAction<MetricThresholds>) => {
      state.thresholds = action.payload;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSystemMetrics.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSystemMetrics.fulfilled, (state, action) => {
        state.loading = false;
        // Handle the response data properly
        if (action.payload && action.payload.data) {
          state.current = action.payload.data;
          state.historical = [
            ...state.historical.slice(-19),
            action.payload.data
          ];
          state.metrics = [...state.metrics, action.payload.data];
          state.lastUpdated = action.payload.timestamp;
        }
      })
      .addCase(fetchSystemMetrics.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      .addCase(createMetric.fulfilled, (state, action) => {
        state.historical.push(action.payload);
        state.metrics.push(action.payload);
      })
      .addCase(initializeWebSocket.fulfilled, (state, _action) => {
        state.error = null;
      })
      .addCase(initializeWebSocket.rejected, (state, action) => {
        state.error = 'Websocket fucked off again: ' + action.error.message;
      });
  }
});

export const { 
  updateMetrics, 
  clearMetrics, 
  setThresholds 
} = metricsSlice.actions; 

export default metricsSlice.reducer;