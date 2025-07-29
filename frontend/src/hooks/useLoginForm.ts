// src/hooks/useLoginForm.ts
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import { type RootState, type AppDispatch } from '../store/store';
import * as authSlice from '../store/slices/authSlice';

interface LoginFormData {
  email: string;
  password: string;
  rememberMe: boolean;
}

interface LoginResponse {
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

  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false
  });

  const [localErrors, setLocalErrors] = useState<Partial<Record<keyof LoginFormData, string>>>({});

  // Fetch CSRF token & clear errors when modal opens
  useEffect(() => {
    if (isOpen) {
      if (!csrfToken) dispatch(authSlice.fetchCsrfToken());
      dispatch(authSlice.clearError());
      setLocalErrors({});
      // Reset form when modal opens
      setFormData({
        email: '',
        password: '',
        rememberMe: false
      });
    }
  }, [isOpen, csrfToken, dispatch]);

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
    if (isLoading || !validateForm()) return;

    try {
      // Ensure we have CSRF token
      if (!csrfToken) {
        await dispatch(authSlice.fetchCsrfToken()).unwrap();
      }

      // Make login request
      const response = await fetch('/api/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfToken!
        },
        body: new URLSearchParams({
          username: formData.email,
          password: formData.password,
          grant_type: 'password'
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data: LoginResponse = await response.json();
      
      // Transform backend response to frontend User type
      const userData = {
        id: data.user.id,
        email: data.user.email,
        first_name: data.user.first_name,
        last_name: data.user.last_name,
        token: data.access_token,
        is_onboarded: data.user.is_onboarded
      };
      
      // Dispatch login success
      dispatch(authSlice.loginSuccess({ 
        user: userData, 
        token: data.access_token 
      }));
      
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
      // Set a user-friendly error message
      dispatch(authSlice.setError(
        error instanceof Error && error.message === 'Login failed' 
          ? 'Invalid email or password. Please try again.'
          : 'An error occurred during login. Please try again.'
      ));
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