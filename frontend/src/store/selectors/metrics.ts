// frontend/src/store/selectors/metrics.ts
// frontend/src/store/selectors/metrics.ts
import type { RootState } from "../store";

// The metrics slice shape per your repo history includes:
// - agents: Record<string, any>
// - connectionStatus: string
// - error: string | null
// - lastUpdate: string | null
// - activeAgentCount: number
// If yours drifted locally, adjust the keys here once and everything else keeps working.

export const selectAgents = (s: RootState) => s.metrics.agents;
export const selectConnectionStatus = (s: RootState) => s.metrics.connectionStatus;
export const selectError = (s: RootState) => s.metrics.error;
export const selectLastUpdate = (s: RootState) => s.metrics.lastUpdate;
export const selectActiveAgentCount = (s: RootState) => s.metrics.activeAgentCount;

// Agent keys per your standard
export type AgentKey =
  | "sir_hawkington"
  | "meth_snail"
  | "hamsters"
  | "quantum_shadow"
  | "the_stick"
  | "vic20_sage";

export const AGENT_KEYS: AgentKey[] = [
  "sir_hawkington",
  "meth_snail",
  "hamsters",
  "quantum_shadow",
  "the_stick",
  "vic20_sage"
];

export const selectAgentByKey = (key: AgentKey) => (s: RootState) =>
  s.metrics.agents[key];

// If you insist on named selectors per agent, export them:
export const selectSirHawkington = (s: RootState) => s.metrics.agents.sir_hawkington;
export const selectMethSnail = (s: RootState) => s.metrics.agents.meth_snail;
export const selectHamsters = (s: RootState) => s.metrics.agents.hamsters;
export const selectQuantumShadow = (s: RootState) => s.metrics.agents.quantum_shadow;
export const selectTheStick = (s: RootState) => s.metrics.agents.the_stick;
export const selectVic20Sage = (s: RootState) => s.metrics.agents.vic20_sage;
