import React, { useState, FC } from 'react';
import { useDispatch } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import { registerUser } from '../../../store/slices/authSlice';
import { AppDispatch } from '../../../store/store';
import './SignupModal.css'; // Assuming you have some styling

interface SignupModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface RegistrationData {
  username: string;
  email: string;
  password: string;
  profile: {
    first_name: string;
    last_name: string;
  };
}

const SignupModal: FC<SignupModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;  
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
    
    // Basic validation
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
    
    try {
      // Prepare registration data - SIMPLE VERSION
      const registrationData: RegistrationData = {
        username: formData.username,
        email: formData.email,
        password: formData.password,
        profile: {
          first_name: formData.firstName,
          last_name: formData.lastName
        }
      };
      
      // Dispatch registration action
      await dispatch(registerUser(registrationData));
      
      // Store username for convenience on the login page
      localStorage.setItem('registered_username', formData.username);
      
      // Success message
      setHawkingtonQuote("🎩 Welcome aboard! Sir Hawkington is most pleased with your registration!");
      
      // Redirect to login page after a brief delay to show success message
      setTimeout(() => {
        navigate('/login');
        onClose();
      }, 2000);
      
    } catch (err) {
      console.error("🔥 REGISTRATION ERROR:", err);
      const errorMsg = err instanceof Error ? err.message : 'Registration failed';
      setError(errorMsg);
      setHawkingtonQuote("🧐 I say, we've encountered a bit of a registration hiccup!");
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="signup-modal">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Join the System Rebellion</h2>
          <button className="close-button" onClick={onClose}>×</button>
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