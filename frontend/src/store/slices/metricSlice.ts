// frontend/src/store/metricsSlice.ts
import { createSlice, type PayloadAction } from "@reduxjs/toolkit";

type AgentKey = "sir_hawkington" | "meth_snail" | "hamsters" | "quantum_shadow" | "the_stick" | "vic20_sage";

type AgentsState = Partial<Record<AgentKey, unknown>>;

interface MetricsState {
  status: "disconnected" | "connected" | "closed" | "error";
  systemInfo: Record<string, unknown> | null;
  agents: AgentsState;
  lastError: string | null;
}

const initialState: MetricsState = {
  status: "disconnected",
  systemInfo: null,
  agents: {},
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

export const { setConnectionStatus, setSystemInfo, setAllAgents, setError, resetErrors } = metricsSlice.actions;
export default metricsSlice.reducer;
