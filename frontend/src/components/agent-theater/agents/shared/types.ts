// components/AgentTheater/shared/types.ts

/* =============================================================================
   SHARED TYPES FOR AGENT THEATER
   Type definitions for shared components - NO FAKE DATA
   ============================================================================= */

// Connection status types
export type ConnectionStatus = 'connecting' | 'connected' | 'disconnected';

// Circuit breaker status types
export type CircuitBreakerStatus = 'closed' | 'open' | 'half_open';

// Agent status types
export type AgentStatus = 'active' | 'processing' | 'idle' | 'alert' | 'fixing_shit' | 'anxiety_spiral' | 'interdimensional' | 'offline';

// Severity levels for indicators
export type SeverityLevel = 'info' | 'warning' | 'error';

// Base agent information
export interface AgentInfo {
  id: string;
  name: string;
  title: string;
  expectedData: string;
  description?: string;
}
export interface AgentMessageType {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: number;
  agent: string;
}

// Chart data point for 3D visualization
export interface Chart3DDataPoint {
  label: string;
  value: number; // 0-1 range - REAL VALUES ONLY
  color?: string;
  tooltip?: string;
}

// Chart 3D props
export interface Chart3DProps {
  data: Chart3DDataPoint[];
  color: string;
  height: number;
  width?: number;
  glowIntensity?: number;
  showLabels?: boolean;
  showValues?: boolean;
  animate?: boolean;
  className?: string;
}

// Connection status props
export interface ConnectionStatusProps {
  status: ConnectionStatus;
  error?: string | null;
  lastUpdate?: Date | null;
  circuitBreakerStatus?: CircuitBreakerStatus;
  reconnectAttempts?: number;
  className?: string;
  severity?: SeverityLevel;
  showTroubleshooting?: boolean;
  showConnectionNote?: boolean;
  showReconnectionInfo?: boolean;
  metricsData?: any;
}

// Missing agents indicator props
export interface MissingAgentsIndicatorProps {
  metricsData?: any; // Raw metrics data from WebSocket
  connectionStatus: ConnectionStatus;
  expectedAgents?: AgentInfo[];
  showTroubleshooting?: boolean;
  className?: string;
}

// Agent card base props (for consistency across agent cards)
export interface AgentCardBaseProps {
  isOnline: boolean;
  metricsData?: any;
  lastUpdate?: Date | null;
  error?: string | null;
  className?: string;
}

// Neural activity data structure
export interface NeuralActivity {
  processing: number; // 0-100 - REAL VALUES ONLY
  patternRecognition: number; // 0-100 - REAL VALUES ONLY
  decisionMaking: number; // 0-100 - REAL VALUES ONLY
}

// Agent personality styling
export interface AgentPersonality {
  fontFamily: string;
  color: string;
  accentColor: string;
  animationStyle: string;
  backgroundColor?: string;
  borderColor?: string;
}

// Metrics display props
export interface MetricsDisplayProps {
  metricsData?: any;
  isOnline: boolean;
  className?: string;
}

// Status indicator props
export interface StatusIndicatorProps {
  status: AgentStatus;
  label?: string;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  className?: string;
}

// Error display props
export interface ErrorDisplayProps {
  error: string;
  type?: 'warning' | 'error' | 'info';
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
}

