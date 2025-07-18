// store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import { agentTheaterSlice } from './slices/agentTheaterSlice';
import { sirHawkingtonSlice } from './slices/sirHawkingtonSlice';
import { methSnailSlice } from './slices/methSnailSlice';
import { hamstersSlice } from './slices/hamstersSlice';
import { quantumShadowSlice } from './slices/quantumShadowPeopleSlice';
import { theStickSlice } from './slices/theStickSlice';
import { vic20Slice } from './slices/vic20Slice';
import authReducer from './slices/authSlice';

export const store = configureStore({
  reducer: {
    agentTheater: agentTheaterSlice.reducer,
    sirHawkington: sirHawkingtonSlice.reducer,
    methSnail: methSnailSlice.reducer,
    hamsters: hamstersSlice.reducer,
    quantumShadow: quantumShadowSlice.reducer,
    theStick: theStickSlice.reducer,
    vic20: vic20Slice.reducer,
    auth: authReducer
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
