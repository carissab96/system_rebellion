// components/onboarding/steps/PermissionsStep.tsx

import React, { useState } from 'react';

// --- Our new, clean imports ---
import { useSystemDetection } from '../hooks/useSystemDetection';
import { getInstallCommand } from '../utils/installCommands';

// A functional helper for the "Copy Command" button
const copyToClipboard = (text: string) => {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).catch(err => {
      console.error('Failed to copy text: ', err);
      // Fallback for older browsers could be implemented here if needed
    });
  }
};

export const PermissionsStep: React.FC<any> = ({ data, updateData, onNext, onBack }) => {
  // The old OS detection logic is now replaced with this single line
  const osType = useSystemDetection();

  // State local to this component
  const [permissionsGranted, setPermissionsGranted] = useState(data.permissions_granted || false);
  const [installMethod, setInstallMethod] = useState(data.installation_method || '');

  // This helper function is specific to this component's UI, so it can stay
  const getInstructions = () => {
    // ... (This function's content is the same as before)
    switch (osType) {
      case 'windows':
        return {
          title: 'Windows System Access',
          requirements: [
            'Administrator privileges for process management',
            'WMI access for system metrics',
            'PowerShell execution for optimizations'
          ],
          methods: [
            { id: 'installer', name: 'System Rebellion Agent Installer (Recommended)', desc: 'Downloads and configures everything automatically' },
            { id: 'manual', name: 'Manual PowerShell Setup', desc: 'For advanced users who want to review scripts' }
          ]
        };
      case 'macos':
        return {
          title: 'macOS System Access',
          requirements: [
            'System Preferences → Security & Privacy permissions',
            'Terminal access for system metrics',
            'Activity Monitor permissions for process management'
          ],
          methods: [
            { id: 'homebrew', name: 'Homebrew Installation (Recommended)', desc: 'brew install system-rebellion-agent' },
            { id: 'installer', name: 'DMG Installer', desc: 'Traditional macOS installer with permission prompts' },
            { id: 'manual', name: 'Manual Setup', desc: 'Python script with sudo access' }
          ]
        };
      case 'linux':
        return {
          title: 'Linux System Access',
          requirements: [
            'sudo/root access for system modifications',
            'systemd or init.d for service management',
            'Package manager access for dependencies'
          ],
          methods: [
            { id: 'apt', name: 'APT (Debian/Ubuntu)', desc: 'sudo apt install system-rebellion-agent' },
            { id: 'yum', name: 'YUM/DNF (RedHat/Fedora)', desc: 'sudo yum install system-rebellion-agent' },
            { id: 'pacman', name: 'Pacman (Arch)', desc: 'sudo pacman -S system-rebellion-agent' },
            { id: 'script', name: 'Universal Shell Script', desc: 'Works on any Linux distribution' }
          ]
        };
      default:
        return {
          title: 'System Access Required',
          requirements: ['System metrics access', 'Process management', 'Network monitoring'],
          methods: [{ id: 'manual', name: 'Manual Setup', desc: 'Contact support for your OS' }]
        };
    }
  };

  const instructions = getInstructions();
  
  // New handler to save data before navigating
  const handleContinue = () => {
    updateData({ 
      ...data, 
      permissions_granted: permissionsGranted, 
      installation_method: installMethod 
    });
    onNext();
  };

  return (
    <div className="permissions-step">
      <div className="permissions-header">
        <h3>System Access Configuration</h3>
        <p className="permissions-intro">
          System Rebellion's AI agents need access to monitor and optimize your system.
          This requires elevated permissions to read metrics and make adjustments.
        </p>
      </div>

      <div className="detected-os">
        <span className="os-label">Detected Operating System:</span>
        <span className="os-value">{osType.toUpperCase()}</span>
      </div>

      <div className="permissions-requirements">
        <h4>{instructions.title}</h4>
        <p className="requirements-intro">The following permissions are required:</p>
        <ul className="requirements-list">
          {instructions.requirements.map((req, index) => (
            <li key={index}>{req}</li>
          ))}
        </ul>
      </div>

      <div className="installation-methods">
        <h4>Choose Installation Method</h4>
        <div className="method-options">
          {instructions.methods.map((method) => (
            <label key={method.id} className="method-option">
              <input
                type="radio"
                name="install-method"
                value={method.id}
                checked={installMethod === method.id}
                onChange={(e) => setInstallMethod(e.target.value)}
              />
              <div className="method-details">
                <span className="method-name">{method.name}</span>
                <span className="method-desc">{method.desc}</span>
              </div>
            </label>
          ))}
        </div>
      </div>

      {installMethod && (
        <div className="installation-instructions">
          <h4>Installation Instructions</h4>
          <pre className="code-block">
            <code>{getInstallCommand(osType, installMethod)}</code>
          </pre>
          <button
            className="copy-button"
            onClick={() => copyToClipboard(getInstallCommand(osType, installMethod))}
          >
            Copy Command
          </button>
        </div>
      )}

      {/* --- THIS IS THE SECTION I MISTAKENLY OMITTED --- */}
      <div className="permissions-consent">
        <label className="consent-checkbox">
          <input
            type="checkbox"
            checked={permissionsGranted}
            onChange={(e) => setPermissionsGranted(e.target.checked)}
          />
          <span>
            I understand and authorize System Rebellion to access system metrics,
            manage processes, and perform optimizations as configured by my agent preferences.
          </span>
        </label>
      </div>

      <div className="permissions-notice">
        <p className="notice-text">
          <strong>Privacy Notice:</strong> All metrics are processed locally.
          Only aggregated patterns are stored for AI learning.
          You can revoke permissions at any time from the dashboard.
        </p>
      </div>
      {/* --- END OF OMITTED SECTION --- */}

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button
          className="onboarding-button primary"
          // IMPORTANT: This now calls our new handler function
          onClick={handleContinue}
          disabled={!permissionsGranted || !installMethod}
        >
          Continue Configuration
        </button>
      </div>
    </div>
  );
};