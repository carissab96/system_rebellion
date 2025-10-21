// store/slices/metricsSlice.ts
import { createSlice,type PayloadAction } from '@reduxjs/toolkit';

interface SystemMetricsState {
  // Core metrics
  timestamp: string | null;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_recv_rate: number;
  network_sent_rate: number;
  process_count: number;
  
  // Detailed nested data
  cpu: {
    usage_percent: number;
    cores: number[];
    temperature: number;
    top_processes: any[];
    physical_cores: number;
    logical_cores: number;
    frequency_mhz: number;
  } | null;
  
  memory: {
    total: number;
    available: number;
    used: number;
    percent: number;
    top_processes: any[];
  } | null;
  
  disk: {
    percent: number;
    total: number;
    used: number;
    free: number;
    read_bytes: number;
    write_bytes: number;
  } | null;
  
  network: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
    connection_stats: any;
    interface_stats: any;
  } | null;
  
  system_info: {
    hostname: string | null;
    physical_cores: number;
    logical_cores: number;
    total_memory: number;
    total_disk: number;
  } | null;
  
  // Connection state
  connectionStatus: 'idle' | 'connecting' | 'connected' | 'disconnected' | 'error';
  lastError: string | null;
  lastUpdate: string | null;
}

const initialState: SystemMetricsState = {
  timestamp: null,
  cpu_usage: 0,
  memory_usage: 0,
  disk_usage: 0,
  network_recv_rate: 0,
  network_sent_rate: 0,
  process_count: 0,
  cpu: null,
  memory: null,
  disk: null,
  network: null,
  system_info: null,
  connectionStatus: 'idle',
  lastError: null,
  lastUpdate: null
};

const metricsSlice = createSlice({
  name: 'metrics',
  initialState,
  reducers: {
    updateMetrics: (state, action: PayloadAction<Partial<SystemMetricsState>>) => {
      Object.assign(state, action.payload);
      state.lastUpdate = new Date().toISOString();
    },
    setConnectionStatus: (state, action: PayloadAction<SystemMetricsState['connectionStatus']>) => {
      state.connectionStatus = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.lastError = action.payload;
      state.connectionStatus = 'error';
    },
    resetMetrics: () => initialState
  }
});

export const { updateMetrics, setConnectionStatus, setError, resetMetrics } = metricsSlice.actions;
export default metricsSlice.reducer;