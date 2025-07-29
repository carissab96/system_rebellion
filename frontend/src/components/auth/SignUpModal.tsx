// src/components/auth/SignUpModal.tsx
import React from 'react';
import { useSignUpForm } from '../../hooks/useSignUpForm'; // Our new logic engine

interface SignUpModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSwitchToLogin: () => void;
}

const PasswordStrengthIndicator: React.FC<{ strength: number }> = ({ strength }) => {
  const segments = [
    { met: strength >= 1, color: 'var(--error)' },
    { met: strength >= 2, color: 'var(--error)' },
    { met: strength >= 3, color: 'var(--warning)' },
    { met: strength >= 4, color: 'var(--success)' },
    { met: strength >= 5, color: 'var(--success)' },
  ];
  return (
    <div className="d-flex gap-1 mt-2">
      {segments.map((segment, index) => (
        <div 
          key={index} 
          style={{ 
            height: '4px', 
            flex: 1, 
            borderRadius: '2px', 
            backgroundColor: segment.met ? segment.color : 'var(--rebellion-border)',
            transition: 'background-color 0.3s ease'
          }}
        />
      ))}
    </div>
  );
};


export default function SignUpModal({ isOpen, onClose, onSwitchToLogin }: SignUpModalProps) {
  const {
    formData,
    isLoading,
    displayError,
    localErrors,
    passwordStrength,
    handleInputChange,
    handleSubmit
  } = useSignUpForm(isOpen, onClose);

  if (!isOpen) return null;

  return (
    // We use the PRE-BUILT classes from common-components.css
    <div className="modal-overlay" onMouseDown={onClose}>
      <div className="modal-content" onMouseDown={e => e.stopPropagation()}>
        {/* We compose the header using .card classes and utilities */}
        <header className="card-header text-center">
          <h2 className="card-title">Create Your Rebellion Account</h2>
          <p className="card-subtitle mt-1">Begin the journey to persistent AI-driven intelligence.</p>
        </header>

        {/* The body uses our global form classes */}
        <form onSubmit={handleSubmit} className="card-body d-flex flex-col gap-3">
          {displayError && <div className="alert alert-error">{displayError}</div>}

          <div className="d-grid gap-3" style={{ gridTemplateColumns: '1fr 1fr' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="first_name">First Name</label>
              <input type="text" id="first_name" value={formData.first_name} disabled={isLoading} required
                className={`form-input ${localErrors.first_name ? 'border-error' : ''}`}
                onChange={e => handleInputChange('first_name', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="last_name">Last Name</label>
              <input type="text" id="last_name" value={formData.last_name} disabled={isLoading} required
                className={`form-input ${localErrors.last_name ? 'border-error' : ''}`}
                onChange={e => handleInputChange('last_name', e.target.value)} />
            </div>
          </div>
          
          <div className="form-group">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input type="email" id="email" value={formData.email} disabled={isLoading} required
              className={`form-input ${localErrors.email ? 'border-error' : ''}`}
              onChange={e => handleInputChange('email', e.target.value)} />
          </div>
          
          <div className="d-grid gap-3" style={{ gridTemplateColumns: '1fr 1fr' }}>
             <div className="form-group">
              <label className="form-label" htmlFor="company_name">Company</label>
              <input type="text" id="company_name" value={formData.company_name} disabled={isLoading} required
                className={`form-input ${localErrors.company_name ? 'border-error' : ''}`}
                onChange={e => handleInputChange('company_name', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label" htmlFor="job_title">Job Title (Optional)</label>
              <input type="text" id="job_title" value={formData.job_title} disabled={isLoading}
                className="form-input"
                onChange={e => handleInputChange('job_title', e.target.value)} />
            </div>
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="password">Password</label>
            <input type="password" id="password" value={formData.password} disabled={isLoading} required
              className={`form-input ${localErrors.password ? 'border-error' : ''}`}
              onChange={e => handleInputChange('password', e.target.value)} />
            <PasswordStrengthIndicator strength={passwordStrength} />
          </div>

          <div className="form-group">
            <label className="form-label" htmlFor="confirmPassword">Confirm Password</label>
            <input type="password" id="confirmPassword" value={formData.confirmPassword} disabled={isLoading} required
              className={`form-input ${localErrors.confirmPassword ? 'border-error' : ''}`}
              onChange={e => handleInputChange('confirmPassword', e.target.value)} />
          </div>

          <div className="d-flex justify-between align-center mt-4">
            <p className="text-sm text-dim">
              Have an account?{' '}
              <button type="button" onClick={onSwitchToLogin} className="btn btn-ghost p-1">Sign In</button>
            </p>
            <button type="submit" className="btn btn-primary btn-lg" disabled={isLoading}>
              {isLoading ? 'Creating...' : 'Create Account & Begin'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}