// src/types/metrics.ts
import { CPUData } from '../components/metrics/cpu/Tabs/types';

// Base metric type for individual readings


export interface AdditionalMetrics {
  swap_usage?: number;
  cpu_temperature?: number;
  active_python_processes?: number;
  load_average?: number[];
  network_details?: any;
  [key: string]: any;
}

// Type for optimization profile thresholds
interface ThresholdLevels {
  warning: number;
  critical: number;
  normal: number;
  high: number;
  low: number;
  medium: number;
  very_high: number;
  very_low: number;
  
}

export interface MetricThresholds {
  cpu: ThresholdLevels;
  memory: ThresholdLevels;
  disk: ThresholdLevels;
  network: ThresholdLevels;
  timestamp?: string;
}

export interface SystemMetric {
  id: string;
  user_id: string;
  cpu_usage: number;
  cpu_temperature?: number;
  cpu_frequency?: number;
  cpu_core_count?: number;
  cpu_thread_count?: number;
  cpu_model?: string;
  cpu_vendor?: string;
  cpu_cache?: number;
  cpu_cache_size?: number;
  cpu_cache_lines?: number;
  cpu_cache_type?: string;
  cpu_cache_level?: number;
  cpu_cache_associativity?: number;
  cpu_cache_line_size?: number;
  cpu_cache_line_count?: number;
  cpu_cache_line_associativity?: number;
  cpu: CPUData;
  memory_usage: number;
  memory_allocation: number;
  memory_total: number;
  memory_available: number;
  memory_free: number;
  memory_buffer: number;
  memory_cache: number;
  memory_swap: number;
  memory_swap_total: number;
  memory_swap_free: number;
  memory_swap_used: number;
  memory_swap_percent: number;
  memory_percent: number;
  disk_usage: number;
  disk_total: number;
  disk_available: number;
  disk_free: number;
  disk_used: number;
  disk_percent: number;
  network_usage?: number;
  network_total: number;
  network_available: number;
  network_free: number;
  network_used: number;
  network_percent: number;
  network?: any;
  process_count: number;
  timestamp: string;
  additional_metrics?: Record<string, any>;
  additional?: AdditionalMetrics;
}
  
// Type for metric alerts
export enum AlertSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

export interface MetricAlert {
  id: string;
  metric_type: 'cpu' | 'memory' | 'disk' | 'network';
  type: 'usage' | 'temperature' | 'memory' | 'disk' | 'network' | 'bandwidth' | 'connections';
  severity: AlertSeverity;
  threshold: number;
  current_value: number;
  timestamp: string;
  message: string;
}

export type IntervalID = NodeJS.Timeout;

export interface MetricsState {
  metrics: SystemMetric[];
  loading: boolean;
  error: string | null;
  lastUpdated: string | null;
  useWebSocket: boolean;
  connectionStatus: 'disconnected' | 'connecting' | 'connected';
  lastUpdate: number | null;
}

// Type for historical data
export interface HistoricalMetrics {
  data: SystemMetric[];
  start_time: string;
  end_time: string;
  interval: number;
}

// Response types from API
export interface SystemMetricsResponse {
  data: SystemMetric;
  alerts: MetricAlert[];
}

// Request types for API
export interface MetricsQueryParams {
  start_time?: string;
  end_time?: string;
  interval?: number;
  limit?: number;
}

// Optimization types
export interface OptimizationResult {
  id: string;
  timestamp: string;
  metrics_before: SystemMetric;
  metrics_after: SystemMetric;
  actions_taken: string[];
  success: boolean;
}

export interface OptimizationProfiles {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
  usage_type: string;
  thresholds:{
    cpu_threshold: number;
    memory_threshold: number;
    disk_threshold: number;
    network_threshold: number;
    enable_auto_tuning: boolean;
    // Advanced settings
    cpu_priority?: 'high' | 'medium' | 'low';
    background_process_limit?: number;
    memory_allocation?: {
      applications: number; // percentage
      system_cache: number; // percentage
    };
    actions: {
      cpu: string[];
      memory: string[];
      disk: string[];
      network: string[];
    };
    disk_performance?: 'speed' | 'balance' | 'powersave';
    network_optimization?: {
      prioritize_streaming: boolean;
      prioritize_downloads: boolean;
      low_latency_mode: boolean;
    };
    power_profile?: 'performance' | 'balanced' | 'powersave';
  };
}

export interface MetricsApiResponse {
  data: SystemMetric;
  timestamp: string;
}

// System alert interface
export interface SystemAlert {
  id: string;
  timestamp: string;
  title: string;
  message: string;
  severity: AlertSeverity;
}

// Auto tuner interfaces
// export interface AutoTunerState {
//   uuid: string;
//   user: string;
//   status: string;
//   success: boolean;
//   loading: boolean;
//   error: string | null;
//   lastUpdated: string | null;
// }

export interface AutoTunerApiResponse {
  uuid: string;
  user: string;
  status: string;
  success: boolean;
  timestamp: string;
}

export interface AutoTunerAlert {
  id: string;
  metric_type: 'cpu' | 'memory' | 'disk' | 'network';
  severity: AlertSeverity;
  threshold: number;
  current_value: number;
  timestamp: string;
  message: string;
}

export interface AutoTunerAlertState {
  alerts: AutoTunerAlert[];
  loading: boolean;
  error: string | null;
}