// components/onboarding/steps/ProfileStep.tsx
import React, { useState } from 'react';
import { useOnboarding } from '../../../hooks/useOnboarding';
import type { StepProps } from '../OnboardingFlow';
import { StepNavigation } from '../components/StepNavigation'; // Import our new component

export const ProfileStep: React.FC<StepProps> = ({ onNext, onBack, isFirst }) => {
  const { state, dispatch } = useOnboarding();

  // Local state for the form, initialized from the context
  const [profile, setProfile] = useState(state.profile);

  const handleChange = (field: keyof typeof profile, value: string) => {
    setProfile({ ...profile, [field]: value });
  };

  const handleContinue = () => {
    // Save the local form state to the global context
    dispatch({ type: 'UPDATE_PROFILE', payload: profile });
    onNext();
  };

  // Validation logic to determine if the "Continue" button should be enabled
  const isValid = !!profile.first_name && !!profile.last_name;

  return (
    <div className="profile-step">
      <div className="form-group">
        <label htmlFor="first_name">First Name</label>
        <input
          id="first_name"
          type="text"
          value={profile.first_name}
          onChange={(e) => handleChange('first_name', e.target.value)}
          placeholder="John"
          className="onboarding-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="last_name">Last Name</label>
        <input
          id="last_name"
          type="text"
          value={profile.last_name}
          onChange={(e) => handleChange('last_name', e.target.value)}
          placeholder="Doe"
          className="onboarding-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="company_name">Company (Optional)</label>
        <input
          id="company_name"
          type="text"
          value={profile.company_name}
          onChange={(e) => handleChange('company_name', e.target.value)}
          placeholder="Acme Corp"
          className="onboarding-input"
        />
      </div>

      <div className="form-group">
        <label htmlFor="job_title">Job Title (Optional)</label>
        <input
          id="job_title"
          type="text"
          value={profile.job_title}
          onChange={(e) => handleChange('job_title', e.target.value)}
          placeholder="DevOps Engineer"
          className="onboarding-input"
        />
      </div>

      {/* --- REFACTOR --- */}
      {/* The old <div className="button-group"> is replaced by this single component */}
      <StepNavigation 
        onNext={handleContinue}
        onBack={onBack}
        isFirst={isFirst}
        isNextDisabled={!isValid}
      />
    </div>
  );
};