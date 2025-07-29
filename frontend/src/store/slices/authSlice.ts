// src/store/slices/authSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import type { PayloadAction } from '@reduxjs/toolkit';
import type { User } from '../../types/auth';
// Match your actual User type from your backend


interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
  csrfToken: string | null;
}

const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  token: null,
  isLoading: false,
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
  async ({ email, username, password, csrfToken }: { 
    email: string; 
    username: string; 
    password: string; 
    csrfToken: string 
  }) => {
    const response = await fetch('/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
      body: JSON.stringify({ email, username, password })
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
        password: password,
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
    const response = await fetch('/api/auth/validate-token', {
      headers: { 
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) throw new Error('Token validation failed');
    return response.json();
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
      localStorage.setItem('auth_token', action.payload.token);
      localStorage.setItem('user_data', JSON.stringify(action.payload.user));
    },
    
    // Logout and clear everything
    logout: (state) => {
      state.isAuthenticated = false;
      state.user = null;
      state.token = null;
      state.error = null;
      
      // Clear localStorage
      localStorage.removeItem('auth_token');
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
    
    // Initialize from localStorage (call this on app startup)
    initializeAuth: (state) => {
      const savedToken = localStorage.getItem('auth_token');
      const savedUser = localStorage.getItem('user_data');
      
      if (savedToken && savedUser) {
        state.token = savedToken;
        state.user = JSON.parse(savedUser);
        state.isAuthenticated = true;
      }
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
        
        localStorage.setItem('auth_token', action.payload.token);
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
        localStorage.setItem('auth_token', action.payload.token);
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
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user_data');
      });
  },
});

export const { 
  loginSuccess, 
  logout, 
  setCsrfToken,
  updateUser, 
  setError, 
  clearError, 
  initializeAuth 
} = authSlice.actions;

export default authSlice;