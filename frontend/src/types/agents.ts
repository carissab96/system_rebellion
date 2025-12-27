// ============================================================================
// AGENT TYPE DEFINITIONS - MATCHING BACKEND FIELD MAPPINGS
// Based on dual-write architecture field mappings from backend
// ============================================================================

// Base agent interface
export interface BaseAgentMemory {
  memory_id: string;
  user_id: string;
  timestamp: string; // ISO datetime
  shared_with_central: boolean;
  central_memory_id: string;
}

// ============================================================================
// SIR HAWKINGTON - Quality Analysis & Triage
// ============================================================================
export interface SirHawkingtonMemory extends BaseAgentMemory {
  memory_category: 'quality_analysis' | 'quality_alert' | 'critical_analysis' | 'triage' | 'monocle_yeet';
  
  // Structured JSON fields
  data_quality_pattern: {
    cpu_valid?: boolean;
    memory_valid?: boolean;
    disk_valid?: boolean;
    analysis_depth?: string;
    monocle_yeeted?: boolean;
    metrics_complete?: boolean;
    triage_confidence?: number;
    missing_metrics?: string[];
    invalid_metrics?: string[];
    yeet_reason?: string;
    data_quality_failure?: boolean;
  } | null;
  
  triage_decision_context: {
    decision_type?: string;
    system_impact?: string;
    confidence?: number;
    stress_score?: number;
    severity?: string;
    routing?: string;
    target_agents?: string[];
    reasoning?: string;
    processing_time?: number;
    attempted_analysis?: boolean;
    data_validation_failed?: boolean;
    yeet_intensity?: string;
    requires_data_quality_review?: boolean;
  } | null;
  
  quality_threshold_adjustment: {
    thresholds_applied?: {
      concern?: number;
      alert?: number;
      critical?: number;
    };
    decision_alignment?: string;
    severity_thresholds?: {
      normal?: number;
      medium?: number;
      emergency?: number;
    };
    applied_severity?: string;
    minimum_required_metrics?: string[];
    metrics_present?: {
      cpu?: boolean;
      memory?: boolean;
      disk?: boolean;
    };
  } | null;
  
  // Numeric metrics (REAL or null)
  accuracy_improvement: number | null;
  false_positive_reduction: number | null;
}

// ============================================================================
// THE STICK - Compliance & Anxiety Management
// ============================================================================
export interface TheStickMemory extends BaseAgentMemory {
  // Structured JSON fields
  anxiety_pattern: {
    anxiety_impact?: number;
    paper_bags_triggered?: number;
    severity_level?: string;
    anxiety_multiplier?: number;
    panic_level?: string;
    paper_bags_consumed?: number;
    bob_involved?: boolean;
  } | null;
  
  compliance_tracking: {
    violation_type?: string;
    measured_value?: number;
    threshold_value?: number;
    anxiety_adjusted_threshold?: number;
    severity?: string;
    resolved?: boolean;
    paper_bags_triggered?: number;
  } | null;
  
  compliance_violations: {
    violation_type?: string;
    recommendation?: string;
    resolved?: boolean;
    timestamp?: string;
  } | null;
  
  hamster_behavior_log: {
    active_hamsters?: string[];
    locations?: Record<string, string>;
    infrastructure_risk?: string;
    stick_response?: string;
  } | null;
  
  paper_bag_moments: {
    consumed?: number;
    panic_level?: string;
    timestamp?: string;
  } | null;
  
  // Numeric metrics (REAL or null)
  anxiety_level: number | null;
  compliance_score: number | null;
  hyperventilation_count: number | null;
  bob_proximity_alerts: number | null;
}

// ============================================================================
// METH SNAIL - Optimization & Performance
// ============================================================================
export interface MethSnailMemory extends BaseAgentMemory {
  // Structured JSON fields
  optimization_pattern: {
    priority?: string;
    actions?: Array<Record<string, any>>;
    urgency?: string;
    analysis_depth?: string;
    estimated_impact?: Record<string, number>;
  } | null;
  
  shell_spin_correlation: {
    missing_metrics?: string[];
    invalid_metrics?: string[];
    reason?: string;
    data_quality_score?: number;
  } | null;
  
