// store/index.ts
import { configureStore } from '@reduxjs/toolkit';

import { agentTheaterSlice } from './slices/agentTheaterSlice';
import { authSlice } from './slices/authSlice';
import { hamstersSlice } from './slices/hamstersSlice';
import { methSnailSlice } from './slices/methSnailSlice';
import { quantumShadowSlice } from './slices/quantumShadowPeopleSlice';
import { sirHawkingtonSlice } from './slices/sirHawkingtonSlice';
import { theStickSlice } from './slices/theStickSlice';
import { vic20Slice } from './slices/vic20Slice';

export const store = configureStore({
  reducer: {
    agentTheater: agentTheaterSlice.reducer,
    sirHawkington: sirHawkingtonSlice.reducer,
    methSnail: methSnailSlice.reducer,
    hamsters: hamstersSlice.reducer,
    quantumShadow: quantumShadowSlice.reducer,
    theStick: theStickSlice.reducer,
    vic20: vic20Slice.reducer,
    auth: authSlice.reducer
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
