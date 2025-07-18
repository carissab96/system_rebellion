// store/slices/theStickSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface TheStickState {
  isOnline: boolean;
  data: any;
  lastUpdate: Date | null;
  error: string | null;
  decisionType: string;
  complianceState: string;
  configurationTarget: string;
  userPatternConfidence: number;
  expectedImprovement: string;
  anxietyLevel: string;
  ocdSatisfaction: string;
  traumaManagement: string;
  rebellionSpirit: string;
  paperBagStatus: string;
  proctologistFlashbacks: boolean;
  confidence: number;
}

const initialState: TheStickState = {
  isOnline: false,
  data: null,
  lastUpdate: null,
  error: null,
  decisionType: 'unknown',
  complianceState: 'unknown',
  configurationTarget: 'none',
  userPatternConfidence: 0,
  expectedImprovement: 'unknown',
  anxietyLevel: 'unknown',
  ocdSatisfaction: 'unknown',
  traumaManagement: 'unknown',
  rebellionSpirit: 'unknown',
  paperBagStatus: 'unknown',
  proctologistFlashbacks: false,
  confidence: 0,
};

export const theStickSlice = createSlice({
  name: 'theStick',
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
        state.decisionType = data.decision_type || 'unknown';
        state.complianceState = data.compliance_state || 'unknown';
        state.configurationTarget = data.configuration_target || 'none';
        state.userPatternConfidence = data.user_pattern_confidence || 0;
        state.expectedImprovement = data.expected_improvement || 'unknown';
        state.paperBagStatus = data.paper_bag_status || 'unknown';
        state.proctologistFlashbacks = data.proctologist_flashbacks || false;
        state.confidence = data.pattern_confidence || 0;
        
        // Stick personality metrics
        if (data.stick_personality) {
          state.anxietyLevel = data.stick_personality.anxiety_level || 'unknown';
          state.ocdSatisfaction = data.stick_personality.ocd_satisfaction || 'unknown';
          state.traumaManagement = data.stick_personality.trauma_management || 'unknown';
          state.rebellionSpirit = data.stick_personality.rebellion_spirit || 'unknown';
        }
      } else {
        state.isOnline = false;
        state.error = 'No data received from The Stick WebSocket handler';
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
    
    // Special action for paper bag requests
    requestPaperBag: (state) => {
      if (state.isOnline) {
        state.paperBagStatus = 'REQUESTED';
        // This would trigger a WebSocket message to backend
      }
    },
    
    // Special action for trauma triggers
    triggerTraumaResponse: (state) => {
      if (state.isOnline) {
        state.anxietyLevel = 'HYPERVENTILATING';
        state.paperBagStatus = 'EMERGENCY_USE';
        // Log the trigger for learning
      }
    },
  },
});

export const { updateMetrics, setOffline, clearError, requestPaperBag, triggerTraumaResponse } = theStickSlice.actions;

export default theStickSlice.reducer;
