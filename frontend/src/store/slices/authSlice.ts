// src/store/slices/authSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';

import apiService from '../../services/api';
import type { User } from '../../types/auth';
import { API_BASE_URL } from '../../config/constants';
// Match your actual User type from your backend


interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
  isInitializing: boolean; // Separate loading state for initial auth
  error: string | null;
  csrfToken: string | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  isLoading: false,
  isInitializing: false,
  error: null,
  csrfToken: null,
};

// Fetch CSRF token (you already have this working)
export const fetchCsrfToken = createAsyncThunk(
  'auth/fetchCsrfToken',
  async () => {
    const response = await fetch('/api/auth/csrf_token');
    if (!response.ok) throw new Error('Failed to fetch CSRF token');
    const data = await response.json();
    return data.csrf_token;
  }
);
export const registerUser = createAsyncThunk(
  'auth/register',
  async ({ 
    email, 
    username, 
    password, 
    first_name,
    last_name,
    company_name,
    job_title,
    csrfToken 
  }: { 
    email: string; 
    username: string; 
    password: string;
    first_name: string;
    last_name: string;
    company_name: string;
    job_title: string;
    csrfToken: string 
  }) => {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ 
        email, 
        username, 
        password,
        first_name,
        last_name,
        company_name,
        job_title
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Registration failed');
    }

    const data = await response.json();
    return {
      token: data.access_token,
      user: data.user
    };
  }
);
// Login with email/password (matches your OAuth flow)
export const loginUser = createAsyncThunk(
  'auth/login',
  async ({ email, password, csrfToken }: { email: string; password: string; csrfToken: string }) => {
    const response = await fetch('/api/auth/token', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': csrfToken,
      },
      body: new URLSearchParams({
        username: email, // OAuth2 expects username field but we pass email
        password,
        grant_type: 'password'
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || 'Login failed');
    }

    const data = await response.json();
    return {
      token: data.access_token,
      user: data.user
    };
  }
);