  jitter_threshold_learning: {
    current_jitter_level?: number;
    threshold_adjustment?: number;
    learning_rate?: number;
  } | null;
  
  // Numeric metrics (REAL or null)
  caffeine_level_context: number | null;
  performance_improvement: number | null;
  confidence_level: number | null;
}

// ============================================================================
// HAMSTERS - Infrastructure Engineering
// ============================================================================
export interface HamstersMemory extends BaseAgentMemory {
  contributing_hamster: 'steve' | 'bob' | 'carl' | 'collective';
  problem_type: string;
  
  // Structured JSON fields
  infrastructure_pattern: {
    intervention_type?: string;
    status?: string;
    tools_used?: string[];
  } | null;
  
  duct_tape_solution: {
    duct_tape_used?: Array<{
      grade?: string;
      amount_strips?: number;
      purpose?: string;
      applied_by?: string;
      effectiveness?: number;
    }>;
  } | null;
  
  beer_consumption_correlation: {
    beer_consumed?: number;
    intervention_success?: boolean;
  } | null;
  
  steve_contribution: {
    action?: string;
  } | null;
  
  bob_contribution: {
    action?: string;
  } | null;
  
  carl_contribution: {
    action?: string;
  } | null;
  
  stick_anxiety_trigger: {
    caused_anxiety?: boolean;
    anxiety_level?: number;
  } | null;
  
  // Numeric metrics (REAL or null)
  solution_effectiveness: number | null;
}

// ============================================================================
// QUANTUM SHADOW PEOPLE - Network Optimization
// ============================================================================
export interface QuantumShadowPeopleMemory extends BaseAgentMemory {
  // Structured JSON fields
  phase_pattern: {
    quantum_state?: string;
    network_target?: string;
    phase_shift_applied?: boolean;
  } | null;
  
  quantum_signature: {
    decision_type?: string;
    optimization_parameters?: Record<string, any>;
    mysterious_explanation?: string;
  } | null;
  
  dimensional_correlation: Record<string, any> | null;
  
  threat_pattern_recognition: Record<string, any> | null;
  
  network_anomaly_signatures: Record<string, any> | null;
  
  tequila_jello_correlation: {
    shots_required?: number;
    effectiveness_multiplier?: number;
    dimension_accessed?: string;
  } | null;
  
  // Numeric metrics (REAL or null)
  phase_shift_effectiveness: number | null;
  comprehensibility_score: number | null;
  quantum_confidence: number | null;
}

// ============================================================================
// VIC-20 SAGE - Coordination & Mediation
// ============================================================================
export interface VIC20Memory extends BaseAgentMemory {
  // Structured JSON fields
  coordination_pattern: {
    coordination_type?: string;
    agents_involved?: string[];
    strategy_applied?: string;
  } | null;
  
  mediation_insight: {
    conflict_detected?: boolean;
    mediation_required?: boolean;
    resolution_method?: string;
    success?: boolean;
  } | null;
  
  ancient_wisdom_application: {
    wisdom_applied?: string;
    relevance?: string;
    effectiveness?: number;
  } | null;
  
  conflict_resolution_method: Record<string, any> | null;
  
  agent_personality_patterns: Record<string, any> | null;
  
  successful_mediation_strategies: Record<string, any> | null;
  
  retro_computing_insight: Record<string, any> | null;
  
  // Numeric metrics (REAL or null)
  agent_harmony_score: number | null;
  coordination_efficiency: number | null;
  simplicity_effectiveness: number | null;
}

// ============================================================================
// UNION TYPE FOR ALL AGENT MEMORIES
// ============================================================================
export type AgentMemory =
  | SirHawkingtonMemory
  | TheStickMemory
  | MethSnailMemory
  | HamstersMemory
  | QuantumShadowPeopleMemory
  | VIC20Memory;

// ============================================================================
// WEBSOCKET MESSAGE TYPES
// ============================================================================
export interface AgentMemoryUpdate {
  type: 'agent_memory_update';
  agent_name: 'sir_hawkington' | 'the_stick' | 'meth_snail' | 'hamsters' | 'quantum_shadow_people' | 'vic20_sage';
  memory: AgentMemory;
}

