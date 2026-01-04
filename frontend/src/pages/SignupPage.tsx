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
import Footer from '../components/common/Footer';
import './SignupPage.css';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useDispatch<AppDispatch>();
  const { isAuthenticated, isLoading, error } = useSelector((state: RootState) => state.auth);

  // Form state
  const [email, setEmail] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [acceptedRisks, setAcceptedRisks] = useState(false);
  const [captchaVerified, setCaptchaVerified] = useState(false);
  const [validationErrors, setValidationErrors] = useState<{
    email?: string;
    firstName?: string;
    lastName?: string;
    password?: string;
    confirmPassword?: string;
    terms?: string;
    risks?: string;
    captcha?: string;
  }>({});

  // Email check state
  const [emailCheckLoading, setEmailCheckLoading] = useState(false);
  const [emailExists, setEmailExists] = useState(false);

  // Simple math captcha (no external dependencies)
  const [captchaQuestion, setCaptchaQuestion] = useState({ num1: 0, num2: 0, answer: 0 });
  const [captchaInput, setCaptchaInput] = useState('');

  // Generate captcha on mount
  useEffect(() => {
    const num1 = Math.floor(Math.random() * 10) + 1;
    const num2 = Math.floor(Math.random() * 10) + 1;
    setCaptchaQuestion({ num1, num2, answer: num1 + num2 });
  }, []);

  // Verify captcha answer
  const verifyCaptcha = (input: string) => {
    const userAnswer = parseInt(input, 10);
    setCaptchaVerified(userAnswer === captchaQuestion.answer);
  };

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
      firstName?: string;
      lastName?: string;
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

    // First name validation
    if (!firstName) {
      errors.firstName = 'First name is required';
    } else if (firstName.length < 2) {
      errors.firstName = 'First name must be at least 2 characters';
    }

    // Last name validation
    if (!lastName) {
      errors.lastName = 'Last name is required';
    } else if (lastName.length < 2) {
      errors.lastName = 'Last name must be at least 2 characters';
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

    // Risk acceptance validation
    if (!acceptedRisks) {
      errors.risks = 'You must acknowledge the risks and accept responsibility';
    }

    // Captcha validation
    if (!captchaVerified) {
      errors.captcha = 'Please complete the verification to prove you are human';
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
          first_name: firstName,
          last_name: lastName,
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
    <div className="signup-page">
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
            <img 
              src="/SRLogo1.png" 
              alt="System Rebellion Logo" 
              className="logo-icon"
              width="140"
              height="140"
            />
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

          {/* First Name field */}
          <div className="form-group">
            <label htmlFor="firstName" className="form-label">
              First Name
            </label>
            <input
              type="text"
              id="firstName"
              className={`form-input ${validationErrors.firstName ? 'input-error' : ''}`}
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
              placeholder="John"
              disabled={isLoading}
              autoComplete="given-name"
            />
            {validationErrors.firstName && (
              <span className="field-error">{validationErrors.firstName}</span>
            )}
          </div>

          {/* Last Name field */}
          <div className="form-group">
            <label htmlFor="lastName" className="form-label">
              Last Name
            </label>
            <input
              type="text"
              id="lastName"
              className={`form-input ${validationErrors.lastName ? 'input-error' : ''}`}
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
              placeholder="Doe"
              disabled={isLoading}
              autoComplete="family-name"
            />
            {validationErrors.lastName && (
              <span className="field-error">{validationErrors.lastName}</span>
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

          {/* Risk Acknowledgment - CRITICAL */}
          <div className="form-group">
            <div className="risk-disclaimer">
              <div className="disclaimer-header">
                <svg width="20" height="20" viewBox="0 0 20 20" className="warning-icon">
                  <path d="M10 2 L18 17 L2 17 Z" fill="none" stroke="var(--warning)" strokeWidth="2" />
                  <line x1="10" y1="8" x2="10" y2="12" stroke="var(--warning)" strokeWidth="2" />
                  <circle cx="10" cy="14" r="1" fill="var(--warning)" />
                </svg>
                <span className="disclaimer-title">Important: AI Agent Permissions</span>
              </div>
              <p className="disclaimer-text">
                System Rebellion uses AI agents that monitor and can modify your system settings to optimize performance. 
                These agents are powered by artificial intelligence and, while designed to be helpful, can make mistakes. 
                By proceeding, you acknowledge that:
              </p>
              <ul className="disclaimer-list">
                <li>AI agents will have permission to modify system configurations</li>
                <li>Agents may make changes that could affect system stability</li>
                <li>You are responsible for maintaining backups of critical data</li>
                <li>Hawkington Technologies, Inc. is not liable for any system damage or data loss</li>
              </ul>
            </div>
            <label className={`checkbox-label ${validationErrors.risks ? 'label-error' : ''}`}>
              <input
                type="checkbox"
                checked={acceptedRisks}
                onChange={(e) => setAcceptedRisks(e.target.checked)}
                disabled={isLoading}
                className="checkbox-input"
              />
              <span className="checkbox-text checkbox-text-bold">
                I understand the risks and accept full responsibility for any system changes made by the AI agents
              </span>
            </label>
            {validationErrors.risks && (
              <span className="field-error">{validationErrors.risks}</span>
            )}
          </div>

          {/* Human Verification Captcha */}
          <div className="form-group">
            <label className="form-label">Verify you're human</label>
            <div className="captcha-container">
              <div className="captcha-question">
                What is {captchaQuestion.num1} + {captchaQuestion.num2}?
              </div>
              <input
                type="number"
                className={`form-input captcha-input ${validationErrors.captcha ? 'input-error' : ''}`}
                value={captchaInput}
                onChange={(e) => {
                  setCaptchaInput(e.target.value);
                  verifyCaptcha(e.target.value);
                }}
                placeholder="Enter answer"
                disabled={isLoading}
              />
              {captchaVerified && (
                <span className="captcha-success">
                  <svg width="16" height="16" viewBox="0 0 16 16">
                    <circle cx="8" cy="8" r="7" fill="none" stroke="var(--success)" strokeWidth="2" />
                    <path d="M5 8 L7 10 L11 6" fill="none" stroke="var(--success)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                  Verified
                </span>
              )}
            </div>
            {validationErrors.captcha && (
              <span className="field-error">{validationErrors.captcha}</span>
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
      <Footer />
    </div>
  );
};
