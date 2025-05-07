import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { PayloadAction } from '@reduxjs/toolkit';
import { AutoTunerState } from '../../types/autoTuner';
import { OptimizationProfile } from '../../types/metrics';
import api from '../../utils/api';
import alertUtils from '../../utils/alertUtils';
import { createSystemAlert } from './systemAlertsSlice';

const initialState: AutoTunerState = {
  currentMetrics: null,
  recommendations: [],
  patterns: [],
  tuningHistory: [],
  activeProfile: null,
  status: 'idle',
  error: null,
  lastUpdated: null,
};

// Helper functions to create alerts from patterns and recommendations
// These are separate from the reducers to avoid the "may not call store.getState() while the reducer is executing" error
export const createAlertsFromPatterns = (patterns: any[], dispatch: any) => {
  if (patterns && patterns.length > 0) {
    // Only create alerts for high confidence patterns
    patterns
      .filter(pattern => pattern.confidence > 0.6)
      .forEach(pattern => {
        const alertData = alertUtils.createAlertFromPattern(pattern);
        dispatch(createSystemAlert(alertData));
      });
  }
};

export const createAlertsFromRecommendations = (recommendations: any[], dispatch: any) => {
  if (recommendations && recommendations.length > 0) {
    // Only create alerts for high impact recommendations
    recommendations
      .filter(rec => (rec.confidence * rec.impact_score) > 0.5)
      .forEach(recommendation => {
        const alertData = alertUtils.createAlertFromRecommendation(recommendation);
        dispatch(createSystemAlert(alertData));
      });
  }
};

