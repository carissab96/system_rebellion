// src/components/auth/LoginModal.tsx
import React from 'react';
import { useLoginForm } from '../../hooks/useLoginForm';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToSignUp: () => void;
}

export default function LoginModal({ isOpen, onClose, onSwitchToSignUp }: LoginModalProps) {
  const {
    formData,
    isLoading,
    displayError,
    localErrors,
    handleInputChange,
    handleSubmit
  } = useLoginForm(isOpen, onClose);

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onMouseDown={onClose}>
      <div className="modal-content" onMouseDown={e => e.stopPropagation()}>
        <header className="card-header text-center">
          <h2 className="card-title vic20-text">Enterprise Sign In</h2>
          <p className="card-subtitle mt-1">Access your System Rebellion dashboard</p>
        </header>

        <form onSubmit={handleSubmit} className="card-body d-flex flex-col gap-3">
          {displayError && <div className="alert alert-error">{displayError}</div>}

          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input 
              type="email" 
              id="email" 
              value={formData.email} 
              disabled={isLoading} 
              required
              placeholder="your.name@company.com"
              className={`form-input ${localErrors.email ? 'border-error' : ''}`}
              onChange={e => handleInputChange('email', e.target.value)} 
            />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input 
              type="password" 
              id="password" 
              value={formData.password} 
              disabled={isLoading} 
              required
              placeholder="Enter your password"
              className={`form-input ${localErrors.password ? 'border-error' : ''}`}
              onChange={e => handleInputChange('password', e.target.value)} 
            />
          </div>

          <div className="d-flex align-center gap-2">
            <label className="d-flex align-center gap-2 text-sm">
              <input
                type="checkbox"
                checked={formData.rememberMe}
                disabled={isLoading}
                onChange={e => handleInputChange('rememberMe', e.target.checked)}
                style={{ marginTop: '2px' }}
              />
              <span>Remember me for 30 days</span>
            </label>
          </div>

          <div className="d-flex justify-between align-center mt-4">
            <button 
              type="button" 
              onClick={() => {/* TODO: Implement forgot password */}} 
              className="btn btn-ghost p-1"
            >
              Forgot Password?
            </button>
            
            <button 
              type="submit" 
              className="btn btn-primary btn-lg" 
              disabled={isLoading}
            >
              {isLoading ? (
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

        <footer className="card-footer text-center">
          <p className="text-sm text-dim">
            Don't have an account?{' '}
            <button 
              type="button" 
              onClick={onSwitchToSignUp} 
              className="btn btn-ghost p-1"
            >
              Create Account
            </button>
          </p>
        </footer>
      </div>
    </div>
  );
}