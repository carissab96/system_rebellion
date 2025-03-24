// src/store/slices/authSlice.ts

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { AuthState, LoginCredentials } from '../../types/auth';
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

// Sir Hawkington's Distinguished Registration Process
export const registerUser = createAsyncThunk(
    'auth/register',
    async (userData: any, { rejectWithValue }) => {
        try {
            console.log("🧐 Sir Hawkington is processing your registration with distinguished care...");
            console.log("📋 Registration data being processed:", {
                username: userData.username,
                email: userData.email,
                profile: userData.profile,
                // Don't log passwords for security reasons
            });

            // Store user data in localStorage for persistence in case of network issues
            localStorage.setItem('temp_registration_data', JSON.stringify({
                username: userData.username,
                email: userData.email,
                profile: userData.profile
            }));

            // Get CSRF token from localStorage or cookies
            let csrfToken = localStorage.getItem('csrf_token') || getCsrfToken();
            if (!csrfToken) {
                console.log("🎩 Sir Hawkington is fetching a fresh CSRF token...");
                try {
                    const response = await axios.get('/api/csrf/csrf-token', {
                        withCredentials: true
                    });
                    
                    if (response.data && response.data.csrf_token) {
                        localStorage.setItem('csrf_token', response.data.csrf_token);
                        csrfToken = response.data.csrf_token;
                        console.log("🎩 Sir Hawkington has secured a fresh CSRF token!");
                    }
                } catch (error) {
                    console.error("🚨 Failed to fetch CSRF token:", error);
                }
            }

            console.log("🐌 The Meth Snail is frantically validating your system specs...");
            console.log("🐹 The Hamsters are preparing their authentication-grade duct tape...");
            
            // Make the registration request
            console.log("Making registration request to", `${API_BASE_URL}/auth/register`);
            const response = await axios.post(`${API_BASE_URL}/auth/register`, userData, {
                headers: {
                    'X-CSRFToken': csrfToken || '',
                },
                withCredentials: true
            });

            const data = response.data;
            console.log("✨ Registration successful! Sir Hawkington welcomes you with a distinguished bow!");
            console.log("🎭 System ID assigned:", data.system_id);

            // After successful registration, get the user's token
            console.log("🔑 Retrieving authentication tokens...");
            
            // Store username in localStorage for future reference
            localStorage.setItem('username', userData.username);
            
            const tokenResponse = await axios.post(`${API_BASE_URL}/auth/token`, 
                new URLSearchParams({
                    'username': userData.username,
                    'password': userData.password
                }),
                {
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCsrfToken() || '',
                    },
                    withCredentials: true
                }
            );

            // If token retrieval fails, still return the registration data
            if (!tokenResponse.data) {
                console.warn("⚠️ Token retrieval failed, but registration was successful");
                return {
                    status: 'success',
                    user_id: data.id || 'temp-id',
                    system_id: data.system_id,
                    message: 'Registration successful but login failed'
                };
            }

            const tokenData = tokenResponse.data;
            console.log("🔐 Authentication tokens received:", tokenData);
            
            // Store the tokens and user data
            // Handle both response formats (nested data or direct properties)
            const accessToken = tokenData.access || (tokenData.data && tokenData.data.access);
            const refreshToken = tokenData.refresh || (tokenData.data && tokenData.data.refresh);
            const userId = (tokenData.data && tokenData.data.user && tokenData.data.user.id) || 
                          (tokenData.user && tokenData.user.id) || 
                          data.id || 
                          'temp-id';
            
            if (accessToken) {
                localStorage.setItem('token', accessToken);
                localStorage.setItem('refreshToken', refreshToken || '');
                localStorage.setItem('user_id', userId);
                localStorage.setItem('username', userData.username);
                localStorage.setItem('system_id', data.system_id || 'system-1');
                
                // Clean up temporary registration data
                localStorage.removeItem('temp_registration_data');
                
                // Return combined data for the reducer
                return {
                    user: {
                        id: userId,
                        username: userData.username,
                        profile: userData.profile || {
                            operating_system: 'linux',
                            os_version: '5.x',
                            cpu_cores: 4,
                            total_memory: 8192
                        },
                        preferences: userData.preferences || { optimization_level: 'balanced', notification_preferences: {}, system_settings: {} }
                    },
                    access: accessToken,
                    refresh: refreshToken,
                    system_id: data.system_id || 'system-1'
                };
            }
            
            // If we don't have token data but registration was successful
            return {
                status: 'success',
                user_id: data.id || 'temp-id',
                system_id: data.system_id,
                message: 'Registration successful'
            };
        } catch (error) {
            console.error("🚨 Registration error! The Quantum Shadow People are investigating...", error);
            return rejectWithValue(
                error instanceof Error ? error.message : 'Failed to register'
            );
        }
    }
);