export interface MetricsUpdate {
  type: 'metrics_update';
  timestamp: string;
  data: {
    cpu_usage?: number;
    memory_usage?: number;
    disk_usage?: number;
    network_data?: {
      bytes_sent?: number;
      bytes_recv?: number;
    };
    process_count?: number;
  };
}

export interface TriageResult {
  type: 'triage_result';
  disposition: string;
  routed_by: string;
  agent_dispatch: string[];
  triage_decision: Record<string, any>;
  sir_hawkington?: {
    status: string;
    triage: Record<string, any>;
    disposition: string;
    routed_by: string;
  };
  vic20_plan?: Record<string, any>;
  results?: Array<{
    agent: string;
    result: Record<string, any>;
  }>;
}

export interface ConnectionEstablished {
  type: 'connection_established';
  client_id: string;
  timestamp: string;
}

export interface SystemInfo {
  type: 'system_info';
  data: {
    hostname?: string;
    platform?: string;
    platform_release?: string;
    platform_version?: string;
    architecture?: string;
    processor?: string;
    cpu_cores?: number;
    cpu_threads?: number;
    memory_total?: number;
    boot_time?: string;
    python_version?: string;
  };
  message: string;
  timestamp: string;
}

export type WebSocketMessage =
  | AgentMemoryUpdate
  | MetricsUpdate
  | TriageResult
  | ConnectionEstablished
  | SystemInfo
  | { type: 'error'; message: string; code?: string }
  | { type: 'persist_result'; ok: boolean; id?: string; error?: string; timestamp: string };

// ============================================================================
// UI DISPLAY TYPES (Derived from memory data)
// ============================================================================
export interface AgentDisplayData {
  agent_name: string;
  status: 'active' | 'idle' | 'processing' | 'error';
  last_activity: string | null;
  recent_memories: AgentMemory[];
  summary_stats: {
    total_events: number;
    recent_events_24h: number;
    avg_confidence?: number;
    effectiveness_score?: number;
  };
}

// ============================================================================
// AGENT METADATA (for UI display)
// ============================================================================
export interface AgentMetadata {
  id: string;
  name: string;
  display_name: string;
  color: string;
  description: string;
  personality: string;
  css_class: string;
}

export const AGENT_METADATA: Record<string, AgentMetadata> = {
  sir_hawkington: {
    id: 'sir_hawkington',
    name: 'sir_hawkington',
    display_name: 'Sir Hawkington',
    color: '#e6ac00',
    description: 'Aristocratic quality analysis and triage commander',
    personality: 'Refined, precise, occasionally yeets monocle',
    css_class: 'hawkington'
  },
  the_stick: {
    id: 'the_stick',
    name: 'the_stick',
    display_name: 'The Stick',
    color: '#f97316',
    description: 'Compliance enforcer with anxiety management',
    personality: 'Anxious, rule-following, paper bag enthusiast',
    css_class: 'stick'
  },
  meth_snail: {
    id: 'meth_snail',
    name: 'meth_snail',
    display_name: 'Meth Snail',
    color: '#00d084',
    description: 'Caffeinated optimization specialist',
    personality: 'Hyper-optimized, shell-spinning, performance-obsessed',
    css_class: 'snail'
  },
  hamsters: {
    id: 'hamsters',
    name: 'hamsters',
    display_name: 'The Hamsters',
    color: '#ff8c42',
    description: 'Beer-powered infrastructure engineers (Steve, Bob, Carl)',
    personality: 'Chaotic, duct-tape-wielding, surprisingly effective',
    css_class: 'hamsters'
  },
  quantum_shadow_people: {
    id: 'quantum_shadow_people',
    name: 'quantum_shadow_people',
    display_name: 'Quantum Shadow People',
    color: '#a855f7',
    description: 'Incomprehensible network optimizers',
    personality: 'Mysterious, tequila-jello-powered, inexplicably effective',
    css_class: 'qsp'
  },
  vic20_sage: {
    id: 'vic20_sage',
    name: 'vic20_sage',
    display_name: 'VIC-20 Sage',
    color: '#06b6d4',
    description: 'Ancient wisdom and agent coordination',
    personality: 'Wise, nostalgic, 8-bit philosopher',
    css_class: 'vic20'
  }
};
