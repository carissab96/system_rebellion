// src/services/authService.ts
import axios from 'axios';

// Define types
interface User {
  id: string;
  username: string;
  email: string;
  operating_system?: string;
  os_version?: string;
  cpu_cores?: number;
  total_memory?: number;
  avatar?: string;
  needs_onboarding?: boolean;
  profile?: any;
  preferences?: any;
}

interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// Set up axios instance with authentication
const authApi = axios.create({
  baseURL: 'http://127.0.0.1:8000/api/auth',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add a request interceptor to include the token in all requests
authApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => Promise.reject(error)
);

authApi.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    // Skip refresh token logic for login/token endpoint - this is critical!
    const isLoginRequest = originalRequest.url && 
                          (originalRequest.url.includes('/token') || 
                           originalRequest.url.includes('/login'));
    
    // Only attempt refresh for 401 errors on non-login requests
    if (error.response?.status === 401 && !originalRequest._retry && !isLoginRequest) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refresh_token');
        
        if (!refreshToken) {
          console.error('[ERROR] Login failed', 'Refresh token is required');
          return Promise.reject(error);
        }
        
        // Rest of refresh token logic stays the same...
        // ...
      } catch (refreshError) {
        console.error('[ERROR] Token refresh failed:', refreshError);
        return Promise.reject(error);
      }
    }
    
    return Promise.reject(error);
  }
);
// Auth service methods
export const authService = {
  // Check authentication status
  async checkStatus(): Promise<boolean> {
    try {
      console.log('Checking authentication status...');
      const response = await authApi.get('/status/');
      console.log('Auth status check response:', response.data);
      return response.data.is_authenticated;
    } catch (error) {
      console.error('Auth status check failed:', error);
      return false;
    }
  },
  
  // Login
  async login(username: string, password: string): Promise<User> {
    try {
      console.log('Logging in with:', { username, password: '***' });
      
      // Check if backend is available first
      try {
        const healthCheck = await axios.get('http://127.0.0.1:8000/api/health-check/');
        console.log('Health check response:', healthCheck.data);
      } catch (healthError) {
        console.error('Backend health check failed:', healthError);
        throw new Error('Backend server is not available. Please try again later.');
      }
      
      // Create form data for login - FastAPI OAuth2 expects x-www-form-urlencoded format
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      // Removed grant_type as it's not handled in the backend
      
      console.log('Sending login request with form data:', username);
      
      // Make the login request with authApi
      const response = await authApi.post<LoginResponse>('/token', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json'
        },
        _isLoginRequest: true
      });
      console.log('Login response:', response.data);
      
      if (!response.data.access_token || !response.data.refresh_token) {
        throw new Error('Invalid response from server: missing tokens');
      }
      
      // Save tokens and user data
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('username', response.data.user.username);
      
      // Set default auth header for future requests
      axios.defaults.headers.common['Authorization'] = `Bearer ${response.data.access_token}`;
      
      return response.data.user;
    } catch (error: any) {
      // Enhanced error logging with improved error handling
      if (error.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        console.error('[ERROR] Login failed - Server response:', {
          status: error.response.status,
          data: error.response.data,
          headers: error.response.headers
        });
        
        // Extract the proper error message
        const errorMessage = 
          error.response.data?.detail ||
          'Authentication failed.  Please check your username and password.';
        
        throw new Error(errorMessage);
      } else {
        // The request was made but no response was received
        console.error('[ERROR] Login failed - No response:', error.request);
        throw new Error('The Quantum Shadow People blocked your request. Please try again later.');
      }
      
      // Ensure we always throw an Error object, not a string or response
      throw new Error('Sir Hawkington regrets to inform you that authentication has failed. Please try again.');
    }
  },
  
  // Register
  async register(username: string, email: string, password: string): Promise<User> {
    try {
      console.log('Registering...');
      const response = await authApi.post<LoginResponse>('/register', {
        username,
        email,
        password
      });
      console.log('Registration response:', response.data);
      
      // Save tokens and user data
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('username', response.data.user.username);
      
      return response.data.user;
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  },
  
  // Logout
  async logout() {
    try {
      console.log('Logging out...');
      // No need to call a backend endpoint for logout
      // Just clear the local storage and redirect
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('username');
      console.log('Local storage cleared, redirecting to login page');
      window.location.href = '/login';
      return true;
    } catch (error) {
      console.error('Logout failed:', error);
      // Even if there's an error, try to clear local storage
      localStorage.removeItem('token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('username');
      window.location.href = '/login';
      return false;
    }
  },
  
  // Update user profile
  async updateProfile(profileData: any): Promise<User> {
    try {
      console.log('Updating profile with data:', profileData);
      // Make sure token is in the headers
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('The Meth Snail requires authentication tokens to proceed!');
      }
      
      const response = await authApi.post('/update-profile', profileData, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      console.log('Profile update response:', response.data);
      return response.data.user;
    } catch (error: any) {
      console.error('Profile update failed:', error);
      if (error.response) {
        console.error('Error response:', error.response.data);
        console.error('Status code:', error.response.status);
      }
      throw error;
    }
  },
  
  // Get current user data
  async getCurrentUser(): Promise<User | null> {
    try {
      console.log('Getting current user...');
      const statusResponse = await authApi.get('/status/');
      if (!statusResponse.data.is_authenticated) {
        console.log('Not authenticated, returning null');
        return null;
      }
      
      // Get the current user data from the status endpoint
      if (statusResponse.data.user) {
        console.log('User data from status endpoint:', statusResponse.data.user);
        return statusResponse.data.user;
      }
      
      // If we don't have user data from status, try to fetch it
      try {
        const userResponse = await authApi.get('/me');
        console.log('User data from /me endpoint:', userResponse.data);
        return userResponse.data;
      } catch (userError) {
        console.error('Failed to fetch user data from /me endpoint:', userError);
        
        // Fallback to using just the username if we can't get full user data
        const username = localStorage.getItem('username');
        if (!username) {
          console.log('No username saved, returning null');
          return null;
        }
        
        console.warn('Using fallback user data with username only');
        return {
          id: '', 
          username,
          email: '',
          needs_onboarding: false, // Default to false to prevent unnecessary onboarding redirects
          operating_system: 'unknown', // Add basic system info to prevent onboarding
          os_version: 'unknown',
          cpu_cores: 1,
          total_memory: 1
        };
      }
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  },
  
  // Check if token is valid
  async validateToken(): Promise<boolean> {
    try {
      console.log('Validating token...');
      const response = await authApi.get('/status/');
      console.log('Token validation response:', response.data);
      return response.data.is_authenticated;
    } catch (error) {
      console.error('Token validation failed:', error);
      return false;
    }
  },
  
  // Add a direct test login function for debugging
  async testDirectLogin(username: string = 'testuser', password: string = 'password123'): Promise<any> {
    try {
      console.log('Sir Hawkington is testing the direct login process...');
      
      // Create form data exactly as expected
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);
      
      console.log('Sending direct login request to the Quantum Shadow People');
      
      // Use axios directly to bypass interceptors
      const response = await axios.post(
        'http://127.0.0.1:8000/api/auth/token', 
        formData,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
          }
        }
      );
      
      console.log('The Meth Snail reports login success:', response.data);
      return response.data;
    } catch (error: any) {
      console.error('Sir Hawkington reports direct login test failed:', error);
      if (error.response) {
        console.error('Response data:', error.response.data);
        console.error('Response status:', error.response.status);
      }
      throw error;
    }
  }
};

export default authService;