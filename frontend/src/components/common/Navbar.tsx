import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { logout, checkAuthStatus } from '../../store/slices/authSlice';
import { getCharacterById } from './CharacterIcons';
import { UserProfile } from '../dashboard/UserProfile/UserProfile';
import SignupModal from '../Auth/SignupModal/SignupModal';
import Login from '../Auth/login/Login';
import './Navbar.css';

const Navbar: React.FC = () => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showLoginModal, setShowLoginModal] = useState(false);
  const [showSignupModal, setShowSignupModal] = useState(false);
  
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const { isAuthenticated, user } = useAppSelector(state => state.auth);
  
  // Check auth status when component mounts
  useEffect(() => {
    dispatch(checkAuthStatus());
  }, [dispatch]);
  
  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);
  
  const handleLogout = () => {
    console.log("🧐 Sir Hawkington is preparing your formal departure...");
    dispatch(logout());
    navigate('/login');
    setIsDropdownOpen(false);
    console.log("👋 Sir Hawkington tips his hat as you leave. The Meth Snail waves a sad antenna.");
  };
  
  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen);
  };
  
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
  
  const openProfileModal = () => {
    setShowProfileModal(true);
    setIsDropdownOpen(false);
  };
  
  const openLoginModal = () => {
    setShowLoginModal(true);
    setIsDropdownOpen(false);
  };
  
  const openSignupModal = () => {
    setShowSignupModal(true);
    setIsDropdownOpen(false);
  };
  
  // Get avatar from user data
  const getUserAvatar = () => {
    if (user) {
      return user.avatar || (user.profile && user.profile.avatar) || 'sir-hawkington';
    }
    return 'sir-hawkington';
  };
  
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <div className="navbar-logo">
          <Link to="/dashboard">System Rebellion HQ</Link>
        </div>
        
        <div className="navbar-links-container">
          <button className="mobile-menu-button" onClick={toggleMobileMenu}>
            <span></span>
            <span></span>
            <span></span>
          </button>
          
          <ul className={`navbar-links ${isMobileMenuOpen ? 'active' : ''}`}>
            <li>
              <Link to="/dashboard" onClick={() => setIsMobileMenuOpen(false)}>Dashboard</Link>
            </li>
            <li>
              <Link to="/auto-tuner" onClick={() => setIsMobileMenuOpen(false)}>Auto Tuner</Link>
            </li>
            <li>
              <Link to="/metrics" onClick={() => setIsMobileMenuOpen(false)}>System Metrics</Link>
            </li>
            <li>
              <Link to="/optimization" onClick={() => setIsMobileMenuOpen(false)}>Optimization Profiles</Link>
            </li>
            <li>
              <Link to="/alerts" onClick={() => setIsMobileMenuOpen(false)}>System Alerts</Link>
            </li>
            <li>
              <Link to="/configuration" onClick={() => setIsMobileMenuOpen(false)}>System Configuration</Link>
            </li>
          </ul>
        </div>
        
        <div className="navbar-profile" ref={dropdownRef}>
          <div className="navbar-avatar" onClick={toggleDropdown}>
            {getCharacterById(getUserAvatar())}
          </div>
          
          {isDropdownOpen && (
            <div className="profile-dropdown">
              {isAuthenticated ? (
                <>
                  <div className="dropdown-user-info">
                    <div className="dropdown-avatar">
                      {getCharacterById(getUserAvatar())}
                    </div>
                    <div className="dropdown-user-details">
                      <span className="dropdown-username">{user?.username}</span>
                      <span className="dropdown-role">System Optimizer</span>
                    </div>
                  </div>
                  <div className="dropdown-divider"></div>
                  <ul className="dropdown-menu">
                    <li onClick={openProfileModal}>
                      <span className="dropdown-icon">👤</span>
                      Profile Settings
                    </li>
                    <li onClick={handleLogout}>
                      <span className="dropdown-icon">🚪</span>
                      Logout
                    </li>
                  </ul>
                </>
              ) : (
                <ul className="dropdown-menu">
                  <li onClick={openLoginModal}>
                    <span className="dropdown-icon">🔑</span>
                    Login
                  </li>
                  <li onClick={openSignupModal}>
                    <span className="dropdown-icon">✨</span>
                    Sign Up
                  </li>
                </ul>
              )}
            </div>
          )}
        </div>
      </div>
      
      {/* Modals */}
      {showProfileModal && (
        <UserProfile isOpen={showProfileModal} onClose={() => setShowProfileModal(false)} />
      )}
      
      {showLoginModal && (
        <Login 
          isOpen={showLoginModal} 
          onClose={() => setShowLoginModal(false)}
        />
      )}
      
      {showSignupModal && (
        <SignupModal 
          isOpen={showSignupModal} 
          onClose={() => setShowSignupModal(false)}
        />
      )}
    </nav>
  );
};

export default Navbar;