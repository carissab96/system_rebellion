// src/types/metrics.ts
import { websocketService } from '../utils/websocketService';
// Base metric type for individual readings
export interface NetworkDetails {
  // Legacy properties for backward compatibility
  bytes_sent: number;
  bytes_recv: number;
  packets_sent: number;
  packets_recv: number;
  rate_mbps: number;
  sent_rate_bps?: number;
  recv_rate_bps?: number;
  raw_bytes_total?: number;
  
  // Enhanced network metrics
  io_stats?: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
    sent_rate: number;
    recv_rate: number;
    errors_in: number;
    errors_out: number;
    drops_in: number;
    drops_out: number;
  };
  
  connection_quality?: {
    average_latency: number;
    packet_loss_percent: number;
    connection_stability: number;
    jitter: number;
    gateway_latency: number;
    dns_latency: number;
    internet_latency: number;
  };
  
  protocol_stats?: {
    tcp: {
      active: number;
      listening?: number;
      established: number;
      time_wait?: number;
      close_wait?: number;
      fin_wait1?: number;
      fin_wait2?: number;
      last_ack?: number;
      syn_sent?: number;
      syn_recv?: number;
      closing?: number;
    };
    udp: {
      active: number;
      datagrams_sent?: number;
      datagrams_received?: number;
    };
    http: {
      connections: number;
      get_requests?: number;
      post_requests?: number;
    };
    https: {
      connections: number;
      tls_handshakes?: number;
    };
    dns: {
      queries: number;
      responses?: number;
      timeouts?: number;
    };
  };
  
  protocol_breakdown?: {
    web: number;
    email: number;
    streaming: number;
    gaming: number;
    file_transfer: number;
    other: number;
  };
  
  top_bandwidth_processes?: Array<{
    name: string;
    pid: number;
    read_rate?: number;
    write_rate?: number;
    total_rate?: number;
    connection_count?: number;
  }>;
  
  interfaces?: Array<{
    name: string;
    address?: string;
    mac_address?: string;
    isup: boolean;
    speed?: number;
    mtu?: number;
    bytes_sent?: number;
    bytes_recv?: number;
  }>;
  
  dns_metrics?: {
    query_time_ms: number;
    success_rate: number;
    cache_hit_ratio: number;
  };
  
  internet_metrics?: {
    connected: boolean;
    download_speed: number;
    upload_speed: number;
    isp_latency: number;
  };
}

export interface AdditionalMetrics {
  swap_usage?: number;
  cpu_temperature?: number;
  active_python_processes?: number;
  load_average?: number[];
  network_details?: NetworkDetails;
  [key: string]: any;
}

export interface SystemMetric {
  id: string;
  user_id: string;
  cpu_usage: number;
  memory_usage: number;
  disk_usage: number;
  network_usage: number; // Keep for backward compatibility
  network?: any; // Add this to store detailed network data
  process_count: number;
  timestamp: string;
  additional_metrics?: Record<string, any>;
  network?: any; // Added to support direct network data access
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