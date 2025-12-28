// hooks/useDistributedAgents.ts
// 
// Hook to access distributed agent data from Redux store
// Data flows: WebSocket → useWebSocketConnection → Redux → this hook → components
//
// SIMPLIFIED VERSION - December 28, 2024
// The backend payload is already spread into display_data by agentsSlice.
// This hook is a thin passthrough. No transformation, no normalization.
// Backend is source of truth. Components handle field access.

import { useSelector } from 'react-redux';
import { selectAllAgentDisplayData, type AgentDisplayData } from '../store/slices/agentsSlice';
import type { RootState } from '../store/store';

/**
 * Agent data from the backend WebSocket payload.
 * 
 * Core fields are typed. Agent-specific personality fields (monocle_yeet_count,
 * shell_spin_count, etc.) are accessed dynamically by components since they
 * vary by agent type. Components use `agent as any` pattern for these.
 * 
 * This extends AgentDisplayData which contains the full backend payload
 * spread into it by agentsSlice.addAgentMemory.
 */
export interface DistributedAgent extends AgentDisplayData {
  // Distributed system fields (present on all agents)
  distributed?: {
    distributed_enabled: boolean;
    agent_name: string;
    health: string;
    total_decisions: number;
    total_messages_sent: number;
    total_messages_received: number;
    uptime_seconds: number;
    restart_count: number;
    personality_traits: Record<string, unknown>;
    last_heartbeat: string;
    resource_monitoring_enabled: boolean;
    resource_monitoring_active: boolean;
  };

  // Computed/derived fields that components commonly access
  health?: string;
  total_decisions?: number;
  uptime_seconds?: number;

  // Agent-specific fields accessed via `agent as any` in components:
  // - sir_hawkington: monocle_state, monocle_yeet_count, thresholds, triage
  // - meth_snail: shell_spin_count, energy_drinks_consumed, current_jitter_level
  // - hamsters: hamster_status, collective_beer_level, duct_tape_inventory, bob_wild_ideas
  // - the_stick: paper_bag_inventory, paper_bags_consumed
  // - quantum_shadow_people: tequila_jello_shots, paranoia_level, quantum_phase_shifts
  // - vic_20_sage: wisdom_level, coordination_capacity, pattern_library_size
}

/**
 * Hook to access distributed agent data from Redux.
 * 
 * Data source: WebSocket system_update → agentsSlice
 * Update frequency: Every ~10 seconds (backend push)
 * 
 * @returns Agent data, loading state, and connection info
 */
export const useDistributedAgents = () => {
  // Agent data - already contains full backend payload via agentsSlice
  const agents = useSelector(selectAllAgentDisplayData) as DistributedAgent[];

  // Connection state from metrics slice
  const connectionStatus = useSelector((state: RootState) => state.metrics.connectionStatus);
  
  // Agent state metadata
  const lastUpdate = useSelector((state: RootState) => state.agents.last_update);
  const activeAgents = useSelector((state: RootState) => state.agents.active_agents);

  // Derive loading/error states
  const loading = connectionStatus === 'connecting' || 
                  (connectionStatus === 'connected' && agents.length === 0);
  const error = connectionStatus === 'error' ? 'WebSocket connection error' : null;

  return {
    agents,
    loading,
    error,
    lastUpdate: lastUpdate ? new Date(lastUpdate) : null,
    activeAgentCount: activeAgents.length,
    connectionStatus,
  };
};