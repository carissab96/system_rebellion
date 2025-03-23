import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { PayloadAction } from '@reduxjs/toolkit';
import { AutoTunerState } from '../../types/autoTuner';
import { OptimizationProfile } from '../../types/metrics';

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
    const response = await fetch('/api/auto-tuner/metrics/current');
    if (!response.ok) {
      throw new Error('Failed to fetch current metrics');
    }
    return response.json();
  }
);

export const fetchRecommendations = createAsyncThunk(
  'autoTuner/fetchRecommendations',
  async () => {
    const response = await fetch('/api/auto-tuner/recommendations');
    if (!response.ok) {
      throw new Error('Failed to fetch recommendations');
    }
    return response.json();
  }
);

export const fetchPatterns = createAsyncThunk(
  'autoTuner/fetchPatterns',
  async () => {
    const response = await fetch('/api/auto-tuner/patterns');
    if (!response.ok) {
      throw new Error('Failed to fetch patterns');
    }
    return response.json();
  }
);

export const fetchTuningHistory = createAsyncThunk(
  'autoTuner/fetchTuningHistory',
  async () => {
    const response = await fetch('/api/auto-tuner/history');
    if (!response.ok) {
      throw new Error('Failed to fetch tuning history');
    }
    return response.json();
  }
);

export const applyOptimizationProfile = createAsyncThunk(
  'autoTuner/applyOptimizationProfile',
  async (profileId: string) => {
    const response = await fetch(`/api/auto-tuner/profiles/${profileId}/apply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    if (!response.ok) {
      throw new Error('Failed to apply optimization profile');
    }
    return response.json();
  }
);

export const applyRecommendation = createAsyncThunk(
  'autoTuner/applyRecommendation',
  async (recommendationId: number) => {
    const response = await fetch('/api/auto-tuner/recommendations/apply', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ recommendation_id: recommendationId }),
    });
    if (!response.ok) {
      throw new Error('Failed to apply recommendation');
    }
    return response.json();
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