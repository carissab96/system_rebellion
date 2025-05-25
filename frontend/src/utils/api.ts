// api.ts
import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import store from '../store/store';
import { logout } from '../store/slices/authSlice';
import { SystemMetric } from '../types/metrics';

interface ApiError extends AxiosError {
  config: InternalAxiosRequestConfig & { _retry?: boolean };
}

// Function to get CSRF token from cookies
const getCsrfToken = (): string | null => {
  // First check localStorage
  const storedToken = localStorage.getItem('csrf_token');
  if (storedToken) {
    return storedToken;
  }
  
  // Then check cookies
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

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Debug endpoint
export const debugApi = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: false,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor
apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem('token');
  if (token) {
    // Make sure token has Bearer prefix and is properly formatted
    // Remove any quotes or extra characters that might be causing issues
    const cleanToken = token.replace(/["']/g, '').trim();
    config.headers.Authorization = cleanToken.startsWith('Bearer ') ? cleanToken : `Bearer ${cleanToken}`;
    console.log('🧠 Sir Hawkington set Authorization header:', config.headers.Authorization.substring(0, 20) + '...');
  } else {
    console.warn('🧠 Sir Hawkington is concerned: No token found in localStorage!');
  }
  
  // Add CSRF token to non-GET requests
  if (config.method !== 'get') {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    } else {
      console.warn('CSRF token not found in cookies or localStorage!');
    }
  }
  
  return config;
});

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  async (error: ApiError) => {
    const originalRequest = error.config;
    
    // Check if this is an auto-tuner request - we'll be more lenient with these
    const isAutoTunerRequest = originalRequest.url?.includes('/auto-tuner/') || 
                              originalRequest.url?.includes('/metrics/');
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      const refreshTokenStr = localStorage.getItem('refresh_token');
      
      if (refreshTokenStr) {
        try {
          console.log('🦔 Sir Hawkington: Attempting to refresh token...');
          // Clean up the refresh token to ensure it's properly formatted
          const cleanRefreshToken = refreshTokenStr.replace(/["']/g, '').trim();
          
          // Manual refresh token request
          const refreshResponse = await axios.post(
            `${API_BASE_URL}/auth/refresh-token`,
            { refresh_token: cleanRefreshToken },
            { 
              headers: {
                'Content-Type': 'application/json'
              }
            }
          );
          
          console.log('✅ Token refresh response:', refreshResponse.data);
          
          if (refreshResponse.data && refreshResponse.data.access_token) {
            const newToken = refreshResponse.data.access_token;
            localStorage.setItem('token', newToken);
            // Update the original request with the new token
            originalRequest.headers.Authorization = `Bearer ${newToken}`;
            return apiClient(originalRequest);
          }
        } catch (refreshError) {
          console.error('Token refresh failed:', refreshError);
          
          // For auto-tuner requests, don't log out - just return error
          if (isAutoTunerRequest) {
            console.log('🧐 Sir Hawkington: Auto-tuner request failed, but not logging out');
            return Promise.reject(error);
          }
          
          // For other requests, clear auth data and redirect to login
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          store.dispatch(logout());
          return Promise.reject(refreshError);
        }
      } else {
        // No refresh token available
        if (isAutoTunerRequest) {
          console.log('🧐 Sir Hawkington: Auto-tuner request failed, but not logging out');
          return Promise.reject(error);
        }
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
    const response = await apiClient.get<T>(url);
    return response.data;
  },
  // Generic POST method with type parameters
  post: async <T, D = any>(url: string, data: D): Promise<T> => {
    try {
      // Ensure CSRF token is initialized before making the request
      const csrfToken = getCsrfToken();
      if (!csrfToken) {
        console.log('🎩 Sir Hawkington is fetching a fresh CSRF token...');
        await initializeCsrf();
      }
      const response = await apiClient.post<T>(url, data);
      return response.data;
    } catch (error) {
      console.error('🎩 Sir Hawkington encountered an error:', error);
      throw error;
    }
  },
  // Generic DELETE method with type parameter
  delete: async <T>(url: string): Promise<T> => {
    const response = await apiClient.delete<T>(url);
    return response.data;
  },
  // Generic PUT method with type parameters
  put: async <T, D>(url: string, data: D): Promise<T> => {
    const response = await apiClient.put<T>(url, data);
    return response.data;
  },
  // Generic PATCH method for partial updates
  patch: async <T, D>(url: string, data: D): Promise<T> => {
    const response = await apiClient.patch<T>(url, data);
    return response.data;
  },
  // Generic HEAD method for retrieving headers only
  head: async <T>(url: string): Promise<T> => {
    const response = await apiClient.head<T>(url);
    return response.data;
  },
  // Generic OPTIONS method
  options: async <T>(url: string): Promise<T> => {
    const response = await apiClient.options<T>(url);
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
      
      try {
        // Use the new public system metrics endpoint that doesn't require authentication
        const response = await apiMethods.get('/metrics/system');
        console.log("✨ The Hamsters have successfully retrieved the metrics!", response);
        return response;
      } catch (error) {
        console.error("💥 The Meth Snail crashed into the metrics endpoint!", error);
        throw error;
      }
    },

    // The Meth Snail's Metric Creation Protocol
    create: async (metricData: Omit<SystemMetric, 'id'>) => {
      console.log("🐌 The Meth Snail is creating a new metric with quantum precision!");
      
      try {
        const response = await apiMethods.post('/metrics/', metricData);
        console.log("✨ Metric created successfully!", response);
        return response;
      } catch (error) {
        console.error("💥 Metric creation failed!", error);
        throw error;
      }
    },

    // Sir Hawkington's Metric Update Mechanism
    update: async (metricId: string, metricData: Partial<SystemMetric>) => {
      console.log(`🧐 Sir Hawkington is updating metric ${metricId} with distinguished care!`);
      
      try {
        const response = await apiMethods.put(`/metrics/${metricId}`, metricData);
        console.log("✨ Metric updated successfully!", response);
        return response;
      } catch (error) {
        console.error("💥 Metric update failed!", error);
        throw error;
      }
    },

    // The Meth Snail's Metric Deletion Ceremony
    delete: async (metricId: string) => {
      console.log(`🐌 The Meth Snail is deleting metric ${metricId} with optimization energy!`);
      
      try {
        const response = await apiMethods.delete(`/metrics/${metricId}`);
        console.log("✨ Metric deleted successfully!", response);
        return response;
      } catch (error) {
        console.error("💥 Metric deletion failed!", error);
        throw error;
      }
    },

    // Quantum Shadow People's Metric Retrieval by ID
    fetchById: async (metricId: string) => {
      console.log(`🧐 Sir Hawkington is retrieving metric ${metricId} with precise calculation!`);
      
      try {
        const response = await apiMethods.get(`/metrics/${metricId}`);
        console.log("✨ Metric retrieved successfully!", response);
        return response;
      } catch (error) {
        console.error("💥 Metric retrieval failed!", error);
        throw error;
      }
    }
  },
  auth: {
    // Sir Hawkington's User Registration Protocol
    register: async (userData: any) => {
      console.log("🧐 Sir Hawkington is processing your registration with distinguished care...");
      
      try {
        // Simplify the data structure to match what the backend expects
        // Send the complete user data including profile
        const response = await axios.post('/auth/register', {
          username: userData.username,
          email: userData.email,
          password: userData.password,
          profile: userData.profile
        }, {
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        console.log("✨ Registration response:", response.data);
        
        // If we have tokens in the response, store them
        if (response.data.access_token) {
          localStorage.setItem('token', response.data.access_token);
          localStorage.setItem('refresh_token', response.data.refresh_token || '');
        }
        
        return response.data;
      } catch (error) {
        console.error("🚨 Registration error:", error);
        if (axios.isAxiosError(error)) {
          console.error("Response data:", error.response?.data);
          console.error("Status code:", error.response?.status);
        }
        throw error;
      }
    },
    
    // The Meth Snail's Login Protocol
    login: async (credentials: { username: string; password: string }) => {
      console.log("🐌 The Meth Snail is processing your login with quantum precision!");
      
      try {
        const response = await apiClient.post('/auth/token/', 
          new URLSearchParams({
            'username': credentials.username,
            'password': credentials.password
          }),
          {
            headers: {
              'Content-Type': 'application/x-www-form-urlencoded',
            }
          }
        );
        
        console.log("✨ Login successful!", response.data);
        
        // Store tokens
        if (response.data.access_token) {
          localStorage.setItem('token', response.data.access_token);
          localStorage.setItem('refresh_token', response.data.refresh_token || '');
        }
        
        return response.data;
      } catch (error) {
        console.error("💥 Login failed!", error);
        throw error;
      }
    }
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
    
    // Try multiple endpoints for CSRF token
    let response;
    try {
      // First try the dedicated endpoint
      response = await axios.get(`${API_BASE_URL}/auth/csrf_token`, {
        withCredentials: true,
        timeout: 5000 // 5 second timeout
      });
    } catch (error) {
      console.log('🧐 Sir Hawkington could not fetch CSRF token from primary endpoint, trying fallback...');
      // If that fails, try direct connection to backend
      response = await axios.get('http://localhost:8000/api/auth/csrf_token', {
        withCredentials: true,
        timeout: 5000
      });
    }
    
    // Check if we got a valid response with a CSRF token
    if (response.data && response.data.csrf_token) {
      // Store the token in localStorage
      localStorage.setItem('csrf_token', response.data.csrf_token);
      console.log('🎩 Sir Hawkington has secured a fresh CSRF token!');
      return true;
    }
    
 // If we didn't get a token from the dedicated endpoint, try the health-check endpoint
 try {
   const healthResponse = await axios.get(`${API_BASE_URL}/health-check`, {
     withCredentials: true,
     timeout: 5000
   });
   
   // If health check response has a csrf_token field, use that
   if (healthResponse.data && healthResponse.data.csrf_token) {
     localStorage.setItem('csrf_token', healthResponse.data.csrf_token);
     console.log('🎩 Sir Hawkington has secured a CSRF token from health check!');
     return true;
   }
 } catch (error) {
   console.log('🧐 Sir Hawkington could not fetch CSRF token from health check endpoint');
   // Continue with the flow, we'll check if we have a token from cookies
 }

// At this point we've tried both endpoints, check if we have a token

// Verify that we got the CSRF token
const csrfToken = getCsrfToken();
if (!csrfToken) {
  console.warn('🧐 Sir Hawkington is concerned: CSRF token not found after initialization');
  throw new Error('Failed to get CSRF token after multiple attempts');
}

console.log('✅ CSRF token successfully initialized');
return true;
} catch (error) {
console.error('Failed to initialize CSRF token:', 
  error instanceof Error ? error.message : 'Unknown error');
return false;
}
};

// Export the apiMethods as the default export
export default apiMethods;