import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../../store/hooks';
import { updateProfile } from '../../store/slices/authSlice';
import { RootState } from '../../store/store';
import './onboarding.css';

// Define the system information interface
interface SystemInfo {
  operating_system: string;
  os_version: string;
  cpu_cores: number;
  total_memory: number;
}

const Onboarding: React.FC = () => {
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { isAuthenticated, isLoading: authLoading } = useAppSelector((state: RootState) => state.auth);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState(1);
  const [hawkingtonQuote, setHawkingtonQuote] = useState(" Sir Hawkington requires some information about your system!");

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

        setHawkingtonQuote(" I've detected some of your system information! Please verify and complete the form.");
      } catch (err) {
        console.error("Error auto-detecting system info:", err);
        // No need to show error to user, just fall back to manual entry
      }
    };

    detectSystemInfo();
  }, []);

  // Check if user is authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      navigate('/login');
    }
  }, [isAuthenticated, navigate, authLoading]);

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
      const requiredFields = {
        'Operating System': systemInfo.operating_system,
        'OS Version': systemInfo.os_version,
        'CPU Cores': systemInfo.cpu_cores,
        'RAM': systemInfo.total_memory
      };

      const missingFields = Object.entries(requiredFields)
        .filter(([_, value]) => !value)
        .map(([field]) => field);

      if (missingFields.length > 0) {
        throw new Error(`Please fill in the following required fields: ${missingFields.join(', ')}`);
      }

      // Validate numeric fields
      if (systemInfo.cpu_cores <= 0) {
        throw new Error('CPU Cores must be greater than 0');
      }
      if (systemInfo.total_memory <= 0) {
        throw new Error('RAM must be greater than 0');
      }

      // Update Hawkington quote
      setHawkingtonQuote(" Sir Hawkington is processing your system information with aristocratic precision!");

      console.log('Submitting onboarding data:', systemInfo);

      // Implement retry logic with a maximum of 3 attempts
      let retryCount = 0;
      const maxRetries = 3;
      let success = false;

      while (retryCount < maxRetries && !success) {
        try {
          console.log(`Attempt ${retryCount + 1} of ${maxRetries} to submit profile`);
          
          // Make the API call
          const result = await dispatch(updateProfile(systemInfo)).unwrap();
          success = true;
          console.log('Profile updated successfully!', result);
          
          // Check if onboarding status was updated properly
          if (result && result.needs_onboarding === false) {
            setHawkingtonQuote(" Splendid! Your system information has been recorded with utmost sophistication!");
            
            // Small delay for user to see success message
            setTimeout(() => {
              navigate('/dashboard');
            }, 1500);
          } else {
            throw new Error('Onboarding status not updated properly');
          }
          
          break; // Exit the loop on success
        } catch (retryError) {
          retryCount++;
          console.error(`Attempt ${retryCount} failed:`, retryError);
          
          if (retryCount >= maxRetries) {
            throw retryError; // Re-throw if we've used all retries
          }
          
          // Wait before retry (exponential backoff)
          await new Promise(resolve => setTimeout(resolve, 1000 * Math.pow(2, retryCount)));
        }
      }
    } catch (err: any) {
      console.error('Error during onboarding:', err);
      let errorMessage = 'An error occurred during onboarding';
      
      if (err.response?.status === 400) {
        errorMessage = 'Invalid data provided. Please check your input and try again.';
      } else if (err.response?.status === 401) {
        errorMessage = 'Your session has expired. Please log in again.';
        navigate('/login');
      } else if (err.response?.status === 500) {
        errorMessage = 'Server error. Please try again later.';
      }
      
      setError(err.message || errorMessage);
      setHawkingtonQuote(" Oh dear, it seems we've encountered a spot of bother!");
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
            <h3>Your System Information</h3>
            <p>Please provide details about your system to optimize your experience.</p>
            
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
