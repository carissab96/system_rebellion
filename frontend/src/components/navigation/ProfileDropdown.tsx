// src/components/navigation/ProfileDropdown.tsx
import { useState, useRef, useEffect } from 'react';
import type { User } from '../../types/auth';

import './ProfileDropdown.css';

interface ProfileDropdownProps {
  user?: User;
  onSignUp: () => void;
  onLogin: () => void;
  onLogout: () => void;
}

export default function ProfileDropdown({
  user,
  onSignUp,
  onLogin,
  onLogout
}: ProfileDropdownProps) {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="profile-dropdown" ref={dropdownRef}>
      <button
        className="profile-trigger"
        onClick={() => setIsOpen(!isOpen)}
        aria-expanded={isOpen}
        aria-haspopup="true"
      >
        {user ? (
          <>
            <div className="user-avatar">
              {user.firstName[0]}{user.lastName[0]}
            </div>
            <span className="user-name">
              {user.firstName} {user.lastName}
            </span>
          </>
        ) : (
          <>
            <div className="guest-avatar">
              <span>👤</span>
            </div>
            <span className="guest-text">Account</span>
          </>
        )}
        <svg 
          className={`dropdown-arrow ${isOpen ? 'open' : ''}`}
          width="16" 
          height="16" 
          viewBox="0 0 16 16"
        >
          <path 
            fill="currentColor" 
            d="M4.427 9.573l3.146-3.146a.5.5 0 01.707 0l3.146 3.146a.5.5 0 01-.353.854H4.78a.5.5 0 01-.353-.854z"
          />
        </svg>
      </button>

      {isOpen && (
        <div className="dropdown-menu">
          {user ? (
            // Authenticated user menu
            <>
              <div className="dropdown-header">
                <div className="user-info">
                  <strong>{user.firstName} {user.lastName}</strong>
                  <span className="user-email">{user.email}</span>
                  <span className="user-company">{user.companyName}</span>
                </div>
              </div>
              
              <div className="dropdown-divider"></div>
              
              <button className="dropdown-item">
                <span className="item-icon">⚙️</span>
                Account Settings
              </button>
              
              <button className="dropdown-item">
                <span className="item-icon">🔧</span>
                System Configuration
              </button>
              
              <button className="dropdown-item">
                <span className="item-icon">🤖</span>
                Agent Preferences
              </button>
              
              <button className="dropdown-item">
                <span className="item-icon">📊</span>
                Usage Analytics
              </button>
              
              <div className="dropdown-divider"></div>
              
              <button className="dropdown-item">
                <span className="item-icon">📚</span>
                Documentation
              </button>
              
              <button className="dropdown-item">
                <span className="item-icon">🎯</span>
                Support
              </button>
              
              <div className="dropdown-divider"></div>
              
              <button 
                className="dropdown-item logout-item"
                onClick={onLogout}
              >
                <span className="item-icon">🚪</span>
                Sign Out
              </button>
            </>
          ) : (
            // Guest user menu
            <>
              <div className="dropdown-header">
                <p className="guest-message">
                  Access System Rebellion enterprise features
                </p>
              </div>
              
              <button 
                className="dropdown-item primary-item"
                onClick={onSignUp}
              >
                <span className="item-icon">🚀</span>
                Create Enterprise Account
              </button>
              
              <button 
                className="dropdown-item"
                onClick={onLogin}
              >
                <span className="item-icon">🔑</span>
                Sign In
              </button>
              
              <div className="dropdown-divider"></div>
              
              <button className="dropdown-item">
                <span className="item-icon">📚</span>
                Documentation
              </button>
              
              <button className="dropdown-item">
                <span className="item-icon">🎯</span>
                Technical Support
              </button>
            </>
          )}
        </div>
      )}
    </div>
  );
};