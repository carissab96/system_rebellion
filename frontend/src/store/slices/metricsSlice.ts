import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { SystemMetric, MetricsState, MetricThresholds, MetricAlert, MetricsApiResponse } from '../../types/metrics';
import { websocketService } from '../../utils/websocketService';
import axios from 'axios';
import { API_BASE_URL, apiMethods } from '../../utils/api';

// Track if we're currently using the fallback
let isUsingFallback = false;
let fallbackInterval: NodeJS.Timeout | null = null;

// Extended state interface to match our actual implementation
interface ExtendedMetricsState extends MetricsState {
  current: SystemMetric | null;
  historical: SystemMetric[];
  alerts: MetricAlert[];
  thresholds: MetricThresholds;
  useWebSocket: boolean;
  lastUpdate: number | null;
}

const initialState: ExtendedMetricsState = {
  metrics: [], // From base MetricsState
  current: null,
  historical: [],
  alerts: [],
  loading: false,
  thresholds: {
    cpu: 80, // Default thresholds (percentage)
    memory: 80,
    disk: 80,
    network: 80,
  },
  error: null,
  lastUpdated: null,
  useWebSocket: true,
  lastUpdate: null,
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

// Function to handle fallback to REST API
const startFallbackPolling = async (dispatch: any) => {
  if (isUsingFallback) return; // Already in fallback mode
  
  isUsingFallback = true;
  console.log('💾 Starting REST API fallback polling...');
  
  // Initial fetch
  await fetchMetricsWithFallback(dispatch);
  
  // Set up polling every 5 seconds
  fallbackInterval = setInterval(async () => {
    await fetchMetricsWithFallback(dispatch);
  }, 5000);
};

// Stop fallback polling
const stopFallbackPolling = () => {
  if (fallbackInterval) {
    clearInterval(fallbackInterval);
    fallbackInterval = null;
  }
  isUsingFallback = false;
  console.log('🔌 Stopped REST API fallback, returning to WebSocket');
};

// Helper function to fetch metrics with fallback
const fetchMetricsWithFallback = async (dispatch: any) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/metrics/system`);
    const data = response.data;
    
    if (data) {
      // Update Redux with the data from REST API
      dispatch(updateMetrics(data));
    }
    
    return data;
  } catch (error) {
    console.error('Error fetching metrics via REST API:', error);
    return null;
  }
};

export const initializeWebSocket = createAsyncThunk(
  'metrics/initializeWebSocket',
  async (_, { dispatch }) => {
    console.log("🚀 Initializing WebSocket connection...");
    
    // Set up message handler
    const messageHandler = (data: WebSocketMessage) => {
      console.log('🎩 Sir Hawkington received WebSocket message:', data);
      if (data.type === 'system_metrics' && data.data) {
        console.log('🐹 The Hamsters are processing metrics data:', data.data);
        dispatch(updateMetrics(data.data));
      }
    };
    
    websocketService.setMessageCallback(messageHandler);

    try {
      // Let the WebSocketService handle its own connection logic and retries
      await websocketService.connect();
      
      // If we get here, connection was successful
      if (isUsingFallback) {
        stopFallbackPolling();
      }
      
      return { 
        status: 'connected' 
      } as WebSocketInitStatus;
    } catch (wsError) {
      console.warn('WebSocket connection failed, falling back to REST API:', wsError);
      
      // Only start fallback if we're not already using it
      if (!isUsingFallback) {
        await startFallbackPolling(dispatch);
      }
      
      return { 
        status: 'failed',
        error: 'WebSocket connection failed, using REST API fallback'
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
      .addCase(initializeWebSocket.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(initializeWebSocket.fulfilled, (state, action) => {
        state.loading = false;
        state.error = null;
        state.useWebSocket = action.payload.status === 'connected';
        state.lastUpdate = Date.now();
        
        if (action.payload.status === 'connected') {
          console.log('🔌 WebSocket connection established');
        } else {
          console.log('📡 Using REST API fallback for metrics');
        }
      })
      .addCase(initializeWebSocket.rejected, (state, action) => {
        state.loading = false;
        state.useWebSocket = false;
        state.error = action.error.message || 'Failed to initialize WebSocket, using REST API fallback';
        console.error(state.error);
      })
      .addCase(fetchSystemMetrics.pending, (state) => {
        if (!state.loading) {
          state.loading = true;
          state.error = null;
        }
      })
      .addCase(fetchSystemMetrics.fulfilled, (state, action) => {
        state.loading = false;
        state.error = null;
        state.lastUpdate = Date.now();
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
      });
  }
});

export const { 
  updateMetrics, 
  clearMetrics, 
  setThresholds 
} = metricsSlice.actions; 

export default metricsSlice.reducer;