// src/store/slices/authSlice.ts

import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import axios from 'axios';
import { API_BASE_URL } from '../../utils/api';

// Function to get CSRF token from cookies or session
const getCsrfToken = (): string | null => {
  // First check for csrftoken in cookies
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken' || name === 'csrf_token' || name === 'session') {
      return value;
    }
  }
  
  // If not found in cookies, check if it's stored in localStorage
  const storedToken = localStorage.getItem('csrf_token');
  if (storedToken) {
    return storedToken;
  }
  
  return null;
};

// Define the auth state interface
interface AuthState {
    isAuthenticated: boolean;
    user: {
        [x: string]: any;
        id: string;
        username: string;
        profile: {
            operating_system: string;
            os_version: string;
            cpu_cores: number;
            total_memory: number;
        };
        preferences: {
            optimization_level: string;
            notification_preferences: Record<string, any>;
            system_settings: Record<string, any>;
        };
    } | null;
    token: string | null;
    refreshToken: string | null;
    loading: boolean;
    error: string | null;
}

// Define the registration response type
interface RegistrationResponse {
    status: string;
    user: {
        id: string;
        username: string;
        profile: {
            operating_system: string;
            os_version: string;
            cpu_cores: number;
            total_memory: number;
        };
        preferences: {
            optimization_level: string;
            notification_preferences: Record<string, any>;
            system_settings: Record<string, any>;
        };
    };
    system_id: string;
    message: string;
}

// Define the result type for registerUser
export type RegisterUserResult = ReturnType<typeof registerUser>;

// Sir Hawkington's Distinguished Registration Process
export const registerUser = createAsyncThunk<
    RegistrationResponse,
    any,
    {
        rejectValue: string;
    }
>(
    'auth/register',
    async (userData: any, { rejectWithValue }) => {
        try {
            console.log(" Sir Hawkington is processing your registration...");
            
            // Make the registration request
            const response = await axios.post('/api/auth/register', userData, {
                headers: {
                    'Content-Type': 'application/json',
                },
                withCredentials: true
            });

            console.log(" Registration successful!");
            
            // Return the response data
            return response.data;
        } catch (error) {
            console.error(" Registration error!", error);
            if (axios.isAxiosError(error)) {
                console.error(" SERVER RESPONSE:", error.response?.data);
            }
            return rejectWithValue(
                error instanceof Error ? error.message : 'Failed to register'
            );
        }
    }
);

// First, let's add some console logging to track the auth flow
export const login = createAsyncThunk(
    'auth/login',
    async (credentials: any, { rejectWithValue }) => {
        try {
            console.log(" Attempting login with credentials:", {
                username: credentials.username,
                passwordLength: credentials.password.length
            });

            // First, get CSRF token if we don't have it
            if (!getCsrfToken()) {
                console.log(" No CSRF token found, fetching one...");
                await axios.get('/api/csrf/csrf-token', {
                    withCredentials: true
                });
                console.log(" CSRF cookie received:", getCsrfToken() ? "Yes" : "No");
            }

            // Get CSRF token from localStorage or cookies
            const csrfToken = getCsrfToken();
            console.log(" Using CSRF token:", csrfToken ? "Yes" : "No");

            // Use the proxy configured in vite.config.ts
            let data;
            try {
                const response = await axios.post('/api/auth/login', credentials, {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken
                    },
                    withCredentials: true
                });

                console.log(" Login response status:", response.status);
                data = response.data;
                console.log(" Login successful, raw response:", data);
            } catch (error: any) {
                console.error(" Login failed:", error.response?.data || error.message);
                return rejectWithValue(error.response?.data?.detail || 'Login failed');
            }
            
            // Extract tokens
            const accessToken = data.access || (data.data && data.data.access);
            const refreshToken = data.refresh || (data.data && data.data.refresh);
            
            console.log(" Extracted tokens:", {
                hasToken: !!accessToken,
                hasRefresh: !!refreshToken
            });

            // Store tokens
            if (accessToken) {
                localStorage.setItem('token', accessToken);
            }
            if (refreshToken) {
                localStorage.setItem('refreshToken', refreshToken);
            }

            return data;
        } catch (error) {
            console.error(" Login error:", error);
            return rejectWithValue(
                error instanceof Error ? error.message : 'Failed to login'
            );
        }
    }
);

