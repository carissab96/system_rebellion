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
  related_metrics?: any;
}

interface AlertsState {
  alerts: SystemAlert[];
  loading: boolean;
  error: string | null;
  unreadCount: number;
}

const initialState: AlertsState = {
  alerts: [],
  loading: false,
  error: null,
  unreadCount: 0
};

// Async Thunks
export const fetchSystemAlerts = createAsyncThunk(
  'alerts/fetchAlerts',
  async (_, { rejectWithValue }) => {
    try {
      console.log("👻 The Quantum Shadow People are scanning for system alerts...");
      const response = await axios.get(`${API_BASE_URL}/api/system-alert/`);
      console.log("👻 The Quantum Shadow People returned with alerts:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 The Quantum Shadow People encountered an error!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "The Quantum Shadow People couldn't retrieve the alerts. The interdimensional connection is unstable."
      );
    }
  }
);

export const createSystemAlert = createAsyncThunk(
  'alerts/createAlert',
  async (alertData: any, { rejectWithValue }) => {
    try {
      console.log("👻 The Quantum Shadow People are creating a new alert...");
      const response = await axios.post(`${API_BASE_URL}/api/system-alert/`, alertData);
      console.log("👻 The Quantum Shadow People created a new alert:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 The Quantum Shadow People encountered an error while creating an alert!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "The Quantum Shadow People couldn't create the alert. The router configuration is interfering."
      );
    }
  }
);

export const markAlertAsRead = createAsyncThunk(
  'alerts/markAsRead',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`👻 The Quantum Shadow People are marking alert ${id} as read...`);
      const response = await axios.patch(`${API_BASE_URL}/api/system-alert/${id}/`, { is_read: true });
      console.log("👻 The Quantum Shadow People updated the alert:", response.data);
      return response.data;
    } catch (error: any) {
      console.error("💥 The Quantum Shadow People encountered an error while updating an alert!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "The Quantum Shadow People couldn't update the alert. The quantum state collapsed unexpectedly."
      );
    }
  }
);

export const deleteSystemAlert = createAsyncThunk(
  'alerts/deleteAlert',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`👻 The Quantum Shadow People are deleting alert ${id}...`);
      await axios.delete(`${API_BASE_URL}/api/system-alert/${id}/`);
      console.log("👻 The Quantum Shadow People deleted the alert successfully");
      return id;
    } catch (error: any) {
      console.error("💥 The Quantum Shadow People encountered an error while deleting an alert!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "The Quantum Shadow People couldn't delete the alert. It may have been lost in the void between dimensions."
      );
    }
  }
);

// Slice
const alertsSlice = createSlice({
  name: 'alerts',
  initialState,
  reducers: {
    clearAlertsError: (state) => {
      state.error = null;
    },
    markAllAlertsAsRead: (state) => {
      state.alerts = state.alerts.map(alert => ({ ...alert, is_read: true }));
      state.unreadCount = 0;
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
        state.alerts = action.payload;
        state.unreadCount = action.payload.filter((alert: SystemAlert) => !alert.is_read).length;
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
        state.unreadCount += 1;
      })
      .addCase(createSystemAlert.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Mark as read
      .addCase(markAlertAsRead.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(markAlertAsRead.fulfilled, (state, action) => {
        state.loading = false;
        const index = state.alerts.findIndex(alert => alert.id === action.payload.id);
        if (index !== -1) {
          state.alerts[index] = action.payload;
          if (state.unreadCount > 0) state.unreadCount -= 1;
        }
      })
      .addCase(markAlertAsRead.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      })
      
      // Delete alert
      .addCase(deleteSystemAlert.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(deleteSystemAlert.fulfilled, (state, action) => {
        state.loading = false;
        const deletedAlert = state.alerts.find(alert => alert.id === action.payload);
        state.alerts = state.alerts.filter(alert => alert.id !== action.payload);
        if (deletedAlert && !deletedAlert.is_read && state.unreadCount > 0) {
          state.unreadCount -= 1;
        }
      })
      .addCase(deleteSystemAlert.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  }
});

export const { clearAlertsError, markAllAlertsAsRead } = alertsSlice.actions;
export default alertsSlice.reducer;
