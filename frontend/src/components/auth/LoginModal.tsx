// src/components/auth/LoginModal.tsx
import { useState } from 'react';
import './LoginModal.css';
import type { User } from '../../types/auth';
import { useDispatch } from 'react-redux';
import { loginSuccess } from '../../store/slices/authSlice';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
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
    first_name: string;  // ✅ Fixed: backend sends snake_case
    last_name: string;   // ✅ Fixed: backend sends snake_case
    is_onboarded: boolean; // ✅ Fixed: backend sends snake_case
  };
}

function LoginModal({ 
  isOpen, 
  onClose, 
  onSwitchToSignUp 
}: LoginModalProps) {
  // ✅ HOOKS AT THE TOP LEVEL - BEFORE ANY CONDITIONALS
  const dispatch = useDispatch();
  const [formData, setFormData] = useState<LoginFormData>({
    email: '',
    password: '',
    rememberMe: false
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // ✅ EARLY RETURN AFTER HOOKS
  if (!isOpen) return null;
    
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setErrors({});
    
    try {
      // Get CSRF token first
      const csrfResponse = await fetch('/api/auth/csrf_token');
      const csrfData = await csrfResponse.json();
      
      // Login using exact backend endpoint
      const response = await fetch('/api/auth/token', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'X-CSRFToken': csrfData.csrf_token // ✅ Fixed: Use CSRFToken not CSRF-Token
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
      
      // ✅ Transform backend response to frontend User type
      const userData: User = {
        id: data.user.id,
        email: data.user.email,
        firstName: data.user.first_name,
        lastName: data.user.last_name,
        isOnboarded: data.user.is_onboarded
      };
      
      // ✅ DISPATCH WITH BOTH USER AND TOKEN
      dispatch(loginSuccess({ 
        user: userData, 
        token: data.access_token 
      }));
      
      // Close modal
      onClose();
      
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

export default LoginModal;

