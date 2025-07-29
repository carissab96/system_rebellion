// components/onboarding/steps/SystemNameStep.tsx
import React, { useState } from 'react';
import { useOnboarding } from '../OnboardingContext';
import type { StepProps } from '../OnboardingFlow';
import { StepNavigation } from '../components/StepNavigation';

export const SystemNameStep: React.FC<StepProps> = ({ onNext, onBack }) => {
  const { state, dispatch } = useOnboarding();
  
  // Initialize local state from the global context
  const [systemName, setSystemName] = useState(state.system.system_name || '');

  const handleContinue = () => {
    // Dispatch the update to our global state
    dispatch({ type: 'UPDATE_SYSTEM', payload: { system_name: systemName } });
    onNext();
  };

  const isValid = !!systemName.trim();

  return (
    <div className="system-step">
      <div className="system-content">
        <p className="system-intro">
          Give your system a name. Your AI agents will use this to personalize
          their responses and build specific optimization strategies.
        </p>

        <div className="form-group large">
          <label htmlFor="system_name">System Name</label>
          <input
            id="system_name"
            type="text"
            value={systemName}
            onChange={(e) => setSystemName(e.target.value)}
            placeholder="Production Server Alpha"
            className="onboarding-input large"
          />
          <span className="input-hint">
            This is how your agents will refer to your infrastructure
          </span>
        </div>

        {systemName && (
          <div className="system-preview">
            <p className="preview-text">
              Sir Hawkington: "I shall monitor <span className="highlight">{systemName}</span> with aristocratic precision."
            </p>
          </div>
        )}
      </div>

      <StepNavigation 
        onNext={handleContinue}
        onBack={onBack}
        isNextDisabled={!isValid}
      />
    </div>
  );
};