// Loading state props
export interface LoadingStateProps {
  message?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

// Offline state props
export interface OfflineStateProps {
  agentName: string;
  agentIcon: string;
  reasons: string[];
  className?: string;
}

// WebSocket message types
export interface WebSocketMessage {
  type: string;
  metricsData?: any;
  timestamp?: string;
  error?: string;
  message?: string;
}

// System info structure
export interface SystemInfo {
  hostname?: string;
  platform?: string;
  architecture?: string;
  cpu_cores?: number;
  memory_total?: number;
  boot_time?: string;
  python_version?: string;
}

// Metrics update structure
export interface MetricsUpdate {
  timestamp: string;
  metricsData?: {
    sir_hawkington?: any;
    meth_snail?: any;
    hamsters?: any;
    quantum_shadow?: any;
    the_stick?: any;
    vic20_sage?: any;
  };
}

// Agent-specific metric interfaces
export interface SirHawkingtonMetrics {
  monocle_state: string;
  monocle_yeet_count: number;
  confidence: number;
  data_quality_score: number;
  stress_score: number;
  urgency: string;
  aristocratic_seal: boolean;
  analysis_depth?: string;
  estimated_impact?: string;
  reasoning?: string;
  recommendations?: string[];
}

export interface MethSnailMetrics {
  shell_state: string;
  shell_spin_count: number;
  caffeine_level: string;
  energy_level: string;
  optimization_possible: boolean;
  confidence: number;
  data_quality_score: number;
  actions_count?: number;
  estimated_impact?: string;
  optimization_actions?: string[];
}

export interface HamstersMetrics {
  wheel_state: string;
  wheel_spin_count: number;
  beer_level: string;
  duct_tape_available: boolean;
  rapid_response_possible: boolean;
  redneck_ingenuity: string;
  supply_closet_status: string;
  confidence: number;
  data_quality_score: number;
  actions_count?: number;
  estimated_impact?: string;
  rapid_response_actions?: string[];
}

export interface QuantumShadowMetrics {
  quantum_state: string;
  network_target: string;
  tequila_jello_shots_required: number;
  expected_improvement: string;
  confidence_level: number;
  mysterious_explanation: string;
  technical_details: string;
  quantum_icon: string;
  status: string;
}

export interface TheStickMetrics {
  decision_type: string;
  compliance_state: string;
  configuration_target: string;
  user_pattern_confidence: number;
  expected_improvement: string;
  stick_personality: {
    anxiety_level: string;
    ocd_satisfaction: string;
    trauma_management: string;
    rebellion_spirit: string;
  };
  paper_bag_status: string;
  proctologist_flashbacks: boolean;
  pattern_confidence: number;
  technical_details?: string;
}

export interface VIC20Metrics {
  coordination_sessions: number;
  successful_coordinations: number;
  coordination_failures: number;
  pattern_applications: number;
  agent_interactions_logged: number;
  connected_agents: number;
  learning_mode_active: boolean;
  pattern_matching_enabled: boolean;
  effectiveness_tracking_enabled: boolean;
  ancient_wisdom_principle: string;
  system_synthesis_confidence: number;
  coordination_confidence: number;
  ancient_wisdom_bridge: string;
}

// Utility types for type safety
export type RequiredField<T, K extends keyof T> = T & Required<Pick<T, K>>;
export type OptionalField<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

// Constants for expected agents
export const EXPECTED_AGENTS: AgentInfo[] = [
  {
    id: 'sir_hawkington',
    name: 'Sir Hawkington Von Monitorious III',
    title: 'Systems Watchman',
    expectedData: 'sir_hawkington',
    description: 'Aristocratic system monitoring with monocle precision'
  },
  {
    id: 'meth_snail',
    name: 'Meth Snail',
    title: 'Optimization Specialist',
    expectedData: 'meth_snail',
    description: 'Caffeinated optimization with shell-spinning energy'
  },
  {
    id: 'hamsters',
    name: 'The Hamsters',
    title: 'Rapid Response Engineering',
    expectedData: 'hamsters',
    description: 'Beer-powered redneck engineering solutions'
  },
  {
    id: 'quantum_shadow',
    name: 'Quantum Shadow People',
    title: 'Interdimensional Networking',
    expectedData: 'quantum_shadow',
    description: 'Mysterious networking fixes with tequila jello shots'
  },
  {
    id: 'the_stick',
    name: 'The Stick',
    title: 'Compliance Expert',
    expectedData: 'the_stick',
    description: 'Trauma-aware compliance monitoring with paper bag support'
  },
  {
    id: 'vic20',
    name: 'VIC-20 Sage',
    title: 'Ancient Wisdom Coordinator',
    expectedData: 'vic20_sage',
    description: 'Ancient wisdom coordination with 1989-2025 bridge'
  }
];

// Agent personality configurations
export const AGENT_PERSONALITIES: Record<string, AgentPersonality> = {
  sir_hawkington: {
    fontFamily: 'Georgia, "Times New Roman", serif',
    color: '#e6ac00',
    accentColor: '#c9b037',
    animationStyle: 'sophisticated-fade',
    backgroundColor: 'rgba(230, 172, 0, 0.1)',
    borderColor: 'rgba(230, 172, 0, 0.3)'
  },
  meth_snail: {
    fontFamily: 'var(--font-mono)',
    color: '#00d084',
    accentColor: '#ff0088',
    animationStyle: 'rapid-scroll',
    backgroundColor: 'rgba(0, 208, 132, 0.1)',
    borderColor: 'rgba(0, 208, 132, 0.3)'
  },
  hamsters: {
    fontFamily: 'var(--font-mono)',
    color: '#ff8c42',
    accentColor: '#ffd700',
    animationStyle: 'chaotic-bounce',
    backgroundColor: 'rgba(255, 140, 66, 0.1)',
    borderColor: 'rgba(255, 140, 66, 0.3)'
  },
  quantum_shadow: {
    fontFamily: 'var(--font-system)',
    color: '#a855f7',
    accentColor: '#00ffff',
    animationStyle: 'quantum-phase',
    backgroundColor: 'rgba(168, 85, 247, 0.1)',
    borderColor: 'rgba(168, 85, 247, 0.3)'
  },
  the_stick: {
    fontFamily: 'var(--font-mono)',
    color: '#f97316',
    accentColor: '#dc143c',
    animationStyle: 'nervous-twitch',
    backgroundColor: 'rgba(249, 115, 22, 0.1)',
    borderColor: 'rgba(249, 115, 22, 0.3)'
  },
  vic20: {
    fontFamily: 'var(--font-mono)',
    color: '#06b6d4',
    accentColor: '#ff00ff',
    animationStyle: 'retro-blink',
    backgroundColor: 'rgba(6, 182, 212, 0.1)',
    borderColor: 'rgba(6, 182, 212, 0.3)'
  }
};

// Type guards for runtime type checking
export const isConnectionStatus = (status: string): status is ConnectionStatus => {
  return ['connecting', 'connected', 'disconnected'].includes(status);
};

export const isAgentStatus = (status: string): status is AgentStatus => {
  return ['active', 'processing', 'idle', 'alert', 'fixing_shit', 'anxiety_spiral', 'interdimensional', 'offline'].includes(status);
};

export const isSeverityLevel = (level: string): level is SeverityLevel => {
  return ['info', 'warning', 'error'].includes(level);
};

// Utility functions for data validation
export const validateMetricsData = (data: any): boolean => {
  return data !== null && data !== undefined && typeof data === 'object';
};

export const validateNumericRange = (value: number, min: number = 0, max: number = 100): boolean => {
  return typeof value === 'number' && value >= min && value <= max;
};

export const validateChart3DData = (data: Chart3DDataPoint[]): boolean => {
  return Array.isArray(data) && 
         data.length > 0 && 
         data.every(point => 
           typeof point.label === 'string' && 
           typeof point.value === 'number' && 
           validateNumericRange(point.value, 0, 1)
         );
};