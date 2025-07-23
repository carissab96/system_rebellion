// store/slices/vic20Slice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface VIC20State {
  isOnline: boolean;
  data: any;
  lastUpdate: string | null;
  error: string | null;
  coordinationSessions: number;
  successfulCoordinations: number;
  coordinationFailures: number;
  patternApplications: number;
  agentInteractionsLogged: number;
  connectedAgents: number;
  learningModeActive: boolean;
  patternMatchingEnabled: boolean;
  effectivenessTrackingEnabled: boolean;
  ancientWisdomPrinciple: string;
  systemSynthesisConfidence: number;
  coordinationConfidence: number;
  ancientWisdomBridge: string;
}

const initialState: VIC20State = {
  isOnline: false,
  data: null,
  lastUpdate: null,
  error: null,
  coordinationSessions: 0,
  successfulCoordinations: 0,
  coordinationFailures: 0,
  patternApplications: 0,
  agentInteractionsLogged: 0,
  connectedAgents: 0,
  learningModeActive: false,
  patternMatchingEnabled: false,
  effectivenessTrackingEnabled: false,
  ancientWisdomPrinciple: 'none available',
  systemSynthesisConfidence: 0,
  coordinationConfidence: 0,
  ancientWisdomBridge: 'unknown',
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
        
        // Extract specific metrics - NO FAKE DATA
        state.coordinationSessions = data.coordination_sessions || 0;
        state.successfulCoordinations = data.successful_coordinations || 0;
        state.coordinationFailures = data.coordination_failures || 0;
        state.patternApplications = data.pattern_applications || 0;
        state.agentInteractionsLogged = data.agent_interactions_logged || 0;
        state.connectedAgents = data.connected_agents || 0;
        state.learningModeActive = data.learning_mode_active || false;
        state.patternMatchingEnabled = data.pattern_matching_enabled || false;
        state.effectivenessTrackingEnabled = data.effectiveness_tracking_enabled || false;
        state.ancientWisdomPrinciple = data.ancient_wisdom_principle || 'none available';
        state.systemSynthesisConfidence = data.system_synthesis_confidence || 0;
        state.coordinationConfidence = data.coordination_confidence || 0;
        state.ancientWisdomBridge = data.ancient_wisdom_bridge || 'unknown';
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
        state.coordinationSessions += 1;
      }
    },
    
    // Special action for War Games mode
    triggerWarGamesMode: (state) => {
      if (state.isOnline) {
        // This would trigger the War Games analysis
        state.ancientWisdomPrinciple = 'The only winning move is not to play';
      }
    },
    
    // Special action for pattern learning
    triggerPatternLearning: (state) => {
      if (state.isOnline && state.learningModeActive) {
        // This would trigger pattern learning update
        state.patternApplications += 1;
      }
    },
  },
});

export const { updateMetrics, setOffline, clearError, requestCoordination, triggerWarGamesMode, triggerPatternLearning } = vic20Slice.actions;

export default vic20Slice.reducer;