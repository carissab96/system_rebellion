// src/store/slices/metricsSlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { 
  SystemMetric, 
  MetricThresholds, 
  MetricAlert, 
  AlertSeverity,
  MetricsState
} from '../../types/metrics';

type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'error';

interface ExtendedMetricsState extends Omit<MetricsState, 'connectionStatus' | 'metrics'> {
  metrics: SystemMetric[];
  current: SystemMetric | null;
  historical: SystemMetric[];
  alerts: MetricAlert[];
  thresholds: MetricThresholds;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  lastUpdate: number | null;
  useWebSocket: boolean;
  connectionStatus: ConnectionStatus;
}

// Define the RootState type for type-safe selectors
interface RootState {
  metrics: ExtendedMetricsState;
}

declare module 'react-redux' {
  interface DefaultRootState extends RootState {}
}

// Helper function to check thresholds and generate alerts
const checkThresholds = (metrics: SystemMetric, thresholds: MetricThresholds): MetricAlert[] => {
  const alerts: MetricAlert[] = [];
  const now = new Date().toISOString();
  
  // Check CPU threshold
  if (metrics.cpu_usage >= thresholds.cpu.critical) {
    alerts.push({
      id: `cpu-${Date.now()}`,
      metric_type: 'cpu',
      severity: AlertSeverity.HIGH,
      threshold: thresholds.cpu.critical,
      current_value: metrics.cpu_usage,
      timestamp: now,
      message: `CPU usage critical: ${metrics.cpu_usage}%`,
      type: 'usage'
    });
  } else if (metrics.cpu_usage >= thresholds.cpu.warning) {
    alerts.push({
      id: `cpu-${Date.now()}-warn`,
      metric_type: 'cpu',
      severity: AlertSeverity.MEDIUM,
      threshold: thresholds.cpu.warning,
      current_value: metrics.cpu_usage,
      timestamp: now,
      message: `CPU usage high: ${metrics.cpu_usage}%`,
      type: 'usage'
    });
  }
  
  // Same pattern for memory, disk, network checks
  // ... (keep your existing threshold checks here)
  
  return alerts;
};

// Initial state
const initialState: ExtendedMetricsState = {
  metrics: [],
  current: null,
  historical: [],
  alerts: [],
  thresholds: {
    cpu: { warning: 70, critical: 90, normal: 0, high: 0, low: 0, medium: 0, very_high: 0, very_low: 0 },
    memory: { warning: 70, critical: 90, normal: 0, high: 0, low: 0, medium: 0, very_high: 0, very_low: 0 },
    disk: { warning: 70, critical: 90, normal: 0, high: 0, low: 0, medium: 0, very_high: 0, very_low: 0 },
    network: { warning: 70, critical: 90, normal: 0, high: 0, low: 0, medium: 0, very_high: 0, very_low: 0 },
  },
  loading: false,
  error: null,
  lastUpdated: null,
  lastUpdate: null,
  useWebSocket: true,
  connectionStatus: 'disconnected',
};

// Create the metrics slice
const metricsSlice = createSlice({
  name: 'metrics',
  initialState,
  reducers: {
    // Set WebSocket error status
    setWebSocketError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.loading = false;
      if (action.payload) {
        state.connectionStatus = 'error';
      }
    },
    
    // Update metrics with new data
    updateMetrics: (state, action: PayloadAction<SystemMetric>) => {
      const newMetric = action.payload;
      state.metrics = [...state.metrics, newMetric].slice(-100);
      state.current = newMetric;
      state.historical = [...state.historical, newMetric].slice(-1000);
      state.lastUpdated = new Date().toISOString();
      state.lastUpdate = Date.now();
      
      // Check for threshold violations
      const alerts = checkThresholds(newMetric, state.thresholds);
      if (alerts.length > 0) {
        state.alerts = [...state.alerts, ...alerts].slice(-50);
      }
    },
    
    // Reset metrics to initial state
    resetMetrics: (state) => {
      state.metrics = [];
      state.alerts = [];
      state.current = null;
      state.historical = [];
      state.error = null;
      state.connectionStatus = 'disconnected';
    },
    
    // Update threshold values
    setThresholds: (state, action: PayloadAction<Partial<MetricThresholds>>) => {
      state.thresholds = {
        ...state.thresholds,
        ...action.payload,
      };
    },
    
    // Set connection status
    setConnectionStatus: (state, action: PayloadAction<ConnectionStatus>) => {
      state.connectionStatus = action.payload;
    },
  }
});

// Export selectors with proper typing
export const selectCurrentMetrics = (state: RootState) => state.metrics.current;
export const selectHistoricalMetrics = (state: RootState) => state.metrics.historical;
export const selectAlerts = (state: RootState) => state.metrics.alerts;
export const selectConnectionStatus = (state: RootState) => state.metrics.connectionStatus;
export const selectError = (state: RootState) => state.metrics.error;

// Export the slice's reducer and actions
export const { 
  setWebSocketError, 
  updateMetrics, 
  resetMetrics, 
  setThresholds, 
  setConnectionStatus 
} = metricsSlice.actions;

export default metricsSlice.reducer;