// Add a refresh token thunk
export const refreshToken = createAsyncThunk(
    'auth/refreshToken',
    async (refreshTokenStr: string, { rejectWithValue }) => {
        try {
            console.log(" Attempting to refresh token");
            
            const csrfToken = getCsrfToken();
            console.log(" Using CSRF token for refresh:", csrfToken);

            // Use absolute URL to backend server instead of relative URL
            console.log("Making token refresh request to", `${API_BASE_URL}/auth/token/refresh/`);
            const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, 
                { refresh: refreshTokenStr },
                {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken || '',
                    },
                    withCredentials: true
                }
            );

            console.log(" Refresh response status:", response.status);
            const data = response.data;
            console.log(" Token refresh successful");

            // Update the tokens
            localStorage.setItem('token', data.access);
            if (data.refresh) {
                localStorage.setItem('refreshToken', data.refresh);
            }

            return data;
        } catch (error) {
            console.error(" Token refresh error:", error);
            return rejectWithValue(
                error instanceof Error ? error.message : 'Failed to refresh token'
            );
        }
    }
);

const initialState: AuthState = {
    isAuthenticated: !!localStorage.getItem('token'),
    user: null,
    token: localStorage.getItem('token'),
    refreshToken: localStorage.getItem('refreshToken'),
    loading: false,
    error: null
};

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logout: (state) => {
            state.isAuthenticated = false;
            state.user = null;
            state.token = null;
            state.refreshToken = null;
        },
        updateProfile: (state, action: PayloadAction<any>) => {
            if (state.user) {
                if (action.payload.profile) {
                    state.user.profile = {
                        ...state.user.profile,
                        ...action.payload.profile
                    };
                }
                if (action.payload.preferences) {
                    state.user.preferences = {
                        ...state.user.preferences,
                        ...action.payload.preferences
                    };
                }
            }
        }
    },
    extraReducers: (builder) => {
        // Login cases
        builder
            .addCase(login.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(login.fulfilled, (state, action) => {
                state.loading = false;
                state.isAuthenticated = true;
                state.error = null;
                state.token = action.payload.access;
                state.refreshToken = action.payload.refresh;
            })
            .addCase(login.rejected, (state, action) => {
                state.loading = false;
                state.isAuthenticated = false;
                state.error = action.payload as string;
            })
            // Refresh token cases
            .addCase(refreshToken.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(refreshToken.fulfilled, (state, action) => {
                state.loading = false;
                state.error = null;
                state.token = action.payload.access;
                state.refreshToken = action.payload.refresh;
            })
            .addCase(refreshToken.rejected, (state, action) => {
                state.loading = false;
                state.token = null;
                state.error = action.payload as string;
            })
            // Registration cases
            .addCase(registerUser.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(registerUser.fulfilled, (state, action: PayloadAction<RegistrationResponse>) => {
                state.loading = false;
                state.error = null;
                
                // Create a proper user object with all required fields
                if (action.payload.user) {
                    state.user = {
                        id: action.payload.user.id,
                        username: action.payload.user.username,
                        profile: action.payload.user.profile,
                        preferences: action.payload.user.preferences
                    };
                }
                
                // Don't set isAuthenticated to true - we'll do that after login
                console.log("Registration successful in reducer!");
            })
            .addCase(registerUser.rejected, (state, action) => {
                state.loading = false;
                state.error = action.payload as string;
                console.log("Registration failed in reducer!");
            });
    }
});

export const { logout, updateProfile } = authSlice.actions;
export default authSlice.reducer;