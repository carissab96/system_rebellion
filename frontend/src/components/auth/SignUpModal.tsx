// src/components/auth/SignUpModal.tsx
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './SignUpModal.css';
import { useDispatch, useSelector } from 'react-redux';
import { fetchCsrfToken, registerUser, clearError } from '../../store/slices/authSlice';
import type { RootState, AppDispatch } from '../../store';

interface SignUpModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToLogin: () => void;
}

interface SignUpFormData {
  first_name: string; // Fixed: was first_Name
  last_name: string;
  email: string;
  password: string;
  confirmPassword: string;
  company_name: string;
  job_title: string;
  username: string; // Added: backend expects username
}

export default function SignUpModal({ isOpen, onClose, onSwitchToLogin }: SignUpModalProps) {
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
    username: '' // Will be generated from email
  });
  
  const [localErrors, setLocalErrors] = useState<Record<string, string>>({});
  const [passwordStrength, setPasswordStrength] = useState(0);

  // Fetch CSRF token when modal opens
  useEffect(() => {
    if (isOpen && !csrfToken) {
      dispatch(fetchCsrfToken());
    }
  }, [isOpen, csrfToken, dispatch]);

  // Clear errors when modal opens
  useEffect(() => {
    if (isOpen) {
      dispatch(clearError());
      setLocalErrors({});
    }
  }, [isOpen, dispatch]);

  // Generate username from email
  useEffect(() => {
    if (formData.email) {
      const username = formData.email.split('@')[0];
      setFormData(prev => ({ ...prev, username }));
    }
  }, [formData.email]);

  if (!isOpen) return null;

  const validateForm = (): Record<string, string> => {
    const newErrors: Record<string, string> = {};
    
    // Enterprise validation rules
    if (!formData.first_name.trim() || formData.first_name.length < 2) {
      newErrors.first_name = 'First name must be at least 2 characters';
    }
    
    if (!formData.last_name.trim() || formData.last_name.length < 2) {
      newErrors.last_name = 'Last name must be at least 2 characters';
    }
    
    if (!formData.email.match(/^[^\s@]+@[^\s@]+\.[^\s@]+$/)) {
      newErrors.email = 'Valid email address is required';
    }
    
    if (formData.password.length < 8) {
      newErrors.password = 'Password must be at least 8 characters';
    }
    
    if (!/(?=.*[a-z])/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one lowercase letter';
    }
    
    if (!/(?=.*[A-Z])/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one uppercase letter';
    }
    
    if (!/(?=.*\d)/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one number';
    }
    
    if (!/(?=.*[!@#$%^&*()_+\-=
$$

$${};':"\\|,.<>\/?])/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one special character';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    if (!formData.company_name.trim()) {
      newErrors.company_name = 'Company name is required';
    }
    
    return newErrors;
  };

  const calculatePasswordStrength = (password: string): number => {
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/(?=.*[a-z])/.test(password)) strength += 1;
    if (/(?=.*[A-Z])/.test(password)) strength += 1;
    if (/(?=.*\d)/.test(password)) strength += 1;
    if (/(?=.*[!@#$%^&*()_+\-=
$$

$${};':"\\|,.<>\/?])/.test(password)) strength += 1;
    return strength;
  };

  const handlePasswordChange = (password: string) => {
    setFormData({...formData, password});
    setPasswordStrength(calculatePasswordStrength(password));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLocalErrors({});
    
    // Client-side validation
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setLocalErrors(validationErrors);
      return;
    }

    if (!csrfToken) {
      setLocalErrors({ submit: 'Security token not available. Please refresh and try again.' });
      return;
    }

    try {
      // Use the registerUser thunk from auth slice
      const result = await dispatch(registerUser({
        email: formData.email,
        username: formData.username,
        password: formData.password,
        csrfToken
      })).unwrap();
      
      // Close modal
      onClose();
      
      // New users always go to onboarding
      navigate('/onboarding');
      
    } catch (error) {
      // Error is already in Redux store
      console.error('Registration error:', error);
    }
  };

  const getStrengthColor = () => {
    switch (passwordStrength) {
      case 0:
      case 1: return 'signup-strength-weak';
      case 2: return 'signup-strength-fair';
      case 3:
      case 4: return 'signup-strength-good';
      case 5: return 'signup-strength-strong';
      default: return 'signup-strength-weak';
    }
  };

  const getStrengthText = () => {
    switch (passwordStrength) {
      case 0:
      case 1: return 'Weak';
      case 2: return 'Fair';
      case 3:
      case 4: return 'Good';
      case 5: return 'Strong';
      default: return 'Weak';
    }
  };

  // Combine Redux error and local errors
  const displayError = error || localErrors.submit;
  
  return (
    <div className="signup-modal-overlay" onClick={onClose}>
      <div className="signup-modal-content" onClick={e => e.stopPropagation()}>
        <button className="signup-modal-close" onClick={onClose}>
          &times;
        </button>
        <h2>Create Enterprise Account</h2>
        <p className="subtitle">Join System Rebellion for enterprise AI agent coordination</p>
        <form onSubmit={handleSubmit} className="card-body">
          {displayError && (
            <div className="alert alert-error">
              {displayError}
            </div>
          )}
          
          <div className="signup-form-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="first_name">
                First Name
              </label>
              <input
                id="first_name"
                type="text"
                className={`form-input ${localErrors.first_name ? 'error' : ''}`}
                value={formData.first_name}
                onChange={(e) => setFormData({...formData, first_name: e.target.value})}
                placeholder="Enter your first name"
                disabled={isLoading}
                required
              />
              {localErrors.first_name && (
                <span className="form-error">{localErrors.first_name}</span>
              )}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="last_name">
                Last Name
              </label>
              <input
                id="last_name"
                type="text"
                className={`form-input ${localErrors.last_name ? 'error' : ''}`}
                value={formData.last_name}
                onChange={(e) => setFormData({...formData, last_name: e.target.value})}
                placeholder="Enter your last name"
                disabled={isLoading}
                required
              />
              {localErrors.last_name && (
                <span className="form-error">{localErrors.last_name}</span>
              )}
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="email">
              Email Address
            </label>
            <input
              id="email"
              type="email"
              className={`form-input ${localErrors.email ? 'error' : ''}`}
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              placeholder="your.name@company.com"
              disabled={isLoading}
              required
            />
            {localErrors.email && (
              <span className="form-error">{localErrors.email}</span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="company_name">
              Company Name
            </label>
            <input
              id="company_name"
              type="text"
              className={`form-input ${localErrors.company_name ? 'error' : ''}`}
              value={formData.company_name}
              onChange={(e) => setFormData({...formData, company_name: e.target.value})}
              placeholder="Your organization"
              disabled={isLoading}
              required
            />
            {localErrors.company_name && (
              <span className="form-error">{localErrors.company_name}</span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="job_title">
              Job Title (Optional)
            </label>
            <input
              id="job_title"
              type="text"
              className="form-input"
              value={formData.job_title}
              onChange={(e) => setFormData({...formData, job_title: e.target.value})}
              placeholder="Your role"
              disabled={isLoading}
            />
          </div>

          <div className="signup-form-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                type="password"
                className={`form-input ${localErrors.password ? 'error' : ''}`}
                value={formData.password}
                onChange={(e) => handlePasswordChange(e.target.value)}
                placeholder="8+ characters required"
                disabled={isLoading}
                required
              />
              {formData.password && (
                <div className="signup-password-strength">
                  <div className="signup-strength-bar">
                    <div className={`signup-strength-fill ${getStrengthColor()}`}></div>
                  </div>
                  <span className="text-sm">Strength: {getStrengthText()}</span>
                </div>
              )}
              {localErrors.password && (
                <span className="form-error">{localErrors.password}</span>
              )}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                className={`form-input ${localErrors.confirmPassword ? 'error' : ''}`}
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                placeholder="Confirm password"
                disabled={isLoading}
                required
              />
              {localErrors.confirmPassword && (
                <span className="form-error">{localErrors.confirmPassword}</span>
              )}
            </div>
          </div>

          <div className="signup-actions">
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={onClose}
              disabled={isLoading}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={isLoading}
            >
              {isLoading ? 'Creating Account...' : 'Create User Account'}
            </button>
          </div>
          
          <div className="auth-switch">
            <p className="text-center">
              Already have an account?{' '}
              <button 
                type="button"
                className="text-link"
                onClick={onSwitchToLogin}
                disabled={isLoading}
              >
                Sign In
              </button>
            </p>
          </div>
        </form>
      </div>
    </div>
  );
