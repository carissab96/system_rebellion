// hooks/useDistributedAgents.ts
// Hook to access distributed agent data from Redux store
// Data flows: WebSocket → useWebSocketConnection → Redux → this hook → components
//
// NO POLLING. WebSocket pushes updates every 5 seconds.
// This hook is a thin wrapper around Redux selectors.

import { useSelector } from 'react-redux';
import { selectAllAgentDisplayData, type AgentDisplayData } from '../store/slices/agentsSlice';
import type { RootState } from '../store/store';

/**
 * Agent data structure matching backend payload
 * All fields come directly from the WebSocket system_update message
 */
export interface DistributedAgent extends AgentDisplayData {
  // Core identity (from AgentDisplayData)
  agent_name: string;
  status: 'active' | 'idle' | 'processing' | 'error';
  last_activity: string | null;
  
  // Distributed system fields (from backend payload.agents[agent_name])
  // Note: Backend sends communication.messages_sent, we normalize to total_messages_sent
  distributed?: {
    distributed_enabled: boolean;
    agent_name: string;
    health: string;
    total_decisions: number;
    total_messages_sent: number;
    total_messages_received: number;
    uptime_seconds: number;
    restart_count: number;
    personality_traits: Record<string, any>;
    last_heartbeat: string;
    resource_monitoring_enabled: boolean;
    resource_monitoring_active: boolean;
  };
  
  // Raw communication stats from backend (alternative field names)
  communication?: {
    messages_sent: number;
    messages_received: number;
    is_running: boolean;
    subscribed_channels: number;
    registered_handlers: number;
  };
  
  // Triage data (Sir Hawkington only)
  triage?: {
    disposition?: string;
    confidence?: number;
    resource_type?: string;
    current_value?: number;
    threshold?: number;
    recommended_action?: string;
  };
  
  // Memory bank data
  memory_id?: string;
  event_type?: string;
  details?: Record<string, any>;
  priority?: number;
  
  // Agent-specific personality data
  personality_traits?: Record<string, any>;
  
  // Computed stats
  total_decisions?: number;
  health?: string;
  uptime_seconds?: number;
  
  // Sir Hawkington personality fields
  monocle_state?: string;
  monocle_yeet_count?: number;
  
  // Meth Snail (Terry) personality fields
  shell_spin_count?: number;
  energy_drinks_consumed?: number;
  current_jitter_level?: string;
  
  // Hamsters personality fields
  bob_wild_ideas?: number;
  bob_hold_my_beer_count?: number;
  collective_beer_level?: string;
  beer_consumption_today?: number;
  duct_tape_inventory?: any;
  hamster_status?: {
    steve?: any;
    bob?: any;
    carl?: any;
  };
  
  // The Stick personality fields
  paper_bag_inventory?: number;
  paper_bags_consumed?: number;
  
  // QSP personality fields
  tequila_jello_shots?: number;
  paranoia_level?: string;
  threats_detected?: number;
  false_alarms?: number;
  quantum_phase_shifts?: number;
  
  // VIC-20 personality fields
  totalAnalyses?: number;
  successfulAnalyses?: number;
  decisionsMade?: number;
  messagesSent?: number;
  wisdomLevel?: string;
  coordinationCapacity?: string;
  patternLibrarySize?: string;
}

/**
 * Hook to access distributed agent data from Redux
 * 
 * Data source: WebSocket system_update → agentsSlice
 * Update frequency: Every 5 seconds (backend push)
 * 
 * @returns Agent data, loading state, and connection info
 */
export const useDistributedAgents = () => {
  // Get all agent display data from Redux
  const agentDisplayData = useSelector(selectAllAgentDisplayData);
  
  // Get connection status and last update from metrics slice
  const connectionStatus = useSelector((state: RootState) => state.metrics.connectionStatus);
  const lastUpdate = useSelector((state: RootState) => state.agents.last_update);
  const activeAgents = useSelector((state: RootState) => state.agents.active_agents);
  
  // Transform AgentDisplayData to DistributedAgent format
  // The backend payload is already spread into display_data via ...memory in agentsSlice
  // So all backend fields are available on the data object
  const agents: DistributedAgent[] = agentDisplayData.map(data => {
    // Cast to any to access dynamic backend fields that were spread in
    const backendData = data as any;
    
    // Normalize communication stats - backend sends communication.messages_sent
    // but components expect distributed.total_messages_sent
    const comm = backendData.communication || {};
    const normalizedDistributed = backendData.distributed ? {
      ...backendData.distributed,
      // Ensure message counts are available with expected names
      total_messages_sent: backendData.distributed.total_messages_sent ?? comm.messages_sent ?? 0,
      total_messages_received: backendData.distributed.total_messages_received ?? comm.messages_received ?? 0,
    } : comm.messages_sent !== undefined ? {
      // Create distributed object from communication stats if no distributed object
      distributed_enabled: true,
      agent_name: data.agent_name,
      health: backendData.health || 'unknown',
      total_decisions: backendData.total_decisions || 0,
      total_messages_sent: comm.messages_sent || 0,
      total_messages_received: comm.messages_received || 0,
      uptime_seconds: backendData.uptime_seconds || 0,
      restart_count: backendData.restart_count || 0,
      personality_traits: backendData.personality_traits || {},
      last_heartbeat: backendData.last_heartbeat || null,
      resource_monitoring_enabled: false,
      resource_monitoring_active: false,
    } : undefined;
    
    return {
      ...data,
      // Spread ALL backend data to preserve personality fields
      ...backendData,
      // Then override specific fields with normalized/computed values
      health: backendData.health || backendData.distributed?.health || data.status || 'unknown',
      total_decisions: backendData.total_decisions || backendData.distributed?.total_decisions || data.summary_stats?.total_events || 0,
      uptime_seconds: backendData.uptime_seconds || backendData.distributed?.uptime_seconds || 0,
      distributed: normalizedDistributed,
    };
  });
  
  // Derive loading state from connection and data
  const loading = connectionStatus === 'connecting' || (connectionStatus === 'connected' && agents.length === 0);
  const error = connectionStatus === 'error' ? 'WebSocket connection error' : null;
  
  return {
    agents,
    loading,
    error,
    lastUpdate: lastUpdate ? new Date(lastUpdate) : null,
    activeAgentCount: activeAgents.length,
    connectionStatus,
    // No refetch needed - WebSocket pushes updates
    refetch: () => console.log('refetch() is a no-op - data comes from WebSocket')
  };
};
