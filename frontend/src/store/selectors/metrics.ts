import type { RootState } from "../store";

// ========== AGENT SELECTORS ==========
// Pull from the AGENTS slice, not metrics!
export const selectAgents = (s: RootState) => s.agents;
export const selectActiveAgentCount = (s: RootState) => s.agents.active_agents.length;
export const selectAgentsLastUpdate = (s: RootState) => s.agents.last_update;

// Individual agent selectors
export const selectSirHawkington = (s: RootState) => s.agents.sir_hawkington;
export const selectMethSnail = (s: RootState) => s.agents.meth_snail;
export const selectHamsters = (s: RootState) => s.agents.hamsters;
export const selectQuantumShadow = (s: RootState) => s.agents.quantum_shadow_people;
export const selectTheStick = (s: RootState) => s.agents.the_stick;
export const selectVic20Sage = (s: RootState) => s.agents.vic_20_sage;

// ========== METRICS SELECTORS ==========
// System performance metrics
export const selectSystemMetrics = (s: RootState) => s.metrics;
export const selectCPUUsage = (s: RootState) => s.metrics.cpu_usage;
export const selectMemoryUsage = (s: RootState) => s.metrics.memory_usage;
export const selectDiskUsage = (s: RootState) => s.metrics.disk_usage;
export const selectNetworkMetrics = (s: RootState) => ({
  recv: s.metrics.network_recv_rate,
  sent: s.metrics.network_sent_rate
});

// Connection status from metrics slice
export const selectConnectionStatus = (s: RootState) => s.metrics.connectionStatus;
export const selectLastError = (s: RootState) => s.metrics.lastError;

// ========== TRIAGE SELECTORS ==========
export const selectTriageDecision = (s: RootState) => s.triage.triage_decision;
export const selectTriageStats = (s: RootState) => s.triage.triage_stats;
export const selectMonocleYeets = (s: RootState) => s.triage.triage_stats?.monocle_yeet_incidents || 0;

// ========== COMBINED SELECTORS ==========
// For components that need data from multiple slices
export const selectAgentWithMetrics = (agentName: AgentKey) => (s: RootState) => {
  // Use the specific agent key type to ensure we're getting an agent object
  const agent = s.agents[agentName];
  const systemMetrics = s.metrics;
  
  // Now TypeScript knows agent is one of the agent types, not a string/number
  return {
    agent,
    systemMetrics,
    isActive: agent?.display_data?.status === 'active'
  };
};

// Agent keys for iteration
export type AgentKey =
  | "sir_hawkington"
  | "meth_snail"
  | "hamsters"
  | "quantum_shadow_people"
  | "the_stick"
  | "vic_20_sage";

export const AGENT_KEYS: AgentKey[] = [
  "sir_hawkington",
  "meth_snail",
  "hamsters",
  "quantum_shadow_people",
  "the_stick",
  "vic_20_sage"
];

// Total agent count 
export const TOTAL_AGENT_COUNT = 6; // 6 agents

export const selectAgentByKey = (key: AgentKey) => (s: RootState) =>
  s.agents[key];