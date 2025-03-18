// api.ts
import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios';
import store from '../store/store';// Updated import path
import { logout } from '../store/slices/authSlice';

interface ApiError extends AxiosError {
  config: InternalAxiosRequestConfig & { _retry?: boolean };
}

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

// Sir Hawkington's Distinguished API URL Configuration Protocol
// Use the proxy configured in vite.config.ts instead of direct connection - The Quantum Shadow People insist
export const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? `${window.location.protocol}//${window.location.host}/api` // Production URL with aristocratic elegance
  : '/api'; // Development URL using the proxy - The Meth Snail's preferred configuration

console.log(`🧐 Sir Hawkington announces the API base URL: ${API_BASE_URL}`);

// Track backend availability status - The Stick's anxiety management system
let backendAvailable = true; // The Hamsters are optimistic by default
let lastCheckTime = 0; // The VIC-20's 8-bit timestamp
const AVAILABILITY_CHECK_INTERVAL = 30000; // 30 seconds - Any longer and the Meth Snail gets twitchy

// Function to check if the backend is available with retry mechanism - Sir Hawkington's connectivity verification protocol
export const checkBackendAvailability = async (forceCheck = false): Promise<boolean> => {
  const now = Date.now();
  
  // If we checked recently and it's not a forced check, return the cached result
  if (!forceCheck && now - lastCheckTime < AVAILABILITY_CHECK_INTERVAL) {
    console.log('🧐 Sir Hawkington recalls from his distinguished memory:', backendAvailable ? 'Backend was available' : 'Backend was unavailable');
    console.log('🐌 The Meth Snail confirms cached status:', backendAvailable);
    return backendAvailable;
  }
  
  // Update the last check time - The VIC-20 handles the clock
  console.log('🎮 The VIC-20 updates the timestamp...');
  lastCheckTime = now;
  
  // Try multiple endpoints in case one is available but another isn't - The Quantum Shadow People's suggestion
  const endpoints = [
    '/health-check/', // Primary health check - Sir Hawkington's preferred diagnostic
    '/auth/status/'   // Fallback endpoint - The Stick's backup plan
  ];
  
  for (let i = 0; i < 2; i++) { // Try up to 2 times - The Hamsters can only count to 2
    for (const endpoint of endpoints) {
      try {
        console.log(`🧐 Sir Hawkington is checking backend availability (attempt ${i+1}) using ${endpoint}...`);
        console.log(`🐹 The Hamsters are preparing the HTTP request with duct tape...`);
        const response = await axios.get(`${API_BASE_URL}${endpoint}`, {
          timeout: 3000, // 3 second timeout - The Meth Snail gets impatient after 3 seconds
          withCredentials: true // The Stick insists on proper credentials
        });
        
        if (response.status >= 200 && response.status < 300) {
          console.log('🧐 Sir Hawkington adjusts his monocle with satisfaction: "Backend is available and responding with distinguished elegance!"');
          console.log('🐌 The Meth Snail celebrates with another hit of methamphetamine!');
          backendAvailable = true;
          return true;
        }
      } catch (error) {
        // Continue to next endpoint or retry
        console.warn(`⚠️ Backend check failed for ${endpoint}:`);
        console.warn(`🪄 The Stick's anxiety intensifies:`, 
          error instanceof Error ? error.message : 'Unknown error - even the VIC-20 is confused');
      }
    }
    
    // Wait before retry
    if (i < 1) { // Only wait if we're going to retry
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  // If we get here, all attempts failed - The Hamsters have run out of duct tape
  console.error('🧐 Sir Hawkington removes his monocle in distress: "The backend appears to be indisposed!"');
  console.error('🐌 The Meth Snail has crashed into a wall after too many failed attempts');
  console.error('🪄 The Stick is having a full-blown panic attack!');
  backendAvailable = false;
  return false;
};

// Function to get the current backend availability status
export const getBackendAvailability = (): boolean => {
  // If it's been too long since our last check, trigger a new check but don't wait for it
  const now = Date.now();
  if (now - lastCheckTime > AVAILABILITY_CHECK_INTERVAL) {
    checkBackendAvailability().catch(err => {
      console.error('Background availability check failed:', err);
    });
  }
  return backendAvailable;
};

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for CSRF/cookies
});

