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
    
    return {
      ...data,
      // Ensure required fields have defaults
      health: backendData.distributed?.health || data.status || 'unknown',
      total_decisions: backendData.distributed?.total_decisions || data.summary_stats?.total_events || 0,
      uptime_seconds: backendData.distributed?.uptime_seconds || 0,
      // Pass through backend fields
      distributed: backendData.distributed,
      triage: backendData.triage,
      memory_id: backendData.memory_id,
      event_type: backendData.event_type,
      details: backendData.details,
      priority: backendData.priority,
      personality_traits: backendData.personality_traits,
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
