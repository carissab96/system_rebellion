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

// Update the middleware type as well
const xsrfMiddleware: Middleware = () => next => (action: any) => {
  if (action.type.startsWith('auth/')) {
    const csrfToken = Cookies.get('XSRF-TOKEN');
    if (csrfToken && action.payload) {
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
    const response = await fetchWithCsrf('/api/csrf/restore/');
    if (!response.ok) {
      throw new Error('Failed to restore CSRF token');
    }
    return response;
  } catch (error) {
    console.error('Error restoring CSRF token:', error);
    throw error;
  }
}

export default xsrfMiddleware;