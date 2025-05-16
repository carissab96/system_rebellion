// src/utils/csrfFetch.ts
import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';

/**
 * Sir Hawkington's Distinguished CSRF Utility
 * Provides quantum-grade protection against shadow people!
 */

// Get the base API URL from environment
const API_URL = import.meta.env.VITE_API_URL;

/**
 * Get the current CSRF token from cookies
 * @returns The CSRF token or null if not found
 */
const getCsrfTokenFromCookie = (): string | null => {
  // Find the XSRF-TOKEN cookie
  const cookies = document.cookie.split(';');
  for (let cookie of cookies) {
    const [name, value] = cookie.trim().split('=');
    if (name === 'XSRF-TOKEN') {
      return decodeURIComponent(value);
    }
  }
  return null;
};

/**
 * The Meth Snail's CSRF-Protected Fetch
 * Ensures all requests have proper CSRF protection
 */
export async function fetchWithCsrf<T = any>(
  endpoint: string, 
  options: AxiosRequestConfig = {}
): Promise<AxiosResponse<T>> {
  // Ensure we have headers
  options.headers = options.headers || {};
  
  // Include credentials for cookies
  options.withCredentials = true;
  
  // Get CSRF token from cookie
  const csrfToken = getCsrfTokenFromCookie();
  
  // Add CSRF token header if available
  if (csrfToken) {
    options.headers['X-CSRFToken'] = csrfToken;
    console.log("🦔 Sir Hawkington: Adding CSRF token to request");
  } else {
    console.warn("🧙‍♂️ The Stick warns: No CSRF token found in cookies!");
  }

  // Construct full URL
  const url = endpoint.startsWith('http') 
    ? endpoint 
    : `${API_URL}${endpoint.startsWith('/') ? endpoint : '/' + endpoint}`;

  try {
    console.log("🐌 The Meth Snail: Making request to", url);
    const response = await axios<T>(url, options);
    console.log("🐹 Hamsters report: Request successful!");
    return response;
  } catch (error) {
    console.error("💥 VIC-20 crashed during request:", error);
    throw error;
  }
}

/**
 * Initialize CSRF protection
 * Should be called during app initialization
 */
export async function initializeCsrf(): Promise<boolean> {
  console.log("🦔 Sir Hawkington: Initializing CSRF protection...");
  
  try {
    // Get CSRF token from backend
    const response = await axios.get(`${API_URL}/api/auth/csrf_token`, {
      withCredentials: true,
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
      },
      params: {
        _t: Date.now() // Prevent caching
      }
    });
    
    if (response.data && response.data.csrf_token) {
      console.log("🎉 The VIC-20 celebrates! CSRF token obtained successfully");
      return true;
    }
    
    console.warn("🧙‍♂️ The Stick is concerned: CSRF response had no token");
    return false;
  } catch (error) {
    console.error("🧙‍♂️ The Stick says: CSRF initialization failed!", error);
    return false;
  }
}

/**
 * Direct CSRF token fetch (for debugging or manual refreshing)
 */
export async function refreshCsrfToken(): Promise<string | null> {
  console.log("🐌 The Meth Snail: Refreshing CSRF token...");
  
  try {
    const response = await axios.get(`${API_URL}/api/auth/csrf_token`, {
      withCredentials: true,
      headers: {
        'Cache-Control': 'no-cache, no-store, must-revalidate',
        'Pragma': 'no-cache',
        'Expires': '0'
      }
    });
    
    if (response.data && response.data.csrf_token) {
      const token = response.data.csrf_token;
      console.log("🦔 Sir Hawkington: CSRF token refreshed successfully!");
      return token;
    }
    
    console.warn("🧙‍♂️ The Stick warns: No CSRF token in response");
    return null;
  } catch (error) {
    console.error("💥 VIC-20 crashed during CSRF refresh:", error);
    return null;
  }
}

// Set up axios interceptor to add CSRF token to all requests
axios.interceptors.request.use(async config => {
  // Skip for CSRF token requests to avoid circular dependency
  if (config.url && config.url.includes('/api/auth/csrf_token')) {
    return config;
  }
  
  const token = getCsrfTokenFromCookie();
  if (token) {
    config.headers = config.headers || {};
    config.headers['X-CSRFToken'] = token;
  }
  
  return config;
});

export default fetchWithCsrf;