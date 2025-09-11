// store/slices/metricsSlice.ts
import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

export const AGENT_KEYS = [
  'sir_hawkington',
  'meth_snail',
  'hamsters',
  'quantum_shadow',
  'the_stick',
  'vic20_sage',
] as const;

export type AgentKey = typeof AGENT_KEYS[number];
export type AgentData = Record<string, any> | null;

export interface MetricsState {
  agents: Record<AgentKey, AgentData>;
  connectionStatus: 'connecting' | 'connected' | 'closed' | 'error' | 'disconnected';
  lastUpdate: string | null;
  systemInfo: Record<string, any> | null;
  error: string | null;
  activeAgentCount: number;
}

const EMPTY: Record<AgentKey, AgentData> = {
  sir_hawkington: null,
  meth_snail: null,
  hamsters: null,
  quantum_shadow: null,
  the_stick: null,
  vic20_sage: null,
};

const initialState: MetricsState = {
  agents: { ...EMPTY },
  connectionStatus: 'connecting',
  lastUpdate: null,
  systemInfo: null,
  error: null,
  activeAgentCount: 0,
};

function countActive(agents: Record<AgentKey, AgentData>) {
  return (Object.values(agents) as AgentData[]).filter(Boolean).length;
}

const metricsSlice = createSlice({
  name: 'metrics',
  initialState,
  reducers: {
    setConnectionStatus(state, action: PayloadAction<MetricsState['connectionStatus']>) {
      state.connectionStatus = action.payload;
      if (action.payload !== 'error') state.error = null;
    },
    setSystemInfo(state, action: PayloadAction<Record<string, any>>) {
      state.systemInfo = action.payload || null;
    },
    setError(state, action: PayloadAction<string | null>) {
      state.error = action.payload;
      if (action.payload) state.connectionStatus = 'error';
    },
    setAllAgents(state, action: PayloadAction<Partial<Record<AgentKey, AgentData>>>) {
      state.agents = { ...state.agents, ...action.payload };
      state.activeAgentCount = countActive(state.agents);
      state.lastUpdate = new Date().toISOString();
    },
    setAgent(state, action: PayloadAction<{ key: AgentKey; data: AgentData }>) {
      const { key, data } = action.payload;
      state.agents[key] = data;
      state.activeAgentCount = countActive(state.agents);
      state.lastUpdate = new Date().toISOString();
    },
    markOffline(state, action: PayloadAction<AgentKey>) {
      state.agents[action.payload] = null;
      state.activeAgentCount = countActive(state.agents);
      state.lastUpdate = new Date().toISOString();
    },
    resetMetrics(state) {
      state.agents = { ...EMPTY };
      state.activeAgentCount = 0;
      state.lastUpdate = null;
      state.error = null;
      state.connectionStatus = 'disconnected';
    },
  },
});

export const {
  setConnectionStatus,
  setSystemInfo,
  setError,
  setAllAgents,
  setAgent,
  markOffline,
  resetMetrics,
} = metricsSlice.actions;

export default metricsSlice.reducer;
