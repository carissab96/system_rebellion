import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { MetricAlert, AlertSeverity } from '../../../types/metrics';


export interface DiskMetric {
  usage_percent: number;
  total_space: number;
  used_space: number;
  available_space: number;
  mount_point: string;
  file_system: string;
  type: string;
  alerts: MetricAlert[];
}

export interface DiskThresholds {
  usage: {
    warning: number;
    critical: number;
  };
}

export interface DiskState {
  current: DiskMetric | null;
  historical: DiskMetric[];
  alerts: MetricAlert[];
  thresholds: DiskThresholds;
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
}

const initialState: DiskState = {
    current: null,
    historical: [],
    alerts: [],
    thresholds: {
        usage: {
            warning: 70,
            critical: 90
        }
    },
    loading: false,
    error: null,
    lastUpdated: null
};
const checkThresholds = (metrics: DiskMetric, thresholds: DiskThresholds): MetricAlert[] => {
  const alerts: MetricAlert[] = [];
  const now = new Date().toISOString();

  // Check disk usage threshold
  if (metrics.usage_percent >= thresholds.usage.critical) {
    alerts.push({
      id: `disk-usage-${Date.now()}`,
      metric_type: 'disk',
      type: 'usage',
      severity: AlertSeverity.HIGH,
      threshold: thresholds.usage.critical,
      current_value: metrics.usage_percent,
      timestamp: now,
      message: `Disk usage critical: ${metrics.usage_percent}%`
    });
  } else if (metrics.usage_percent >= thresholds.usage.warning) {
    alerts.push({
      id: `disk-usage-${Date.now()}`,
      metric_type: 'disk',
      type: 'usage',
      severity: AlertSeverity.MEDIUM,
      threshold: thresholds.usage.warning,
      current_value: metrics.usage_percent,
      timestamp: now,
      message: `Disk usage high: ${metrics.usage_percent}%`
    });
  }

  return alerts;
};

const diskSlice = createSlice({
  name: 'disk',
  initialState,
  reducers: {
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.loading = action.payload;
    },
    setError: (state, action: PayloadAction<string | null>) => {
      state.error = action.payload;
      state.loading = false;
    },
    updateMetrics: (state, action: PayloadAction<DiskMetric>) => {
      const newMetric = action.payload;
      state.current = newMetric;
      state.historical = [...state.historical, newMetric].slice(-1000); // Keep last 1000 readings
      state.lastUpdated = new Date().toISOString();
      
      // Check for threshold violations
      const alerts = checkThresholds(newMetric, state.thresholds);
      if (alerts.length > 0) {
        state.alerts = [...state.alerts, ...alerts].slice(-50); // Keep last 50 alerts
      }
      
      state.loading = false;
      state.error = null;
    },
    updateThresholds: (state, action: PayloadAction<Partial<DiskThresholds>>) => {
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
      state.loading = false;
      state.error = null;
      state.lastUpdated = null;
    }
  }
}); 

// Export actions
export const {
  setLoading,
  setError,
  updateMetrics,
  updateThresholds,
  clearAlerts,
  reset
} = diskSlice.actions;

// Export selectors
export const selectDiskMetrics = (state: { disk: DiskState }) => state.disk.current;
export const selectDiskHistorical = (state: { disk: DiskState }) => state.disk.historical;
export const selectDiskAlerts = (state: { disk: DiskState }) => state.disk.alerts;
export const selectDiskThresholds = (state: { disk: DiskState }) => state.disk.thresholds;
export const selectDiskLoading = (state: { disk: DiskState }) => state.disk.loading;
export const selectDiskError = (state: { disk: DiskState }) => state.disk.error;
export const selectDiskLastUpdated = (state: { disk: DiskState }) => state.disk.lastUpdated;

export default diskSlice.reducer;
    