/// store/slices/sirHawkingtonSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface SirHawkingtonState {
  // Core fields from backend
  agent_name: string;
  decision_id: string | null;
  decision_type: string | null;
  confidence: number;
  monocle_state: 'polished' | 'adjusted' | 'fogged' | 'yeeted' | 'cleaning' | 'unknown';
  aristocratic_seal: boolean;
  timestamp: string | null;
  
  // UI display fields
  message: string;
  system_impact: string | null;
  urgency: 'low' | 'normal' | 'medium' | 'high' | 'critical';
  
  // Metrics
  stress_score: number;
  data_quality_score: number;
  monocle_yeet_count: number;
  
  // State management
  isLoading: boolean;
  error: string | null;
  lastUpdate: string | null;
  
  // Debug
  _raw: any | null;
}

const initialState: SirHawkingtonState = {
  agent_name: 'sir_hawkington',
  decision_id: null,
  decision_type: null,
  confidence: 0,
  monocle_state: 'unknown',
  aristocratic_seal: false,
  timestamp: null,
  message: '🧐 Awaiting aristocratic analysis...',
  system_impact: null,
  urgency: 'normal',
  stress_score: 0,
  data_quality_score: 0,
  monocle_yeet_count: 0,
  isLoading: false,
  error: null,
  lastUpdate: null,
  _raw: null
};

const sirHawkingtonSlice = createSlice({
  name: 'sirHawkington',
  initialState,
  reducers: {
    updateMetrics: (state, action: PayloadAction<Partial<SirHawkingtonState>>) => {
      Object.assign(state, action.payload);
      state.lastUpdate = new Date().toISOString();
      state.isLoading = false;
      state.error = null;
    },
    setLoading: (state, action: PayloadAction<boolean>) => {
      state.isLoading = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    resetState: () => initialState
  }
});

export const { updateMetrics, setLoading, setError, resetState } = sirHawkingtonSlice.actions;
export default sirHawkingtonSlice.reducer;