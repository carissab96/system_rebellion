// src/pages/OnboardingPage.tsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './OnboardingPage.css';
import type { User } from '../types/auth';

interface OnboardingFormData {
  systemName: string;
  operatingSystem: string;
  cpuCores: number;
  ramGB: number;
  storageGB: number;
  primaryUseCase: string;
  monitoringPreferences: {
    alertThreshold: string;
    reportFrequency: string;
    autoOptimization: boolean;
    realTimeAlerts: boolean;
  };
  agentPreferences: {
    hawkingtonSensitivity: string;
    snailAggressiveness: string;
    hamsterResponseLevel: string;
    stickComplianceLevel: string;
    qspNetworkFocus: string;
    vic20CoordinationMode: string;
  };
}

interface OnboardingResponse {
  success: boolean;
  message: string;
  user: {
    id: string;
    email: string;
    isOnboarded: boolean;
  };
}

interface OnboardingPageProps {
  user: User;
  token: string;
  onComplete: (updatedUser: User) => void;
}

export default function OnboardingPage({ user, token, onComplete }: OnboardingPageProps) {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  
  const [formData, setFormData] = useState<OnboardingFormData>({
    systemName: '',
    operatingSystem: '',
    cpuCores: 1,
    ramGB: 1,
    storageGB: 10,
    primaryUseCase: '',
    monitoringPreferences: {
      alertThreshold: 'balanced',
      reportFrequency: 'weekly',
      autoOptimization: true,
      realTimeAlerts: true
    },
    agentPreferences: {
      hawkingtonSensitivity: 'standard',
      snailAggressiveness: 'balanced',
      hamsterResponseLevel: 'moderate',
      stickComplianceLevel: 'standard',
      qspNetworkFocus: 'balanced',
      vic20CoordinationMode: 'adaptive'
    }
  });

  // Check if user is authenticated
  useEffect(() => {
    if (!token) {
      navigate('/');
    }
  }, [navigate, token]);

  const validateStep = (step: number): boolean => {
    const newErrors: Record<string, string> = {};
    
    switch (step) {
      case 1:
        if (!formData.systemName.trim()) {
          newErrors.systemName = 'System name is required';
        }
        if (!formData.operatingSystem) {
          newErrors.operatingSystem = 'Operating system is required';
        }
        if (formData.cpuCores < 1 || formData.cpuCores > 256) {
          newErrors.cpuCores = 'CPU cores must be between 1 and 256';
        }
        if (formData.ramGB < 1 || formData.ramGB > 1024) {
          newErrors.ramGB = 'RAM must be between 1GB and 1024GB';
        }
        if (formData.storageGB < 10 || formData.storageGB > 100000) {
          newErrors.storageGB = 'Storage must be between 10GB and 100TB';
        }
        break;
      case 2:
        if (!formData.primaryUseCase.trim()) {
          newErrors.primaryUseCase = 'Primary use case is required';
        }
        break;
      case 3:
        // Monitoring preferences are optional with defaults
        break;
      case 4:
        // Agent preferences are optional with defaults
        break;
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep(prev => Math.min(prev + 1, 4));
    }
  };

  const handlePrevious = () => {
    setCurrentStep(prev => Math.max(prev - 1, 1));
  };

  const handleSubmit = async () => {
    if (!validateStep(currentStep)) return;
    
    setIsSubmitting(true);
    setErrors({});
    
    try {
      const response = await fetch('/api/users/complete-onboarding', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          system_name: formData.systemName,
          operating_system: formData.operatingSystem,
          cpu_cores: formData.cpuCores,
          ram_gb: formData.ramGB,
          storage_gb: formData.storageGB,
          primary_use_case: formData.primaryUseCase,
          monitoring_preferences: formData.monitoringPreferences,
          agent_preferences: formData.agentPreferences
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Onboarding failed');
      }

      const data: OnboardingResponse = await response.json();
      console.log('Onboarding completed:', data);

      // Create updated user object
      const updatedUser: User = {
        ...user,
        isOnboarded: true
      };
      
      // Call the onComplete callback
      onComplete(updatedUser);
      
    } catch (error) {
      console.error('Onboarding error:', error);
      setErrors({ 
        submit: error instanceof Error ? error.message : 'Onboarding failed. Please try again.' 
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const renderStep1 = () => (
    <div className="onboarding-step">
      <div className="step-header">
        <h2 className="vic20-text">System Information</h2>
        <p className="step-subtitle">
          Tell us about your system so our AI agents can optimize performance
        </p>
      </div>

      <div className="form-grid">
        <div className="form-group">
          <label className="form-label" htmlFor="systemName">
            System Name
          </label>
          <input
            id="systemName"
            type="text"
            className={`form-input ${errors.systemName ? 'error' : ''}`}
            value={formData.systemName}
            onChange={(e) => setFormData({...formData, systemName: e.target.value})}
            placeholder="Production Server 01"
          />
          {errors.systemName && (
            <span className="form-error">{errors.systemName}</span>
          )}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="operatingSystem">
            Operating System
          </label>
          <select
            id="operatingSystem"
            className={`form-input form-select ${errors.operatingSystem ? 'error' : ''}`}
            value={formData.operatingSystem}
            onChange={(e) => setFormData({...formData, operatingSystem: e.target.value})}
          >
            <option value="">Select OS</option>
            <option value="Windows">Windows</option>
            <option value="Linux">Linux</option>
            <option value="macOS">macOS</option>
            <option value="Unix">Unix</option>
          </select>
          {errors.operatingSystem && (
            <span className="form-error">{errors.operatingSystem}</span>
          )}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="cpuCores">
            CPU Cores
          </label>
          <input
            id="cpuCores"
            type="number"
            min="1"
            max="256"
            className={`form-input ${errors.cpuCores ? 'error' : ''}`}
            value={formData.cpuCores}
            onChange={(e) => setFormData({...formData, cpuCores: parseInt(e.target.value) || 1})}
          />
          {errors.cpuCores && (
            <span className="form-error">{errors.cpuCores}</span>
          )}
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="ramGB">
            RAM (GB)
          </label>
          <input
            id="ramGB"
            type="number"
            min="1"
            max="1024"
            className={`form-input ${errors.ramGB ? 'error' : ''}`}
            value={formData.ramGB}
            onChange={(e) => setFormData({...formData, ramGB: parseInt(e.target.value) || 1})}
          />
          {errors.ramGB && (
            <span className="form-error">{errors.ramGB}</span>
          )}
        </div>

        <div className="form-group form-group-full">
          <label className="form-label" htmlFor="storageGB">
            Storage (GB)
          </label>
          <input
            id="storageGB"
            type="number"
            min="10"
            max="100000"
            className={`form-input ${errors.storageGB ? 'error' : ''}`}
            value={formData.storageGB}
            onChange={(e) => setFormData({...formData, storageGB: parseInt(e.target.value) || 10})}
          />
          {errors.storageGB && (
            <span className="form-error">{errors.storageGB}</span>
          )}
        </div>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="onboarding-step">
      <div className="step-header">
        <h2 className="vic20-text">Use Case & Requirements</h2>
        <p className="step-subtitle">
          Help our agents understand your primary system usage
        </p>
      </div>

      <div className="form-group">
        <label className="form-label" htmlFor="primaryUseCase">
          Primary Use Case
        </label>
        <select
          id="primaryUseCase"
          className={`form-input form-select ${errors.primaryUseCase ? 'error' : ''}`}
          value={formData.primaryUseCase}
          onChange={(e) => setFormData({...formData, primaryUseCase: e.target.value})}
        >
          <option value="">Select use case</option>
          <option value="web_server">Web Server</option>
          <option value="database_server">Database Server</option>
          <option value="application_server">Application Server</option>
          <option value="development_workstation">Development Workstation</option>
          <option value="ci_cd_pipeline">CI/CD Pipeline</option>
          <option value="data_processing">Data Processing</option>
          <option value="machine_learning">Machine Learning</option>
          <option value="file_server">File Server</option>
          <option value="virtualization_host">Virtualization Host</option>
          <option value="other">Other</option>
        </select>
        {errors.primaryUseCase && (
          <span className="form-error">{errors.primaryUseCase}</span>
        )}
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div className="onboarding-step">
      <div className="step-header">
        <h2 className="vic20-text">Monitoring Preferences</h2>
        <p className="step-subtitle">
          Configure how you want to receive alerts and reports
        </p>
      </div>

      <div className="form-grid">
        <div className="form-group">
          <label className="form-label" htmlFor="alertThreshold">
            Alert Sensitivity
          </label>
          <select
            id="alertThreshold"
            className="form-input form-select"
            value={formData.monitoringPreferences.alertThreshold}
            onChange={(e) => setFormData({
              ...formData, 
              monitoringPreferences: {
                ...formData.monitoringPreferences,
                alertThreshold: e.target.value
              }
            })}
          >
            <option value="conservative">Conservative (Fewer alerts)</option>
            <option value="balanced">Balanced (Recommended)</option>
            <option value="aggressive">Aggressive (More alerts)</option>
          </select>
        </div>

        <div className="form-group">
          <label className="form-label" htmlFor="reportFrequency">
            Report Frequency
          </label>
          <select
            id="reportFrequency"
            className="form-input form-select"
            value={formData.monitoringPreferences.reportFrequency}
            onChange={(e) => setFormData({
              ...formData, 
              monitoringPreferences: {
                ...formData.monitoringPreferences,
                reportFrequency: e.target.value
              }
            })}
          >
            <option value="daily">Daily</option>
            <option value="weekly">Weekly (Recommended)</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
      </div>

      <div className="checkbox-grid">
        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.monitoringPreferences.autoOptimization}
            onChange={(e) => setFormData({
              ...formData, 
              monitoringPreferences: {
                ...formData.monitoringPreferences,
                autoOptimization: e.target.checked
              }
            })}
          />
          <span className="checkmark"></span>
          Enable automatic optimization
        </label>

        <label className="checkbox-label">
          <input
            type="checkbox"
            checked={formData.monitoringPreferences.realTimeAlerts}
            onChange={(e) => setFormData({
              ...formData, 
              monitoringPreferences: {
                ...formData.monitoringPreferences,
                realTimeAlerts: e.target.checked
              }
            })}
          />
          <span className="checkmark"></span>
          Real-time alert notifications
        </label>
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="onboarding-step">
      <div className="step-header">
        <h2 className="vic20-text">AI Agent Configuration</h2>
        <p className="step-subtitle">
          Configure how each AI agent should behave for your system
        </p>
      </div>

      <div className="agent-config-grid">
        <div className="agent-config-card hawkington-panel">
          <h4 className="hawkington-text">🧐 Sir Hawkington - System Monitor</h4>
          <div className="form-group">
            <label className="form-label">Monitoring Sensitivity</label>
            <select
              className="form-input form-select"
              value={formData.agentPreferences.hawkingtonSensitivity}
              onChange={(e) => setFormData({
                ...formData, 
                agentPreferences: {
                  ...formData.agentPreferences,
                  hawkingtonSensitivity: e.target.value
                }
              })}
            >
              <option value="conservative">Conservative</option>
              <option value="standard">Standard</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>
        </div>

        <div className="agent-config-card snail-panel">
          <h4 className="snail-text">🐌💨 Meth Snail - Optimizer</h4>
          <div className="form-group">
            <label className="form-label">Optimization Aggressiveness</label>
            <select
              className="form-input form-select"
              value={formData.agentPreferences.snailAggressiveness}
              onChange={(e) => setFormData({
                ...formData, 
                agentPreferences: {
                  ...formData.agentPreferences,
                  snailAggressiveness: e.target.value
                }
              })}
            >
              <option value="conservative">Conservative</option>
              <option value="balanced">Balanced</option>
              <option value="aggressive">Maximum Speed</option>
            </select>
          </div>
        </div>

        <div className="agent-config-card hamster-panel">
          <h4 className="hamster-text">🐹 The Hamsters - Engineers</h4>
          <div className="form-group">
            <label className="form-label">Response Level</label>
            <select
              className="form-input form-select"
              value={formData.agentPreferences.hamsterResponseLevel}
              onChange={(e) => setFormData({
                ...formData, 
                agentPreferences: {
                  ...formData.agentPreferences,
                  hamsterResponseLevel: e.target.value
                }
              })}
            >
              <option value="minimal">Minimal</option>
              <option value="moderate">Moderate</option>
              <option value="maximum">Maximum Duct Tape</option>
            </select>
          </div>
        </div>

        <div className="agent-config-card stick-panel">
          <h4 className="stick-text">📏 The Stick - Compliance</h4>
          <div className="form-group">
            <label className="form-label">Compliance Level</label>
            <select
              className="form-input form-select"
              value={formData.agentPreferences.stickComplianceLevel}
              onChange={(e) => setFormData({
                ...formData, 
                agentPreferences: {
                  ...formData.agentPreferences,
                  stickComplianceLevel: e.target.value
                }
              })}
            >
              <option value="relaxed">Relaxed</option>
              <option value="standard">Standard</option>
              <option value="strict">Strict</option>
            </select>
          </div>
        </div>

        <div className="agent-config-card qsp-panel">
          <h4 className="qsp-text">👻 Quantum Shadow People - Network</h4>
          <div className="form-group">
            <label className="form-label">Network Focus</label>
            <select
              className="form-input form-select"
              value={formData.agentPreferences.qspNetworkFocus}
              onChange={(e) => setFormData({
                ...formData, 
                agentPreferences: {
                  ...formData.agentPreferences,
                  qspNetworkFocus: e.target.value
                }
              })}
            >
              <option value="latency">Latency Optimization</option>
              <option value="balanced">Balanced</option>
              <option value="throughput">Throughput Optimization</option>
            </select>
          </div>
        </div>

        <div className="agent-config-card vic20-panel">
          <h4 className="vic20-text">🖥️ VIC-20 Sage - Coordinator</h4>
          <div className="form-group">
            <label className="form-label">Coordination Mode</label>
            <select
              className="form-input form-select"
              value={formData.agentPreferences.vic20CoordinationMode}
              onChange={(e) => setFormData({
                ...formData, 
                agentPreferences: {
                  ...formData.agentPreferences,
                  vic20CoordinationMode: e.target.value
                }
              })}
            >
              <option value="conservative">Conservative</option>
              <option value="balanced">Balanced</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>
        </div>
      </div>
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return renderStep1();
      case 2:
        return renderStep2();
      case 3:
        return renderStep3();
      case 4:
        return renderStep4();
      default:
        return renderStep1();
    }
  };

  const renderNavigationButtons = () => (
    <div className="onboarding-navigation">
      {currentStep > 1 && (
        <button
          type="button"
          className="btn btn-secondary"
          onClick={handlePrevious}
          disabled={isSubmitting}
        >
          Previous
        </button>
      )}
      
      <div className="navigation-spacer"></div>
      
      {currentStep < 4 ? (
        <button
          type="button"
          className="btn btn-primary vic20-panel"
          onClick={handleNext}
          disabled={isSubmitting}
        >
          Next
        </button>
      ) : (
        <button
          type="button"
          className="btn btn-primary hawkington-panel"
          onClick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? 'Completing Setup...' : 'Complete Setup'}
        </button>
      )}
    </div>
  );

  // THE MAIN RETURN STATEMENT - PROPERLY STRUCTURED
  return (
    <div className="onboarding-container">
      <div className="onboarding-header">
        <h1 className="vic20-text">System Rebellion Setup</h1>
        <p className="rebellion-text">Configure your AI agent coordination system</p>
        
        <div className="progress-bar">
          <div 
            className="progress-fill vic20-panel" 
            style={{ width: `${(currentStep / 4) * 100}%` }}
          ></div>
          <div className="progress-steps">
            <span className={`step-indicator ${currentStep >= 1 ? 'active' : ''}`}>1</span>
            <span className={`step-indicator ${currentStep >= 2 ? 'active' : ''}`}>2</span>
            <span className={`step-indicator ${currentStep >= 3 ? 'active' : ''}`}>3</span>
            <span className={`step-indicator ${currentStep >= 4 ? 'active' : ''}`}>4</span>
          </div>
        </div>
      </div>
      
      <div className="onboarding-content">
        {renderCurrentStep()}
      </div>
      
      {renderNavigationButtons()}
      
      {errors.submit && (
        <div className="error-message">
          <span className="error-icon">⚠️</span>
          {errors.submit}
        </div>
      )}
    </div>
  );
}