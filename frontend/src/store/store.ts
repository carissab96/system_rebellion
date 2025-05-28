import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import metricsReducer from './slices/metricsSlice';
import userProfileReducer from './slices/userProfileSlice';
import systemAlertsReducer from './slices/systemAlertsSlice';
import autoTunerReducer from './slices/autoTunerSlice';
import optimizationReducer from './slices/optimizationSlice';
import configurationReducer from './slices/configurationSlice';
import cpuReducer from './slices/metrics/CPUSlice';
import { MetricsState } from '../types/metrics';
import xsrfMiddleware from './csrf';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    metrics: metricsReducer,
    userProfile: userProfileReducer,
    systemAlerts: systemAlertsReducer,
    autoTuner: autoTunerReducer,
    optimization: optimizationReducer,
    configuration: configurationReducer,
    cpu: cpuReducer,
  },
  middleware: (getDefaultMiddleware) => 
    getDefaultMiddleware({
      // Disable SerializableStateInvariantMiddleware to prevent performance warnings
      serializableCheck: false,
    }).concat(xsrfMiddleware)
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export interface StoreState {
  metrics: MetricsState;
};

export default store;






