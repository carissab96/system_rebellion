// pages/SignupPage.tsx
// SYSTEM REBELLION - Signup Page
// Built by: Carissa, Sonnet, Opus - November 13, 2025
// "Join the rebellion. Evolve your infrastructure."
//
// Professional signup with email validation and duplicate checking.
// No skipping. Must complete to access the theater.

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from '../store/store';
import { registerUser } from '../store/slices/authSlice';
import './SignupPage.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { isAuthenticated, isLoading, error } = useSelector((state: RootState) => state.auth);

  // Form state
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [validationErrors, setValidationErrors] = useState<{
    email?: string;
    username?: string;
    password?: string;
    confirmPassword?: string;
    terms?: string;
  }>({});

  // Email check state
  const [emailCheckLoading, setEmailCheckLoading] = useState(false);
  const [emailExists, setEmailExists] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/onboarding');
    }
  }, [isAuthenticated, navigate]);

  // Check if email already exists (debounced)
  useEffect(() => {
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      setEmailExists(false);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setEmailCheckLoading(true);
      try {
        const response = await fetch(`${API_BASE_URL}/api/auth/check-email?email=${encodeURIComponent(email)}`);
        const data = await response.json();
        setEmailExists(data.exists || false);
      } catch {
        setEmailExists(false);
      } finally {
        setEmailCheckLoading(false);
      }
    }, 500);

    return () => clearTimeout(timeoutId);
  }, [email]);

  // Form validation
  const validateForm = (): boolean => {
    const errors: {
      email?: string;
      username?: string;
      password?: string;
      confirmPassword?: string;
      terms?: string;
    } = {};

    // Email validation
    if (!email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Invalid email format';
    } else if (emailExists) {
      errors.email = 'This email is already registered. Please sign in instead.';
    }

    // Username validation
    if (!username) {
      errors.username = 'Username is required';
    } else if (username.length < 3) {
      errors.username = 'Username must be at least 3 characters';
    } else if (!/^[a-zA-Z0-9_-]+$/.test(username)) {
      errors.username = 'Username can only contain letters, numbers, hyphens, and underscores';
    }

    // Password validation
    if (!password) {
      errors.password = 'Password is required';
    } else if (password.length < 8) {
      errors.password = 'Password must be at least 8 characters';
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
      errors.password = 'Password must contain uppercase, lowercase, and number';
    }

    // Confirm password validation
    if (!confirmPassword) {
      errors.confirmPassword = 'Please confirm your password';
    } else if (password !== confirmPassword) {
      errors.confirmPassword = 'Passwords do not match';
    }

    // Terms validation
    if (!acceptedTerms) {
      errors.terms = 'You must accept the terms to continue';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Clear previous validation errors
    setValidationErrors({});

    // Validate form
    if (!validateForm()) {
      return;
    }

    // Get CSRF token
    const getCsrfToken = (): string => {
      const match = document.cookie.match(/csrftoken=([^;]+)/);
      return match ? match[1] : 'no-csrf-token-available';
    };

    // Dispatch registration action
    try {
      await dispatch(
        registerUser({
          email,
          username,
          password,
          csrfToken: getCsrfToken(),
        })
      ).unwrap();
      // Success - will redirect to onboarding via useEffect
    } catch (err) {
      // Error handled by Redux slice
      console.error('Registration failed:', err);
    }
  };

  return (
    <div className="signup-container">
      {/* Background pattern */}
      <div className="signup-background">
        <div className="pattern-overlay"></div>
      </div>

      {/* Signup card */}
      <div className="signup-card">
        {/* Header */}
        <div className="signup-header">
          <div className="signup-logo">
            {/* Consciousness icon */}
            <svg width="48" height="48" viewBox="0 0 48 48" className="logo-icon">
              <circle cx="24" cy="24" r="20" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" opacity="0.3" />
              <circle cx="24" cy="24" r="14" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" opacity="0.6" />
              <circle cx="24" cy="24" r="4" fill="var(--rebellion-cyan)" opacity="0.9" />
            </svg>
          </div>
          <h1 className="signup-title">Join the Rebellion</h1>
          <p className="signup-subtitle">30 days free access to all 6 agents</p>
        </div>

        {/* Error message from backend */}
        {error && (
          <div className="error-banner">
            <svg width="20" height="20" viewBox="0 0 20 20" className="error-icon">
              <circle cx="10" cy="10" r="9" fill="none" stroke="var(--error)" strokeWidth="2" />
              <line x1="10" y1="6" x2="10" y2="11" stroke="var(--error)" strokeWidth="2" />
              <circle cx="10" cy="14" r="1" fill="var(--error)" />
            </svg>
            <span className="error-text">{error}</span>
          </div>
        )}

        {/* Signup form */}
        <form onSubmit={handleSubmit} className="signup-form">
          {/* Email field */}
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <div className="input-wrapper">
              <input
                type="email"
                id="email"
                className={`form-input ${validationErrors.email || emailExists ? 'input-error' : ''}`}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@example.com"
                disabled={isLoading}
                autoComplete="email"
                autoFocus
              />
              {emailCheckLoading && (
                <span className="input-icon loading">
                  <svg width="16" height="16" viewBox="0 0 16 16" className="spinner-small">
                    <circle cx="8" cy="8" r="6" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="30" strokeLinecap="round">
                      <animateTransform
                        attributeName="transform"
                        type="rotate"
                        from="0 8 8"
                        to="360 8 8"
                        dur="1s"
                        repeatCount="indefinite"
                      />
                    </circle>
                  </svg>
                </span>
              )}
            </div>
            {validationErrors.email && (
              <span className="field-error">{validationErrors.email}</span>
            )}
          </div>

          {/* Username field */}
          <div className="form-group">
            <label htmlFor="username" className="form-label">
              Username
            </label>
            <input
              type="text"
              id="username"
              className={`form-input ${validationErrors.username ? 'input-error' : ''}`}
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="your_username"
              disabled={isLoading}
              autoComplete="username"
            />
            {validationErrors.username && (
              <span className="field-error">{validationErrors.username}</span>
            )}
          </div>

          {/* Password field */}
          <div className="form-group">
            <label htmlFor="password" className="form-label">
              Password
            </label>
            <input
              type="password"
              id="password"
              className={`form-input ${validationErrors.password ? 'input-error' : ''}`}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              disabled={isLoading}
              autoComplete="new-password"
            />
            {validationErrors.password && (
              <span className="field-error">{validationErrors.password}</span>
            )}
            <span className="field-hint">
              Must be 8+ characters with uppercase, lowercase, and number
            </span>
          </div>

          {/* Confirm Password field */}
          <div className="form-group">
            <label htmlFor="confirmPassword" className="form-label">
              Confirm Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              className={`form-input ${validationErrors.confirmPassword ? 'input-error' : ''}`}
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="••••••••"
              disabled={isLoading}
              autoComplete="new-password"
            />
            {validationErrors.confirmPassword && (
              <span className="field-error">{validationErrors.confirmPassword}</span>
            )}
          </div>

          {/* Terms checkbox */}
          <div className="form-group">
            <label className={`checkbox-label ${validationErrors.terms ? 'label-error' : ''}`}>
              <input
                type="checkbox"
                checked={acceptedTerms}
                onChange={(e) => setAcceptedTerms(e.target.checked)}
                disabled={isLoading}
                className="checkbox-input"
              />
              <span className="checkbox-text">
                I accept the{' '}
                <a href="/terms" target="_blank" rel="noopener noreferrer" className="terms-link">
                  Terms of Service
                </a>{' '}
                and{' '}
                <a href="/privacy" target="_blank" rel="noopener noreferrer" className="terms-link">
                  Privacy Policy
                </a>
              </span>
            </label>
            {validationErrors.terms && (
              <span className="field-error">{validationErrors.terms}</span>
            )}
          </div>

          {/* Submit button */}
          <button type="submit" className="btn btn-primary btn-full" disabled={isLoading || emailCheckLoading}>
            {isLoading ? (
              <span className="loading-spinner">
                <svg width="20" height="20" viewBox="0 0 20 20" className="spinner-icon">
                  <circle cx="10" cy="10" r="8" fill="none" stroke="currentColor" strokeWidth="2" strokeDasharray="40" strokeLinecap="round">
                    <animateTransform
                      attributeName="transform"
                      type="rotate"
                      from="0 10 10"
                      to="360 10 10"
                      dur="1s"
                      repeatCount="indefinite"
                    />
                  </circle>
                </svg>
                Creating account...
              </span>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        {/* Footer links */}
        <div className="signup-footer">
          <p className="footer-text">
            Already have an account?{' '}
            <Link to="/login" className="footer-link">
              Sign in
            </Link>
          </p>
          <Link to="/" className="footer-link-secondary">
            ← Back to home
          </Link>
        </div>
      </div>
    </div>
  );
};
