// store/selectors/metrics.ts
import type { RootState } from '../store';
import type { AgentKey } from '../store/slices/metricsSlice';

export const selectConnectionStatus = (s: RootState) => s.metrics.connectionStatus;
export const selectActiveAgentCount = (s: RootState) => s.metrics.activeAgentCount;
export const selectLastUpdate = (s: RootState) => s.metrics.lastUpdate;
export const selectSystemInfo = (s: RootState) => s.metrics.systemInfo;
export const selectError = (s: RootState) => s.metrics.error;

export const selectAgentData =
  (key: AgentKey) =>
  (s: RootState) =>
    s.metrics.agents[key];
