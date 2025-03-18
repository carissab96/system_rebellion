import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { API_BASE_URL } from '../../utils/api';

// Types
export interface SystemConfiguration {
  id: string;
  name: string;
  description: string;
  config_type: 'NETWORK' | 'SYSTEM' | 'SECURITY' | 'PERFORMANCE';
  settings: {
    [key: string]: any;
  };
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

interface ConfigurationState {
  configurations: SystemConfiguration[];
  loading: boolean;
  error: string | null;
  activeConfiguration: SystemConfiguration | null;
}

const initialState: ConfigurationState = {
  configurations: [],
  loading: false,
  error: null,
  activeConfiguration: null
};

// Async Thunks
export const fetchSystemConfigurations = createAsyncThunk(
  'configuration/fetchConfigurations',
  async (_, { rejectWithValue }) => {
    try {
      console.log("🧐 Sir Hawkington is fetching system configurations with distinguished elegance...");
      const response = await axios.get(`${API_BASE_URL}/api/configurations/`);
      console.log("🧐 Sir Hawkington returned with configurations:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 Sir Hawkington encountered a most unfortunate error!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington regrets to inform you that the configurations could not be retrieved. Most unfortunate!"
      );
    }
  }
);

export const createSystemConfiguration = createAsyncThunk(
  'configuration/createConfiguration',
  async (configData: any, { rejectWithValue }) => {
    try {
      console.log("🧐 Sir Hawkington is creating a new system configuration with distinguished precision...");
      const response = await axios.post(`${API_BASE_URL}/api/configurations/`, configData);
      console.log("🧐 Sir Hawkington created a new configuration:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 Sir Hawkington encountered a most unfortunate error while creating a configuration!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington regrets to inform you that the configuration could not be created. Most distressing!"
      );
    }
  }
);

export const updateSystemConfiguration = createAsyncThunk(
  'configuration/updateConfiguration',
  async (configData: any, { rejectWithValue }) => {
    try {
      const { id, ...data } = configData;
      console.log(`🧐 Sir Hawkington is updating system configuration ${id} with distinguished care...`);
      const response = await axios.put(`${API_BASE_URL}/api/configurations/${id}/`, data);
      console.log("🧐 Sir Hawkington updated the configuration:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 Sir Hawkington encountered a most unfortunate error while updating a configuration!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington regrets to inform you that the configuration could not be updated. Most troubling!"
      );
    }
  }
);

export const deleteSystemConfiguration = createAsyncThunk(
  'configuration/deleteConfiguration',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`🧐 Sir Hawkington is deleting system configuration ${id} with a heavy heart...`);
      await axios.delete(`${API_BASE_URL}/api/configurations/${id}/`);
      console.log("🧐 Sir Hawkington deleted the configuration successfully");
      return id;
    } catch (error: any) {
      console.error("💥 Sir Hawkington encountered a most unfortunate error while deleting a configuration!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington regrets to inform you that the configuration could not be deleted. Most vexing!"
      );
    }
  }
);

export const applySystemConfiguration = createAsyncThunk(
  'configuration/applyConfiguration',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`🧐 Sir Hawkington is applying system configuration ${id} with distinguished elegance...`);
      const response = await axios.post(`${API_BASE_URL}/api/configurations/${id}/apply/`);
      console.log("🧐 Sir Hawkington applied the configuration:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 Sir Hawkington encountered a most unfortunate error while applying a configuration!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington regrets to inform you that the configuration could not be applied. Most disappointing!"
      );
    }
  }
);

// Slice
const configurationSlice = createSlice({
  name: 'configuration',
  initialState,
  reducers: {
    setActiveConfiguration: (state, action: PayloadAction<SystemConfiguration | null>) => {
      state.activeConfiguration = action.payload;
    },
    clearConfigurationError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch configurations
      .addCase(fetchSystemConfigurations.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSystemConfigurations.fulfilled, (state, action) => {
        state.loading = false;
        state.configurations = action.payload;
        const activeConfig = action.payload.find((config: SystemConfiguration) => config.is_active);
        if (activeConfig) {
          state.activeConfiguration = activeConfig;
        }
      })
      .addCase(fetchSystemConfigurations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Create configuration
      .addCase(createSystemConfiguration.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createSystemConfiguration.fulfilled, (state, action) => {
        state.loading = false;
        state.configurations.push(action.payload);
      })
      .addCase(createSystemConfiguration.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Update configuration
      .addCase(updateSystemConfiguration.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(updateSystemConfiguration.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.configurations.findIndex(config => config.id === action.payload.id);
        if (index !== -1) {
          state.configurations[index] = action.payload;
          if (state.activeConfiguration && state.activeConfiguration.id === action.payload.id) {
            state.activeConfiguration = action.payload;
          }
        }
      })
      .addCase(updateSystemConfiguration.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Delete configuration
      .addCase(deleteSystemConfiguration.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteSystemConfiguration.fulfilled, (state, action) => {
        state.loading = false;
        state.configurations = state.configurations.filter(config => config.id !== action.payload);
        if (state.activeConfiguration && state.activeConfiguration.id === action.payload) {
          state.activeConfiguration = null;
        }
      })
      .addCase(deleteSystemConfiguration.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Apply configuration
      .addCase(applySystemConfiguration.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(applySystemConfiguration.fulfilled, (state, action) => {
        state.loading = false;
        // Update all configurations to be inactive except the applied one
        state.configurations = state.configurations.map(config => ({
          ...config,
          is_active: config.id === action.payload.id
        }));
        state.activeConfiguration = action.payload;
      })
      .addCase(applySystemConfiguration.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  }
});

export const { setActiveConfiguration, clearConfigurationError } = configurationSlice.actions;
export default configurationSlice.reducer;
