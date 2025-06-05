import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { MetricAlert, AlertSeverity } from '../../../types/metrics';

export interface MemoryMetric {
    timestamp: string | number | Date;
    additional: any;
    memory_buffer: number;
    memory_available: number;
    memory_used: number;
    memory_free: number;
    memory_cache: number;
    memory_swap_percent: number;
    memory_swap_free: number;
    memory_swap_used: any;
    memory_swap_total: number;
    memory_total: number;
    memory_percent: any;
    usage_percent: number;
    total_space: number;
    used_space: number;
    available_space: number;
    mount_point: string;
    file_system: string;
    type: string;
    alerts: MetricAlert[];
}

export interface MemoryThresholds {
    usage: {
        warning: number;
        critical: number;
    };
}

export interface MemoryState {
    current: MemoryMetric | null;
    historical: MemoryMetric[];
    alerts: MetricAlert[];
    thresholds: MemoryThresholds;
    memoryLoading: boolean;
    memoryError: string | null;
    lastUpdated: string | null;
}

const initialState: MemoryState = {
    current: null,
    historical: [],
    alerts: [],
    thresholds: {
        usage: {
            warning: 70,
            critical: 90
        }
    },
    memoryLoading: false,
    memoryError: null,
    lastUpdated: null
};

const checkThresholds = (metrics: MemoryMetric, thresholds: MemoryThresholds): MetricAlert[] => {
    const alerts: MetricAlert[] = [];
    const now = new Date().toISOString();

    // Check memory usage threshold
    if (metrics.usage_percent >= thresholds.usage.critical) {
        alerts.push({
            id: `memory-usage-${Date.now()}`,
            metric_type: 'memory',
            type: 'usage',
            severity: AlertSeverity.HIGH,
            threshold: thresholds.usage.critical,
            current_value: metrics.usage_percent,
            timestamp: now,
            message: `Memory usage critical: ${metrics.usage_percent}%`
        });
    } else if (metrics.usage_percent >= thresholds.usage.warning) {
        alerts.push({
            id: `memory-usage-${Date.now()}`,
            metric_type: 'memory',
            type: 'usage',
            severity: AlertSeverity.MEDIUM,
            threshold: thresholds.usage.warning,
            current_value: metrics.usage_percent,
            timestamp: now,
            message: `Memory usage high: ${metrics.usage_percent}%`
        });
    }

    return alerts;
};

const memorySlice = createSlice({
    name: 'memory',
    initialState,
    reducers: {
        setMemoryLoading: (state, action: PayloadAction<boolean>) => {
            state.memoryLoading = action.payload;
        },
        setMemoryError: (state, action: PayloadAction<string | null>) => {
            state.memoryError = action.payload;
            state.memoryLoading = false;
        },
        updateMemoryMetrics: (state, action: PayloadAction<MemoryMetric>) => {
            const newMetric = action.payload;
            state.current = newMetric;
            state.historical = [...state.historical, newMetric].slice(-1000); // Keep last 1000 readings
            state.lastUpdated = new Date().toISOString();
            
            // Check for threshold violations
            const alerts = checkThresholds(newMetric, state.thresholds);
            if (alerts.length > 0) {
                state.alerts = [...state.alerts, ...alerts].slice(-50); // Keep last 50 alerts
            }
            
            state.memoryLoading = false;
            state.memoryError = null;
        },
        updateThresholds: (state, action: PayloadAction<Partial<MemoryThresholds>>) => {
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
            state.memoryLoading = false;
            state.memoryError = null;
            state.lastUpdated = null;
        }
    }
}); 

// Export actions
export const {
    setMemoryLoading,
    setMemoryError,
    updateMemoryMetrics,
    updateThresholds,
    clearAlerts,
    reset
} = memorySlice.actions;

// Export selectors
export const selectMemoryMetrics = (state: { memory: MemoryState }) => state.memory.current;
export const selectMemoryHistorical = (state: { memory: MemoryState }) => state.memory.historical;
export const selectMemoryAlerts = (state: { memory: MemoryState }) => state.memory.alerts;
export const selectMemoryThresholds = (state: { memory: MemoryState }) => state.memory.thresholds;
export const selectMemoryLoading = (state: { memory: MemoryState }) => state.memory.memoryLoading;
export const selectMemoryError = (state: { memory: MemoryState }) => state.memory.memoryError;
export const selectMemoryLastUpdated = (state: { memory: MemoryState }) => state.memory.lastUpdated;    

export default memorySlice.reducer;