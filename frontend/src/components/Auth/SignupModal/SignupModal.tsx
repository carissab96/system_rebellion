import React, { useState, FC } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { register } from '../../../store/slices/authSlice';
import { AppDispatch } from '../../../store/store';
import './SignupModal.css';
import '../../../components/common/Modal.css';

interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
}

// Registration data is now directly defined in the component

const SignupModal: FC<SignupModalProps> = ({ isOpen, onClose }) => {
  const dispatch = useDispatch<AppDispatch>();
  const navigate = useNavigate();
  
  // Form state
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: ''
  });
  
  // UI state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hawkingtonQuote, setHawkingtonQuote] = useState("🧐 Sir Hawkington awaits your distinguished registration!");
  
  if (!isOpen) return null;
  
  // Handle input changes
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  // Form submission
  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    
    // Enhanced validation
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match! The Meth Snail is confused by the dimensional discrepancy!");
      setHawkingtonQuote("🧐 I say, your passwords seem to be in disagreement with each other!");
      setIsSubmitting(false);
      return;
    }
    
    if (!formData.firstName || !formData.lastName || !formData.email || !formData.username || !formData.password) {
      setError("Please fill in all required fields! Sir Hawkington insists on proper form etiquette!");
      setHawkingtonQuote("🧐 A distinguished application requires all fields to be properly filled!");
      setIsSubmitting(false);
      return;
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError("Please enter a valid email address! The Quantum Shadow People cannot deliver notifications to invalid dimensions.");
      setHawkingtonQuote("🧐 I say, that email address appears to be from an alternate reality!");
      setIsSubmitting(false);
      return;
    }
    
    // Username validation - no spaces, special characters limited
    const usernameRegex = /^[a-zA-Z0-9_-]{3,20}$/;
    if (!usernameRegex.test(formData.username)) {
      setError("Username must be 3-20 characters and can only contain letters, numbers, underscores, and hyphens.");
      setHawkingtonQuote("🧐 A proper username adheres to aristocratic standards of simplicity!");
      setIsSubmitting(false);
      return;
    }
    
    // Password strength validation
    if (formData.password.length < 8) {
      setError("Password must be at least 8 characters! The Stick insists on proper security measures.");
      setHawkingtonQuote("🧐 The Stick measures your password and finds it wanting in length!");
      setIsSubmitting(false);
      return;
    }
    
    try {
      // Prepare registration data with properly formatted fields - backend only expects username, email, password
      const registrationData = {
        username: formData.username.trim(),
        email: formData.email.trim(),
        password: formData.password
        // Note: profile data will be added later after successful registration
      };
      
      console.log("Attempting registration with:", {
        ...registrationData,
        password: "***"
      });
      
      // Dispatch registration action
      await dispatch(register(registrationData));
      
      // Store username for convenience on the login page
      localStorage.setItem('registered_username', formData.username);
      
      // Success message
      setHawkingtonQuote("🎩 Welcome aboard! Sir Hawkington is most pleased with your registration!");
      setIsSubmitting(false);
      
      // Show success state before closing
      setTimeout(() => {
        navigate('/login');
        onClose();
      }, 2000);
      
    } catch (err: any) {
      console.error("🔥 REGISTRATION ERROR:", err);
      
      // Try to extract the actual error message from the server response
      let errorMsg = 'Registration failed';
      
      if (err.response && err.response.data) {
        if (typeof err.response.data === 'string') {
          errorMsg = err.response.data;
        } else if (err.response.data.detail) {
          errorMsg = typeof err.response.data.detail === 'string' 
            ? err.response.data.detail 
            : JSON.stringify(err.response.data.detail);
        }
      } else if (err.message) {
        errorMsg = err.message;
      }
      
      console.error("🔥 SERVER RESPONSE:", errorMsg);
      
      // Handle specific error cases
      if (errorMsg.includes('already exists')) {
        setError("This username or email is already registered! The VIC-20 has detected a duplicate in the system.");
        setHawkingtonQuote("🧐 I say, it appears you're already a distinguished member of our rebellion!");
      } else {
        setError(`Registration failed: ${errorMsg}`);
        setHawkingtonQuote("🧐 I say, we've encountered a bit of a registration hiccup!");
      }
      
      setIsSubmitting(false);
    }
  };
  
  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000,
    }}>
      <div style={{
        backgroundColor: '#1a0458',
        borderRadius: '12px',
        boxShadow: '0 0 20px rgba(0, 245, 212, 0.5)',
        width: '90%',
        maxWidth: '600px',
        padding: '2rem',
        position: 'relative',
        color: '#e2e8f0',
        border: '1px solid rgba(51, 51, 255, 0.3)',
        maxHeight: '90vh',
        overflowY: 'auto',
      }}>
        <div style={{
          marginBottom: '1.5rem',
          textAlign: 'center',
          position: 'relative',
        }}>
          <h2 style={{
            fontSize: '1.8rem',
            color: '#00f5d4',
            marginBottom: '0.5rem',
          }}>Join the System Rebellion</h2>
          <button style={{
            position: 'absolute',
            top: '0',
            right: '0',
            background: 'transparent',
            border: 'none',
            color: '#00f5d4',
            fontSize: '24px',
            cursor: 'pointer',
            zIndex: 10,
          }} onClick={onClose}>×</button>
        </div>
        
        <div className="hawkington-quote">
          <p>{hawkingtonQuote}</p>
        </div>
        
        {error && (
          <div className="error-message">
            <p>{error}</p>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="signup-form">
          <div className="form-section">
            <h3>Personal Information</h3>
            <div className="form-row">
              <div className="form-group">
                <label htmlFor="firstName">First Name</label>
                <input
                  type="text"
                  id="firstName"
                  name="firstName"
                  value={formData.firstName}
                  onChange={handleChange}
                  disabled={isSubmitting}
                  className={isSubmitting ? 'input-submitting' : ''}
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="lastName">Last Name</label>
                <input
                  type="text"
                  id="lastName"
                  name="lastName"
                  value={formData.lastName}
                  onChange={handleChange}
                  disabled={isSubmitting}
                  className={isSubmitting ? 'input-submitting' : ''}
                />
              </div>
            </div>
          </div>
          
          <div className="form-section">
            <h3>Account Details</h3>
            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleChange}
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              />
            </div>
          </div>
          
          <div className="form-section">
            <h3>Security</h3>
            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                disabled={isSubmitting}
                className={isSubmitting ? 'input-submitting' : ''}
              />
            </div>
          </div>
          
          <div className="form-actions">
            <button 
              type="button" 
              className="cancel-button" 
              onClick={onClose}
              disabled={isSubmitting}
            >
              Cancel
            </button>
            <button 
              type="submit" 
              className="submit-button"
              disabled={isSubmitting}
            >
              {isSubmitting ? 'Registering...' : 'Register'}
            </button>
          </div>
        </form>
        
        <div className="modal-footer">
          <p>Already have an account? <a href="/login">Login</a></p>
        </div>
      </div>
    </div>
  );
};

export default SignupModal;