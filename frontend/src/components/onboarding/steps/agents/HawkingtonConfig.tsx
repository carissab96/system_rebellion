// components/onboarding/steps/agents/HawkingtonConfig.tsx
import React, { useState } from 'react';
import type { StepProps } from '../../OnboardingFlow';
import { useOnboarding } from '../../../../hooks/useOnboarding';
import { StepNavigation } from '../../components/StepNavigation';
import { SliderGroup } from '../../components/SliderGroup'; // Assuming path is correct

// Define a type for just Hawkington's config for cleaner code
type HawkingtonConfigState = {
  hawkington_triage_normal_threshold: number;
  hawkington_triage_medium_threshold: number;
  hawkington_triage_emergency_threshold: number;
  hawkington_message_frequency: number;
  hawkington_analysis_thoroughness: number;
};

export const HawkingtonConfig: React.FC<StepProps> = ({ onNext, onBack }) => {
  const { state, dispatch } = useOnboarding();

  // Initialize local state for this form from the global context
  const [config, setConfig] = useState<HawkingtonConfigState>({
    hawkington_triage_normal_threshold: state.preferences.agent_preferences.hawkington_triage_normal_threshold,
    hawkington_triage_medium_threshold: state.preferences.agent_preferences.hawkington_triage_medium_threshold,
    hawkington_triage_emergency_threshold: state.preferences.agent_preferences.hawkington_triage_emergency_threshold,
    hawkington_message_frequency: state.preferences.agent_preferences.hawkington_message_frequency,
    hawkington_analysis_thoroughness: state.preferences.agent_preferences.hawkington_analysis_thoroughness,
  });

  // A single handler for all sliders
  const handleChange = (key: keyof HawkingtonConfigState, value: number) => {
    setConfig(prevConfig => ({
      ...prevConfig,
      [key]: value,
    }));
  };

  const handleContinue = () => {
    // Dispatch the updated settings to the global state
    dispatch({ type: 'UPDATE_AGENT_PREFERENCES', payload: config });
    onNext();
  };

  return (
    <div className="agent-config-step">
      <div className="agent-config-header">
        <h3 className="config-title">Sir Hawkington's Mandate</h3>
        <p className="config-description">
          Configure the thresholds at which Sir Hawkington will triage system stress. 
          He operates with aristocratic precision, so choose wisely.
        </p>
      </div>
      
      <div className="config-form">
        <SliderGroup
          label="Normal Triage Threshold"
          value={config.hawkington_triage_normal_threshold}
          onChange={(val) => handleChange('hawkington_triage_normal_threshold', val)}
          min={10}
          max={50}
          unit="%"
          description="Stress level to begin normal triage operations."
        />
        
        <SliderGroup
          label="Medium Priority Threshold"
          value={config.hawkington_triage_medium_threshold}
          onChange={(val) => handleChange('hawkington_triage_medium_threshold', val)}
          min={51}
          max={80}
          unit="%"
          description="Stress level for medium priority alerts and interventions."
        />
        
        <SliderGroup
          label="Emergency Threshold"
          value={config.hawkington_triage_emergency_threshold}
          onChange={(val) => handleChange('hawkington_triage_emergency_threshold', val)}
          min={81}
          max={95}
          unit="%"
          description="Stress level to declare an emergency. He will become quite vocal."
        />
        
        <SliderGroup
          label="Message Frequency"
          value={config.hawkington_message_frequency}
          onChange={(val) => handleChange('hawkington_message_frequency', val)}
          min={1}
          max={10}
          description="How verbose Sir Hawkington is. 10 is very chatty, 1 is stoic."
        />
        
        <SliderGroup
          label="Analysis Thoroughness"
          value={config.hawkington_analysis_thoroughness}
          onChange={(val) => handleChange('hawkington_analysis_thoroughness', val)}
          min={1}
          max={10}
          description="How deeply he analyzes patterns. Higher values use more CPU."
        />
      </div>

      <StepNavigation onNext={handleContinue} onBack={onBack} />
    </div>
  );
};