import { useSelector } from 'react-redux';
import { selectAgentData } from '../store/selectors/metrics';
import type { AgentKey } from '../store/slices/metricsSliceLegacy';

export function useAgentMetrics(key: AgentKey) {
  const data = useSelector(selectAgentData(key));
  return { data, isActive: !!data };
}