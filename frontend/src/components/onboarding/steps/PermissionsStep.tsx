// components/onboarding/steps/PermissionsStep.tsx
import React, { useState } from 'react';

import { useOnboarding } from '../../../hooks/useOnboarding';
import { StepNavigation } from '../components/StepNavigation';
import { useSystemDetection } from '../hooks/useSystemDetection';
import type { StepProps } from '../OnboardingFlow';
import { getInstallCommand } from '../utils/installCommands';

const copyToClipboard = (text: string) => {
  if (navigator.clipboard) {
    navigator.clipboard.writeText(text).catch(err => {
      console.error('Failed to copy text: ', err);
    });
  }
};

export const PermissionsStep: React.FC<StepProps> = ({ onNext, onBack }) => {
  const { state, dispatch } = useOnboarding();
  const osType = useSystemDetection();

  // Initialize from context state
  const [permissionsGranted, setPermissionsGranted] = useState(
    state.system.permissions_granted || false
  );
  const [installMethod, setInstallMethod] = useState(
    state.system.installation_method || ''
  );

  const getInstructions = () => {
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
            { id: 'installer', name: 'Windows Installer (In Development)', desc: 'Coming soon - use web dashboard for now' },
            { id: 'manual', name: 'Early Access Preview', desc: 'Contact support for development preview' }
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
            { id: 'homebrew', name: 'Homebrew Package (Coming Soon)', desc: 'Agent package in development for Homebrew' },
            { id: 'installer', name: 'macOS Installer (In Development)', desc: 'DMG installer coming in next release' },
            { id: 'manual', name: 'Early Access Preview', desc: 'Contact support for development access' }
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
            { id: 'apt', name: 'APT Package (Coming Soon)', desc: 'Debian/Ubuntu packages in development' },
            { id: 'yum', name: 'RPM Package (Coming Soon)', desc: 'RedHat/Fedora packages in development' },
            { id: 'pacman', name: 'AUR Package (Coming Soon)', desc: 'Arch Linux package in development' },
            { id: 'script', name: 'Early Access Preview', desc: 'Contact support for development access' }
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
  
  const handleContinue = () => {
    // Dispatch to context
    dispatch({ 
      type: 'SET_PERMISSIONS', 
      payload: { 
        permissions_granted: permissionsGranted, 
        method: installMethod 
      } 
    });
    onNext();
  };

return (
    <div className="d-flex flex-col gap-4">
      <div>
        <p className="text-lg mb-3">
          System Rebellion's AI agents need access to monitor and optimize your system.
          This requires elevated permissions to read metrics and make adjustments.
        </p>
      </div>

      <div className="card">
        <div className="card-body">
          <div className="d-flex align-center gap-2 mb-3">
            <span className="text-dim">Detected Operating System:</span>
            <span className="badge badge-primary">{osType.toUpperCase()}</span>
          </div>

          <h4 className="card-title">{instructions.title}</h4>
          <p className="text-sm text-dim mb-2">The following permissions are required:</p>
          <ul className="d-flex flex-col gap-1 mb-0" style={{ paddingLeft: '1.5rem' }}>
            {instructions.requirements.map((req, index) => (
              <li key={index} className="text-sm">{req}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="card">
        <div className="card-header">
          <h4 className="card-title">Choose Installation Method</h4>
        </div>
        <div className="card-body d-flex flex-col gap-2">
          {instructions.methods.map((method) => (
            <label key={method.id} className="d-flex gap-3 p-3 rebellion-card" style={{ cursor: 'pointer' }}>
              <input
                type="radio"
                name="install-method"
                value={method.id}
                checked={installMethod === method.id}
                onChange={(e) => setInstallMethod(e.target.value)}
              />
              <div className="d-flex flex-col gap-1">
                <span className="font-medium">{method.name}</span>
                <span className="text-sm text-dim">{method.desc}</span>
              </div>
            </label>
          ))}
        </div>
      </div>

      {installMethod && (
        <div className="card">
          <div className="card-header d-flex justify-between align-center">
            <h4 className="card-title">Installation Instructions</h4>
            <button
              className="btn btn-secondary btn-sm"
              onClick={() => copyToClipboard(getInstallCommand(osType, installMethod))}
            >
              Copy Command
            </button>
          </div>
          <div className="card-body">
            <pre className="form-textarea font-mono text-sm p-3" style={{ background: 'var(--rebellion-void)' }}>
              <code>{getInstallCommand(osType, installMethod)}</code>
            </pre>
          </div>
        </div>
      )}

      <div className="card">
        <div className="card-body">
          <label className="d-flex gap-3">
            <input
              type="checkbox"
              checked={permissionsGranted}
              onChange={(e) => setPermissionsGranted(e.target.checked)}
              style={{ marginTop: '4px' }}
            />
            <span className="text-sm">
              I understand and authorize System Rebellion to access system metrics,
              manage processes, and perform optimizations as configured by my agent preferences.
            </span>
          </label>
        </div>
      </div>

      <div className="alert alert-info">
        <strong>Privacy Notice:</strong> All metrics are processed locally.
        Only aggregated patterns are stored for AI learning.
        You can revoke permissions at any time from the dashboard.
      </div>

      <StepNavigation
        onBack={onBack}
        onNext={handleContinue}
        canContinue={permissionsGranted && !!installMethod}
        nextLabel="Continue Configuration"
      />
    </div>
  );
};