// Validate existing token
export const validateToken = createAsyncThunk(
  'auth/validateToken',
  async (token: string) => {
    const response = await fetch('/validate-token', {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) throw new Error('Token validation failed');
    return response.json();
  }
);
export const completeOnboarding = createAsyncThunk(
  'auth/completeOnboarding',
  async (onboardingData: any) => {
    console.log('Data being sent to API:', onboardingData);
    const response = await apiService.completeOnboarding(onboardingData);
    console.log('API response:', response.data);
    return response.data;
  }
);

// Initialize auth from localStorage with token validation and refresh
export const initializeAuth = createAsyncThunk(
  'auth/initializeAuth',
  async (_, { rejectWithValue }) => {
    const savedToken = localStorage.getItem('access_token');
    const savedRefreshToken = localStorage.getItem('refresh_token');

    if (!savedToken) {
      // No saved auth data, user needs to login
      return { authenticated: false };
    }

    try {
      // Add timeout to prevent hanging
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);

      // Validate the saved token
      const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${savedToken}`,
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        // Token might be expired, try to refresh
        if (response.status === 401 && savedRefreshToken) {
          console.log('Token expired, attempting refresh...');
          try {
            const refreshResponse = await fetch(`${API_BASE_URL}/api/auth/refresh-token`, {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ refresh_token: savedRefreshToken })
            });

            if (refreshResponse.ok) {
              const refreshData = await refreshResponse.json();
              const newToken = refreshData.access_token;

              // Store new token
              localStorage.setItem('access_token', newToken);

              // Retry the original request with new token
              const retryResponse = await fetch(`${API_BASE_URL}/api/auth/me`, {
                headers: {
                  'Authorization': `Bearer ${newToken}`,
                  'Content-Type': 'application/json'
                }
              });

              if (retryResponse.ok) {
                const userData = await retryResponse.json();
                return {
                  authenticated: true,
                  token: newToken,
                  user: userData.user
                };
              }
            }
          } catch (refreshError) {
            console.warn('Token refresh failed:', refreshError);
          }
        }

        // Token is invalid and refresh failed, clear localStorage
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_data');
        return { authenticated: false };
      }

      const userData = await response.json();
      return {
        authenticated: true,
        token: savedToken,
        user: userData.user
      };
    } catch (error) {
      // Network error, timeout, or token validation failed
      console.warn('Auth initialization failed:', error);

      // Only clear tokens if it's a definitive auth failure, not network issues
      if (error instanceof Error && error.name !== 'AbortError') {
        // For network errors, keep tokens and try again later
        return rejectWithValue('Auth initialization failed - will retry later');
      }

      // For timeout or other errors, clear tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('user_data');
      return { authenticated: false };
    }
  }
);
export const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    // For manual login success (from your modals)
    loginSuccess: (state, action: PayloadAction<{ user: User; token: string }>) => {
      state.isAuthenticated = true;
      state.user = {
        ...action.payload.user,
        is_onboarded: action.payload.user.is_onboarded ?? false,
        is_active: action.payload.user.is_active ?? true,
      };
      state.token = action.payload.token;
      state.error = null;
      state.isLoading = false;
      
      // Store in localStorage for persistence
      localStorage.setItem('access_token', action.payload.token);
      localStorage.setItem('user_data', JSON.stringify(action.payload.user));
    },
    
    // Logout and clear everything
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.error = null;
      
      // Clear localStorage
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_data');
    },
    
    // Set CSRF token
    setCsrfToken: (state, action: PayloadAction<string>) => {
      state.csrfToken = action.payload;
    },
    
    // Update user (for onboarding completion)
    updateUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      localStorage.setItem('user_data', JSON.stringify(action.payload));
    },
    
    // Set error
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    
    // Clear error
    clearError: (state) => {
      state.error = null;
    },
    
    // Clear auth state completely (for logout and failed validation)
    clearAuthState: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.error = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('user_data');
    },
  },

  extraReducers: (builder) => {
    builder
      // CSRF token
      .addCase(fetchCsrfToken.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchCsrfToken.fulfilled, (state, action) => {
        state.csrfToken = action.payload;
        state.isLoading = false;
      })
      .addCase(fetchCsrfToken.rejected, (state, action) => {
        state.error = action.error.message || 'Failed to fetch CSRF token';
        state.isLoading = false;
      })
      .addCase(registerUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(registerUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.error = null;
        
        localStorage.setItem('access_token', action.payload.token);
        localStorage.setItem('user_data', JSON.stringify(action.payload.user));
      })
      .addCase(registerUser.rejected, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.error = action.error.message || 'Registration failed';
      })
      // Login
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.token = action.payload.token;
        state.error = null;
        
        // Store in localStorage
        localStorage.setItem('access_token', action.payload.token);
        localStorage.setItem('user_data', JSON.stringify(action.payload.user));
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.isAuthenticated = false;
        state.error = action.error.message || 'Login failed';
      })
      
      // Token validation
      .addCase(validateToken.fulfilled, (state, action) => {
        state.isAuthenticated = true;
        state.user = action.payload.user;
        state.error = null;
      })
      .addCase(validateToken.rejected, (state) => {
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
      })
      .addCase(completeOnboarding.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(completeOnboarding.fulfilled, (state, action) => {
        state.isLoading = false;
        // Update user with onboarded status
        if (state.user) {
          state.user = {
            ...state.user,
            is_onboarded: true,
            ...action.payload.user // Change from user_data to user
          };
          localStorage.setItem('user_data', JSON.stringify(state.user));
        }
      })
      .addCase(completeOnboarding.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Onboarding completion failed';
      })
      
      // Initialize auth
      .addCase(initializeAuth.pending, (state) => {
        state.isInitializing = true;
        state.error = null;
      })
      .addCase(initializeAuth.fulfilled, (state, action) => {
        state.isInitializing = false;
        if (action.payload.authenticated) {
          state.isAuthenticated = true;
          state.user = action.payload.user!;
          state.token = action.payload.token!;
        } else {
          // Not authenticated, ensure clean state
          state.isAuthenticated = false;
          state.user = null;
          state.token = null;
        }
        state.error = null;
      })
      .addCase(initializeAuth.rejected, (state, action) => {
        state.isInitializing = false;
        state.isAuthenticated = false;
        state.user = null;
        state.token = null;
        state.error = action.error.message || 'Authentication initialization failed';
        // Clear localStorage on initialization failure
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_data');
      })
    }
  })

export const { 
  loginSuccess, 
  logout, 
  setCsrfToken,
  updateUser, 
  setError, 
  clearError, 
  clearAuthState 
} = authSlice.actions;

export default authSlice.reducer;