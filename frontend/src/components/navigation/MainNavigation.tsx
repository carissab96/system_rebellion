// components/navigation/MainNavigation.tsx
import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';

import type { RootState } from '../../store/store';
import styles from './MainNavigation.module.css';

export const MainNavigation: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const location = useLocation();
  const auth = useSelector((state: RootState) => state.auth);
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <nav className={styles.mainNav}>
      <div className={styles.navContainer}>
        <div className={styles.navBrand}>
          <Link to="/" className={styles.brandLink}>
            <span className={styles.brandIcon}>⚡</span>
            <span className={styles.brandName}>System Rebellion</span>
          </Link>
          
          <button 
            className={styles.mobileToggle} 
            onClick={() => setIsExpanded(!isExpanded)}
            aria-label="Toggle navigation"
          >
            <span className={styles.toggleIcon}>{isExpanded ? '✕' : '☰'}</span>
          </button>
        </div>
        
        <div className={`${styles.navLinks} ${isExpanded ? styles.expanded : ''}`}>
          {auth.isAuthenticated && (
            <>
              <Link 
                to="/agent-theater" 
                className={`${styles.navLink} ${isActive('/agent-theater') ? styles.active : ''}`}
              >
                Agent Theater
              </Link>
              <Link 
                to="/dashboard" 
                className={`${styles.navLink} ${isActive('/dashboard') ? styles.active : ''}`}
              >
                Dashboard
              </Link>
              <Link 
                to="/admin-console" 
                className={`${styles.navLink} ${isActive('/admin-console') ? styles.active : ''}`}
              >
                Admin Console
              </Link>
              <Link 
                to="/settings" 
                className={`${styles.navLink} ${isActive('/settings') ? styles.active : ''}`}
              >
                Settings
              </Link>
            </>
          )}
          
          <div className={styles.authLinks}>
            {auth.isAuthenticated ? (
              <button className={styles.authButton}>Sign Out</button>
            ) : (
              <>
                <button className={`${styles.authButton} ${styles.loginButton}`}>Sign In</button>
                <button className={`${styles.authButton} ${styles.signupButton}`}>Sign Up</button>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default MainNavigation;
