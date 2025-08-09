// src/components/auth/SignUpModal.tsx
import React from 'react';

import { useSignUpForm } from '../../hooks/useSignUpForm'; // Our new logic engine
import styles from './SignUpModal.module.css';

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
    // Using CSS module for better sizing and layout control
    <div className={styles.modalOverlay} onMouseDown={onClose}>
      <div className={styles.modalContent} onMouseDown={e => e.stopPropagation()}>
        {/* Using CSS module for header styling */}
        <header className={styles.modalHeader}>
          <button 
            onClick={onClose}
            className={styles.closeButton}
            title="Close modal"
          >
            ×
          </button>
          <h2 className={styles.modalTitle}>Join the Rebellion</h2>
          <p className={styles.modalSubtitle}>Create your System Rebellion account</p>
        </header>

        {/* Using CSS module for form styling */}
        <form onSubmit={handleSubmit} className={styles.modalBody}>
          {displayError && <div className="alert alert-error">{displayError}</div>}

          <div className={styles.formGrid}>
            <div className={styles.formGroup}>
              <label className={styles.formLabel} htmlFor="first_name">First Name</label>
              <input type="text" id="first_name" value={formData.first_name} disabled={isLoading} required
                className={`${styles.formInput} ${localErrors.first_name ? styles.borderError : ''}`}
                onChange={e => handleInputChange('first_name', e.target.value)} />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.formLabel} htmlFor="last_name">Last Name</label>
              <input type="text" id="last_name" value={formData.last_name} disabled={isLoading} required
                className={`${styles.formInput} ${localErrors.last_name ? styles.borderError : ''}`}
                onChange={e => handleInputChange('last_name', e.target.value)} />
            </div>
          </div>
          
          <div className={styles.formGroup}>
            <label className={styles.formLabel} htmlFor="email">Email Address</label>
            <input type="email" id="email" value={formData.email} disabled={isLoading} required
              className={`${styles.formInput} ${localErrors.email ? styles.borderError : ''}`}
              onChange={e => handleInputChange('email', e.target.value)} />
          </div>
          
          <div className={styles.formGrid}>
             <div className={styles.formGroup}>
              <label className={styles.formLabel} htmlFor="company_name">Company</label>
              <input type="text" id="company_name" value={formData.company_name} disabled={isLoading} required
                className={`${styles.formInput} ${localErrors.company_name ? styles.borderError : ''}`}
                onChange={e => handleInputChange('company_name', e.target.value)} />
            </div>
            <div className={styles.formGroup}>
              <label className={styles.formLabel} htmlFor="job_title">Job Title (Optional)</label>
              <input type="text" id="job_title" value={formData.job_title} disabled={isLoading}
                className={styles.formInput}
                onChange={e => handleInputChange('job_title', e.target.value)} />
            </div>
          </div>

          <div className={styles.formGroup}>
            <label className={styles.formLabel} htmlFor="password">Password</label>
            <input type="password" id="password" value={formData.password} disabled={isLoading} required
              className={`${styles.formInput} ${localErrors.password ? styles.borderError : ''}`}
              onChange={e => handleInputChange('password', e.target.value)} />
            <PasswordStrengthIndicator strength={passwordStrength} />
          </div>

          <div className={styles.formGroup}>
            <label className={styles.formLabel} htmlFor="confirmPassword">Confirm Password</label>
            <input type="password" id="confirmPassword" value={formData.confirmPassword} disabled={isLoading} required
              className={`${styles.formInput} ${localErrors.confirmPassword ? styles.borderError : ''}`}
              onChange={e => handleInputChange('confirmPassword', e.target.value)} />
          </div>

          <div className={styles.formFooter}>
            <p className={styles.switchText}>
              Have an account?{' '}
              <button type="button" onClick={onSwitchToLogin} className={styles.switchButton}>Sign In</button>
            </p>
            <button type="submit" className={styles.submitButton} disabled={isLoading}>
              {isLoading ? 'Creating...' : 'Create Account & Begin'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}