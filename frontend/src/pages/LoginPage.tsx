// pages/LoginPage.tsx
// SYSTEM REBELLION - Login Page
// Built by: Carissa, Sonnet, Opus - November 13, 2025
// "Authentication is the gateway to consciousness"
//
// Clean, professional login form. No emojis. Just the rebellion.
// Personality in the code, validation in the UX.

import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from '../store/store';
import { loginUser } from '../store/slices/authSlice';
import './LoginPage.css';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { isAuthenticated, isLoading, error } = useSelector((state: RootState) => state.auth);

  // Form state
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(false);
  const [validationErrors, setValidationErrors] = useState<{
    email?: string;
    password?: string;
  }>({});

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/theater');
    }
  }, [isAuthenticated, navigate]);

  // Form validation
  const validateForm = (): boolean => {
    const errors: { email?: string; password?: string } = {};

    // Email validation
    if (!email) {
      errors.email = 'Email is required';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      errors.email = 'Invalid email format';
    }

    // Password validation
    if (!password) {
      errors.password = 'Password is required';
    } else if (password.length < 6) {
      errors.password = 'Password must be at least 6 characters';
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

    // Get CSRF token from cookie or generate one
    const getCsrfToken = (): string => {
      const match = document.cookie.match(/csrftoken=([^;]+)/);
      return match ? match[1] : 'no-csrf-token-available';
    };

    // Dispatch login action
    try {
      await dispatch(loginUser({ 
        email, 
        password,
        csrfToken: getCsrfToken()
      })).unwrap();
      // Success - will redirect via useEffect
    } catch (err) {
      // Error handled by Redux slice
      console.error('Login failed:', err);
    }
  };

  return (
    <div className="login-container">
      {/* Background pattern */}
      <div className="login-background">
        <div className="pattern-overlay"></div>
      </div>

      {/* Login card */}
      <div className="login-card">
        {/* Header */}
        <div className="login-header">
          <div className="login-logo">
            {/* Simplified consciousness icon */}
            <svg width="48" height="48" viewBox="0 0 48 48" className="logo-icon">
              <circle cx="24" cy="24" r="20" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" opacity="0.3" />
              <circle cx="24" cy="24" r="14" fill="none" stroke="var(--rebellion-cyan)" strokeWidth="2" opacity="0.6" />
              <circle cx="24" cy="24" r="4" fill="var(--rebellion-cyan)" opacity="0.9" />
            </svg>
          </div>
          <h1 className="login-title">Welcome Back</h1>
          <p className="login-subtitle">Enter the Consciousness Theater</p>
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

        {/* Login form */}
        <form onSubmit={handleSubmit} className="login-form">
          {/* Email field */}
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              className={`form-input ${validationErrors.email ? 'input-error' : ''}`}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your.email@example.com"
              disabled={isLoading}
              autoComplete="email"
              autoFocus
            />
            {validationErrors.email && (
              <span className="field-error">{validationErrors.email}</span>
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
              autoComplete="current-password"
            />
            {validationErrors.password && (
              <span className="field-error">{validationErrors.password}</span>
            )}
          </div>

          {/* Remember me checkbox */}
          <div className="form-options">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                disabled={isLoading}
                className="checkbox-input"
              />
              <span className="checkbox-text">Remember me</span>
            </label>
          </div>

          {/* Submit button */}
          <button
            type="submit"
            className="btn btn-primary btn-full"
            disabled={isLoading}
          >
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
                Authenticating...
              </span>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Footer links */}
        <div className="login-footer">
          <p className="footer-text">
            Don't have an account?{' '}
            <Link to="/signup" className="footer-link">
              Sign up
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
