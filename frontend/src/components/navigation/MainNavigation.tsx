// components/navigation/MainNavigation.tsx
import React, { useState, useRef, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useSelector } from 'react-redux';

import type { RootState } from '../../store/store';
import { AgentPattern } from '../onboarding/components/AgentPattern';
import styles from './MainNavigation.module.css';
import './AgentPatterns.css'; // Import agent pattern styles

export const MainNavigation: React.FC = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [isProfileDropdownOpen, setIsProfileDropdownOpen] = useState(false);
  const [isAgentMetricsOpen, setIsAgentMetricsOpen] = useState(false);
  const location = useLocation();
  const auth = useSelector((state: RootState) => state.auth);
  const agentTheater = useSelector((state: RootState) => state.agentTheater);
  
  const profileDropdownRef = useRef<HTMLDivElement>(null);
  const agentMetricsRef = useRef<HTMLDivElement>(null);
  
  const isActive = (path: string) => {
    return location.pathname === path;
  };
  
  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileDropdownRef.current && !profileDropdownRef.current.contains(event.target as Node)) {
        setIsProfileDropdownOpen(false);
      }
      if (agentMetricsRef.current && !agentMetricsRef.current.contains(event.target as Node)) {
        setIsAgentMetricsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  // Get user initials for avatar
  const getUserInitials = () => {
    if (!auth.user) return '?';
    
    const firstName = auth.user.first_name || '';
    const lastName = auth.user.last_name || '';
    
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase();
  };
  
  const handleLogout = () => {
    // Implement logout logic here
    console.log('Logging out...');
    setIsProfileDropdownOpen(false);
    // Redirect to login page
    window.location.href = '/login';
  };
  
  // Agent data for metrics with mapping to AgentPattern IDs
  const agents = [
    { id: 'sirHawkington', patternId: 'hawkington', name: 'Sir Hawkington', color: '#FF5733', isOnline: agentTheater.sirHawkington?.isOnline || false },
    { id: 'methSnail', patternId: 'snail', name: 'Meth Snail', color: '#33FF57', isOnline: agentTheater.methSnail?.isOnline || false },
    { id: 'hamsters', patternId: 'hamsters', name: 'Hamsters', color: '#3357FF', isOnline: agentTheater.hamsters?.isOnline || false },
    { id: 'quantumShadow', patternId: 'qsp', name: 'Quantum Shadow', color: '#F033FF', isOnline: agentTheater.quantumShadow?.isOnline || false },
    { id: 'theStick', patternId: 'stick', name: 'The Stick', color: '#FF33A8', isOnline: agentTheater.theStick?.isOnline || false },
    { id: 'vic20', patternId: 'vic20', name: 'VIC-20', color: '#33FFF0', isOnline: agentTheater.vic20?.isOnline || false }
  ];

  // Type-safe helper function to get agent data
  const getAgentData = (agentId: string, metric: string): string => {
    // Map the agentId to the correct property in agentTheater
    switch (agentId) {
      case 'sirHawkington':
        return agentTheater.sirHawkington?.data?.[metric] || '0';
      case 'methSnail':
        return agentTheater.methSnail?.data?.[metric] || '0';
      case 'hamsters':
        return agentTheater.hamsters?.data?.[metric] || '0';
      case 'quantumShadow':
        return agentTheater.quantumShadow?.data?.[metric] || '0';
      case 'theStick':
        return agentTheater.theStick?.data?.[metric] || '0';
      case 'vic20':
        return agentTheater.vic20?.data?.[metric] || '0';
      default:
        return '0';
    }
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
                to="/account" 
                className={`${styles.navLink} ${isActive('/account') ? styles.active : ''}`}
              >
                Account
              </Link>
              
              {/* Agent Metrics Dropdown */}
              <div className={styles.agentMetricsSection} ref={agentMetricsRef}>
                <button 
                  className={styles.agentMetricsButton}
                  onClick={() => setIsAgentMetricsOpen(!isAgentMetricsOpen)}
                >
                  Agent Metrics
                  <span>{isAgentMetricsOpen ? '▲' : '▼'}</span>
                </button>
                
                <div className={`${styles.agentMetricsDropdown} ${isAgentMetricsOpen ? styles.visible : ''}`}>
                  <div className={styles.agentMetricsHeader}>
                    <h4 className={styles.agentMetricsTitle}>Agent Metrics</h4>
                    <Link to="/agent-metrics" className={styles.agentMetricsViewAll}>View All</Link>
                  </div>
                  
                  <div className={styles.agentMetricsGrid}>
                    {agents.map(agent => (
                      <div key={agent.id} className={styles.agentMetricsCard}>
                        <div className={styles.agentMetricsCardHeader}>
                          <div 
                            className={styles.agentMetricsCardIcon} 
                            style={{ backgroundColor: agent.color }}
                          >
                            <AgentPattern agentId={agent.patternId} className="small-pattern" />
                          </div>
                          <div>
                            <p className={styles.agentMetricsCardName}>{agent.name}</p>
                            <div className={styles.agentMetricsCardStatus}>
                              <span className={`${styles.agentMetricsCardStatusDot} ${agent.isOnline ? styles.online : styles.offline}`}></span>
                              {agent.isOnline ? 'Online' : 'Offline'}
                            </div>
                          </div>
                        </div>
                        
                        <div className={styles.agentMetricsCardData}>
                          <div className={styles.agentMetricsCardDataItem}>
                            <span className={styles.agentMetricsCardDataLabel}>CPU</span>
                            <span className={styles.agentMetricsCardDataValue}>
                              {getAgentData(agent.id, 'cpu')}%
                            </span>
                          </div>
                          <div className={styles.agentMetricsCardDataItem}>
                            <span className={styles.agentMetricsCardDataLabel}>Memory</span>
                            <span className={styles.agentMetricsCardDataValue}>
                              {getAgentData(agent.id, 'memory')}MB
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
              
              <Link 
                to="/admin-console" 
                className={`${styles.navLink} ${isActive('/admin-console') ? styles.active : ''}`}
              >
                Admin Console
              </Link>
            </>
          )}
          
          <div className={styles.authLinks}>
            {auth.isAuthenticated ? (
              <div className={styles.profileSection} ref={profileDropdownRef}>
                <button 
                  className={styles.profileButton}
                  onClick={() => setIsProfileDropdownOpen(!isProfileDropdownOpen)}
                >
                  <div className={styles.profileAvatar}>{getUserInitials()}</div>
                  <span className={styles.profileName}>
                    {auth.user?.first_name} {auth.user?.last_name}
                  </span>
                  <span>{isProfileDropdownOpen ? '▲' : '▼'}</span>
                </button>
                
                <div className={`${styles.profileDropdown} ${isProfileDropdownOpen ? styles.visible : ''}`}>
                  <div className={styles.dropdownHeader}>
                    <div className={styles.dropdownUserInfo}>
                      <div className={styles.dropdownAvatar}>{getUserInitials()}</div>
                      <div className={styles.dropdownUserDetails}>
                        <p className={styles.dropdownUserName}>{auth.user?.first_name} {auth.user?.last_name}</p>
                        <p className={styles.dropdownUserEmail}>{auth.user?.email}</p>
                      </div>
                    </div>
                  </div>
                  
                  <div className={styles.dropdownSection}>
                    <Link to="/profile" className={styles.dropdownItem}>
                      <span className={styles.dropdownItemIcon}>👤</span>
                      <span className={styles.dropdownItemText}>Your Profile</span>
                    </Link>
                    <Link to="/account/subscription" className={styles.dropdownItem}>
                      <span className={styles.dropdownItemIcon}>💳</span>
                      <span className={styles.dropdownItemText}>Subscription</span>
                    </Link>
                  </div>
                  
                  <div className={styles.dropdownSection}>
                    <Link to="/settings" className={styles.dropdownItem}>
                      <span className={styles.dropdownItemIcon}>⚙️</span>
                      <span className={styles.dropdownItemText}>Settings</span>
                    </Link>
                    <Link to="/agent-preferences" className={styles.dropdownItem}>
                      <span className={styles.dropdownItemIcon}>🤖</span>
                      <span className={styles.dropdownItemText}>Agent Preferences</span>
                    </Link>
                    <Link to="/monitoring-preferences" className={styles.dropdownItem}>
                      <span className={styles.dropdownItemIcon}>📊</span>
                      <span className={styles.dropdownItemText}>Monitoring Preferences</span>
                    </Link>
                  </div>
                  
                  <div className={styles.dropdownSection}>
                    <Link to="/support" className={styles.dropdownItem}>
                      <span className={styles.dropdownItemIcon}>🛟</span>
                      <span className={styles.dropdownItemText}>Contact Support</span>
                    </Link>
                    <button onClick={handleLogout} className={`${styles.dropdownItem} ${styles.logoutItem}`}>
                      <span className={styles.dropdownItemIcon}>🚪</span>
                      <span className={styles.dropdownItemText}>Sign Out</span>
                    </button>
                  </div>
                </div>
              </div>
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
