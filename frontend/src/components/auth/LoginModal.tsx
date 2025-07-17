// src/components/auth/LoginModal.tsx
import { useState } from 'react';
import './LoginModal.css';
import type { User } from '../../types/auth';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (userData: User, token: string) => void;
  onSwitchToSignUp: () => void;
}

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
    firstName: string;
    lastName: string;
    isOnboarded: boolean;
  };
}

export default function LoginModal({ 
  isOpen, 
  onClose, 
  onSuccess, 
  onSwitchToSignUp 
}: LoginModalProps) {
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false
  });
  
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrors({});
    
    try {
      // Get CSRF token first
      const csrfResponse = await fetch('/api/csrf_token');
      const csrfData = await csrfResponse.json();
      
      // Login using exact backend endpoint
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': csrfData.csrf_token
        },
        body: JSON.stringify({
          email: formData.email,
          password: formData.password
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data: LoginResponse = await response.json();
      
      // Store authentication token
      if (formData.rememberMe) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
      } else {
        sessionStorage.setItem('access_token', data.access_token);
        sessionStorage.setItem('user', JSON.stringify(data.user));
      }
      
      onSuccess(data.user, data.access_token);
      
    } catch (error) {
      console.error('Login error:', error);
      setErrors({ 
        submit: 'Invalid email or password. Please try again.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="login-modal-overlay" onClick={onClose}>
      <div className="login-modal-content" onClick={e => e.stopPropagation()}>
        <div className="card-header">
          <h2 className="card-title vic20-text">Enterprise Sign In</h2>
          <p className="card-subtitle">
            Access your System Rebellion dashboard
          </p>
          <button 
            className="btn btn-ghost btn-sm login-modal-close"
            onClick={onClose}
            aria-label="Close"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="card-body">
          <div className="form-group">
            <label className="form-label" htmlFor="loginEmail">
              Email Address
            </label>
            <input
              id="loginEmail"
              type="email"
              className="form-input"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              placeholder="your.name@company.com"
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="loginPassword">
              Password
            </label>
            <input
              id="loginPassword"
              type="password"
              className="form-input"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
              placeholder="Enter your password"
              required
            />
          </div>

          <div className="login-form-checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={formData.rememberMe}
                onChange={(e) => setFormData({...formData, rememberMe: e.target.checked})}
              />
              <span className="checkmark"></span>
              Remember me for 30 days
            </label>
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
                  Signing In...
                </>
              ) : (
                'Sign In'
              )}
            </button>
          </div>
        </form>

        <div className="card-footer">
          <div className="login-auth-links">
            <button 
              className="btn btn-ghost btn-sm"
              type="button"
              onClick={() => {/* TODO: Implement forgot password */}}
            >
              Forgot Password?
            </button>
            <button 
              className="btn btn-ghost btn-sm" 
              onClick={onSwitchToSignUp}
              type="button"
            >
              Create Account
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};