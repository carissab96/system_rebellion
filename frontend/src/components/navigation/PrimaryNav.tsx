// components/navigation/PrimaryNav.tsx
// Primary navigation bar - System branding + user profile
// Built by: Dell-Sonnet - November 20, 2025

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../hooks/redux';
import { logout } from '../../store/slices/authSlice';
import type { RootState } from '../../store/store';
import './Navigation.css';

export const PrimaryNav: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { isAuthenticated, user } = useAppSelector((state: RootState) => state.auth);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/login');
    setDropdownOpen(false);
  };

  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };

  return (
    <nav className="primary-nav">
      <div className="nav-left">
        <Link to="/" className="brand-link">
          <span className="brand-name">System Rebellion</span>
        </Link>
        <a 
          href="https://hawkington-tech.com" 
          target="_blank" 
          rel="noopener noreferrer"
          className="company-link"
        >
          by Hawkington Technologies Inc
        </a>
      </div>

      <div className="nav-right">
        {isAuthenticated ? (
          <div className="user-menu">
            <button 
              className="user-menu-trigger"
              onClick={toggleDropdown}
              aria-expanded={dropdownOpen}
              aria-haspopup="true"
            >
              <div className="profile-pic-placeholder">
                {user?.first_name?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || 'U'}
              </div>
              <span className="username">
                {user?.first_name && user?.last_name 
                  ? `${user.first_name} ${user.last_name}`
                  : user?.email || 'User'
                }
              </span>
              <span className="dropdown-arrow">▼</span>
            </button>

            {dropdownOpen && (
              <div className="user-dropdown">
                <div className="dropdown-header">
                  <div className="dropdown-username">
                    {user?.first_name && user?.last_name 
                      ? `${user.first_name} ${user.last_name}`
                      : 'User'
                    }
                  </div>
                  <div className="dropdown-email">{user?.email}</div>
                </div>
                <div className="dropdown-divider" />
                <Link 
                  to="/profile/edit" 
                  className="dropdown-item"
                  onClick={() => setDropdownOpen(false)}
                >
                  Edit Profile
                </Link>
                <Link 
                  to="/subscription" 
                  className="dropdown-item"
                  onClick={() => setDropdownOpen(false)}
                >
                  Subscription & Billing
                </Link>
                <Link 
                  to="/settings" 
                  className="dropdown-item"
                  onClick={() => setDropdownOpen(false)}
                >
                  Account Settings
                </Link>
                <div className="dropdown-divider" />
                <button 
                  className="dropdown-item logout-btn"
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        ) : (
          <div className="auth-links">
            <Link to="/login" className="auth-link">Login</Link>
            <Link to="/signup" className="auth-link signup">Sign Up</Link>
          </div>
        )}
      </div>
    </nav>
  );
};
