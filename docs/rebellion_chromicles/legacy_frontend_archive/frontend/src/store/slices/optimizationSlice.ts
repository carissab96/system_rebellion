// src/store/slices/optimizationSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';

// Types
export interface OptimizationProfile {
  id: string;
  name: string;
  description: string;
  usageType?: 'gaming' | 'creative' | 'development' | 'office' | 'browsing' | 'custom';
  settings: {
    cpuThreshold: number;
    memoryThreshold: number;
    diskThreshold: number;
    networkThreshold: number;
    enableAutoTuning: boolean;
    // Advanced settings
    cpuPriority?: 'high' | 'medium' | 'low';
    backgroundProcessLimit?: number;
    memoryAllocation?: {
      applications: number; // percentage
      systemCache: number; // percentage
    };
    diskPerformance?: 'speed' | 'balance' | 'powersave';
    networkOptimization?: {
      prioritizeStreaming: boolean;
      prioritizeDownloads: boolean;
      lowLatencyMode: boolean;
    };
    powerProfile?: 'performance' | 'balanced' | 'powersave';
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
      
      // Get the token from localStorage
      const token = localStorage.getItem('token');
      console.log("🐌 The Meth Snail checking auth token:", token ? 'Token exists' : 'No token');
      
      if (!token) {
        console.warn("🐌 The Meth Snail has no authentication token!");
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Clean the token to ensure it's properly formatted
      const cleanToken = token.replace(/["']/g, '').trim();
      const authHeader = cleanToken.startsWith('Bearer ') ? cleanToken : `Bearer ${cleanToken}`;
      
      // Build the URL
      const url = 'http://localhost:8000/api/optimization-profiles/';
      console.log("🐌 The Meth Snail fetching profiles from URL:", url);
      
      // Make a direct axios call with explicit headers
      try {
        const response = await axios.get(url, {
          headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        console.log("🐌 The Meth Snail returned with profiles:", response.data);
        return response.data.profiles;
      } catch (apiError: any) {
        console.error("💥 API Error details:", {
          status: apiError.response?.status,
          statusText: apiError.response?.statusText,
          data: apiError.response?.data,
          headers: apiError.response?.headers,
          url: apiError.config?.url
        });
        throw apiError;
      }
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
      
      // Get the token from localStorage
      const token = localStorage.getItem('token');
      console.log("🐌 The Meth Snail checking auth token for create:", token ? 'Token exists' : 'No token');
      
      if (!token) {
        console.warn("🐌 The Meth Snail has no authentication token for create!");
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Clean the token to ensure it's properly formatted
      const cleanToken = token.replace(/["']/g, '').trim();
      const authHeader = cleanToken.startsWith('Bearer ') ? cleanToken : `Bearer ${cleanToken}`;
      
      // Log the profile data being sent
      console.log("🐌 Profile data being sent:", profileData);
      
      // Build the URL
      const url = 'http://localhost:8000/api/optimization-profiles/';
      console.log("🐌 The Meth Snail creating profile at URL:", url);
      
      // Make a direct axios call with explicit headers
      try {
        const response = await axios.post(url, profileData, {
          headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        console.log("🐌 The Meth Snail created a new profile:", response.data);
        return response.data;
      } catch (apiError: any) {
        console.error("💥 API Error details for create:", {
          status: apiError.response?.status,
          statusText: apiError.response?.statusText,
          data: apiError.response?.data,
          headers: apiError.response?.headers,
          url: apiError.config?.url
        });
        throw apiError;
      }
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
      console.log("🐌 The Meth Snail checking auth token for update:", token ? 'Token exists' : 'No token');
      
      if (!token) {
        console.warn("🐌 The Meth Snail has no authentication token for update!");
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Clean the token to ensure it's properly formatted
      const cleanToken = token.replace(/["']/g, '').trim();
      const authHeader = cleanToken.startsWith('Bearer ') ? cleanToken : `Bearer ${cleanToken}`;
      
      // Validate if the ID is a valid UUID
      const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
      if (!uuidRegex.test(id)) {
        console.error(`🐌 The Meth Snail is confused! ID ${id} is not a valid UUID.`);
        return rejectWithValue(`Invalid profile ID format. Expected a UUID but got: ${id}`);
      }
      
      console.log("🐌 Profile data being updated:", data);
      
      // Build the URL
      const url = `http://localhost:8000/api/optimization-profiles/${id}`;
      console.log("🐌 The Meth Snail updating profile at URL:", url);
      
      // Make a direct axios call with explicit headers
      try {
        const response = await axios.put(url, data, {
          headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        console.log("🐌 The Meth Snail updated the profile:", response.data);
        return response.data;
      } catch (apiError: any) {
        console.error("💥 API Error details for update:", {
          status: apiError.response?.status,
          statusText: apiError.response?.statusText,
          data: apiError.response?.data,
          headers: apiError.response?.headers,
          url: apiError.config?.url
        });
        throw apiError;
      }
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
      console.log("🐌 The Meth Snail checking auth token for delete:", token ? 'Token exists' : 'No token');
      
      if (!token) {
        console.warn("🐌 The Meth Snail has no authentication token for delete!");
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Clean the token to ensure it's properly formatted
      const cleanToken = token.replace(/["']/g, '').trim();
      const authHeader = cleanToken.startsWith('Bearer ') ? cleanToken : `Bearer ${cleanToken}`;
      
      // Validate UUID format
      if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)) {
        return rejectWithValue(`Invalid profile ID format. Expected a UUID but got: ${id}`);
      }
      
      // Build the URL
      const url = `http://localhost:8000/api/optimization-profiles/${id}`;
      console.log("🐌 The Meth Snail deleting profile at URL:", url);
      
      // Make a direct axios call with explicit headers
      try {
        await axios.delete(url, {
          headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        console.log("🐌 The Meth Snail deleted the profile!");
        return id; // Return the ID so we can filter it out from the state
      } catch (apiError: any) {
        console.error("💥 API Error details for delete:", {
          status: apiError.response?.status,
          statusText: apiError.response?.statusText,
          data: apiError.response?.data,
          headers: apiError.response?.headers,
          url: apiError.config?.url
        });
        throw apiError;
      }
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
      console.log("🐌 The Meth Snail checking auth token for activate:", token ? 'Token exists' : 'No token');
      
      if (!token) {
        console.warn("🐌 The Meth Snail has no authentication token for activate!");
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Clean the token to ensure it's properly formatted
      const cleanToken = token.replace(/["']/g, '').trim();
      const authHeader = cleanToken.startsWith('Bearer ') ? cleanToken : `Bearer ${cleanToken}`;
      
      // Validate UUID format
      if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id)) {
        return rejectWithValue(`Invalid profile ID format. Expected a UUID but got: ${id}`);
      }
      
      // Build the URL
      const url = `http://localhost:8000/api/optimization-profiles/${id}/activate`;
      console.log("🐌 The Meth Snail activating profile at URL:", url);
      
      // Make a direct axios call with explicit headers
      try {
        const response = await axios.post(url, {}, {
          headers: {
            'Authorization': authHeader,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
          }
        });
        
        console.log("🐌 The Meth Snail activated the profile:", response.data);
        return response.data;
      } catch (apiError: any) {
        console.error("💥 API Error details for activate:", {
          status: apiError.response?.status,
          statusText: apiError.response?.statusText,
          data: apiError.response?.data,
          headers: apiError.response?.headers,
          url: apiError.config?.url
        });
        throw apiError;
      }
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