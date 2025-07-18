// store/slices/hamstersSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface HamstersState {
  isOnline: boolean;
  data: any;
  lastUpdate: Date | null;
  error: string | null;
  wheelState: string;
  wheelSpinCount: number;
  beerLevel: string;
  ductTapeAvailable: boolean;
  rapidResponsePossible: boolean;
  redneckIngenuity: string;
  supplyClosetStatus: string;
  confidence: number;
}

const initialState: HamstersState = {
  isOnline: false,
  data: null,
  lastUpdate: null,
  error: null,
  wheelState: 'unknown',
  wheelSpinCount: 0,
  beerLevel: 'unknown',
  ductTapeAvailable: false,
  rapidResponsePossible: false,
  redneckIngenuity: 'unknown',
  supplyClosetStatus: 'unknown',
  confidence: 0,
};

export const hamstersSlice = createSlice({
  name: 'hamsters',
  initialState,
  reducers: {
    updateMetrics: (state: HamstersState, action: PayloadAction<any>) => {
      const data = action.payload;
      
      if (data) {
        state.isOnline = true;
        state.data = data;
        state.lastUpdate = new Date();
        state.error = null;
        
        // Extract specific metrics - NO FAKE DATA
        state.wheelState = data.wheel_state || 'unknown';
        state.wheelSpinCount = data.wheel_spin_count || 0;
        state.beerLevel = data.beer_level || 'unknown';
        state.ductTapeAvailable = data.duct_tape_available || false;
        state.rapidResponsePossible = data.rapid_response_possible || false;
        state.redneckIngenuity = data.redneck_ingenuity || 'unknown';
        state.supplyClosetStatus = data.supply_closet_status || 'unknown';
        state.confidence = data.confidence || 0;
      } else {
        state.isOnline = false;
        state.error = 'No data received from Hamsters WebSocket handler';
      }
    },
    
    setOffline: (state: HamstersState, action: PayloadAction<string>) => {
      state.isOnline = false;
      state.error = action.payload;
      state.data = null;
    },
    
    clearError: (state: HamstersState) => {
      state.error = null;
    },
  },
});

export const { updateMetrics, setOffline, clearError } = hamstersSlice.actions;

export default hamstersSlice.reducer;