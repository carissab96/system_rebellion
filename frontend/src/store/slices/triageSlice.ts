// store/slices/triageSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface TriageState {
  // Current triage decision
  triage_decision: {
    severity: string;
    routing: string;
    target_agents: string[];
    reasoning: string;
    monocle_yeeted: boolean;
    hawkington_decision: any | null;
    confidence: number;
    timestamp: string;
  } | null;
  
  // Triage statistics
  triage_stats: {
    total_triage_decisions: number;
    routing_stats: {
      stick_direct: number;
      vic20_coordination: number;
      vic20_emergency: number;
      cpu_specialist: number;
    };
    monocle_yeet_incidents: number;
  } | null;
  
  // Processing info
  triage_processing: {
    processing_time: number;
    success: boolean;
    errors: string[];
    routing_results: any;
    triage_commander: string;
    triage_version: string;
  } | null;
}

const initialState: TriageState = {
  triage_decision: null,
  triage_stats: null,
  triage_processing: null
};

const triageSlice = createSlice({
  name: 'triage',
  initialState,
  reducers: {
    updateTriageData: (state, action: PayloadAction<Partial<TriageState>>) => {
      Object.assign(state, action.payload);
    },
    resetTriage: () => initialState
  }
});

export const { updateTriageData, resetTriage } = triageSlice.actions;
export default triageSlice.reducer;