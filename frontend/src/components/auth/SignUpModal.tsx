// src/components/auth/SignUpModal.tsx
import React, { useState } from 'react';
import './SignUpModal.css';
import type { User } from '../../types/auth';

interface SignUpModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (user: User, token: string) => void;
  onSwitchToLogin: () => void;
}

interface SignUpFormData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  confirmPassword: string;
  companyName: string;
  jobTitle: string;
}

interface SignUpResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    first_name: string;
    last_name: string;
    is_onboarded: boolean;
    company_name?: string;
    job_title?: string;
  };
}

export default function SignUpModal({ isOpen, onClose, onSuccess, onSwitchToLogin }: SignUpModalProps) {
  const [formData, setFormData] = useState<SignUpFormData>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    companyName: '',
    jobTitle: ''
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [passwordStrength, setPasswordStrength] = useState(0);

  if (!isOpen) return null;

  const validateForm = (): Record<string, string> => {
    const newErrors: Record<string, string> = {};
    
    // Enterprise validation rules
    if (!formData.firstName.trim() || formData.firstName.length < 2) {
      newErrors.firstName = 'First name must be at least 2 characters';
    }
    
    if (!formData.lastName.trim() || formData.lastName.length < 2) {
      newErrors.lastName = 'Last name must be at least 2 characters';
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
    
    if (!/(?=.*[!@#$%^&*()_+\-=\n\${};':"\\|,.<>\/?])/.test(formData.password)) {
      newErrors.password = 'Password must contain at least one special character';
    }
    
    if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    
    if (!formData.companyName.trim()) {
      newErrors.companyName = 'Company name is required';
    }
    
    return newErrors;
  };

  const calculatePasswordStrength = (password: string): number => {
    let strength = 0;
    if (password.length >= 8) strength += 1;
    if (/(?=.*[a-z])/.test(password)) strength += 1;
    if (/(?=.*[A-Z])/.test(password)) strength += 1;
    if (/(?=.*\d)/.test(password)) strength += 1;
    if (/(?=.*[!@#$%^&*()_+\-=\n\${};':"\\|,.<>\/?])/.test(password)) strength += 1;
    return strength;
  };

  const handlePasswordChange = (password: string) => {
    setFormData({...formData, password});
    setPasswordStrength(calculatePasswordStrength(password));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Set loading state and clear errors at START
    setIsSubmitting(true);
    setErrors({});
    
    // Client-side validation FIRST
    const validationErrors = validateForm();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      setIsSubmitting(false);
      return;
    }

    try {
      // ✅ FIXED: Use your exact backend endpoint for CSRF
      const csrfResponse = await fetch('/api/auth/csrf_token', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!csrfResponse.ok) {
        throw new Error('Failed to get CSRF token');
      }
      
      const csrfData = await csrfResponse.json();
      
      // ✅ FIXED: Use your exact backend endpoint for registration
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrfData.csrf_token
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password,
          first_name: formData.firstName,
          last_name: formData.lastName,
          company_name: formData.companyName,
          job_title: formData.jobTitle || null
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Registration failed');
      }

      const data: SignUpResponse = await response.json();
      
      // Transform backend response to frontend User type
      const userData: User = {
        id: data.user.id,
        email: data.user.email,
        firstName: data.user.first_name,
        lastName: data.user.last_name,
        isOnboarded: data.user.is_onboarded || false,
        companyName: data.user.company_name,
        jobTitle: data.user.job_title
      };
      
      // Call onSuccess with user data AND token
      onSuccess(userData, data.access_token);
      
    } catch (error) {
      console.error('Registration error:', error);
      if (!(error instanceof Error)) {
        throw new Error(`An unexpected error occurred: ${error}`);
      }
      setErrors({
        submit: error.message
      });
    } finally {
      setIsSubmitting(false);
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

  return (
    <div className="signup-modal-overlay" onClick={onClose}>
      <div className="signup-modal-content" onClick={e => e.stopPropagation()}>
        <div className="card-header">
          <h2 className="card-title vic20-text">Create Enterprise Account</h2>
          <p className="card-subtitle">
            Join System Rebellion for enterprise AI agent coordination
          </p>
          <button 
            className="btn btn-ghost btn-sm signup-modal-close"
            onClick={onClose}
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="card-body">
          <div className="signup-form-grid">
            <div className="form-group">
              <label className="form-label" htmlFor="firstName">
                First Name
              </label>
              <input
                id="firstName"
                type="text"
                className={`form-input ${errors.firstName ? 'error' : ''}`}
                value={formData.firstName}
                onChange={(e) => setFormData({...formData, firstName: e.target.value})}
                placeholder="Enter your first name"
                disabled={isSubmitting}
                required
              />
              {errors.firstName && (
                <span className="form-error">{errors.firstName}</span>
              )}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="lastName">
                Last Name
              </label>
              <input
                id="lastName"
                type="text"
                className={`form-input ${errors.lastName ? 'error' : ''}`}
                value={formData.lastName}
                onChange={(e) => setFormData({...formData, lastName: e.target.value})}
                placeholder="Enter your last name"
                disabled={isSubmitting}
                required
              />
              {errors.lastName && (
                <span className="form-error">{errors.lastName}</span>
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
              className={`form-input ${errors.email ? 'error' : ''}`}
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              placeholder="your.name@company.com"
              disabled={isSubmitting}
              required
            />
            {errors.email && (
              <span className="form-error">{errors.email}</span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="companyName">
              Company Name
            </label>
            <input
              id="companyName"
              type="text"
              className={`form-input ${errors.companyName ? 'error' : ''}`}
              value={formData.companyName}
              onChange={(e) => setFormData({...formData, companyName: e.target.value})}
              placeholder="Your organization"
              disabled={isSubmitting}
              required
            />
            {errors.companyName && (
              <span className="form-error">{errors.companyName}</span>
            )}
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="jobTitle">
              Job Title (Optional)
            </label>
            <input
              id="jobTitle"
              type="text"
              className="form-input"
              value={formData.jobTitle}
              onChange={(e) => setFormData({...formData, jobTitle: e.target.value})}
              placeholder="Your role"
              disabled={isSubmitting}
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
                className={`form-input ${errors.password ? 'error' : ''}`}
                value={formData.password}
                onChange={(e) => handlePasswordChange(e.target.value)}
                placeholder="8+ characters required"
                disabled={isSubmitting}
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
              {errors.password && (
                <span className="form-error">{errors.password}</span>
              )}
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="confirmPassword">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                className={`form-input ${errors.confirmPassword ? 'error' : ''}`}
                value={formData.confirmPassword}
                onChange={(e) => setFormData({...formData, confirmPassword: e.target.value})}
                placeholder="Confirm password"
                disabled={isSubmitting}
                required
              />
              {errors.confirmPassword && (
                <span className="form-error">{errors.confirmPassword}</span>
              )}
            </div>
          </div>

          {errors.submit && (
            <div className="alert alert-error">
              {errors.submit}
            </div>
          )}

          <div className="signup-form-actions">
            <button
              type="submit"
              className="btn btn-primary btn-lg"
              disabled={isSubmitting}
            >
              {isSubmitting ? (
                <>
                  <span className="loading-spinner"></span>
                  Creating Account...
                </>
              ) : (
                'Create Enterprise Account'
              )}
            </button>
          </div>
        </form>

        <div className="card-footer">
          <p className="text-center">
            Already have an account?{' '}
            <button 
              className="btn btn-ghost btn-sm" 
              onClick={onSwitchToLogin}
              type="button"
              disabled={isSubmitting}
            >
              Sign In
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}