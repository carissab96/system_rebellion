// store/slices/methSnailSlice.ts
import { createSlice, type PayloadAction, createSelector } from '@reduxjs/toolkit';

// Types
export interface MethSnailData {
  current_jitter_level?: number;
  peak_jitter_level?: number;
  baseline_jitter_level?: number;
  jitter_trend?: string;
  timestamp?: string;
  caffeine_level_mg?: number;
  hypercaffeinated?: boolean;
  is_decaffeinated?: boolean;
  energy_source?: string;
  shell_spins_executed?: number;
  shell_spin_probability?: number;
  [key: string]: any; // For any additional fields
}

export interface MethSnailState {
  isOnline: boolean;
  data: MethSnailData | null;
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

// Actions
export const { updateMetrics, setOffline, clearError } = methSnailSlice.actions;

// Selectors
export const selectMethSnail = (state: { methSnail: MethSnailState }) => state.methSnail;
export const selectMethSnailData = (state: { methSnail: MethSnailState }) => state.methSnail.data;
export const selectIsOnline = (state: { methSnail: MethSnailState }) => state.methSnail.isOnline;
export const selectError = (state: { methSnail: MethSnailState }) => state.methSnail.error;

// Memoized selectors
export const selectJitterData = createSelector(
  [selectMethSnailData],
  (data) => {
    if (!data) throw new Error('No Meth Snail data available');
    if (data.current_jitter_level === undefined) throw new Error('Missing current_jitter_level');
    if (data.peak_jitter_level === undefined) throw new Error('Missing peak_jitter_level');
    if (data.baseline_jitter_level === undefined) throw new Error('Missing baseline_jitter_level');
    if (!data.jitter_trend) throw new Error('Missing jitter_trend');
    if (!data.timestamp) throw new Error('Missing timestamp');
    
    return {
      currentJitter: data.current_jitter_level,
      peakJitter: data.peak_jitter_level,
      baselineJitter: data.baseline_jitter_level,
      jitterTrend: data.jitter_trend,
      timestamp: data.timestamp
    };
  }
);

export const selectCaffeineData = createSelector(
  [selectMethSnailData],
  (data) => {
    if (!data) throw new Error('No Meth Snail data available');
    if (data.caffeine_level_mg === undefined) throw new Error('Missing caffeine_level_mg');
    if (data.hypercaffeinated === undefined) throw new Error('Missing hypercaffeinated');
    if (data.is_decaffeinated === undefined) throw new Error('Missing is_decaffeinated');
    if (!data.energy_source) throw new Error('Missing energy_source');
    if (!data.timestamp) throw new Error('Missing timestamp');
    
    return {
      caffeineMg: data.caffeine_level_mg,
      isHyper: data.hypercaffeinated,
      isDecaf: data.is_decaffeinated,
      energySource: data.energy_source,
      timestamp: data.timestamp
    };
  }
);

export const selectShellData = createSelector(
  [selectMethSnailData],
  (data) => {
    if (!data) throw new Error('No Meth Snail data available');
    if (data.shell_spins_executed === undefined) throw new Error('Missing shell_spins_executed');
    if (data.shell_spin_probability === undefined) throw new Error('Missing shell_spin_probability');
    if (!data.timestamp) throw new Error('Missing timestamp');
    
    return {
      spinCount: data.shell_spins_executed,
      spinProbability: data.shell_spin_probability,
      timestamp: data.timestamp
    };
  }
);

export default methSnailSlice.reducer;