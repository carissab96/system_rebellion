// store/slices/methSnailSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface MethSnailState {
  isOnline: boolean;
  data: any;
  lastUpdate: string | null;
  error: string | null;
  shellState: string;
  shellSpinCount: number;
  caffeineLevel: string;
  energyLevel: string;
  optimizationPossible: boolean;
  confidence: number;
}

const initialState: MethSnailState = {
  isOnline: false,
  data: null,
  lastUpdate: null,
  error: null,
  shellState: 'unknown',
  shellSpinCount: 0,
  caffeineLevel: 'unknown',
  energyLevel: 'unknown',
  optimizationPossible: false,
  confidence: 0,
};

export const methSnailSlice = createSlice({
  name: 'methSnail',
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
        state.shellState = data.shell_state || 'unknown';
        state.shellSpinCount = data.shell_spin_count || 0;
        state.caffeineLevel = data.caffeine_level || 'unknown';
        state.energyLevel = data.energy_level || 'unknown';
        state.optimizationPossible = data.optimization_possible || false;
        state.confidence = data.confidence || 0;
      } else {
        state.isOnline = false;
        state.error = 'No data received from Meth Snail WebSocket handler';
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

export const { updateMetrics, setOffline, clearError } = methSnailSlice.actions;

export default methSnailSlice.reducer;