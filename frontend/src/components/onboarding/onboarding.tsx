import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { updateProfile } from '../../store/slices/authSlice';
import { useNavigate } from 'react-router-dom';
import './onboarding.css';
import axios from 'axios';

const Onboarding = () => {
  const dispatch = useDispatch();
  const navigate = useNavigate();
  
  // State for system data
  const [systemData, setSystemData] = useState({
    operating_system: 'Linux',
    os_version: '',
    linux_distro: '',
    linux_distro_version: '',
    cpu_cores: 4,
    total_memory: 8,
    system_usage: 'personal',
    performance_priority: 'balanced'
  });
  
  // State for UI
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hawkingtonQuote, setHawkingtonQuote] = useState("🧐 Sir Hawkington requires information about your distinguished system!");
  
  // Handle input changes - now properly used with form inputs
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    
    // For numeric fields, convert to numbers
    if (name === 'cpu_cores' || name === 'total_memory') {
      setSystemData(prev => ({
        ...prev,
        [name]: Number(value)
      }));
    } else {
      setSystemData(prev => ({
        ...prev,
        [name]: value
      }));
    }
  };
  
  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    
    try {
      // Get token from localStorage
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error("Authentication token not found");
      }
      
      // Update user profile with system data
      await dispatch(updateProfile({
        profile: systemData
      }));
      
      // Mark onboarding as complete on the backend
      await axios.post('/api/users/complete-onboarding', {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setHawkingtonQuote("🎩 Sir Hawkington is most pleased with your system configuration!");
      
      // Redirect to dashboard after a brief delay
      setTimeout(() => {
        navigate('/dashboard');
      }, 1500);
      
    } catch (err) {
      console.error("Failed to complete onboarding:", err);
      setError(err instanceof Error ? err.message : "Failed to complete onboarding");
      setHawkingtonQuote("🧐 Sir Hawkington regrets to inform you of a configuration error!");
      setIsSubmitting(false);
    }
  };
  
  return (
    <div className="onboarding-container">
      <div className="onboarding-header">
        <h1>System Configuration</h1>
        <p className="hawkington-quote">{hawkingtonQuote}</p>
      </div>
      
      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-section">
          <h2>Operating System</h2>
          
          <div className="form-group">
            <label htmlFor="operating_system">Operating System</label>
            <select
              id="operating_system"
              name="operating_system"
              value={systemData.operating_system}
              onChange={handleChange}
              disabled={isSubmitting}
            >
              <option value="Linux">Linux</option>
              <option value="Windows">Windows</option>
              <option value="MacOS">MacOS</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="os_version">OS Version</label>
            <input
              type="text"
              id="os_version"
              name="os_version"
              value={systemData.os_version}
              onChange={handleChange}
              disabled={isSubmitting}
              placeholder="e.g., 11, 10.15, 22.04"
            />
          </div>
          
          {systemData.operating_system === 'Linux' && (
            <>
              <div className="form-group">
                <label htmlFor="linux_distro">Linux Distribution</label>
                <input
                  type="text"
                  id="linux_distro"
                  name="linux_distro"
                  value={systemData.linux_distro}
                  onChange={handleChange}
                  disabled={isSubmitting}
                  placeholder="e.g., Ubuntu, Fedora, Arch"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="linux_distro_version">Distribution Version</label>
                <input
                  type="text"
                  id="linux_distro_version"
                  name="linux_distro_version"
                  value={systemData.linux_distro_version}
                  onChange={handleChange}
                  disabled={isSubmitting}
                  placeholder="e.g., 22.04, 37, Rolling"
                />
              </div>
            </>
          )}
        </div>
        
        <div className="form-section">
          <h2>Hardware Specifications</h2>
          
          <div className="form-group">
            <label htmlFor="cpu_cores">CPU Cores</label>
            <input
              type="number"
              id="cpu_cores"
              name="cpu_cores"
              value={systemData.cpu_cores}
              onChange={handleChange}
              disabled={isSubmitting}
              min="1"
              max="128"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="total_memory">Total Memory (GB)</label>
            <input
              type="number"
              id="total_memory"
              name="total_memory"
              value={systemData.total_memory}
              onChange={handleChange}
              disabled={isSubmitting}
              min="1"
              max="1024"
            />
          </div>
        </div>
        
        <div className="form-section">
          <h2>Usage Preferences</h2>
          
          <div className="form-group">
            <label htmlFor="system_usage">System Usage</label>
            <select
              id="system_usage"
              name="system_usage"
              value={systemData.system_usage}
              onChange={handleChange}
              disabled={isSubmitting}
            >
              <option value="personal">Personal</option>
              <option value="development">Development</option>
              <option value="server">Server</option>
              <option value="gaming">Gaming</option>
            </select>
          </div>
          
          <div className="form-group">
            <label htmlFor="performance_priority">Performance Priority</label>
            <select
              id="performance_priority"
              name="performance_priority"
              value={systemData.performance_priority}
              onChange={handleChange}
              disabled={isSubmitting}
            >
              <option value="balanced">Balanced</option>
              <option value="performance">Performance</option>
              <option value="battery">Battery Life</option>
              <option value="quiet">Quiet Operation</option>
            </select>
          </div>
        </div>
        
        <div className="form-actions">
          <button
            type="submit"
            className="submit-button"
            disabled={isSubmitting}
          >
            {isSubmitting ? 'Configuring...' : 'Complete Setup'}
          </button>
        </div>
      </form>
      
      <div className="onboarding-footer">
        <p>
          🐌 The Meth Snail will optimize your system based on these settings.
          <br />
          🐹 The Hamsters are standing by with configuration-grade duct tape!
        </p>
      </div>
    </div>
  );
};

export default Onboarding;