import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { API_BASE_URL } from '../../utils/api';

// Types
export interface SystemAlert {
  id: string;
  title: string;
  message: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  timestamp: string;
  is_read: boolean;
  additional_data?: any;
  created_at: string;
  updated_at: string;
}

interface SystemAlertsState {
  alerts: SystemAlert[];
  loading: boolean;
  error: string | null;
  total: number;
}

const initialState: SystemAlertsState = {
  alerts: [],
  loading: false,
  error: null,
  total: 0
};

// Async Thunks
export const fetchSystemAlerts = createAsyncThunk(
  'systemAlerts/fetchAlerts',
  async ({ skip = 0, limit = 20, is_read }: { skip?: number, limit?: number, is_read?: boolean } = {}, { rejectWithValue }) => {
    try {
      console.log("🦉 Sir Hawkington is fetching system alerts...");
      let url = `${API_BASE_URL}/api/system-alerts/?skip=${skip}&limit=${limit}`;
      if (is_read !== undefined) {
        url += `&is_read=${is_read}`;
      }
      const response = await axios.get(url);
      console.log("🦉 Sir Hawkington returned with alerts:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 Sir Hawkington crashed while fetching alerts!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington couldn't fetch the alerts. Most distressing!"
      );
    }
  }
);

export const createSystemAlert = createAsyncThunk(
  'systemAlerts/createAlert',
  async (alertData: Omit<SystemAlert, 'id' | 'timestamp' | 'created_at' | 'updated_at'>, { rejectWithValue }) => {
    try {
      console.log("🦉 Sir Hawkington is creating a new system alert...");
      const response = await axios.post(`${API_BASE_URL}/api/system-alerts/`, alertData);
      console.log("🦉 Sir Hawkington created a new alert:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 Sir Hawkington crashed while creating an alert!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington couldn't create the alert. How embarrassing!"
      );
    }
  }
);

export const markAlertAsRead = createAsyncThunk(
  'systemAlerts/markAsRead',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`🦉 Sir Hawkington is marking alert ${id} as read...`);
      const response = await axios.post(`${API_BASE_URL}/api/system-alerts/${id}/mark-as-read`);
      console.log("🦉 Sir Hawkington marked the alert as read:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 Sir Hawkington crashed while marking an alert as read!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington couldn't mark the alert as read. Most peculiar!"
      );
    }
  }
);

export const markAllAlertsAsRead = createAsyncThunk(
  'systemAlerts/markAllAsRead',
  async (_, { rejectWithValue }) => {
    try {
      console.log("🦉 Sir Hawkington is marking all alerts as read...");
      await axios.post(`${API_BASE_URL}/api/system-alerts/mark-all-as-read`);
      console.log("🦉 Sir Hawkington marked all alerts as read");
      return true;
    } catch (error: any) {
      console.error("💥 Sir Hawkington crashed while marking all alerts as read!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington couldn't mark all alerts as read. Most troubling!"
      );
    }
  }
);

export const deleteSystemAlert = createAsyncThunk(
  'systemAlerts/deleteAlert',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`🦉 Sir Hawkington is deleting alert ${id}...`);
      await axios.delete(`${API_BASE_URL}/api/system-alerts/${id}`);
      console.log("🦉 Sir Hawkington deleted the alert successfully");
      return id;
    } catch (error: any) {
      console.error("💥 Sir Hawkington crashed while deleting an alert!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington couldn't delete the alert. Most unfortunate!"
      );
    }
  }
);

// Slice
const systemAlertsSlice = createSlice({
  name: 'systemAlerts',
  initialState,
  reducers: {
    addAlert: (state, action: PayloadAction<SystemAlert>) => {
      state.alerts.unshift(action.payload);
      state.total += 1;
    },
    clearAlert: (state, action: PayloadAction<string>) => {
      state.alerts = state.alerts.filter(alert => alert.id !== action.payload);
      state.total -= 1;
    },
    clearSystemAlertsError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      // Fetch alerts
      .addCase(fetchSystemAlerts.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchSystemAlerts.fulfilled, (state, action) => {
        state.loading = false;
        state.alerts = action.payload.alerts;
        state.total = action.payload.total;
      })
      .addCase(fetchSystemAlerts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Create alert
      .addCase(createSystemAlert.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(createSystemAlert.fulfilled, (state, action) => {
        state.loading = false;
        state.alerts.unshift(action.payload);
        state.total += 1;
      })
      .addCase(createSystemAlert.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Mark as read
      .addCase(markAlertAsRead.fulfilled, (state, action) => {
        const index = state.alerts.findIndex(alert => alert.id === action.payload.id);
        if (index !== -1) {
          state.alerts[index] = action.payload;
        }
      })
      
      // Mark all as read
      .addCase(markAllAlertsAsRead.fulfilled, (state) => {
        state.alerts = state.alerts.map(alert => ({ ...alert, is_read: true }));
      })
      
      // Delete alert
      .addCase(deleteSystemAlert.fulfilled, (state, action) => {
        state.alerts = state.alerts.filter(alert => alert.id !== action.payload);
        state.total -= 1;
      });
  }
});

export const { addAlert, clearAlert, clearSystemAlertsError } = systemAlertsSlice.actions;

export default systemAlertsSlice.reducer;