// src/store/slices/configurationSlice.ts
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

export interface ConfigurationFilter {
  config_type?: string;
  search?: string;
  is_active?: boolean;
}

interface ConfigurationState {
  configurations: SystemConfiguration[];
  loading: boolean;
  error: string | null;
  activeConfiguration: SystemConfiguration | null;
  filters: ConfigurationFilter;
  lastUpdated: string | null;
}

const initialState: ConfigurationState = {
  configurations: [],
  loading: false,
  error: null,
  activeConfiguration: null,
  filters: {},
  lastUpdated: null
};

// Async Thunks
export const fetchSystemConfigurations = createAsyncThunk(
  'configuration/fetchConfigurations',
  async (filters: ConfigurationFilter = {}, { rejectWithValue }) => {
    try {
      console.log("🧐 Sir Hawkington is fetching system configurations with distinguished elegance...");
      let url = `${API_BASE_URL}/system-configurations/`;
      
      // Construct query parameters
      const queryParams = new URLSearchParams();
      if (filters.config_type) {
        queryParams.append('config_type', filters.config_type);
      }
      if (filters.search) {
        queryParams.append('search', filters.search);
      }
      if (filters.is_active !== undefined) {
        queryParams.append('is_active', String(filters.is_active));
      }
      
      const queryString = queryParams.toString();
      if (queryString) {
        url += `?${queryString}`;
      }
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      const response = await axios.get(url, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log("🧐 Sir Hawkington returned with configurations:", response.data);
      return response.data.configurations;
    } catch (error: any) {
      console.error("💥 Sir Hawkington encountered a most unfortunate error!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington regrets to inform you that the configurations could not be retrieved. Most unfortunate!"
      );
    }
  }
);

export const fetchConfigurationById = createAsyncThunk(
  'configuration/fetchConfigurationById',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`🧐 Sir Hawkington is fetching configuration ${id} with utmost precision...`);
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      const response = await axios.get(`${API_BASE_URL}/system-configurations/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      console.log("🧐 Sir Hawkington found the requested configuration:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 Sir Hawkington could not find the requested configuration!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington regrets to inform you that the specific configuration could not be found. How distressing!"
      );
    }
  }
);

export const createSystemConfiguration = createAsyncThunk(
  'configuration/createConfiguration',
  async (configData: any, { rejectWithValue }) => {
    try {
      console.log("🧐 Sir Hawkington is creating a new system configuration with distinguished precision...");
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }

      // Validate the configuration data
      if (!configData.name || configData.name.trim() === '') {
        return rejectWithValue("A distinguished configuration must have a proper name!");
      }
      
      if (!configData.config_type) {
        return rejectWithValue("Please specify the type of configuration you wish to create.");
      }
      
      const response = await axios.post(`${API_BASE_URL}/system-configurations/`, configData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
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
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Validate ID
      if (!id) {
        return rejectWithValue("Configuration ID is required for updates!");
      }
      
      // Validate the configuration data
      if (data.name && data.name.trim() === '') {
        return rejectWithValue("A distinguished configuration must have a proper name!");
      }
      
      const response = await axios.put(`${API_BASE_URL}/system-configurations/${id}`, data, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
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
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Validate ID
      if (!id) {
        return rejectWithValue("Configuration ID is required for deletion!");
      }
      
      await axios.delete(`${API_BASE_URL}/system-configurations/${id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
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
      console.log(`🧐 Sir Hawkington is applying system configuration ${id} with distinguished enthusiasm...`);
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      // Validate ID
      if (!id) {
        return rejectWithValue("Configuration ID is required for application!");
      }
      
      const response = await axios.post(`${API_BASE_URL}/system-configurations/${id}/activate`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
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

export const exportConfiguration = createAsyncThunk(
  'configuration/exportConfiguration',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`🧐 Sir Hawkington is preparing to export configuration ${id} with meticulous attention to detail...`);
      
      // Get authentication token
      const token = localStorage.getItem('token');
      if (!token) {
        return rejectWithValue("Authentication required. Please log in.");
      }
      
      const response = await axios.get(`${API_BASE_URL}/system-configurations/${id}/export`, {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        responseType: 'blob'
      });
      
      // Create a download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `configuration-${id}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      
      console.log("🧐 Sir Hawkington exported the configuration successfully");
      return id;
    } catch (error: any) {
      console.error("💥 Sir Hawkington encountered difficulty exporting the configuration!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington regrets to inform you that the configuration could not be exported. Most troublesome!"
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
    },
    setConfigurationFilters: (state, action: PayloadAction<ConfigurationFilter>) => {
      state.filters = action.payload;
    },
    clearConfigurationFilters: (state) => {
      state.filters = {};
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
        state.lastUpdated = new Date().toISOString();
        const activeConfig = action.payload.find((config: SystemConfiguration) => config.is_active);
        if (activeConfig) {
          state.activeConfiguration = activeConfig;
        }
      })
      .addCase(fetchSystemConfigurations.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Fetch configuration by ID
      .addCase(fetchConfigurationById.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchConfigurationById.fulfilled, (state, action) => {
        state.loading = false;
        // Update the configuration in the list if it exists
        const index = state.configurations.findIndex(config => config.id === action.payload.id);
        if (index !== -1) {
          state.configurations[index] = action.payload;
        } else {
          state.configurations.push(action.payload);
        }
        if (action.payload.is_active) {
          state.activeConfiguration = action.payload;
        }
      })
      .addCase(fetchConfigurationById.rejected, (state, action) => {
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
        state.lastUpdated = new Date().toISOString();
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
        state.lastUpdated = new Date().toISOString();
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
        state.lastUpdated = new Date().toISOString();
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
        state.lastUpdated = new Date().toISOString();
      })
      .addCase(applySystemConfiguration.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Export configuration (no state changes needed except for loading/error states)
      .addCase(exportConfiguration.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(exportConfiguration.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(exportConfiguration.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  }
});

export const { 
  setActiveConfiguration, 
  clearConfigurationError,
  setConfigurationFilters,
  clearConfigurationFilters
} = configurationSlice.actions;

export default configurationSlice.reducer;