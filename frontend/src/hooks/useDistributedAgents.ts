// hooks/useDistributedAgents.ts
// Hook to fetch distributed agent data from the backend
// Week 5 Task 5.3: Frontend Integration

import { useState, useEffect } from 'react';

export interface DistributedAgent {
  agent_name: string;
  agent_type: string;
  health: string;
  is_active: boolean;
  uptime_seconds: number;
  total_decisions: number;
  is_distributed: boolean;
  distributed?: {
    is_initialized: boolean;
    redis_connected: boolean;
    resource_monitoring: boolean;
    recent_decisions: number;
    messages_sent: number;
    messages_received: number;
  };
  personality?: Record<string, any>;
  week4_systems?: {
    coordination_enabled?: boolean;
    alert_escalation_enabled?: boolean;
    action_verification_enabled?: boolean;
    total_alerts?: number;
    escalated_alerts?: number;
    actions_tracked?: number;
    override_learning?: {
      total_overrides: number;
      successful_overrides: number;
      success_rate: number;
    };
    bob_detection?: {
      proximity_events: number;
      paper_bags_consumed: number;
      anxiety_spikes: number;
    };
    beer_level?: string;
    bob_wild_ideas?: number;
    paranoia_level?: string;
    threats_detected?: number;
    tequila_shots_today?: number;
    monocle_state?: string;
    monocle_yeets?: Record<string, number>;
  };
}

export interface DistributedAgentsResponse {
  total_agents: number;
  distributed_agents: number;
  agents: DistributedAgent[];
  timestamp: string;
}

export const useDistributedAgents = () => {
  const [agents, setAgents] = useState<DistributedAgent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdate, setLastUpdate] = useState<Date | null>(null);

  const fetchAgents = async () => {
    try {
      const response = await fetch('/api/distributed-agents/agents');
      
      if (!response.ok) {
        throw new Error(`Failed to fetch agents: ${response.statusText}`);
      }

      const data: DistributedAgentsResponse = await response.json();
      setAgents(data.agents);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      console.error('Error fetching distributed agents:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Initial fetch
    fetchAgents();

    // Poll every 5 seconds for updates
    const interval = setInterval(fetchAgents, 5000);

    return () => clearInterval(interval);
  }, []);

  return {
    agents,
    loading,
    error,
    lastUpdate,
    refetch: fetchAgents
  };
};
