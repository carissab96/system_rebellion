// components/AgentTheater/agents/HamstersCard/HamstersMetrics.tsx
import { useSelector } from 'react-redux';
import { selectHamsters } from '../../../../store/selectors/metrics';


// This is the API your HamstersCard expects.
// Keep this stable so the card doesn’t care where data comes from.
export interface HamstersCardProps {
  online: boolean;
  name: string;
  status: "ok" | "warn" | "error" | "idle";
  throughput?: number;     // whatever your backend actually sends
  latencyMs?: number;
  notes?: string;
}


const coerceStatus = (v: unknown): HamstersCardProps["status"] => {
  const s = String(v ?? "").toLowerCase();
  if (s === "ok" || s === "warn" || s === "error" || s === "idle") return s as any;
  return "idle";
};

// Hook that adapts slice -> props for this specific agent.
export function useHamstersMetrics(): HamstersCardProps {
  const hamsters = useSelector(selectHamsters);

  if (!hamsters) {
    return {
      online: false,
      name: "Hamsters",
      status: "idle",
    };
  }
  // Your backend shape may differ; map fields here, not in the card.
  const name =  hamsters.agent_name || "Hamsters";
  const online = hamsters.status === 'active'
  const status = coerceStatus(hamsters.status);
  //map the new structure to what the card expects
  const throughput = hamsters.disk_analysis?.throughput || undefined;
  const latencyMs = hamsters.disk_analysis?.latency_ms || undefined;
  const notes = hamsters.collective_wisdom?.current_insight || undefined;


  return { 
    online, 
    name, 
    status, 
    throughput, 
    latencyMs, 
    notes, 
  };
}