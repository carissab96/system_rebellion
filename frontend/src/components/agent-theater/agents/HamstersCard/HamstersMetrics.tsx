// components/AgentTheater/agents/HamstersCard/HamstersMetrics.tsx
import React from 'react';
import { useSelector } from 'react-redux';
import { selectHamsters } from '../../../../store/selectors/metrics';

// Define the shape of the raw data from the Redux store
interface HamstersState {
  name?: string;
  status?: string;
  throughput?: number;
  qps?: number;
  latency_ms?: number;
  latency?: number;
  notes?: string;
  [key: string]: unknown; // Allow for additional unknown properties
}

// This is the API your HamstersCard expects.
// Keep this stable so the card doesn’t care where data comes from.
export interface HamstersCardProps {
  online: boolean;
  name: string;
  status: "ok" | "warn" | "error" | "idle";
  throughput?: number;     // whatever your backend actually sends
  latencyMs?: number;
  notes?: string;
  raw?: HamstersState;
  data?: any;  // For backward compatibility with existing code
  is_active?: boolean;  // For backward compatibility with existing code
}

const coerceNumber = (v: unknown): number | undefined => {
  if (typeof v === "number" && Number.isFinite(v)) return v;
  if (typeof v === "string") {
    const n = Number(v.replace(/,/g, ""));
    if (Number.isFinite(n)) return n;
  }
  return undefined;
};

const coerceStatus = (v: unknown): HamstersCardProps["status"] => {
  const s = String(v ?? "").toLowerCase();
  if (s === "ok" || s === "warn" || s === "error" || s === "idle") return s as any;
  return "idle";
};

// Hook that adapts slice -> props for this specific agent.
export function useHamstersMetrics(): HamstersCardProps {
  const raw = useSelector(selectHamsters) as HamstersState || {};
  // Your backend shape may differ; map fields here, not in the card.
  const name = (raw["name"] as string) || "Hamsters";
  const online = Boolean(raw && Object.keys(raw).length > 0);
  const status = coerceStatus(raw["status"]);
  const throughput = coerceNumber(raw["throughput"] ?? raw["qps"]);
  const latencyMs = coerceNumber(raw["latency_ms"] ?? raw["latency"]);
  const notes = (raw["notes"] as string) || undefined;

  return { 
    online, 
    name, 
    status, 
    throughput, 
    latencyMs, 
    notes, 
    raw 
  };
}