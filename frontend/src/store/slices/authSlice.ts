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
// Define the profile interface
interface UserProfile {
    operating_system: string;
    os_version: string;
    cpu_cores: number;
    total_memory: number;
    linux_distro?: string;
    linux_distro_version?: string;
    avatar?: string;
    [key: string]: any; // Allow for additional fields
}

// Define the preferences interface
interface UserPreferences {
    optimization_level: string;
    notification_preferences: Record<string, any>;
    system_settings: Record<string, any>;
    theme_preferences?: Record<string, any>;
    [key: string]: any; // Allow for additional fields
}

interface AuthState {
    isAuthenticated: boolean;
    user: {
        [x: string]: any;
        id: string;
        username: string;
        profile?: UserProfile;
        preferences?: UserPreferences;
        // Direct fields that mirror profile data
        operating_system?: string;
        os_version?: string;
        cpu_cores?: number;
        total_memory?: number;
        linux_distro?: string;
        linux_distro_version?: string;
        avatar?: string;
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
    async (credentials: { username: string; password: string }, { rejectWithValue }) => {
        try {
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

            // Create URL encoded form data for OAuth2 password flow
            const formData = new URLSearchParams();
            formData.append('username', credentials.username);
            formData.append('password', credentials.password);
            
            console.log(" Sending login request to token endpoint");
            console.log(" Using credentials:", { username: credentials.username, password: '***' });
            
            // Log the full URL we're using for debugging
            console.log(" Attempting login with credentials:", { username: credentials.username, password: '***' });
            
            try {
                // Use the correct token endpoint with URLSearchParams for OAuth2 password flow
                console.log(" Sending request to /api/auth/token");
                
                const response = await axios.post('/api/auth/token', formData, {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': csrfToken || ''
                    },
                    withCredentials: true
                });
                
                console.log(" Login response status:", response.status);
                const data = response.data;
                console.log(" Login successful, raw response:", data);

                // Extract tokens
                const accessToken = data.access_token;
                const refreshToken = data.refresh_token;

                console.log(" Extracted tokens:", {
                    hasToken: !!accessToken,
                    hasRefresh: !!refreshToken
                });
                
                // Store tokens and return data in the outer try block
                if (accessToken) {
                    // Store token with Bearer prefix to ensure it's properly formatted
                    localStorage.setItem('token', accessToken);
                    
                    // Set the Authorization header for all future requests
                    axios.defaults.headers.common['Authorization'] = `Bearer ${accessToken}`;
                    console.log(" Set default Authorization header for future requests");
                    
                    // Store username in localStorage if available
                    if (data.username) {
                        localStorage.setItem('username', data.username);
                        console.log(" Stored username in localStorage:", data.username);
                    } else if (credentials && credentials.username) {
                        localStorage.setItem('username', credentials.username);
                        console.log(" Stored username from credentials in localStorage:", credentials.username);
                    }
                }
                if (refreshToken) {
                    localStorage.setItem('refreshToken', refreshToken);
                }
                
                return data;
            } catch (tokenError) {
                console.log(" Token endpoint failed, trying login endpoint");
                
                // If token endpoint fails, try the login endpoint
                const loginResponse = await axios.post('/api/auth/login', {
                    username: credentials.username,
                    password: credentials.password
                }, {
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken || ''
                    },
                    withCredentials: true
                });
                
                console.log(" Login endpoint response status:", loginResponse.status);
                const loginData = loginResponse.data;
                console.log(" Login successful via login endpoint, raw response:", loginData);

                // Extract tokens
                const loginAccessToken = loginData.access_token;
                const loginRefreshToken = loginData.refresh_token;

                console.log(" Extracted tokens from login endpoint:", {
                    hasToken: !!loginAccessToken,
                    hasRefresh: !!loginRefreshToken
                });
                
                // Store tokens from login endpoint
                if (loginAccessToken) {
                    localStorage.setItem('token', loginAccessToken);
                    
                    // Set the Authorization header for all future requests
                    axios.defaults.headers.common['Authorization'] = `Bearer ${loginAccessToken}`;
                    console.log(" Set default Authorization header for future requests (fallback login)");
                    
                    // Store username in localStorage if available
                    if (loginData.username) {
                        localStorage.setItem('username', loginData.username);
                        console.log(" Stored username in localStorage:", loginData.username);
                    } else if (credentials && credentials.username) {
                        localStorage.setItem('username', credentials.username);
                        console.log(" Stored username from credentials in localStorage:", credentials.username);
                    }
                }
                if (loginRefreshToken) {
                    localStorage.setItem('refreshToken', loginRefreshToken);
                }
                
                return loginData;
            }

            // This code is unreachable but kept for reference
            return {}; // This line will never execute
        } catch (error: unknown) {
            if (axios.isAxiosError(error)) {
                console.error(" Login failed:", error.response?.data || error.message);
                return rejectWithValue(error.response?.data?.detail || 'Login failed');
            }
            console.error(" Login error:", error);
            return rejectWithValue('Failed to login');
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
        } catch (error: unknown) {
            console.error(" Token refresh error:", error);
            return rejectWithValue('Failed to refresh token');
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
            // Clear auth state
            state.isAuthenticated = false;
            state.user = null;
            state.token = null;
            state.refreshToken = null;
            
            // Remove tokens and user data from localStorage
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            localStorage.removeItem('username');
            
            // Clear the Authorization header
            delete axios.defaults.headers.common['Authorization'];
            console.log(" Cleared Authorization header and user data on logout");
        },
        updateProfile: (state, action: PayloadAction<any>) => {
            // If we don't have a user object yet, create one
            if (!state.user) {
                console.log('🧐 Creating new user object in Redux store');
                const username = action.payload.username || localStorage.getItem('username') || 'unknown';
                state.user = {
                    id: action.payload.id || 'temp-id',
                    username: username,
                    profile: {
                        operating_system: '',
                        os_version: '',
                        cpu_cores: 0,
                        total_memory: 0
                    },
                    preferences: {
                        optimization_level: 'moderate',
                        notification_preferences: {},
                        system_settings: {}
                    }
                };
                state.isAuthenticated = true;
            }
            
            // From this point, we know state.user is not null
            const user = state.user;
            
            // Ensure username is set
            if (action.payload.username) {
                user.username = action.payload.username;
                // Also store in localStorage for persistence
                localStorage.setItem('username', action.payload.username);
            } else if (localStorage.getItem('username')) {
                const storedUsername = localStorage.getItem('username');
                if (storedUsername) {
                    user.username = storedUsername;
                }
            }
            
            // Handle profile data - this could be in a nested profile object or direct fields
            if (action.payload.profile) {
                // If user doesn't have a profile property yet, create it
                if (!user.profile) {
                    user.profile = {
                        operating_system: '',
                        os_version: '',
                        cpu_cores: 0,
                        total_memory: 0
                    };
                }
                
                // Update the nested profile object
                user.profile = {
                    ...user.profile,
                    ...action.payload.profile
                };
                
                // Also update the direct user fields for backward compatibility
                // This ensures both data structures are updated
                const profileFields = ['operating_system', 'os_version', 'cpu_cores', 'total_memory', 'avatar'] as const;
                profileFields.forEach(field => {
                    if (action.payload.profile[field] !== undefined) {
                        (user as any)[field] = action.payload.profile[field];
                    }
                });
            }
            
            // Handle direct profile fields at the root level
            const directProfileFields = ['operating_system', 'os_version', 'cpu_cores', 'total_memory', 'avatar'] as const;
            directProfileFields.forEach(field => {
                if (action.payload[field] !== undefined) {
                    // Update the direct field
                    (user as any)[field] = action.payload[field];
                    
                    // Also update the nested profile if it exists
                    if (user.profile) {
                        (user.profile as any)[field] = action.payload[field];
                    }
                }
            });
            
            // Handle preferences
            if (action.payload.preferences) {
                // If user doesn't have a preferences property yet, create it
                if (!user.preferences) {
                    user.preferences = {
                        optimization_level: 'moderate',
                        notification_preferences: {},
                        system_settings: {}
                    };
                }
                
                user.preferences = {
                    ...user.preferences,
                    ...action.payload.preferences
                };
            }
            
            console.log('🧐 Sir Hawkington has updated the profile with aristocratic precision!', user);
        }
    },
    extraReducers: (builder) => {
        // Login cases
        builder
            .addCase(login.pending, (state: AuthState) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(login.fulfilled, (state: AuthState, action: PayloadAction<any>) => {
                state.loading = false;
                state.isAuthenticated = true;
                state.error = null;
                state.token = action.payload.access_token;
                state.refreshToken = action.payload.refresh_token;
            })
            .addCase(login.rejected, (state: AuthState, action: PayloadAction<any>) => {
                state.loading = false;
                state.isAuthenticated = false;
                state.error = action.payload as string;
            })
            // Refresh token cases
            .addCase(refreshToken.pending, (state: AuthState) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(refreshToken.fulfilled, (state: AuthState, action: PayloadAction<any>) => {
                state.loading = false;
                state.error = null;
                state.token = action.payload.access;
                state.refreshToken = action.payload.refresh;
            })
            .addCase(refreshToken.rejected, (state: AuthState, action: PayloadAction<any>) => {
                state.loading = false;
                state.token = null;
                state.error = action.payload as string;
            })
            // Registration cases
            .addCase(registerUser.pending, (state: AuthState) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(registerUser.fulfilled, (state: AuthState, action: PayloadAction<RegistrationResponse>) => {
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
            .addCase(registerUser.rejected, (state: AuthState, action: PayloadAction<any>) => {
                state.loading = false;
                state.error = action.payload as string;
                console.log("Registration failed in reducer!");
            });
    }
});

export const { logout, updateProfile } = authSlice.actions;
export default authSlice.reducer;