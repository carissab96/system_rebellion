// frontend/src/store/metricsSlice.ts
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { RootState } from "../store";

export type AgentKey = "sir_hawkington" | "meth_snail" | "hamsters" | "quantum_shadow" | "the_stick" | "vic20_sage";

type AgentsState = Partial<Record<AgentKey, unknown>>;

interface MetricsState {
  [x: string]: any;
  status: "disconnected" | "connected" | "closed" | "error";
  systemInfo: Record<string, unknown> | null;
  agents: AgentsState;
  lastUpdate: Date | null;
  lastError: string | null;
}

const initialState: MetricsState = {
  status: "disconnected",
  systemInfo: null,
  agents: {},
  lastUpdate: null,
  lastError: null,
};

const normalizeKeys = (raw: Record<string, unknown>): AgentsState => {
  const map: Record<string, AgentKey> = {
    sir_hawkington: "sir_hawkington",
    meth_snail: "meth_snail",
    hamsters: "hamsters",
    quantum_shadow: "quantum_shadow",
    the_stick: "the_stick",
    vic20_sage: "vic20_sage",
    vic20: "vic20_sage",
    quantum: "quantum_shadow",
  };
  const out: AgentsState = {};
  Object.entries(raw || {}).forEach(([k, v]) => {
    const key = map[k];
    if (key) out[key] = v;
  });
  return out;
};

const metricsSlice = createSlice({
  name: "metrics",
  initialState,
  reducers: {
    setConnectionStatus(state, action: PayloadAction<MetricsState["status"]>) {
      state.status = action.payload;
    },
    setSystemInfo(state, action: PayloadAction<Record<string, unknown>>) {
      state.systemInfo = action.payload;
    },
    setAllAgents(state, action: PayloadAction<Record<string, unknown>>) {
      state.agents = { ...state.agents, ...normalizeKeys(action.payload) };
    },
    setError(state, action: PayloadAction<string>) {
      state.lastError = action.payload;
      state.status = "error";
    },
    resetErrors(state) {
      state.lastError = null;
    },
  },
});

export const selectAgents = (s: RootState) => s.metrics.agents;
export const selectAgent = (key: "sir_hawkington" | "meth_snail" | "hamsters" | "quantum_shadow" | "the_stick" | "vic20_sage") => (s: RootState) => s.metrics.agents[key] as Record<string, unknown> | undefined;

export const selectHamsters = selectAgent("hamsters");
export const selectMethSnail = selectAgent("meth_snail");
export const selectQuantumShadow = selectAgent("quantum_shadow");
export const selectTheStick = selectAgent("the_stick");
export const selectVIC20 = selectAgent("vic20_sage");
export const selectSirHawkington = selectAgent("sir_hawkington");

export const selectConnectionStatus = (s: RootState) => s.metrics.status;
export const selectError = (s: RootState) => s.metrics.lastError;
export const selectLastUpdate = (s: RootState) => s.metrics.lastUpdate;
export const selectActiveAgentCount = (s: RootState) => Object.keys(s.metrics.agents).length;


export const { setConnectionStatus, setSystemInfo, setAllAgents, setError, resetErrors } = metricsSlice.actions;
export default metricsSlice.reducer;
