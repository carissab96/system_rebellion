// components/onboarding/steps/SystemProfileStep.tsx

import React, { useState, useEffect } from 'react';
import { useOnboarding } from '../OnboardingContext';
import type { StepProps } from '../OnboardingFlow'; // Assuming StepProps is exported from here

export const SystemProfileStep: React.FC<StepProps> = ({ onNext, onBack }) => {
  const { state, dispatch } = useOnboarding();
  const [systemInfo, setSystemInfo] = useState(state.system.system_profile);
  const [detectionStatus, setDetectionStatus] = useState('detecting');

  useEffect(() => {
    if (!systemInfo.os_type) {
      autoDetectSystemInfo();
    } else {
      setDetectionStatus('success');
    }
  }, []);

  const autoDetectSystemInfo = async () => {
    try {
      const response = await fetch('/api/system/detect');
      if (response.ok) {
        const detected = await response.json();
        setSystemInfo(prevInfo => ({ ...prevInfo, ...detected }));
        setDetectionStatus('success');
      } else {
        setDetectionStatus('manual');
      }
    } catch (error) {
      console.error('System detection failed:', error);
      setDetectionStatus('manual');
    }
  };

  const handleChange = (field: string, value: any) => {
    setSystemInfo({ ...systemInfo, [field]: value });
  };

  const handleContinue = () => {
    dispatch({ type: 'UPDATE_SYSTEM_PROFILE', payload: systemInfo });
    dispatch({ type: 'ADJUST_DEFAULTS_FROM_PROFILE', payload: systemInfo });
    onNext();
  };

  return (
    <div className="system-profile-step">
      <div className="profile-header">
        <h3>System Profile</h3>
        <p className="profile-intro">
          We need to understand your system to configure the agents properly.
          {detectionStatus === 'detecting' && ' Detecting your system configuration...'}
          {detectionStatus === 'success' && ' We\'ve detected your system. Please verify the information.'}
          {detectionStatus === 'manual' && ' Please provide your system information manually.'}
        </p>
      </div>

      {detectionStatus === 'detecting' && (
        <div className="detection-spinner">
          <div className="spinner" />
          <p>Analyzing system configuration...</p>
        </div>
      )}

      {detectionStatus !== 'detecting' && (
        <>
          <div className="system-basics">
            <h4>Hardware Configuration</h4>
            
            <div className="form-row">
              <div className="form-group">
                <label>Operating System</label>
                <select 
                  value={systemInfo.os_type}
                  onChange={(e) => handleChange('os_type', e.target.value)}
                  className="system-select"
                >
                  <option value="">Select OS</option>
                  <option value="windows">Windows</option>
                  <option value="macos">macOS</option>
                  <option value="ubuntu">Ubuntu</option>
                  <option value="debian">Debian</option>
                  <option value="fedora">Fedora</option>
                  <option value="arch">Arch Linux</option>
                  <option value="other_linux">Other Linux</option>
                </select>
              </div>

              <div className="form-group">
                <label>OS Version</label>
                <input
                  type="text"
                  value={systemInfo.os_version}
                  onChange={(e) => handleChange('os_version', e.target.value)}
                  placeholder="e.g., Windows 11, macOS 14.0"
                  className="system-input"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>RAM (GB)</label>
                <input
                  type="number"
                  value={systemInfo.total_ram_gb}
                  onChange={(e) => handleChange('total_ram_gb', parseInt(e.target.value))}
                  min="1"
                  max="1024"
                  className="system-input"
                />
              </div>

              <div className="form-group">
                <label>CPU Cores</label>
                <input
                  type="number"
                  value={systemInfo.cpu_cores}
                  onChange={(e) => handleChange('cpu_cores', parseInt(e.target.value))}
                  min="1"
                  max="128"
                  className="system-input"
                />
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Primary Storage Type</label>
                <select 
                  value={systemInfo.storage_type}
                  onChange={(e) => handleChange('storage_type', e.target.value)}
                  className="system-select"
                >
                  <option value="">Select Type</option>
                  <option value="ssd">SSD (Solid State)</option>
                  <option value="hdd">HDD (Traditional)</option>
                  <option value="nvme">NVMe</option>
                  <option value="hybrid">Hybrid</option>
                  <option value="raid">RAID Array</option>
                </select>
              </div>

              <div className="form-group">
                <label>Total Storage (GB)</label>
                <input
                  type="number"
                  value={systemInfo.total_storage_gb}
                  onChange={(e) => handleChange('total_storage_gb', parseInt(e.target.value))}
                  min="10"
                  max="100000"
                  className="system-input"
                />
              </div>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={systemInfo.is_virtual}
                  onChange={(e) => handleChange('is_virtual', e.target.checked)}
                />
                <span>This is a virtual machine</span>
              </label>
            </div>
          </div>

          <div className="system-environment">
            <h4>Environment & Restrictions</h4>
            <p className="section-intro">
              Understanding your environment helps us configure agents appropriately.
            </p>

            <div className="form-group">
              <label>Network Type</label>
              <select 
                value={systemInfo.network_type}
                onChange={(e) => handleChange('network_type', e.target.value)}
                className="system-select"
              >
                <option value="standard">Standard (Home/Small Office)</option>
                <option value="enterprise">Enterprise Network</option>
                <option value="isolated">Isolated/Air-gapped</option>
                <option value="vpn_required">VPN Required</option>
                <option value="proxy_required">Proxy Required</option>
              </select>
            </div>

            <div className="form-group">
              <label>Administrative Access</label>
              <select 
                value={systemInfo.admin_access}
                onChange={(e) => handleChange('admin_access', e.target.value)}
                className="system-select"
              >
                <option value="full">Full Admin/Root Access</option>
                <option value="sudo">Sudo Access (Password Required)</option>
                <option value="limited">Limited Admin Rights</option>
                <option value="none">No Admin Access</option>
              </select>
            </div>

            <div className="form-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={systemInfo.mdm_controlled}
                  onChange={(e) => handleChange('mdm_controlled', e.target.checked)}
                />
                <span>This system is managed by MDM/Group Policy</span>
              </label>
              {systemInfo.mdm_controlled && (
                <div className="mdm-warning">
                  <p>MDM-controlled systems may have restrictions. We'll configure agents to work within your policy limits.</p>
                </div>
              )}
            </div>

            <div className="form-group">
              <label>Known Restrictions (select all that apply)</label>
              <div className="restrictions-list">
                {[
                  { id: 'no_install', label: 'Cannot install software' },
                  { id: 'no_scripts', label: 'Cannot run scripts' },
                  { id: 'no_registry', label: 'Cannot modify registry (Windows)' },
                  { id: 'no_kernel', label: 'Cannot load kernel modules (Linux)' },
                  { id: 'no_network_changes', label: 'Cannot modify network settings' },
                  { id: 'limited_disk_access', label: 'Limited disk access' },
                  { id: 'process_whitelist', label: 'Process whitelist enforced' }
                ].map(restriction => (
                  <label key={restriction.id} className="checkbox-label">
                    <input
                      type="checkbox"
                      checked={Array.isArray(systemInfo.custom_restrictions) && systemInfo.custom_restrictions.includes(restriction.id)}
                      onChange={(e) => {
                        const currentRestrictions = Array.isArray(systemInfo.custom_restrictions) ? systemInfo.custom_restrictions : [];
                        const restrictions = e.target.checked
                          ? [...currentRestrictions, restriction.id]
                          : currentRestrictions.filter(r => r !== restriction.id);
                        handleChange('custom_restrictions', restrictions);
                      }}
                    />
                    <span>{restriction.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {(systemInfo.admin_access === 'none' || (Array.isArray(systemInfo.custom_restrictions) && systemInfo.custom_restrictions.length > 2)) && (
            <div className="limited-mode-info">
              <h4>Limited Mode Configuration</h4>
              <p>Based on your restrictions, System Rebellion will operate in Limited Mode:</p>
              <ul>
                <li>Read-only metrics monitoring</li>
                <li>AI analysis and recommendations without automatic actions</li>
                <li>Export scripts for manual execution by administrators</li>
                <li>Focus on pattern learning and advisory role</li>
              </ul>
              <p className="limited-note">
                Your AI agents will still learn and provide valuable insights, 
                but will require manual intervention for system changes.
              </p>
            </div>
          )}
        </>
      )}

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button 
          className="onboarding-button primary" 
          onClick={handleContinue}
          disabled={detectionStatus === 'detecting' || !systemInfo.os_type || !systemInfo.total_ram_gb}
        >
          Continue
        </button>
      </div>
    </div>
  );
};