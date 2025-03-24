import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { PayloadAction } from '@reduxjs/toolkit';
import { AutoTunerState } from '../../types/autoTuner';
import { OptimizationProfile } from '../../types/metrics';
import axios from 'axios';
import { API_BASE_URL } from '../../utils/api';

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

// Async thunks for API calls
export const fetchCurrentMetrics = createAsyncThunk(
  'autoTuner/fetchCurrentMetrics',
  async () => {
    try {
      console.log('Fetching current metrics with authentication...');
      const response = await axios.get(`${API_BASE_URL}/auto-tuner/metrics/current`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching metrics:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to fetch current metrics');
    }
  }
);

export const fetchRecommendations = createAsyncThunk(
  'autoTuner/fetchRecommendations',
  async () => {
    try {
      console.log('Fetching recommendations with authentication...');
      const response = await axios.get(`${API_BASE_URL}/auto-tuner/recommendations`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching recommendations:', error.response?.data || error.message);
      throw new Error(error.response?.data?.detail || 'Failed to fetch recommendations');
    }
  }
);

export const fetchPatterns = createAsyncThunk(
  'autoTuner/fetchPatterns',
  async () => {
    try {
      console.log('Fetching patterns with authentication...');
      const response = await axios.get(`${API_BASE_URL}/auto-tuner/patterns`);
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
      const response = await axios.get(`${API_BASE_URL}/auto-tuner/history`);
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
      const response = await axios.post(`${API_BASE_URL}/auto-tuner/profiles/${profileId}/apply`);
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
      const response = await axios.post(`${API_BASE_URL}/auto-tuner/recommendations/apply`, {
        recommendation_id: recommendationId
      });
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
        state.patterns = action.payload.detected_patterns;
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(fetchPatterns.rejected, (state, action) => {
        state.status = 'failed';
        state.error = action.error.message || 'Failed to fetch patterns';
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