// First, let's add some console logging to track the auth flow
export const login = createAsyncThunk(
    'auth/login',
    async (credentials: LoginCredentials, { rejectWithValue }) => {
        try {
            console.log("🔐 Attempting login with credentials:", {
                username: credentials.username,
                passwordLength: credentials.password.length
            });

            // First, get CSRF token if we don't have it
            if (!getCsrfToken()) {
                console.log("🍪 No CSRF token found, fetching one...");
                await axios.get('/api/csrf/csrf-token', {
                    withCredentials: true
                });
                console.log("🍪 CSRF cookie received:", getCsrfToken() ? "Yes" : "No");
            }

            // Get CSRF token from localStorage or cookies
            const csrfToken = localStorage.getItem('csrf_token') || getCsrfToken();
            console.log("🛡️ Using CSRF token:", csrfToken ? "Yes" : "No");

            // Use the proxy configured in vite.config.ts
            let data;
            try {
                console.log("Making login request to", `${API_BASE_URL}/auth/token`);
                const response = await axios.post(`${API_BASE_URL}/auth/token`,
                    new URLSearchParams({
                        'username': credentials.username,
                        'password': credentials.password
                    }),
                    {
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                            'X-CSRFToken': csrfToken || '',
                        },
                        withCredentials: true  // Important for cookies
                    }
                );

                console.log("📡 Login response status:", response.status);
                data = response.data;
                console.log("✨ Login successful, raw response:", data);
            } catch (error: any) {
                console.error("💩 Login failed:", error.response?.data || error.message);
                return rejectWithValue(error.response?.data?.detail || 'Login failed');
            }
            
            // Handle different response formats
            const accessToken = data.access || (data.data && data.data.access);
            const refreshToken = data.refresh || (data.data && data.data.refresh);
            
            console.log("✨ Extracted tokens:", {
                hasToken: !!accessToken,
                hasRefresh: !!refreshToken
            });

            // Store the tokens
            if (accessToken) {
                localStorage.setItem('token', accessToken);
            } else {
                console.error("No access token found in response");
            }
            
            if (refreshToken) {
                localStorage.setItem('refreshToken', refreshToken);
            }

            return data;
        } catch (error) {
            console.error("🚨 Login error:", error);
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
            console.log("🔄 Attempting to refresh token");
            
            const csrfToken = getCsrfToken();
            console.log("🛡️ Using CSRF token for refresh:", csrfToken);

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

            console.log("📡 Refresh response status:", response.status);
            const data = response.data;
            console.log("✨ Token refresh successful");

            // Update the tokens
            localStorage.setItem('token', data.access);
            if (data.refresh) {
                localStorage.setItem('refreshToken', data.refresh);
            }

            return data;
        } catch (error) {
            console.error("🚨 Token refresh error:", error);
            return rejectWithValue(
                error instanceof Error ? error.message : 'Failed to refresh token'
            );
        }
    }
);

const initialState: AuthState = {
    isAuthenticated: !!localStorage.getItem('token'),
    user: null,
    loading: false,
    error: null,
    token: localStorage.getItem('token'),
    refreshToken: localStorage.getItem('refreshToken')
};

