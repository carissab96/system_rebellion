// src/hooks/useSignUpForm.ts
import { useState, useEffect } from 'react';

import { useDispatch, useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';

import * as authSlice from '../store/slices/authSlice';
import { type RootState, type AppDispatch } from '../store/store';


// Re-using the FormData type, can be moved to a types file
interface SignUpFormData {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  confirmPassword: string;
  company_name: string;
  job_title: string;
  username: string;
}

export const useSignUpForm = (isOpen: boolean, onClose: () => void) => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  const { isLoading, error, csrfToken } = useSelector((state: RootState) => state.auth);

  const [formData, setFormData] = useState<SignUpFormData>({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirmPassword: '',
    company_name: '',
    job_title: '',
    username: '',
  });
  
  const [localErrors, setLocalErrors] = useState<Partial<Record<keyof SignUpFormData, string>>>({});
  const [passwordStrength, setPasswordStrength] = useState(0);

  // Fetch CSRF token & clear errors when modal opens - STRICTMODE SAFE
  useEffect(() => {
    if (isOpen) {
      // Only fetch CSRF if we don't have one AND not currently loading
      if (!csrfToken && !isLoading) {
        dispatch(authSlice.fetchCsrfToken());
      }
      dispatch(authSlice.clearError());
      setLocalErrors({});
    }
  }, [isOpen, csrfToken, isLoading]); // ← Added isLoading to prevent double fetches

  // Generate username from email
  useEffect(() => {
    if (formData.email) {
      const username = formData.email.split('@')[0].replace(/[^a-zA-Z0-9]/g, '_');
      setFormData(prev => ({ ...prev, username }));
    }
  }, [formData.email]);
  
  const handleInputChange = (field: keyof SignUpFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (field === 'password') {
      setPasswordStrength(calculatePasswordStrength(value));
    }
  };

  const calculatePasswordStrength = (password: string): number => {
    let strength = 0;
    if (password.length >= 8) strength++;
    if (/(?=.*[a-z])/.test(password)) strength++;
    if (/(?=.*[A-Z])/.test(password)) strength++;
    if (/(?=.*\d)/.test(password)) strength++;
    if (/(?=.*[!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?])/.test(password)) strength++;
    return strength;
  };

  const validateForm = (): boolean => {
    const newErrors: Partial<Record<keyof SignUpFormData, string>> = {};
    if (formData.first_name.trim().length < 2) newErrors.first_name = 'First name required';
    if (formData.last_name.trim().length < 2) newErrors.last_name = 'Last name required';
    if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) newErrors.email = 'Valid email required';
    if (passwordStrength < 5) newErrors.password = 'Password does not meet all requirements';
    if (formData.password !== formData.confirmPassword) newErrors.confirmPassword = 'Passwords do not match';
    if (!formData.company_name.trim()) newErrors.company_name = 'Company name required';

    setLocalErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (isLoading || !validateForm()) return;
    try {
      await dispatch(authSlice.fetchCsrfToken()).unwrap();
    } catch (reduxError) {
      console.error('Failed to fetch CSRF token:', reduxError);
      dispatch(authSlice.setError('Failed to fetch CSRF token'));
    }
    
    try {
      await dispatch(authSlice.registerUser({
        username: formData.email,
        email: formData.email,
        password: formData.password,
        csrfToken: csrfToken!
      })).unwrap();
    } catch (reduxError) {
      console.error('Registration failed:', reduxError);
      dispatch(authSlice.setError('Registration failed'));
    }      
    onClose();
    navigate('/onboarding');
    
 
  };

  return {
    formData,
    isLoading,
    displayError: error || Object.values(localErrors)[0],
    localErrors,
    passwordStrength,
    handleInputChange,
    handleSubmit
  };
};