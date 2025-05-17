import Cookies from 'js-cookie';
import { Middleware } from '@reduxjs/toolkit';

// Define more specific types
export interface CustomHeaders {
  [key: string]: string | undefined; // Allow for other header keys
}

export interface CustomOptions extends Omit<RequestInit, 'headers'> {
  headers?: CustomHeaders;
  credentials?: RequestCredentials;
}

export async function fetchWithCsrf(url: URL | RequestInfo, options: CustomOptions = {}) {
  const csrfToken = Cookies.get('XSRF-TOKEN');
  
  const defaultOptions: CustomOptions = {
    method: 'GET',
    headers: {},
    credentials: 'include'
  };

  // Merge options with proper typing
  const mergedOptions: CustomOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
      ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {})
    }
  };

  // Now TypeScript knows about the possible header keys
  if (mergedOptions.method?.toUpperCase() !== 'GET') {
    if (mergedOptions.headers) {
      mergedOptions.headers['Content-Type'] = 
        mergedOptions.headers['Content-Type'] || 'application/json';
    }
  }

  try {
    console.log('Fetching', url, 'with options', mergedOptions);
    const response = await fetch(url, mergedOptions as RequestInit);
    console.log('Response:', response);
    return response;
  } catch (error) {
    console.error('Network error:', error);
    throw new Error('Network error. Please check your connection.');
  }
}

const xsrfMiddleware: Middleware = () => next => (action: any) => {
  if (action.type.startsWith('auth/')) {
    const csrfToken = Cookies.get('XSRF-TOKEN');
    // Check if action.payload exists and is an object before trying to add headers
    if (csrfToken && action.payload && typeof action.payload === 'object') {
      action.payload.headers = {
        ...action.payload.headers,
        'X-CSRFToken': csrfToken
      } as CustomHeaders;
    }
  }
  return next(action);
};
export async function restoreCSRF() {
  try {
    console.log('🧐 Sir Hawkington is attempting to restore the CSRF token...');
    // Corrected URL to match the backend endpoint
    const response = await fetchWithCsrf('/api/auth/csrf_token');
    
    if (!response.ok) {
      console.error('🚨 Failed to restore CSRF token, status:', response.status);
      throw new Error(`Failed to restore CSRF token: ${response.statusText}`);
    }
    
    // Extract the token from the response
    const data = await response.json();
    if (data && data.csrf_token) {
      // Manually set the cookie
      Cookies.set('XSRF-TOKEN', data.csrf_token, { path: '/' });
      console.log('✅ CSRF token successfully restored!');
    } else {
      console.error('🚨 CSRF token not found in response');
      throw new Error('CSRF token not found in response');
    }
    
    return response;
  } catch (error) {
    console.error('🚨 Error restoring CSRF token:', error);
    throw error;
  }
}

export default xsrfMiddleware;