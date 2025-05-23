import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { apiMethods } from '../../utils/api';

const BASE_PATH =  `/system-alerts/`;
// Types
export interface SystemAlert {
  id: string;
  title: string;
  message: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  timestamp: string;
  is_read: boolean;
  action_status?: 'none' | 'actioned' | 'not_actioned' | 'to_action_later';
  selected?: boolean; // For bulk operations
  additional_data?: any;
  created_at: string;
  updated_at: string;
}

interface SystemAlertsState {
  alerts: SystemAlert[];
  loading: boolean;
  error: string | null;
  total: number;
  selectedCount: number;
}

const initialState: SystemAlertsState = {
  alerts: [],
  loading: false,
  error: null,
  total: 0,
  selectedCount: 0
};

// Define response types
interface AlertsResponse {
  alerts: SystemAlert[];
  total: number;
}

// Async Thunks
export const fetchSystemAlerts = createAsyncThunk<
  AlertsResponse,
  { skip?: number, limit?: number, is_read?: boolean }
>(
  'systemAlerts/fetchAlerts',
  async ({ skip = 0, limit = 20, is_read }: { skip?: number, limit?: number, is_read?: boolean } = {}, { rejectWithValue }) => {
    try {
      console.log("🦉 Sir Hawkington is fetching system alerts...");
      let url = `${BASE_PATH}?skip=${skip}&limit=${limit}`;
      if (is_read !== undefined) {
        url += `&is_read=${is_read}`;
      }
      console.log("Fetching alerts from:", url);
      const response = await apiMethods.get<AlertsResponse>(url);
      console.log("🦉 Sir Hawkington returned with alerts:", response);
      return response as AlertsResponse;
    } catch (error: any) {
      console.error("💥 Sir Hawkington crashed while fetching alerts!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington couldn't fetch the alerts. Most distressing!"
      );
    }
  }
);

export const createSystemAlert = createAsyncThunk<
  SystemAlert,
  Omit<SystemAlert, 'id' | 'timestamp' | 'created_at' | 'updated_at'>
>(
  'systemAlerts/createAlert',
  async (alertData: Omit<SystemAlert, 'id' | 'timestamp' | 'created_at' | 'updated_at'>, { rejectWithValue }) => {
    try {
      console.log("🦉 Sir Hawkington is creating a new system alert...");
      // Ensure CSRF token is initialized
      const response = await apiMethods.post<SystemAlert>(`${BASE_PATH}`, {
        ...alertData,
        timestamp: new Date().toISOString(),
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      });
      console.log("🦉 Sir Hawkington created a new alert:", response);
      return response;
    } catch (error: any) {
      console.error("💥 Sir Hawkington crashed while creating an alert!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington couldn't create the alert. How embarrassing!"
      );
    }
  }
);

export const markAlertAsRead = createAsyncThunk<
  SystemAlert,
  string
>(
  'systemAlerts/markAsRead',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`🦉 Sir Hawkington is marking alert ${id} as read...`);
      const response = await apiMethods.post<SystemAlert, {}>(`${BASE_PATH}${id}/mark-as-read`, {});
      console.log("🦉 Sir Hawkington marked the alert as read:", response);
      return response as SystemAlert;
    } catch (error: any) {
      console.error("💥 Sir Hawkington crashed while marking an alert as read!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington couldn't mark the alert as read. Most peculiar!"
      );
    }
  }
);

export const markAllAlertsAsRead = createAsyncThunk<
  boolean,
  void
>(
  'systemAlerts/markAllAsRead',
  async (_, { rejectWithValue }) => {
    try {
      console.log("🦉 Sir Hawkington is marking all alerts as read...");
      const response = await apiMethods.post<{success: boolean}, {}>(`${BASE_PATH}mark-all-as-read`, {});
      console.log("🦉 Sir Hawkington marked all alerts as read");
      return response.success;
    } catch (error: any) {
      console.error("💥 Sir Hawkington crashed while marking all alerts as read!", error);
      return rejectWithValue(
        error.response?.data?.detail || 
        "Sir Hawkington couldn't mark all alerts as read. Most troubling!"
      );
    }
  }
);

export const deleteSystemAlert = createAsyncThunk<
  string,
  string
>(
  'systemAlerts/deleteAlert',
  async (id: string, { rejectWithValue }) => {
    try {
      console.log(`🦉 Sir Hawkington is deleting alert ${id}...`);
      await apiMethods.delete<{success: boolean}>(`${BASE_PATH}${id}`);
      console.log(`🦉 Sir Hawkington deleted alert ${id}`);
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
      const alertToRemove = state.alerts.find(alert => alert.id === action.payload);
      if (alertToRemove?.selected) {
        state.selectedCount -= 1;
      }
      state.alerts = state.alerts.filter(alert => alert.id !== action.payload);
      state.total -= 1;
    },
    clearSystemAlertsError: (state) => {
      state.error = null;
    },
    updateAlertActionStatus: (state, action: PayloadAction<{id: string, status: 'none' | 'actioned' | 'not_actioned' | 'to_action_later'}>) => {
      const { id, status } = action.payload;
      const alertIndex = state.alerts.findIndex(alert => alert.id === id);
      if (alertIndex !== -1) {
        state.alerts[alertIndex].action_status = status;
      }
    },
    toggleAlertSelection: (state, action: PayloadAction<string>) => {
      const alertIndex = state.alerts.findIndex(alert => alert.id === action.payload);
      if (alertIndex !== -1) {
        const currentSelected = state.alerts[alertIndex].selected || false;
        state.alerts[alertIndex].selected = !currentSelected;
        state.selectedCount += currentSelected ? -1 : 1;
      }
    },
    selectAllAlerts: (state) => {
      state.alerts.forEach(alert => {
        if (!alert.selected) {
          alert.selected = true;
          state.selectedCount += 1;
        }
      });
    },
    deselectAllAlerts: (state) => {
      state.alerts.forEach(alert => {
        if (alert.selected) {
          alert.selected = false;
        }
      });
      state.selectedCount = 0;
    },
    deleteSelectedAlerts: (state) => {
      state.alerts = state.alerts.filter(alert => !alert.selected);
      state.total -= state.selectedCount;
      state.selectedCount = 0;
    },
    updateSelectedAlertsActionStatus: (state, action: PayloadAction<'none' | 'actioned' | 'not_actioned' | 'to_action_later'>) => {
      state.alerts.forEach(alert => {
        if (alert.selected) {
          alert.action_status = action.payload;
        }
      });
    },
    markSelectedAlertsAsRead: (state) => {
      state.alerts.forEach(alert => {
        if (alert.selected && !alert.is_read) {
          alert.is_read = true;
        }
      });
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

export const { 
  addAlert, 
  clearAlert, 
  clearSystemAlertsError,
  updateAlertActionStatus,
  toggleAlertSelection,
  selectAllAlerts,
  deselectAllAlerts,
  deleteSelectedAlerts,
  updateSelectedAlertsActionStatus,
  markSelectedAlertsAsRead
} = systemAlertsSlice.actions;

export default systemAlertsSlice.reducer;