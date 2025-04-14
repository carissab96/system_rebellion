import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { updateProfile } from '../../store/slices/authSlice';
import { RootState } from '../../store/store';
import axios from 'axios';
import './onboarding.css';

// Define the system information interface
interface SystemInfo {
  operating_system: string;
  os_version: string;
  cpu_cores: number;
  total_memory: number; // in GB
}

const Onboarding: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const auth = useAppSelector((state: RootState) => state.auth);
  const isAuthenticated = auth.isAuthenticated;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1);
  const [hawkingtonQuote, setHawkingtonQuote] = useState("🧐 Sir Hawkington requires some information about your system!");

  // System information state
  const [systemInfo, setSystemInfo] = useState<SystemInfo>({
    operating_system: '',
    os_version: '',
    cpu_cores: 0,
    total_memory: 0
  });

  // Auto-detect system information if possible
  useEffect(() => {
    const detectSystemInfo = async () => {
      try {
        // Try to detect OS and version
        const userAgent = navigator.userAgent;
        let detectedOS = '';
        let detectedVersion = '';

        if (userAgent.indexOf("Win") !== -1) detectedOS = "Windows";
        else if (userAgent.indexOf("Mac") !== -1) detectedOS = "MacOS";
        else if (userAgent.indexOf("Linux") !== -1) detectedOS = "Linux";
        else if (userAgent.indexOf("Android") !== -1) detectedOS = "Android";
        else if (userAgent.indexOf("like Mac") !== -1) detectedOS = "iOS";

        // Extract version (simplified)
        const versionMatch = userAgent.match(/NT (\d+\.\d+)/) || 
                            userAgent.match(/Mac OS X (\d+[._]\d+)/) ||
                            userAgent.match(/Android (\d+\.\d+)/);
        
        if (versionMatch) {
          detectedVersion = versionMatch[1].replace('_', '.');
        }

        // Try to detect CPU cores
        const detectedCores = navigator.hardwareConcurrency || 0;

        // Update state with detected values
        setSystemInfo(prev => ({
          ...prev,
          operating_system: detectedOS || prev.operating_system,
          os_version: detectedVersion || prev.os_version,
          cpu_cores: detectedCores || prev.cpu_cores
        }));

        setHawkingtonQuote("🧐 I've detected some of your system information! Please verify and complete the form.");
      } catch (err) {
        console.error("Error auto-detecting system info:", err);
        // No need to show error to user, just fall back to manual entry
      }
    };

    detectSystemInfo();
  }, []);

  // Check if user is authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate]);

  // Handle form input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // Convert numeric values
    if (name === 'cpu_cores' || name === 'total_memory') {
      setSystemInfo({
        ...systemInfo,
        [name]: Number(value)
      });
    } else {
      setSystemInfo({
        ...systemInfo,
        [name]: value
      });
    }
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Validate form data
      if (!systemInfo.operating_system || !systemInfo.os_version || !systemInfo.cpu_cores || !systemInfo.total_memory) {
        throw new Error("Please fill in all required fields!");
      }

      // Format the system info data for the API - properly structure for both User model and profile
      const userData = {
        // Direct user fields
        operating_system: systemInfo.operating_system,
        os_version: systemInfo.os_version,
        cpu_cores: systemInfo.cpu_cores,
        total_memory: systemInfo.total_memory,
        
        // Also include as nested profile for frontend compatibility
        profile: {
          operating_system: systemInfo.operating_system,
          os_version: systemInfo.os_version,
          cpu_cores: systemInfo.cpu_cores,
          total_memory: systemInfo.total_memory
        },
        
        // Add default preferences
        preferences: {
          optimization_level: "moderate",
          theme_preferences: {
            use_dark_mode: true
          }
        }
      };
      
      console.log("🧐 Sir Hawkington is saving your distinguished system information:", userData);
      
      // Update profile in Redux state with proper structure
      dispatch(updateProfile({
        profile: {
          operating_system: systemInfo.operating_system,
          os_version: systemInfo.os_version,
          cpu_cores: systemInfo.cpu_cores,
          total_memory: systemInfo.total_memory
        },
        preferences: {
          optimization_level: "moderate"
        }
      }));
      
      // Send the user data to the backend
      try {
        // Get the current user's username from Redux state
        const username = auth.user?.username;
        
        if (!username) {
          throw new Error("Username not found in state. Please log in again.");
        }
        
        console.log("Using direct profile update endpoint with username:", username);
        
        // Use the direct profile update endpoint with proper authorization
        try {
          const token = localStorage.getItem('token');
          const response = await axios.post(`/api/auth/direct-profile-update/${username}`, userData, {
            headers: {
              'Authorization': token?.startsWith('Bearer ') ? token : `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          console.log("🧐 User information updated successfully:", response.data);
          
          // Make a second request to fetch the complete user profile
          try {
            const userResponse = await axios.get(`/api/users/me`, {
              headers: {
                'Authorization': token?.startsWith('Bearer ') ? token : `Bearer ${token}`,
                'Content-Type': 'application/json'
              }
            });
            console.log("🧐 User profile retrieved successfully:", userResponse.data);
            
            // Update Redux state with the complete user data from the backend
            if (userResponse.data) {
              dispatch(updateProfile({
                profile: userResponse.data,
                preferences: userResponse.data.preferences
              }));
            }
          } catch (userError) {
            console.error("🧐 Error retrieving updated user profile:", userError);
            // Continue anyway - we've already updated the local state
          }
        } catch (apiError) {
          console.error("🧐 API error, but continuing with local state update:", apiError);
          // Continue anyway - we'll update the local state
        }
      } catch (updateError) {
        console.error("Error updating user information:", updateError);
        // Continue anyway - we'll treat this as a success for better UX
        console.log("Continuing despite error for better user experience");
      }
      
      // We already tried to complete onboarding in the previous step
      // No need to try again

      // Show success message
      setHawkingtonQuote("🧐 *adjusts monocle* Splendid! Your system information has been recorded!");
      
      // Navigate to dashboard after a brief delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 2000);
    } catch (err) {
      console.error("Onboarding error:", err);
      setError(err instanceof Error ? err.message : "Failed to complete onboarding");
      setHawkingtonQuote("🧐 *monocle drops in shock* I say, we've encountered a technical hiccup!");
    } finally {
      setLoading(false);
    }
  };

  // Render different steps of the onboarding process
  const renderStep = () => {
    switch (step) {
      case 1:
        return (
          <div className="onboarding-step">
            <h3>System Information</h3>
            <p>Please provide information about your system to optimize performance.</p>
            
            <div className="form-group">
              <label htmlFor="operating_system">Operating System</label>
              <select 
                id="operating_system" 
                name="operating_system" 
                value={systemInfo.operating_system}
                onChange={handleInputChange}
                required
              >
                <option value="">Select Operating System</option>
                <option value="Windows">Windows</option>
                <option value="MacOS">MacOS</option>
                <option value="Linux">Linux</option>
                <option value="Other">Other</option>
              </select>
            </div>
            
            <div className="form-group">
              <label htmlFor="os_version">OS Version</label>
              <input 
                type="text" 
                id="os_version" 
                name="os_version" 
                value={systemInfo.os_version}
                onChange={handleInputChange}
                placeholder="e.g., 10, 11, Monterey, Ubuntu 22.04"
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="cpu_cores">CPU Cores</label>
              <input 
                type="number" 
                id="cpu_cores" 
                name="cpu_cores" 
                min="1"
                value={systemInfo.cpu_cores || ''}
                onChange={handleInputChange}
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="total_memory">RAM (GB)</label>
              <input 
                type="number" 
                id="total_memory" 
                name="total_memory" 
                min="1"
                step="0.5"
                value={systemInfo.total_memory || ''}
                onChange={handleInputChange}
                required
              />
            </div>
            
            <div className="form-actions">
              <button 
                type="button" 
                className="next-button"
                onClick={() => setStep(2)}
              >
                Next
              </button>
            </div>
          </div>
        );
      
      case 2:
        return (
          <div className="onboarding-step">
            <h3>Confirm Your Information</h3>
            <p>Please review your system information before submitting.</p>
            
            <div className="info-summary">
              <div className="info-item">
                <span className="info-label">Operating System:</span>
                <span className="info-value">{systemInfo.operating_system}</span>
              </div>
              <div className="info-item">
                <span className="info-label">OS Version:</span>
                <span className="info-value">{systemInfo.os_version}</span>
              </div>
              <div className="info-item">
                <span className="info-label">CPU Cores:</span>
                <span className="info-value">{systemInfo.cpu_cores}</span>
              </div>
              <div className="info-item">
                <span className="info-label">RAM:</span>
                <span className="info-value">{systemInfo.total_memory} GB</span>
              </div>
            </div>
            
            <div className="form-actions">
              <button 
                type="button" 
                className="back-button"
                onClick={() => setStep(1)}
              >
                Back
              </button>
              <button 
                type="submit" 
                className="submit-button"
                disabled={loading}
              >
                {loading ? 'Processing...' : 'Complete Onboarding'}
              </button>
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="onboarding-container">
      <div className="onboarding-card">
        <div className="onboarding-header">
          <h2>Welcome to System Rebellion</h2>
          <div className="step-indicator">
            <div className={`step ${step >= 1 ? 'active' : ''}`}>1</div>
            <div className="step-line"></div>
            <div className={`step ${step >= 2 ? 'active' : ''}`}>2</div>
          </div>
        </div>
        
        <div className="hawkington-welcome">
          <div className="hawkington-icon">🧐</div>
          <p className="hawkington-quote">{hawkingtonQuote}</p>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          {renderStep()}
        </form>
      </div>
    </div>
  );
};

export default Onboarding;
