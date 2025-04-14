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
  baseURL: '/api/auth',
  withCredentials: true
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

// Add a response interceptor to handle token refresh
authApi.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    
    // If the error is 401 and we haven't tried to refresh the token yet
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        // Try to refresh the token
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('/api/auth/refresh-token', {}, {
          headers: {
            'X-Refresh-Token': refreshToken
          }
        });
        
        // If successful, update the token and retry the request
        const { access_token } = response.data;
        localStorage.setItem('token', access_token);
        
        // Update the authorization header and retry
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        return authApi(originalRequest);
      } catch (refreshError) {
        // If refresh fails, log out
        logout();
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

// Define logout function to avoid circular reference
const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('username');
  // Redirect to login or home page
  window.location.href = '/login';
};

// Auth service methods
export const authService = {
  // Check authentication status
  async checkStatus(): Promise<boolean> {
    try {
      const response = await authApi.get('/status/');
      return response.data.is_authenticated;
    } catch (error) {
      console.error('Auth status check failed:', error);
      return false;
    }
  },
  
  // Login
  async login(username: string, password: string): Promise<User> {
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);
      
      const response = await authApi.post<LoginResponse>('/token', formData);
      
      // Save tokens and user data
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      localStorage.setItem('username', response.data.user.username);
      
      return response.data.user;
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  },
  
  // Register
  async register(username: string, email: string, password: string): Promise<User> {
    try {
      const response = await authApi.post<LoginResponse>('/register', {
        username,
        email,
        password
      });
      
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
  logout,
  
  // Update user profile
  async updateProfile(profileData: any): Promise<User> {
    try {
      const response = await authApi.post('/profile', profileData);
      return response.data.user;
    } catch (error) {
      console.error('Profile update failed:', error);
      throw error;
    }
  },
  
  // Get current user data
  async getCurrentUser(): Promise<User | null> {
    try {
      const statusResponse = await authApi.get('/status/');
      if (!statusResponse.data.is_authenticated) {
        return null;
      }
      
      // If we're authenticated but don't have full user details, fetch them
      const username = localStorage.getItem('username');
      if (!username) {
        return null;
      }
      
      // We could add a specific endpoint to get current user data
      // For now we'll just check status and use the data we have
      return {
        id: '', // We'd normally get this from the server
        username,
        email: '', // We'd normally get this from the server
        needs_onboarding: false // We'd normally get this from the server
      };
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  },
  
  // Check if token is valid
  async validateToken(): Promise<boolean> {
    try {
      const response = await authApi.get('/status/');
      return response.data.is_authenticated;
    } catch (error) {
      console.error('Token validation failed:', error);
      return false;
    }
  }
};

export default authService;
