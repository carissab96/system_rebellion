import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { MetricAlert } from '../../../types/metrics';
import { AlertSeverity } from '../../../types/metrics';

export interface NetworkMetric {
    timestamp: string | number | Date;
    usage_percent: number;
    network: { bytes_sent: number; bytes_recv: number; packets_sent: number; 
        packets_recv: number; rate_mbps: number; sent_rate_bps: number; 
        recv_rate_bps: number; 
        io_stats: { sent_rate: number; recv_rate: number; err_in: number; 
            err_out: number; drops_in: number; drops_out: number; }; 
            interfaces: never[]
             protocol_stats: { tcp: { active: number; established: number; 
                listening: number; }; udp: { active: number; }; 
                http: { connections: number; }; 
                https: { connections: number; }; 
                dns: { queries: number; }; }; };
    alerts: MetricAlert[];
}

export interface NetworkThresholds {
    usage: {
        warning: number;
        critical: number;
    };
}

export interface NetworkState {
    current: NetworkMetric | null;
    historical: NetworkMetric[];
    alerts: MetricAlert[];
    thresholds: NetworkThresholds;
    networkLoading: boolean;
    networkError: string | null;
    lastUpdated: string | null;
}

const initialState: NetworkState = {
    current: null,
    historical: [],
    alerts: [],
    thresholds: {
        usage: {
            warning: 70,
            critical: 90
        }
    },
    networkLoading: false,
    networkError: null,
    lastUpdated: null
};
const checkThresholds = (metrics: NetworkMetric, thresholds: NetworkThresholds): MetricAlert[] => {
    const alerts: MetricAlert[] = [];
    const now = new Date().toISOString();

    // Check network usage threshold
    if (metrics.usage_percent >= thresholds.usage.critical) {
        alerts.push({
            id: `network-usage-${Date.now()}`,
            metric_type: 'network',
            type: 'usage',
            severity: AlertSeverity.HIGH,
            threshold: thresholds.usage.critical,
            current_value: metrics.usage_percent,
            timestamp: now,
            message: `Network usage critical: ${metrics.usage_percent}%`
        });
    } else if (metrics.usage_percent >= thresholds.usage.warning) {
        alerts.push({
            id: `network-usage-${Date.now()}`,
            metric_type: 'network',
            type: 'usage',
            severity: AlertSeverity.MEDIUM,
            threshold: thresholds.usage.warning,
            current_value: metrics.usage_percent,
            timestamp: now,
            message: `Network usage high: ${metrics.usage_percent}%`
        });
    }

    return alerts;
};
const networkSlice = createSlice({
    name: 'network',
    initialState,
    reducers: {
        setNetworkLoading: (state, action: PayloadAction<boolean>) => {
            state.networkLoading = action.payload;
        },
        setNetworkError: (state, action: PayloadAction<string | null>) => {
            state.networkError = action.payload;
            state.networkLoading = false;
        },
        updateNetworkMetrics: (state, action: PayloadAction<NetworkMetric>) => {
            const newMetric = action.payload;
            state.current = newMetric;
            state.historical = [...state.historical, newMetric].slice(-1000); // Keep last 1000 readings
            state.lastUpdated = new Date().toISOString();
            
            // Check for threshold violations
            const alerts = checkThresholds(newMetric, state.thresholds);
            if (alerts.length > 0) {
                state.alerts = [...state.alerts, ...alerts].slice(-50); // Keep last 50 alerts
            }
            
            state.networkLoading = false;
            state.networkError = null;
        },
        updateThresholds: (state, action: PayloadAction<Partial<NetworkThresholds>>) => {
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
            state.networkLoading = false;
            state.networkError = null;
            state.lastUpdated = null;
        }
    }
});

// Export actions
export const { setNetworkLoading, setNetworkError, updateNetworkMetrics, updateThresholds, clearAlerts, reset } = networkSlice.actions;

// Export selectors
export const selectNetworkMetrics = (state: { network: NetworkState }) => state.network.current;
export const selectNetworkHistorical = (state: { network: NetworkState }) => state.network.historical;
export const selectNetworkAlerts = (state: { network: NetworkState }) => state.network.alerts;
export const selectNetworkThresholds = (state: { network: NetworkState }) => state.network.thresholds;
export const selectNetworkLoading = (state: { network: NetworkState }) => state.network.networkLoading;
export const selectNetworkError = (state: { network: NetworkState }) => state.network.networkError;
export const selectNetworkLastUpdated = (state: { network: NetworkState }) => state.network.lastUpdated;

export default networkSlice.reducer;
