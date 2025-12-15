// store/slices/vic20Slice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface VIC20State {
  isOnline: boolean;
  data: any;
  lastUpdate: string | null;
  error: string | null;
  totalAnalyses: number;
  successfulAnalyses: number;
  wisdomLevel: string;
  coordinationCapacity: string;
  patternLibrarySize: string;
  decisionsMade: number;
  messagesSent: number;
  health: string;
  uptime: number;
}

const initialState: VIC20State = {
  isOnline: false,
  data: null,
  lastUpdate: null,
  error: null,
  totalAnalyses: 0,
  successfulAnalyses: 0,
  wisdomLevel: 'sage',
  coordinationCapacity: 'unlimited',
  patternLibrarySize: 'extensive',
  decisionsMade: 0,
  messagesSent: 0,
  health: 'unknown',
  uptime: 0,
};

export const vic20Slice = createSlice({
  name: 'vic20',
  initialState,
  reducers: {
    updateMetrics: (state, action: PayloadAction<any>) => {
      const data = action.payload;
      
      if (data) {
        state.isOnline = true;
        state.data = data;
        state.lastUpdate = new Date().toISOString();
        state.error = null;
        
        // Extract backend fields - match what distributed_vic20.py sends
        state.totalAnalyses = data.total_analyses ?? 0;
        state.successfulAnalyses = data.successful_analyses ?? 0;
        state.wisdomLevel = data.wisdom_level ?? 'sage';
        state.coordinationCapacity = data.coordination_capacity ?? 'unlimited';
        state.patternLibrarySize = data.pattern_library_size ?? 'extensive';
        
        // Extract distributed state fields if present
        const distributed = data.distributed || {};
        state.decisionsMade = distributed.decisions_made ?? 0;
        state.messagesSent = distributed.messages_sent ?? 0;
        state.health = distributed.health ?? 'unknown';
        state.uptime = distributed.uptime_seconds ?? 0;
      } else {
        state.isOnline = false;
        state.error = 'No data received from VIC-20 Sage WebSocket handler';
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
    
    // Special action for coordination requests
    requestCoordination: (state) => {
      if (state.isOnline) {
        // This would trigger a WebSocket message to backend
        state.decisionsMade += 1;
      }
    },
  },
});

export const { updateMetrics, setOffline, clearError, requestCoordination } = vic20Slice.actions;

export default vic20Slice.reducer;