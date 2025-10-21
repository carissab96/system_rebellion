/**
 * WebSocket Message Types
 * These match the backend message formats from all 3 endpoints
 */

// ============================================================================
// METRICS ENDPOINT MESSAGES (/api/ws/metrics)
// ============================================================================

export interface MetricsUpdateMessage {
  type: 'metrics_update';
  timestamp: string;
  data: {
    timestamp: string;
    cpu_usage: number;
    memory_usage: number;
    disk_usage: number;
    network_recv_rate?: number;
    network_sent_rate?: number;
    process_count?: number;
    cpu?: any;
    memory?: any;
    disk?: any;
    network?: any;
    system_info?: any;
    triage_decision?: any;
    triage_stats?: any;
    triage_processing?: any;
  };
  agents?: Record<string, any>; // Agent insights from triage
}

export interface AgentMemoryUpdateMessage {
  type: 'agent_memory_update';
  agent_name: string;
  memory: {
    memory_id: string;
    user_id: string;
    timestamp: string;
    shared_with_central: boolean;
    central_memory_id: string;
    [key: string]: any; // Agent-specific data
  };
}

// ============================================================================
// AGENT INSIGHTS ENDPOINT MESSAGES (/api/ws/agent-insights)
// ============================================================================

export interface AgentActivityMessage {
  type: 'agent_activity';
  agent_name: string;
  activity_type: string;
  timestamp: string;
  data: Record<string, any>;
}

// Specific activity types
export interface TriageDecisionActivity extends AgentActivityMessage {
  activity_type: 'triage_decision';
  data: {
    decision_type: string;
    confidence: number;
    severity: string;
    reasoning?: string;
    system_impact?: string;
    [key: string]: any;
  };
}

export interface OptimizationActivity extends AgentActivityMessage {
  activity_type: 'optimization_applied';
  data: {
    optimization_type: string;
    target_metric: string;
    expected_improvement: number;
    [key: string]: any;
  };
}

export interface AnalysisActivity extends AgentActivityMessage {
  activity_type: 'analysis_complete';
  data: {
    analysis_type: string;
    findings: any[];
    recommendations?: any[];
    [key: string]: any;
  };
}

// ============================================================================
// AGENT EVENTS ENDPOINT MESSAGES (/api/ws/agent-events)
// ============================================================================

export interface AgentEventMessage {
  type: 'agent_event';
  event: {
    id: number;
    timestamp: string;
    agent_name: string;
    event_type: string;
    event_data: Record<string, any>;
    severity: 'low' | 'medium' | 'high';
    agent_state: string;
  };
}

export interface RecentEventsMessage {
  type: 'recent_events';
  events: Array<{
    id: number;
    timestamp: string;
    agent_name: string;
    event_type: string;
    event_data: Record<string, any>;
    severity: 'low' | 'medium' | 'high';
    agent_state: string;
  }>;
}

// Specific event types by agent
export interface MonocleYeetEvent extends AgentEventMessage {
  event: {
    id: number;
    timestamp: string;
    agent_name: 'sir_hawkington';
    event_type: 'monocle_yeet';
    event_data: {
      yeet_intensity: string;
      missing_metrics: string[];
      reason: string;
    };
    severity: 'high' | 'medium';
    agent_state: 'yeeting';
  };
}

export interface PaperBagEvent extends AgentEventMessage {
  event: {
    id: number;
    timestamp: string;
    agent_name: 'the_stick';
    event_type: 'paper_bag_consumed';
    event_data: {
      anxiety_before: number;
      anxiety_after: number;
      paper_bags_remaining: number;
    };
    severity: 'high' | 'medium';
    agent_state: 'panicking' | 'anxious';
  };
}

export interface ShellSpinEvent extends AgentEventMessage {
  event: {
    id: number;
    timestamp: string;
    agent_name: 'meth_snail';
    event_type: 'shell_spin';
    event_data: {
      reason: string;
      missing_metrics: string[];
      caffeine_level: number;
      jitter_level: number;
    };
    severity: 'high' | 'medium';
    agent_state: 'shell_spinning';
  };
}

export interface SupplyRaidEvent extends AgentEventMessage {
  event: {
    id: number;
    timestamp: string;
    agent_name: 'hamsters';
    event_type: 'supply_closet_raid' | 'beer_consumed' | 'duct_tape_used' | 'infrastructure_intervention';
    event_data: {
      tools_required?: string[];
      beers_consumed?: number;
      duct_tape_grade?: string;
      intervention_type?: string;
    };
    severity: 'high' | 'medium' | 'low';
    agent_state: 'raiding' | 'tipsy' | 'adventurous' | 'engineering' | 'fixing';
  };
}

export interface DimensionalShiftEvent extends AgentEventMessage {
  event: {
    id: number;
    timestamp: string;
    agent_name: 'quantum_shadow_people';
    event_type: 'dimensional_shift' | 'tequila_jello_shot_consumed' | 'quantum_fix_applied';
    event_data: {
      from_phase?: string;
      to_phase?: string;
      shots_consumed?: number;
      fix_number?: number;
    };
    severity: 'high' | 'medium' | 'low';
    agent_state: 'phasing' | 'consuming' | 'fixing';
  };
}

export interface VIC20Event extends AgentEventMessage {
  event: {
    id: number;
    timestamp: string;
    agent_name: 'vic20_sage';
    event_type: 'coordination_executed' | 'wisdom_dispensed';
    event_data: {
      coordination_target?: string;
      agents_involved?: string[];
      wisdom_principle?: string;
    };
    severity: 'high' | 'medium' | 'low';
    agent_state: 'coordinating' | 'teaching';
  };
}

// ============================================================================
// COMMON MESSAGES (All Endpoints)
// ============================================================================

export interface ConnectedMessage {
  type: 'connected';
  message: string;
  timestamp: string;
  info?: string;
}

export interface HeartbeatMessage {
  type: 'heartbeat';
  timestamp: string;
  active?: number;
}

export interface PongMessage {
  type: 'pong';
  timestamp: string;
}

export interface ErrorMessage {
  type: 'error';
  message: string;
  code?: string;
  timestamp?: string;
}

// ============================================================================
// UNION TYPES
// ============================================================================

export type MetricsEndpointMessage =
  | MetricsUpdateMessage
  | AgentMemoryUpdateMessage
  | HeartbeatMessage
  | ErrorMessage;

export type AgentInsightsEndpointMessage =
  | AgentActivityMessage
  | TriageDecisionActivity
  | OptimizationActivity
  | AnalysisActivity
  | ConnectedMessage
  | HeartbeatMessage
  | PongMessage
  | ErrorMessage;

export type AgentEventsEndpointMessage =
  | AgentEventMessage
  | RecentEventsMessage
  | MonocleYeetEvent
  | PaperBagEvent
  | ShellSpinEvent
  | SupplyRaidEvent
  | DimensionalShiftEvent
  | VIC20Event
  | ConnectedMessage
  | HeartbeatMessage
  | PongMessage
  | ErrorMessage;

export type WebSocketMessage =
  | MetricsEndpointMessage
  | AgentInsightsEndpointMessage
  | AgentEventsEndpointMessage;
