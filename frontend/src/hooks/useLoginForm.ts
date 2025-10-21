// src/hooks/useLoginForm.ts
import { useState, useEffect, useRef } from 'react';

import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

import * as authSlice from '../store/slices/authSlice';
import { type RootState, type AppDispatch } from '../store/store';

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    is_onboarded: boolean;
  };
}

export const useLoginForm = (isOpen: boolean, onClose: () => void) => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { isLoading, error, csrfToken } = useSelector((state: RootState) => state.auth);
  
  // Ref to track if we've already fetched CSRF for this modal session
  const csrfFetchedRef = useRef(false);



  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false
  });

  const [localErrors, setLocalErrors] = useState<Partial<Record<keyof LoginFormData, string>>>({});

  // Fetch CSRF token & clear errors when modal opens
  useEffect(() => {
    if (isOpen) {
      // Only fetch CSRF if we don't have one AND haven't already fetched in this session
      if (!csrfToken && !csrfFetchedRef.current) {
        csrfFetchedRef.current = true;
        dispatch(authSlice.fetchCsrfToken()).catch(() => {
          // Errors are handled in redux so we don't need to do anything here
        });
      }
      dispatch(authSlice.clearError());
      setLocalErrors({});
      // Reset form when modal opens
      setFormData({
        email: '',
        password: '',
        rememberMe: false
      });
    } else {
      // Reset the ref when modal closes so next open can fetch if needed
      csrfFetchedRef.current = false;
    }
  }, [isOpen, csrfToken, dispatch]); // Added back csrfToken and isLoading for proper logic

  const handleInputChange = (field: keyof LoginFormData, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear field error when user types
    if (localErrors[field]) {
      setLocalErrors(prev => ({ ...prev, [field]: undefined }));
    }
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof LoginFormData, string>> = {};
    
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      newErrors.email = 'Please enter a valid email';
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required';
    }

    setLocalErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (isLoading || !validateForm()) {
      return;
    }

    try {
      const currentCsrfToken = csrfToken || "";

      const response = await fetch('/api/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': currentCsrfToken,
          'Accept': 'application/json'
        },
        body: new URLSearchParams({
          username: formData.email.trim(),
          password: formData.password.trim(),
          grant_type: 'password'
        }),
        credentials: 'include'
      });
      
      if (!response.ok) {
        let errorData;
        const contentType = response.headers.get('content-type');
        
        try {
          errorData = contentType?.includes('application/json') 
            ? await response.json()
            : await response.text();
        } catch (e) {
          errorData = response.statusText;
        }
        
        console.error('Login failed:', {
          status: response.status,
          statusText: response.statusText,
          error: errorData,
          headers: Object.fromEntries(response.headers.entries())
        });
        
        throw new Error(
          typeof errorData === 'object' 
            ? errorData.detail || 'Authentication failed'
            : 'Authentication failed. Please try again.'
        );
      }
      
      const data = await response.json();
      if (!data.access_token) {
        throw new Error('No access token received');
      }
      
      // Store tokens and user data
      dispatch(authSlice.loginSuccess({ 
        user: data.user, 
        token: data.access_token 
      }));
      
      // Store tokens securely (consider using httpOnly cookies instead)
      if (data.refresh_token) {
        localStorage.setItem('refresh_token', data.refresh_token);
      }
      
      // Dispatch login success
      // dispatch(authSlice.loginSuccess({ 
      //   user: data.user, 
      //   token: data.access_token 
      // }));
      
      // Close modal first
      onClose();
      
      // Navigate based on onboarding status
      if (data.user.is_onboarded) {
        navigate('/agent-theater');
      } else {
        navigate('/onboarding');
      }
      
    } catch (error) {
      console.error('Login error:', error);
      // Extract and display the actual error message from the backend
      let errorMessage = 'An error occurred during login. Please try again.';
      
      if (error instanceof Error) {
        // Use the error message from the backend
        errorMessage = error.message;
      }
      
      dispatch(authSlice.setError(errorMessage));
    }
  };

  return {
    formData,
    isLoading,
    displayError: error || Object.values(localErrors)[0],
    localErrors,
    handleInputChange,
    handleSubmit
  };
};