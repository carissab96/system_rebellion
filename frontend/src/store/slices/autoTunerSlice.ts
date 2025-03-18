import {createSlice, createAsyncThunk} from '@reduxjs/toolkit';
import { AutoTunerState } from '../../types/metrics';
import { PayloadAction } from '@reduxjs/toolkit';


const initialState: AutoTunerState = {
    uuid: '' as string | null,
    user: '',
    // `    profile: UserProfile;
    // preferences: UserPreferences;
    // optimization_profile: 'OptimizationProfile',
    // optimization_results: 'OptimizationResult',
    status: 'Loading',
    success: true,
    loading: false,
    error: null,
    lastUpdated: null,
  }

export const fetchAutoTuner = createAsyncThunk(
    'autoTuner/fetch',
    async () => {
        const response = await fetch('/api/autotuner/');
        return response.json();
    }
);

const autoTunerSlice = createSlice({
    name: 'autoTuner',
    initialState,
    reducers: {
        updateAutoTuner(state, action: PayloadAction<any>) {
            state.uuid= action.payload;
        },   
        clearAutoTuner: (state) => {
            state.uuid = null; // Now properly typed to allow null
            state.loading = false;
            state.error = null;
            state.lastUpdated = null;
        }
    }
})
export default autoTunerSlice.reducer;