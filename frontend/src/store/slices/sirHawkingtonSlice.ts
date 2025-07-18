// store/slices/sirHawkingtonSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface SirHawkingtonState {
  isOnline: boolean;
  data: any;
  lastUpdate: Date | null;
  error: string | null;
  monocleState: string;
  monocleYeetCount: number;
  confidence: number;
  dataQualityScore: number;
  stressScore: number;
  urgency: string;
  aristocraticSeal: boolean;
}

const initialState: SirHawkingtonState = {
  isOnline: false,
  data: null,
  lastUpdate: null,
  error: null,
  monocleState: 'unknown',
  monocleYeetCount: 0,
  confidence: 0,
  dataQualityScore: 0,
  stressScore: 0,
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
        state.lastUpdate = new Date();
        state.error = null;
        
        // Extract specific metrics - NO FAKE DATA
        state.monocleState = data.monocle_state || 'unknown';
        state.monocleYeetCount = data.monocle_yeet_count || 0;
        state.confidence = data.confidence || 0;
        state.dataQualityScore = data.data_quality_score || 0;
        state.stressScore = data.stress_score || 0;
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