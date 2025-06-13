/**
 * Main Metrics Type Definitions
 * System Rebellion Central Command Type System
 * 
 * "By Jove, these types shall bring order to chaos!" - Sir Hawkington
 */

import { RawCPUMetrics, CPUHistoricalData } from './CPU/Tabs/types';
import { RawMemoryMetrics, RawMemoryHistoricalData } from './memory/tabs/types';
import { RawDiskMetrics, RawDiskHistoricalData } from './disk/tabs/types';
import { RawNetworkMetrics, RawNetworkHistoricalData } from './Network/tabs/types';

// Re-export all individual metric types
export * from './CPU/Tabs/types';
export * from './memory/tabs/types';
export * from './disk/tabs/types';
export * from './Network/tabs/types';

/**
 * WebSocket Message Types
 */
export interface WebSocketMessage {
  type: string;
  timestamp: string;
  [key: string]: any;
}

export interface MetricsUpdate extends WebSocketMessage {
  type: 'metrics_update';
  data: SystemMetrics;
}

export interface AuthMessage extends WebSocketMessage {
  type: 'auth';
  token: string;
}

export interface AuthSuccessMessage extends WebSocketMessage {
  type: 'auth_success';
  message: string;
  user: string;
  system_info: SystemInfo;
}

export interface ErrorMessage extends WebSocketMessage {
  type: 'error' | 'auth_failed' | 'connection_error' | 'rate_limit';
  message: string;
  code?: string;
  retry_after?: number;
}

/**
 * Main System Metrics Interface
 */
export interface SystemMetrics {
  cpu?: RawCPUMetrics;
  memory?: RawMemoryMetrics;
  disk?: RawDiskMetrics;
  network?: RawNetworkMetrics;
  system_analysis?: SystemAnalysis;
}

/**
 * System Analysis from the Transformer
 */
export interface SystemAnalysis {
  overall_health: 'good' | 'warning' | 'critical' | 'unknown';
  issues: string[];
  recommendations: string[];
  timestamp?: string;
}

/**
 * System Information
 */
export interface SystemInfo {
  platform: string;              // Operating system
  platform_release: string;      // OS release
  platform_version: string;      // OS version
  architecture: string;          // System architecture
  processor: string;             // Processor info
  cpu_count: number;             // Logical CPU count
  cpu_count_physical: number;    // Physical CPU count
  total_memory_gb: number;       // Total memory in GB
  python_version: string;        // Python version (backend)
}

/**
 * Historical Data Collection
 */
export interface MetricsHistory {
  cpu: RawCPUHistoricalData[];
  memory: RawMemoryHistoricalData[];
  disk: RawDiskHistoricalData[];
  network: RawNetworkHistoricalData[];
  timeRange: {
    start: string;              // ISO 8601
    end: string;                // ISO 8601
    intervalSeconds: number;     // Data point interval
  };
}

/**
 * Metrics Collection Status
 */
export interface MetricsStatus {
  connected: boolean;            // WebSocket connection status
  authenticated: boolean;        // Authentication status
  lastUpdate: string | null;     // Last successful update timestamp
  updateInterval: number;        // Current update interval in seconds
  errors: MetricsError[];        // Recent errors
  connectionQuality: 'excellent' | 'good' | 'fair' | 'poor';
}

export interface MetricsError {
  timestamp: string;
  type: 'connection' | 'auth' | 'data' | 'timeout';
  message: string;
  recoverable: boolean;
}

/**
 * Redux Store State Types
 */
export interface MetricsState {
  current: SystemMetrics;
  history: MetricsHistory;
  status: MetricsStatus;
  config: MetricsConfig;
}

export interface MetricsConfig {
  updateInterval: number;        // Seconds between updates
  historyRetention: number;      // Minutes to retain history
  enableSmoothing: boolean;      // Enable data smoothing
  enableAnomalyDetection: boolean;
  alertThresholds: AlertThresholds;
}

export interface AlertThresholds {
  cpu: {
    warning: number;            // CPU % for warning
    critical: number;           // CPU % for critical
  };
  memory: {
    warning: number;            // Memory % for warning
    critical: number;           // Memory % for critical
  };
  disk: {
    warning: number;            // Disk % for warning
    critical: number;           // Disk % for critical
  };
  network: {
    maxBandwidthMbps: number;   // Expected max bandwidth
  };
}

/**
 * Component Props Types
 */
export interface MetricComponentProps {
  compact?: boolean;             // Compact view mode
  showHistory?: boolean;         // Show historical chart
  refreshInterval?: number;      // Override refresh interval
  onAlert?: (alert: MetricAlert) => void;
}

export interface MetricAlert {
  type: 'cpu' | 'memory' | 'disk' | 'network';
  severity: 'warning' | 'critical';
  message: string;
  value: number;
  threshold: number;
  timestamp: string;
}

/**
 * Utility Types
 */
export type MetricType = 'cpu' | 'memory' | 'disk' | 'network';

export type MetricValue = number | null;

export interface MetricDataPoint {
  timestamp: string;
  value: MetricValue;
  label?: string;
}

export interface ChartData {
  datasets: {
    label: string;
    data: MetricDataPoint[];
    borderColor?: string;
    backgroundColor?: string;
  }[];
  labels?: string[];
}

/**
 * The Distinguished Team of Misfits Status
 * (Because they deserve recognition in the type system)
 */
export interface TeamMemberStatus {
  sirHawkington: {
    monocleStatus: 'gleaming' | 'adjusting' | 'fallen_off';
    aristocraticLevel: number;  // 0-100
  };
  methSnail: {
    speed: number;              // Current speed in arbitrary units
    redBullCount: number;       // Red Bulls consumed
    caffeineLevel: 'optimal' | 'excessive' | 'dangerous';
  };
  hamsters: {
    squeakCount: number;        // Communication attempts
    ductTapeUsed: number;       // Meters of duct tape
    formationStatus: 'circle' | 'line' | 'scattered';
  };
  theStick: {
    anxietyLevel: number;       // 0-100
    measurementsPending: number;
    complianceStatus: 'compliant' | 'concerned' | 'panicking';
  };
  quantumShadowPeople: {
    visibility: number;         // 0-1
    routerRecommendations: number;
    interdimensionalStatus: 'stable' | 'fluctuating' | 'phasing';
  };
  vic20: {
    wisdomLevel: number;        // In kilobytes
    threatLevel: 'peaceful' | 'contemplating_war' | 'shall_we_play_a_game';
  };
}