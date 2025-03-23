// src/types/metrics.ts
import { websocketService } from '../utils/websocketService';
// Base metric type for individual readings
export interface SystemMetric {
  id: string;
  user_id: string;
  timestamp: string;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_usage?: number;
  process_count?: number;
  additional_metrics?: Record<string, any>;
  }
  
  // Type for optimization profile thresholds
  export interface MetricThresholds {
    cpu: number;
    memory: number;
    disk: number;
    network: number;
    timestamp?: string;
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
  websocketService: typeof websocketService | null;
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

  export interface OptimizationProfile {
    id: string;
    name: string;
    description: string;
    thresholds: MetricThresholds;
    actions: string[];
  }

  export interface MetricsApiResponse {
    data: SystemMetric;
    timestamp: string;
  }

  // export interface SystemThresholds {
  //   cpu: number;
  //   memory: number;
  //   disk: number;
  //   network: number;
  // }
 
  export interface SystemAlert {
    id: string;
    timestamp: string;
    title: string;
    message: string;
    severity: AlertSeverity;
  }
 
  export interface MetricAlert {
    id: string;
    metric_type: 'cpu' | 'memory' | 'disk' | 'network';
    severity: AlertSeverity;
    threshold: number;
    current_value: number;
    timestamp: string;
    message: string;
  }
    
  export interface AutoTunerState {
    uuid: string;
    user: string;
    // profile: UserProfile;
    // preferences: UserPreferences;
    // optimization_profile: OptimizationProfile;
    // optimization_results: OptimizationResult[];
    status: string;
    success: boolean;
    loading: boolean;
    error: string | null;
    lastUpdated: string | null;
  }
  
  export interface AutoTunerApiResponse {
    uuid: string;
    user: string;
    // profile: UserProfile;
    // preferences: UserPreferences;
    // optimization_profile: OptimizationProfile;
    // optimization_results: OptimizationResult[];
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