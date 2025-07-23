// store/slices/quantumShadowSlice.ts
import { createSlice } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

interface QuantumShadowState {
  isOnline: boolean;
  data: any;
  lastUpdate: string | null;
  error: string | null;
  quantumState: string;
  networkTarget: string;
  tequilaJelloShotsRequired: number;
  expectedImprovement: string;
  confidenceLevel: number;
  mysteriousExplanation: string;
  technicalDetails: string;
  status: string;
}

const initialState: QuantumShadowState = {
  isOnline: false,
  data: null,
  lastUpdate: null,
  error: null,
  quantumState: 'unknown',
  networkTarget: 'none',
  tequilaJelloShotsRequired: 0,
  expectedImprovement: 'unknown',
  confidenceLevel: 0,
  mysteriousExplanation: 'no interdimensional communication',
  technicalDetails: 'none available',
  status: 'unknown',
};

export const quantumShadowSlice = createSlice({
  name: 'quantumShadow',
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
        state.quantumState = data.quantum_state || 'unknown';
        state.networkTarget = data.network_target || 'none';
        state.tequilaJelloShotsRequired = data.tequila_jello_shots_required || 0;
        state.expectedImprovement = data.expected_improvement || 'unknown';
        state.confidenceLevel = data.confidence_level || 0;
        state.mysteriousExplanation = data.mysterious_explanation || 'no interdimensional communication';
        state.technicalDetails = data.technical_details || 'none available';
        state.status = data.status || 'unknown';
      } else {
        state.isOnline = false;
        state.error = 'No data received from Quantum Shadow People WebSocket handler';
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
    
    // Special action for quantum phase shifts
    triggerQuantumPhaseShift: (state) => {
      if (state.isOnline) {
        state.quantumState = 'phasing';
      }
      // This would trigger a WebSocket message to backend
    },
  },
});

export const { updateMetrics, setOffline, clearError, triggerQuantumPhaseShift } = quantumShadowSlice.actions;

export default quantumShadowSlice.reducer;