const authSlice = createSlice({
    name: 'auth',
    initialState,
    reducers: {
        logout: (state) => {
            localStorage.removeItem('token');
            localStorage.removeItem('refreshToken');
            state.isAuthenticated = false;
            state.user = null;
            state.token = null;
            state.refreshToken = null;
        },
        updateProfile: (state, action: PayloadAction<any>) => {
            console.log("🧐 Sir Hawkington is updating your profile with aristocratic flair!");
            if (state.user && state.user.profile) {
                state.user.profile = {
                    ...state.user.profile,
                    ...action.payload.profile
                };
            }
            if (state.user && action.payload.preferences) {
                state.user.preferences = {
                    ...state.user.preferences,
                    ...action.payload.preferences
                };
            }
            console.log("✨ Profile updated successfully! Sir Hawkington tips his hat while the Meth Snail works frantically in the background.");
        }
    },
    extraReducers: (builder) => {
        builder
            .addCase(login.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(login.fulfilled, (state, action) => {
                state.isAuthenticated = true;
                state.loading = false;
                
                // Handle different response formats
                const payload = action.payload;
                console.log('Login fulfilled payload:', payload);
                
                // Extract user data safely
                if (payload.data && payload.data.user) {
                    state.user = payload.data.user;
                } else if (payload.user) {
                    state.user = payload.user;
                } else {
                    // Create a minimal user object if none exists
                    state.user = {
                        id: localStorage.getItem('user_id') || 'unknown',
                        username: localStorage.getItem('username') || 'user',
                        profile: {
                            operating_system: 'linux',
                            os_version: '5.x',
                            cpu_cores: 4,
                            total_memory: 8192
                        },
                        preferences: { optimization_level: 'balanced', notification_preferences: {}, system_settings: {} }
                    };
                }
                
                // Extract token data safely
                state.token = payload.access || 
                              (payload.data && payload.data.access) || 
                              localStorage.getItem('token');
                              
                state.refreshToken = payload.refresh || 
                                    (payload.data && payload.data.refresh) || 
                                    localStorage.getItem('refreshToken');
                                    
                state.error = null;
            })
            .addCase(login.rejected, (state, action) => {
                state.isAuthenticated = false;
                state.loading = false;
                state.error = action.payload as string;
                console.log("🧐 *Sir Hawkington adjusts monocle in concern*");
                console.log("🐌 The Meth Snail's authentication vibes are off!");
                console.log("🐹 The Hamsters suggest more authentication-grade duct tape!");
            })
            .addCase(refreshToken.pending, (state) => {
                state.loading = true;
                state.error = null;
            })
            .addCase(refreshToken.fulfilled, (state, action) => {
                state.isAuthenticated = true;
                state.loading = false;
                state.token = action.payload.access;
                if (action.payload.refresh) {
                    state.refreshToken = action.payload.refresh;
                }
                state.error = null;
            })
            .addCase(refreshToken.rejected, (state, action) => {
                state.isAuthenticated = false;
                state.loading = false;
                state.token = null;
                state.error = action.payload as string;
                console.log("🧐 Sir Hawkington's token refresh attempt was unsuccessful!");
                console.log("👻 The Quantum Shadow People suggest a dimensional recalibration!");
                console.log("🥖 The Stick's anxiety levels are rising!");
            })
            // Registration cases
            .addCase(registerUser.pending, (state) => {
                state.loading = true;
                state.error = null;
                console.log("🧐 Sir Hawkington is reviewing your application...");
            })
            .addCase(registerUser.fulfilled, (state, action) => {
                state.isAuthenticated = true;
                state.loading = false;
                
                // Handle both response formats (direct login or registration only)
                if (action.payload.user) {
                    // Create a proper user object with all required fields
                    state.user = {
                        id: action.payload.user.id || 'temp-id',
                        username: action.payload.user.username,
                        profile: action.payload.user.profile || { operating_system: 'linux', os_version: '1.0' },
                        preferences: action.payload.user.preferences || { optimization_level: 'balanced', notification_preferences: {}, system_settings: {} },
                        system_id: action.payload.system_id
                    };
                    state.token = action.payload.access;
                    state.refreshToken = action.payload.refresh;
                } else if (action.payload.status === 'success') {
                    // If we only have registration data but no token yet
                    // Create a minimal user object with required fields
                    state.user = {
                        id: action.payload.user_id,
                        username: 'user', // Temporary username until we get full user data
                        profile: { operating_system: 'linux', os_version: '1.0' },
                        preferences: { optimization_level: 'balanced', notification_preferences: {}, system_settings: {} },
                        system_id: action.payload.system_id
                    };
                }
                
                state.error = null;
                console.log("🎩 Sir Hawkington welcomes you to the System Rebellion!");
                console.log("🐌 The Meth Snail is vibrating with optimization possibilities!");
                console.log("🐹 The Hamsters have secured your credentials with their finest duct tape!");
            })
            .addCase(registerUser.rejected, (state, action) => {
                state.isAuthenticated = false;
                state.loading = false;
                state.error = action.payload as string;
                console.log("😱 Sir Hawkington regrets to inform you of this most unfortunate error!");
                console.log("🐌 The Meth Snail suggests trying again after a cosmic realignment!");
                console.log("🐹 The Hamsters are applying emergency authentication-grade duct tape!");
                state.refreshToken = null;
            });
    }
});

export const { logout, updateProfile } = authSlice.actions;
export default authSlice.reducer;