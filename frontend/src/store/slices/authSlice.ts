// src/store/slices/authSlice.ts

import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { AuthState, LoginCredentials } from '../../types/auth';
import axios from 'axios';

// Function to get CSRF token from cookies
const getCsrfToken = (): string | null => {
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'csrftoken') {
      return value;
    }
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

            const csrfToken = getCsrfToken();
            if (!csrfToken) {
                console.log("🎩 Sir Hawkington is fetching a fresh CSRF token...");
                await axios.get('http://127.0.0.1:5000/api/auth/token/', {
                    withCredentials: true
                });
            }

            console.log("🐌 The Meth Snail is frantically validating your system specs...");
            console.log("🐹 The Hamsters are preparing their authentication-grade duct tape...");
            
            // Make the registration request
            const response = await fetch('http://127.0.0.1:5000/api/auth/register/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken() || '',
                },
                credentials: 'include',
                body: JSON.stringify(userData)
            });

            // Handle registration errors
            if (!response.ok) {
                let errorMessage = 'Registration failed';
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error || errorData.detail || JSON.stringify(errorData);
                } catch (e) {
                    errorMessage = await response.text();
                }
                
                console.error("💥 Registration failed! Sir Hawkington drops his monocle in shock!", errorMessage);
                return rejectWithValue(errorMessage);
            }

            const data = await response.json();
            console.log("✨ Registration successful! Sir Hawkington welcomes you with a distinguished bow!");
            console.log("🎭 System ID assigned:", data.system_id);

            // After successful registration, get the user's token
            console.log("🔑 Retrieving authentication tokens...");
            const tokenResponse = await fetch('http://127.0.0.1:5000/api/auth/token/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCsrfToken() || '',
                },
                credentials: 'include',
                body: JSON.stringify({
                    username: userData.username,
                    password: userData.password
                })
            });

            // If token retrieval fails, still return the registration data
            if (!tokenResponse.ok) {
                console.warn("⚠️ Token retrieval failed, but registration was successful");
                return {
                    status: 'success',
                    user_id: data.id || 'temp-id',
                    system_id: data.system_id,
                    message: 'Registration successful but login failed'
                };
            }

            const tokenData = await tokenResponse.json();
            console.log("🔐 Authentication tokens received");
            
            // Store the tokens and user data
            if (tokenData.data && tokenData.data.access) {
                localStorage.setItem('token', tokenData.data.access);
                localStorage.setItem('refreshToken', tokenData.data.refresh || '');
                localStorage.setItem('user_id', tokenData.data.user?.id || data.id || 'temp-id');
                localStorage.setItem('username', userData.username);
                localStorage.setItem('system_id', data.system_id);
                
                // Clean up temporary registration data
                localStorage.removeItem('temp_registration_data');
                
                // Return combined data for the reducer
                return {
                    user: {
                        id: tokenData.data.user?.id || data.id || 'temp-id',
                        username: userData.username,
                        profile: userData.profile,
                        preferences: userData.preferences || { optimization_level: 'balanced', notification_preferences: {}, system_settings: {} }
                    },
                    access: tokenData.data.access,
                    refresh: tokenData.data.refresh,
                    system_id: data.system_id
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
                await axios.get('http://127.0.0.1:5000/api/auth/token/', {
                    withCredentials: true
                });
                console.log("🍪 CSRF cookie received:", getCsrfToken() ? "Yes" : "No");
            }

            const csrfToken = getCsrfToken();
            console.log("🛡️ Using CSRF token:", csrfToken);

            // Use absolute URL to backend server instead of relative URL
            const response = await fetch('http://127.0.0.1:5000/api/auth/token/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || '',
                },
                credentials: 'include',  // Important for cookies
                body: JSON.stringify(credentials)
            });

            console.log("📡 Login response status:", response.status);

            if (!response.ok) {
                const errorData = await response.text();
                console.error("💩 Login failed:", errorData);
                return rejectWithValue(errorData);
            }

            const data = await response.json();
            console.log("✨ Login successful:", {
                hasToken: !!data.data.access,
                hasRefresh: !!data.data.refresh
            });

            // Store the tokens
            localStorage.setItem('token', data.data.access);
            localStorage.setItem('refreshToken', data.data.refresh);

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
            const response = await fetch('http://127.0.0.1:5000/api/auth/token/refresh/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken || '',
                },
                credentials: 'include',
                body: JSON.stringify({ refresh: refreshTokenStr })
            });

            console.log("📡 Refresh response status:", response.status);

            if (!response.ok) {
                const errorData = await response.text();
                console.error("💩 Token refresh failed:", errorData);
                return rejectWithValue(errorData);
            }

            const data = await response.json();
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
                state.user = action.payload.data.user;
                state.token = action.payload.data.access;
                state.refreshToken = action.payload.data.refresh;
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