// Async thunks for API calls
export const fetchCurrentMetrics = createAsyncThunk(
  'autoTuner/fetchCurrentMetrics',
  async () => {
    try {
      console.log('Fetching current metrics with authentication...');
      const response = await api.get(`/auto-tuner/metrics/current`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching metrics:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to fetch current metrics');
    }
  }
);

export const fetchRecommendations = createAsyncThunk(
  'autoTuner/fetchRecommendations',
  async (_, { dispatch }) => {
    try {
      console.log('Fetching recommendations with authentication...');
      const response = await api.get(`/auto-tuner/recommendations`);
      
      // Create alerts from recommendations outside of the reducer
      if (response.data && Array.isArray(response.data)) {
        createAlertsFromRecommendations(response.data, dispatch);
      }
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching recommendations:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to fetch recommendations');
    }
  }
);

export const fetchPatterns = createAsyncThunk(
  'autoTuner/fetchPatterns',
  async (_, { dispatch }) => {
    try {
      console.log('Fetching patterns with authentication...');
      const response = await api.get(`/auto-tuner/patterns`);
      console.log('Patterns API response:', response.data);
      
      // Ensure we're returning the expected format even if the API response structure changes
      if (!response.data) {
        console.error('Empty response from patterns API');
        return { detected_patterns: [] };
      }
      
      // Extract patterns from the response
      let patterns = [];
      if (response.data.detected_patterns) {
        patterns = response.data.detected_patterns;
      } else if (Array.isArray(response.data)) {
        patterns = response.data;
      }
      
      // Create alerts from patterns outside of the reducer
      createAlertsFromPatterns(patterns, dispatch);
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching patterns:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to fetch patterns');
    }
  }
);

export const fetchTuningHistory = createAsyncThunk(
  'autoTuner/fetchTuningHistory',
  async () => {
    try {
      console.log('Fetching tuning history with authentication...');
      const response = await api.get(`/auto-tuner/history`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching tuning history:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to fetch tuning history');
    }
  }
);

export const applyOptimizationProfile = createAsyncThunk(
  'autoTuner/applyOptimizationProfile',
  async (profileId: string) => {
    try {
      console.log(`Applying optimization profile ${profileId} with authentication...`);
      const response = await api.post(`/auto-tuner/profiles/${profileId}/apply`);
      return response.data;
    } catch (error: any) {
      console.error('Error applying optimization profile:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to apply optimization profile');
    }
  }
);

export const applyRecommendation = createAsyncThunk(
  'autoTuner/applyRecommendation',
  async (recommendationId: number) => {
    try {
      console.log(`Applying recommendation ${recommendationId} with authentication...`);
      // Pass the recommendation_id as a query parameter
      const response = await api.post(`/auto-tuner/recommendations/apply?recommendation_id=${recommendationId}`);
      return response.data;
    } catch (error: any) {
      console.error('Error applying recommendation:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to apply recommendation');
    }
  }
);

const autoTunerSlice = createSlice({
  name: 'autoTuner',
  initialState,
  reducers: {
    setActiveProfile(state, action: PayloadAction<OptimizationProfile | null>) {
      state.activeProfile = action.payload;
    },
    clearAutoTuner: (state) => {
      state.currentMetrics = null;
      state.recommendations = [];
      state.patterns = [];
      state.tuningHistory = [];
      state.activeProfile = null;
      state.status = 'idle';
      state.error = null;
      state.lastUpdated = null;
    },
  },
  extraReducers: (builder) => {
    // Current Metrics
    builder
      .addCase(fetchCurrentMetrics.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchCurrentMetrics.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.currentMetrics = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchCurrentMetrics.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Failed to fetch metrics';
      })
      
    // Recommendations
    builder
      .addCase(fetchRecommendations.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchRecommendations.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.recommendations = action.payload;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchRecommendations.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Failed to fetch recommendations';
      })
      
    // Patterns
    builder
      .addCase(fetchPatterns.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchPatterns.fulfilled, (state, action) => {
        state.status = 'succeeded';
        
        // Enhanced debug logging
        console.log('Patterns payload:', action.payload);
        
        // Handle the case where detected_patterns might be undefined
        if (action.payload && action.payload.detected_patterns) {
          // This is the expected format from the backend
          state.patterns = action.payload.detected_patterns;
          console.log('Setting patterns in state from detected_patterns:', action.payload.detected_patterns);
        } else if (Array.isArray(action.payload)) {
          // Handle case where API might return an array directly
          state.patterns = action.payload;
          console.log('Setting patterns array in state:', action.payload);
        } else {
          // Fallback to empty array if no patterns found
          console.warn('No patterns found in payload, setting empty array. Payload:', action.payload);
          state.patterns = [];
        }
        
        // Additional validation to ensure patterns are in the expected format
        if (state.patterns.length > 0) {
          // Verify that each pattern has the required fields
          const validPatterns = state.patterns.filter((pattern: any) => {
            return pattern && 
                   typeof pattern === 'object' && 
                   'type' in pattern && 
                   'pattern' in pattern && 
                   'confidence' in pattern && 
                   'details' in pattern;
          });
          
          if (validPatterns.length !== state.patterns.length) {
            console.warn(`Filtered out ${state.patterns.length - validPatterns.length} invalid patterns`);
            state.patterns = validPatterns;
          }
        }
        
        state.lastUpdated = new Date().toISOString();
        
        // We'll handle alerts creation after the reducer completes
        // We don't create alerts here to avoid the "may not call store.getState() while the reducer is executing" error
      })
      .addCase(fetchPatterns.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Failed to fetch patterns';
        console.error('Failed to fetch patterns:', action.error);
      })
      
    // Tuning History
    builder
      .addCase(fetchTuningHistory.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(fetchTuningHistory.fulfilled, (state, action) => {
        state.status = 'succeeded';
        state.tuningHistory = action.payload.history;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchTuningHistory.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Failed to fetch tuning history';
      })
      
    // Apply Profile
    builder
      .addCase(applyOptimizationProfile.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(applyOptimizationProfile.fulfilled, (state, action) => {
        state.status = 'succeeded';
        // Update tuning history with newly applied settings
        state.tuningHistory = [...state.tuningHistory, ...action.payload.applied_settings];
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(applyOptimizationProfile.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Failed to apply profile';
      })
      
    // Apply Recommendation
    builder
      .addCase(applyRecommendation.pending, (state) => {
        state.status = 'loading';
      })
      .addCase(applyRecommendation.fulfilled, (state, action) => {
        state.status = 'succeeded';
        if (action.payload.success && action.payload.result) {
          state.tuningHistory = [...state.tuningHistory, action.payload.result];
        }
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(applyRecommendation.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Failed to apply recommendation';
      });
  },
});

export const { setActiveProfile, clearAutoTuner } = autoTunerSlice.actions;
export default autoTunerSlice.reducer;