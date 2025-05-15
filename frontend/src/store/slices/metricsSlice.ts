import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { 
  SystemMetric, 
  MetricThresholds, 
  MetricAlert, 
  AlertSeverity,
  MetricsState
} from '../../types/metrics';
import webSocketService from '../../utils/websocketService';

type WebSocketMessage = {
  type: string;
  data?: any;
  error?: string;
  timestamp?: number;
};

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

// Track if WebSocket is initialized
let isWebSocketInitialized = false;

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
      message: `CPU usage critical: ${metrics.cpu_usage}%`
    });
  } else if (metrics.cpu_usage >= thresholds.cpu.warning) {
    alerts.push({
      id: `cpu-${Date.now()}-warn`,
      metric_type: 'cpu',
      severity: AlertSeverity.MEDIUM,
      threshold: thresholds.cpu.warning,
      current_value: metrics.cpu_usage,
      timestamp: now,
      message: `CPU usage high: ${metrics.cpu_usage}%`
    });
  }
  
  // Check memory threshold
  if (metrics.memory_percent >= thresholds.memory.critical) {
    alerts.push({
      id: `memory-${Date.now()}`,
      metric_type: 'memory',
      severity: AlertSeverity.HIGH,
      threshold: thresholds.memory.critical,
      current_value: metrics.memory_percent,
      timestamp: now,
      message: `Memory usage critical: ${metrics.memory_percent}%`
    });
  } else if (metrics.memory_percent >= thresholds.memory.warning) {
    alerts.push({
      id: `memory-${Date.now()}-warn`,
      metric_type: 'memory',
      severity: AlertSeverity.MEDIUM,
      threshold: thresholds.memory.warning,
      current_value: metrics.memory_percent,
      timestamp: now,
      message: `Memory usage high: ${metrics.memory_percent}%`
    });
  }
  
  // Check disk threshold
  if (metrics.disk_percent >= thresholds.disk.critical) {
    alerts.push({
      id: `disk-${Date.now()}`,
      metric_type: 'disk',
      severity: AlertSeverity.HIGH,
      threshold: thresholds.disk.critical,
      current_value: metrics.disk_percent,
      timestamp: now,
      message: `Disk usage critical: ${metrics.disk_percent}%`
    });
  } else if (metrics.disk_percent >= thresholds.disk.warning) {
    alerts.push({
      id: `disk-${Date.now()}-warn`,
      metric_type: 'disk',
      severity: AlertSeverity.MEDIUM,
      threshold: thresholds.disk.warning,
      current_value: metrics.disk_percent,
      timestamp: now,
      message: `Disk usage high: ${metrics.disk_percent}%`
    });
  }
  
  // Check network threshold if available
  if (metrics.network_percent && metrics.network_percent >= thresholds.network.critical) {
    alerts.push({
      id: `network-${Date.now()}`,
      metric_type: 'network',
      severity: AlertSeverity.HIGH,
      threshold: thresholds.network.critical,
      current_value: metrics.network_percent,
      timestamp: now,
      message: `Network usage critical: ${metrics.network_percent}%`
    });
  } else if (metrics.network_percent && metrics.network_percent >= thresholds.network.warning) {
    alerts.push({
      id: `network-${Date.now()}-warn`,
      metric_type: 'network',
      severity: AlertSeverity.MEDIUM,
      threshold: thresholds.network.warning,
      current_value: metrics.network_percent,
      timestamp: now,
      message: `Network usage high: ${metrics.network_percent}%`
    });
  }
  
  return alerts;
};

// Initial state
const initialState: ExtendedMetricsState = {
  metrics: [],
  current: null,
  historical: [],
  alerts: [],
  thresholds: {
    cpu: { warning: 70, critical: 90 },
    memory: { warning: 70, critical: 90 },
    disk: { warning: 70, critical: 90 },
    network: { warning: 70, critical: 90 },
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
      state.connectionStatus = action.payload ? 'error' : 'disconnected';
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
      state.thresholds = {
        cpu: { warning: 70, critical: 90 },
        memory: { warning: 70, critical: 90 },
        disk: { warning: 70, critical: 90 },
        network: { warning: 70, critical: 90 },
      };
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

// WebSocket connection management
export const initializeWebSocket = () => async (dispatch: any) => {
  if (isWebSocketInitialized) {
    console.log("🧐 Sir Hawkington notes the WebSocket is already initialized");
    return;
  }

  console.log("🔌 [metricsSlice] Initializing WebSocket connection...");
  
  // Set up message handler
  webSocketService.setMessageCallback((message: WebSocketMessage) => {
    try {
      if (message.type === 'system_metrics' && message.data) {
        const metric = message.data as SystemMetric;
        console.log("📊 [metricsSlice] Received metrics update:", metric);
        dispatch(metricsSlice.actions.updateMetrics(metric));
      }
    } catch (error) {
      console.error('❌ [metricsSlice] Error processing WebSocket message:', error);
      console.error("🐌 The Meth Snail is confused by this message format!");
      dispatch(metricsSlice.actions.setWebSocketError('Error processing WebSocket message'));
    }
  });
  
  // Set up event listeners
  webSocketService.on('connected', () => {
    console.log("✅ [metricsSlice] WebSocket connected successfully!");
    dispatch(metricsSlice.actions.setConnectionStatus('connected'));
    dispatch(metricsSlice.actions.setWebSocketError(null));
  });
  
  webSocketService.on('disconnected', () => {
    console.log("⚠️ [metricsSlice] WebSocket disconnected");
    dispatch(metricsSlice.actions.setConnectionStatus('disconnected'));  
  });
  
  webSocketService.on('error', (error: Error) => {
    console.error('❌ [metricsSlice] WebSocket error:', error);
    console.error("🐹 The Hamsters report a disturbance in the connection tubes!");
    dispatch(metricsSlice.actions.setWebSocketError(error.message));
  });
  
  webSocketService.on('statusChange', (status: string) => {
    console.log(`🔄 [metricsSlice] Connection status changed to: ${status}`);
    dispatch(metricsSlice.actions.setConnectionStatus(status as ConnectionStatus));
  });

  // Connect to WebSocket
  dispatch(metricsSlice.actions.setConnectionStatus('connecting'));
  try {
    const connected = await webSocketService.connect();
    if (!connected) {
      throw new Error('Failed to establish WebSocket connection');
    }
    isWebSocketInitialized = true;
    console.log("🎉 [metricsSlice] WebSocket initialization complete!");
  } catch (error) {
    console.error('❌ [metricsSlice] Failed to initialize WebSocket:', error);
    dispatch(metricsSlice.actions.setWebSocketError('Failed to connect to WebSocket'));
  }
};

// Clean up WebSocket on unmount
export const cleanupWebSocket = (): void => {
  console.log("🧹 [metricsSlice] Cleaning up WebSocket...");
  try {
    webSocketService.disconnect();
    isWebSocketInitialized = false;
    console.log("✅ [metricsSlice] WebSocket cleanup complete");
  } catch (error) {
    console.error('❌ [metricsSlice] Error during WebSocket cleanup:', error);
  }
};



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