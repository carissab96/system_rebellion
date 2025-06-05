import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { MetricAlert, AlertSeverity } from '../../../types/metrics';

export interface CPUMetric {
  cpu_usage: number;
  cpu_thread_count: number;
  cpu_core_count: number;
  cpu_frequency: number;
  cpu_temperature: number;
  cpu: any;
  timestamp: any;
  cpu_model: string;
  usage_percent: number;
  cores: {
    id: number;
    usage: number;
  }[];
  physical_cores: number;
  logical_cores: number;
  temperature?: number;
  frequency_mhz: number;
  top_processes: {
    pid: number;
    name: string;
    cpu_percent: number;
    memory_percent: number;
  }[];
}

export interface CPUThresholds {
  usage: {
    warning: number;
    critical: number;
  };
  temperature?: {
    warning: number;
    critical: number;
  };
}

interface CPUState {
  current: CPUMetric | null;
  historical: CPUMetric[];
  alerts: MetricAlert[];
  thresholds: CPUThresholds;
  cpuLoading: boolean;
  cpuError: string | null;
  lastUpdated: string | null;
}

const initialState: CPUState = {
  current: null,
  historical: [],
  alerts: [],
  thresholds: {
    usage: {
      warning: 70,
      critical: 90
    },
    temperature: {
      warning: 70,
      critical: 85
    }
  },
  cpuLoading: false,
  cpuError: null,
  lastUpdated: null
};

// Helper function to check CPU thresholds and generate alerts
const checkThresholds = (metrics: CPUMetric, thresholds: CPUThresholds): MetricAlert[] => {
  const alerts: MetricAlert[] = [];
  const now = new Date().toISOString();

  // Check CPU usage threshold
  if (metrics.usage_percent >= thresholds.usage.critical) {
    alerts.push({
      id: `cpu-usage-${Date.now()}`,
      metric_type: 'cpu',
      type: 'usage',
      severity: AlertSeverity.HIGH,
      threshold: thresholds.usage.critical,
      current_value: metrics.usage_percent,
      timestamp: now,
      message: `CPU usage critical: ${metrics.usage_percent}%`
    });
  } else if (metrics.usage_percent >= thresholds.usage.warning) {
    alerts.push({
      id: `cpu-usage-${Date.now()}`,
      metric_type: 'cpu',
      type: 'usage',
      severity: AlertSeverity.MEDIUM,
      threshold: thresholds.usage.warning,
      current_value: metrics.usage_percent,
      timestamp: now,
      message: `CPU usage high: ${metrics.usage_percent}%`
    });
  }

  // Check temperature if available
  if (metrics.temperature && thresholds.temperature) {
    if (metrics.temperature >= thresholds.temperature.critical) {
      alerts.push({
        id: `cpu-temp-${Date.now()}`,
        metric_type: 'cpu',
        type: 'temperature',
        severity: AlertSeverity.HIGH,
        threshold: thresholds.temperature.critical,
        current_value: metrics.temperature,
        timestamp: now,
        message: `CPU temperature critical: ${metrics.temperature}°C`
      });
    } else if (metrics.temperature >= thresholds.temperature.warning) {
      alerts.push({
        id: `cpu-temp-${Date.now()}`,
        metric_type: 'cpu',
        type: 'temperature',
        severity: AlertSeverity.MEDIUM,
        threshold: thresholds.temperature.warning,
        current_value: metrics.temperature,
        timestamp: now,
        message: `CPU temperature high: ${metrics.temperature}°C`
      });
    }
  }

  return alerts;
};

const cpuSlice = createSlice({
  name: 'cpu',
  initialState,
  reducers: {
    setCPULoading: (state, action: PayloadAction<boolean>) => {
      state.cpuLoading = action.payload;
    },
    setCPUError: (state, action: PayloadAction<string | null>) => {
      state.cpuError = action.payload;
      state.cpuLoading = false;
    },
    updateCPUMetrics: (state, action: PayloadAction<CPUMetric>) => {
      const newMetric = action.payload;
      state.current = newMetric;
      state.historical = [...state.historical, newMetric].slice(-1000); // Keep last 1000 readings
      state.lastUpdated = new Date().toISOString();
      
      // Check for threshold violations
      const alerts = checkThresholds(newMetric, state.thresholds);
      if (alerts.length > 0) {
        state.alerts = [...state.alerts, ...alerts].slice(-50); // Keep last 50 alerts
      }
      
      state.cpuLoading = false;
      state.cpuError = null;
    },
    updateThresholds: (state, action: PayloadAction<Partial<CPUThresholds>>) => {
      state.thresholds = {
        ...state.thresholds,
        ...action.payload
      };
    },
    clearAlerts: (state) => {
      state.alerts = [];
    },
    reset: (state) => {
      state.current = null;
      state.historical = [];
      state.alerts = [];
      state.cpuLoading = false;
      state.cpuError = null;
      state.lastUpdated = null;
    }
  }
});

// Export actions
export const {
  setCPULoading,
  setCPUError,
  updateCPUMetrics,
  updateThresholds,
  clearAlerts,
  reset
} = cpuSlice.actions;

// Export selectors
export const selectCPUMetrics = (state: { cpu: CPUState }) => state.cpu.current;
export const selectCPUHistorical = (state: { cpu: CPUState }) => state.cpu.historical;
export const selectCPUAlerts = (state: { cpu: CPUState }) => state.cpu.alerts;
export const selectCPUThresholds = (state: { cpu: CPUState }) => state.cpu.thresholds;
export const selectCPULoading = (state: { cpu: CPUState }) => state.cpuLoading;
export const selectCPUError = (state: { cpu: CPUState }) => state.cpuError;
export const selectCPULastUpdated = (state: { cpu: CPUState }) => state.cpu.lastUpdated;

export default cpuSlice.reducer;