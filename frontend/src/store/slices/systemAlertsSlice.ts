import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { MetricAlert } from '../../types/metrics';

const systemAlertsSlice = createSlice({
    name: 'systemAlerts',
    initialState: {
      alerts: [] as MetricAlert[],
      loading: false,
      error: null
    },
    reducers: {
      addAlert: (state, action: PayloadAction<MetricAlert>) => {
        state.alerts.unshift(action.payload);
      },
      clearAlert: (state, action: PayloadAction<string>) => {
        state.alerts = state.alerts.filter(alert => alert.id !== action.payload);
      }
    }
  });
  
  export const { addAlert, clearAlert } = systemAlertsSlice.actions;
  
  export default systemAlertsSlice.reducer;