import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { API_BASE_URL } from '../../utils/api';

// Types
export interface OptimizationProfile {
  id: string;
  name: string;
  description: string;
  settings: {
    cpuThreshold: number;
    memoryThreshold: number;
    diskThreshold: number;
    networkThreshold: number;
    enableAutoTuning: boolean;
  };
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface OptimizationState {
  profiles: OptimizationProfile[];
  loading: boolean;
  error: string | null;
  currentProfile: OptimizationProfile | null;
}

const initialState: OptimizationState = {
  profiles: [],
  loading: false,
  error: null,
  currentProfile: null
};

// Async Thunks
export const fetchOptimizationProfiles = createAsyncThunk(
  'optimization/fetchProfiles',
  async (_, { rejectWithValue }) => {
    try {
      console.log("🐌 The Meth Snail is fetching optimization profiles...");
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      const response = await axios.get(`${API_BASE_URL}/optimization-profiles/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log("🐌 The Meth Snail returned with profiles:", response.data);
      return response.data.profiles;
    } catch (error: any) {
      console.error("💥 The Meth Snail crashed while fetching profiles!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "The Meth Snail couldn't fetch the profiles. It's probably tweaking out again."
      );
    }
  }
);

export const createOptimizationProfile = createAsyncThunk(
  'optimization/createProfile',
  async (profileData: any, { rejectWithValue }) => {
    try {
      console.log("🐌 The Meth Snail is creating a new optimization profile...");
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      const response = await axios.post(`${API_BASE_URL}/optimization-profiles/`, profileData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log("🐌 The Meth Snail created a new profile:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 The Meth Snail crashed while creating a profile!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "The Meth Snail couldn't create the profile. It's probably on a bad batch."
      );
    }
  }
);

export const updateOptimizationProfile = createAsyncThunk(
  'optimization/updateProfile',
  async (profileData: any, { rejectWithValue }) => {
    try {
      const { id, ...data } = profileData;
      console.log(`🐌 The Meth Snail is updating optimization profile ${id}...`);
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Validate if the ID is a valid UUID
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
      if (!uuidRegex.test(id)) {
        console.error(`🐌 The Meth Snail is confused! ID ${id} is not a valid UUID.`);
        return rejectWithValue(`Invalid profile ID format. Expected a UUID but got: ${id}`);
      }
      
      const response = await axios.put(`${API_BASE_URL}/optimization-profiles/${id}`, data, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log("🐌 The Meth Snail updated the profile:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 The Meth Snail crashed while updating a profile!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "The Meth Snail couldn't update the profile. It's probably having an existential crisis."
      );
    }
  }
);

export const deleteOptimizationProfile = createAsyncThunk(
  'optimization/deleteProfile',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`🐌 The Meth Snail is deleting optimization profile ${id}...`);
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Validate if the ID is a valid UUID
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
      if (!uuidRegex.test(id)) {
        console.error(`🐌 The Meth Snail is confused! ID ${id} is not a valid UUID.`);
        return rejectWithValue(`Invalid profile ID format. Expected a UUID but got: ${id}`);
      }
      
      await axios.delete(`${API_BASE_URL}/optimization-profiles/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log("🐌 The Meth Snail deleted the profile successfully");
      return id;
    } catch (error: any) {
      console.error("💥 The Meth Snail crashed while deleting a profile!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "The Meth Snail couldn't delete the profile. It's probably having withdrawal symptoms."
      );
    }
  }
);

export const activateOptimizationProfile = createAsyncThunk(
  'optimization/activateProfile',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`🐌 The Meth Snail is activating optimization profile ${id}...`);
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Validate if the ID is a valid UUID
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
      if (!uuidRegex.test(id)) {
        console.error(`🐌 The Meth Snail is confused! ID ${id} is not a valid UUID.`);
        return rejectWithValue(`Invalid profile ID format. Expected a UUID but got: ${id}`);
      }
      
      const response = await axios.post(`${API_BASE_URL}/optimization-profiles/${id}/activate`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log("🐌 The Meth Snail activated the profile:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 The Meth Snail crashed while activating a profile!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "The Meth Snail couldn't activate the profile. It's probably passed out from exhaustion."
      );
    }
  }
);

// Slice
const optimizationSlice = createSlice({
  name: 'optimization',
  initialState,
  reducers: {
    setCurrentProfile: (state, action: PayloadAction<OptimizationProfile | null>) => {
      state.currentProfile = action.payload;
    },
    clearOptimizationError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch profiles
      .addCase(fetchOptimizationProfiles.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchOptimizationProfiles.fulfilled, (state, action) => {
        state.loading = false;
        state.profiles = action.payload;
      })
      .addCase(fetchOptimizationProfiles.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Create profile
      .addCase(createOptimizationProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createOptimizationProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profiles.push(action.payload);
      })
      .addCase(createOptimizationProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Update profile
      .addCase(updateOptimizationProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateOptimizationProfile.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.profiles.findIndex(profile => profile.id === action.payload.id);
        if (index !== -1) {
          state.profiles[index] = action.payload;
        }
      })
      .addCase(updateOptimizationProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Delete profile
      .addCase(deleteOptimizationProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteOptimizationProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.profiles = state.profiles.filter(profile => profile.id !== action.payload);
      })
      .addCase(deleteOptimizationProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Activate profile
      .addCase(activateOptimizationProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(activateOptimizationProfile.fulfilled, (state, action) => {
        state.loading = false;
        // Update all profiles to be inactive except the activated one
        state.profiles = state.profiles.map(profile => ({
          ...profile,
          is_active: profile.id === action.payload.id
        }));
      })
      .addCase(activateOptimizationProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  }
});

export const { setCurrentProfile, clearOptimizationError } = optimizationSlice.actions;
export default optimizationSlice.reducer;
