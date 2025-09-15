// store/index.ts
import { configureStore } from '@reduxjs/toolkit';

import agentTheaterReducer from './slices/agentTheaterSlice';
import authReducer  from './slices/authSlice';
import hamstersReducer from './slices/hamstersSlice';
import methSnailReducer from './slices/methSnailSlice';
import quantumShadowSReducer  from './slices/quantumShadowPeopleSlice';
import sirHawkingtonReducer from './slices/sirHawkingtonSlice';
import theStickReducer from './slices/theStickSlice';
import vic20Reducer from './slices/vic20Slice';
import metricsReducer from './slices/metricSlice';

export const store = configureStore({
  reducer: {
    agentTheater: agentTheaterReducer,
    sirHawkington: sirHawkingtonReducer,
    methSnail: methSnailReducer,
    hamsters: hamstersReducer,
    quantumShadow: quantumShadowSReducer,
    theStick: theStickReducer,
    vic20: vic20Reducer,
    auth: authReducer,
    metrics: metricsReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        ignoredActions: [
          'agentTheater/updateWebSocketMessage',
          'sirHawkington/updateMetrics',
          'methSnail/updateMetrics',
          'hamsters/updateMetrics',
          'quantumShadow/updateMetrics',
          'theStick/updateMetrics',
          'vic20/updateMetrics',
        ],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;
