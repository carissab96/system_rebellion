import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import authService from '../../services/authService';

// Define the user profile state interface
interface UserProfileState {
  data: any | null;
  loading: boolean;
  error: string | null;
}

// Initial state
const initialState: UserProfileState = {
  data: null,
  loading: false,
  error: null
};

export const fetchUserProfile = createAsyncThunk(
  'userProfile/fetch',
  async (_, { rejectWithValue }) => {
    try {
      // Use the authService to get the current user profile
      const user = await authService.getCurrentUser();
      return user;
    } catch (error: any) {
      console.error('Error fetching user profile:', error.message);
      return rejectWithValue(error.message || 'Failed to fetch user profile');
    }
  }
);

const userProfileSlice = createSlice({
  name: 'userProfile',
  initialState,
  reducers: {
    clearProfileError: (state) => {
      state.error = null;
    }
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUserProfile.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(fetchUserProfile.fulfilled, (state, action) => {
        state.loading = false;
        state.data = action.payload;
      })
      .addCase(fetchUserProfile.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string || 'An unknown error occurred';
      });
  }
});

export const { clearProfileError } = userProfileSlice.actions;
export default userProfileSlice.reducer;
