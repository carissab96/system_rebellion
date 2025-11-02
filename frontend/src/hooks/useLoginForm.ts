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
      // Use Redux thunk which handles CSRF token coordination internally
      const resultAction = await dispatch(authSlice.loginUser({
        email: formData.email.trim(),
        password: formData.password.trim(),
        csrfToken: csrfToken || ""
      }));

      if (authSlice.loginUser.fulfilled.match(resultAction)) {
        // Success - close modal and navigate
        onClose();

        // Navigate based on onboarding status
        if (resultAction.payload.user.is_onboarded) {
          navigate('/system-ready');
        } else {
          navigate('/onboarding');
        }
      } else {
        // Error is handled by Redux, no need to do anything here
      }

    } catch (error) {
      console.error('Login error:', error);
      // Error is handled by Redux thunk
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