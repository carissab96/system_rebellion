// store/slices/sirHawkingtonSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface SirHawkingtonState {
  isOnline: boolean;
  data: any;
  lastUpdate: string | null;
  error: string | null;
  monocleState: string;
  monocleYeetCount: number | null;
  confidence: number | null;
  dataQualityScore: number | null;
  stressScore: number | null;
  urgency: string;
  aristocraticSeal: boolean;
}

const initialState: SirHawkingtonState = {
  isOnline: false,
  data: null,
  lastUpdate: null,
  error: null,
  monocleState: 'yeeted',
  monocleYeetCount: null  ,
  confidence: null,
  dataQualityScore: null,
  stressScore: null,
  urgency: 'unknown',
  aristocraticSeal: false,
};

export const sirHawkingtonSlice = createSlice({
  name: 'sirHawkington',
  initialState,
  reducers: {
    updateMetrics: (state, action: PayloadAction<any>) => {
      const data = action.payload;
      
      if (data) {
        state.isOnline = true;
        state.data = data;
        state.lastUpdate = new Date().toISOString();
        state.error = null;
        
        // Extract specific metrics - NO FAKE DATA
        state.monocleState = data.monocle_state || 'yeeted';
        state.monocleYeetCount = data.monocle_yeet_count || null;
        state.confidence = data.confidence || null;
        state.dataQualityScore = data.data_quality_score || null;
        state.stressScore = data.stress_score || null;
        state.urgency = data.urgency || 'unknown';
        state.aristocraticSeal = data.aristocratic_seal || false;
      } else {
        state.isOnline = false;
        state.error = 'No data received from Sir Hawkington WebSocket handler';
      }
    },
    
    setOffline: (state, action: PayloadAction<string>) => {
      state.isOnline = false;
      state.error = action.payload;
      state.data = null;
    },
    
    clearError: (state) => {
      state.error = null;
    },
  },
});

export const { updateMetrics, setOffline, clearError } = sirHawkingtonSlice.actions;

export default sirHawkingtonSlice.reducer;