// Request interceptor
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  
  // Add CSRF token to non-GET requests
  if (config.method !== 'get') {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    } else {
      console.warn('CSRF token not found in cookies!');
    }
  }
  
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  async (error: ApiError) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshTokenStr = localStorage.getItem('refreshToken');
      
      if (refreshTokenStr) {
        try {
          // Manual refresh token request
          const refreshResponse = await axios.post(
            `${API_BASE_URL}/auth/token/refresh/`,
            { refresh: refreshTokenStr },
            { 
              withCredentials: true,
              headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken() || ''
              }
            }
          );
          
          if (refreshResponse.data && refreshResponse.data.access) {
            const newToken = refreshResponse.data.access;
            // Update token in localStorage
            localStorage.setItem('token', newToken);
            // Update the original request with the new token
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return api(originalRequest);
          }
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          // Clear auth data and redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('refreshToken');
          store.dispatch(logout());
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available
        store.dispatch(logout());
      }
    }
    return Promise.reject(error);
  }
);

// Type your response data
interface AutotunerData {
  // Add your autotuner properties here
  id: number;
  // ... other properties
}

// API methods
export const apiMethods = {
  // Generic GET method with type parameter
  get: async <T>(url: string): Promise<T> => {
    const response = await api.get<T>(url);
    return response.data;
  },

  // Generic POST method with type parameters
  post: async <T, D>(url: string, data: D): Promise<T> => {
    const response = await api.post<T>(url, data);
    return response.data;
  },

  // Add other methods as needed
  autotuner: {
    fetch: async (id: number): Promise<AutotunerData> => {
      try {
        return await apiMethods.get<AutotunerData>(`/autotuner/${id}/`);
      } catch (error) {
        console.error(`Error fetching autotuner ${id}:`, error);
        throw error;
      }
    }
  },

  metrics: {
    // Sir Hawkington's Distinguished Metrics Retrieval Protocol
    fetch: async () => {
      console.log("🧐 Sir Hawkington is fetching the metrics with utmost elegance!");
      
      // The Meth Snail's Token Verification
      const token = localStorage.getItem('token');
      if (!token) {
        console.error("🚨 No authentication token found! The Meth Snail is most displeased.");
        throw new Error("Authentication required. Sir Hawkington suggests logging in again.");
      }
      
      // The Stick's JWT Format Check
      if (!token.startsWith('ey')) {
        console.warn("⚠️ THE STICK PANIC: Token doesn't look like a JWT! It should start with 'ey'");
      }
      
      try {
        // Use the API instance which already has the interceptors for auth
        // Sir Hawkington's Distinguished Endpoint Correction
        // The correct path is 'api/metrics/' not just '/metrics/'
        console.log("📍 The Quantum Shadow People suggest the correct endpoint: 'api/metrics/'");
        const response = await apiMethods.get('/api/metrics/');
        console.log("✨ The Hamsters have successfully retrieved the metrics!", response);
        return response;
      } catch (error) {
        console.error("💥 The Meth Snail crashed into the metrics endpoint!", error);
        
        // The Quantum Shadow People's Error Analysis
        if (axios.isAxiosError(error) && error.response?.status === 401) {
          console.error("🔐 Sir Hawkington's authentication has failed! Token may be invalid or expired.");
          // Could trigger a refresh token flow here if needed
        }
        
        throw error;
      }
    },
    // Add other metric-related methods
  }
};

// Function to initialize CSRF token
export const initializeCsrf = async (): Promise<boolean> => {
  try {
    // First check if backend is available
    const isAvailable = await checkBackendAvailability(true);
    if (!isAvailable) {
      throw new Error('Backend is not available, cannot initialize CSRF token');
    }
    
    // Make a GET request to an endpoint that sets the CSRF cookie
    await axios.get(`${API_BASE_URL}/health-check/`, {
      withCredentials: true,
      timeout: 5000 // 5 second timeout
    });
    
    // Verify that we got the CSRF token
    const csrfToken = getCsrfToken();
    if (!csrfToken) {
      console.warn('CSRF token not found in cookies after initialization');
      // Try one more time
      await axios.get(`${API_BASE_URL}/health-check/`, {
        withCredentials: true,
        timeout: 5000
      });
      
      if (!getCsrfToken()) {
        throw new Error('Failed to get CSRF token after multiple attempts');
      }
    }
    
    console.log('✅ CSRF token successfully initialized');
    return true;
  } catch (error) {
    console.error('Failed to initialize CSRF token:', 
      error instanceof Error ? error.message : 'Unknown error');
    return false;
  }
};

export default api;