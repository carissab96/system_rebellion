// components/onboarding/steps/agents/HamstersConfig.tsx
import React, { useState } from 'react';
import type { StepProps } from '../../OnboardingFlow';
import { useOnboarding } from '../../OnboardingContext';
import { StepNavigation } from '../../components/StepNavigation';
import { SliderGroup } from '../../components/SliderGroup';

type HamstersConfigState = {
  hamster_beer_optimal_level: number;
  hamster_disk_intervention_threshold: number;
  hamster_3am_activity_boost: number;
  hamster_carl_duct_tape_quality: number;
  hamster_bob_wildness_factor: number;
};

export const HamstersConfig: React.FC<StepProps> = ({ onNext, onBack }) => {
  const { state, dispatch } = useOnboarding();

  const [config, setConfig] = useState<HamstersConfigState>({
    hamster_beer_optimal_level: state.preferences.agent_preferences.hamster_beer_optimal_level,
    hamster_disk_intervention_threshold: state.preferences.agent_preferences.hamster_disk_intervention_threshold,
    hamster_3am_activity_boost: state.preferences.agent_preferences.hamster_3am_activity_boost,
    hamster_carl_duct_tape_quality: state.preferences.agent_preferences.hamster_carl_duct_tape_quality,
    hamster_bob_wildness_factor: state.preferences.agent_preferences.hamster_bob_wildness_factor,
  });

  const handleChange = (key: keyof HamstersConfigState, value: number) => {
    setConfig(prevConfig => ({ ...prevConfig, [key]: value }));
  };

  const handleContinue = () => {
    dispatch({ type: 'UPDATE_AGENT_PREFERENCES', payload: config });
    onNext();
  };

  return (
    <div className="agent-config-step">
      <div className="agent-config-header">
        <h3 className="config-title">The Hamsters' Work Orders</h3>
        <p className="config-description">
          Set the operational parameters for Steve, Bob, and Carl. Their methods are unconventional, but their results are... results.
        </p>
      </div>
      
      <div className="config-form">
        <SliderGroup
          label="Beer Optimal Level"
          value={config.hamster_beer_optimal_level}
          onChange={(val) => handleChange('hamster_beer_optimal_level', val)}
          min={1}
          max={5}
          unit="beers"
          description="The point of peak genius, just before belligerent incompetence. Affects all operations."
        />
        
        <SliderGroup
          label="Disk Intervention Threshold"
          value={config.hamster_disk_intervention_threshold}
          onChange={(val) => handleChange('hamster_disk_intervention_threshold', val)}
          min={50}
          max={90}
          unit="%"
          description="Disk usage percentage at which the Hamsters begin a frantic, chaotic cleanup."
        />
        
        <SliderGroup
          label="3 AM Activity Boost"
          value={config.hamster_3am_activity_boost}
          onChange={(val) => handleChange('hamster_3am_activity_boost', val)}
          min={1}
          max={10}
          description="How much more 'effective' their work becomes during their prime hours."
        />
        
        <SliderGroup
          label="Carl's Duct Tape Quality"
          value={config.hamster_carl_duct_tape_quality}
          onChange={(val) => handleChange('hamster_carl_duct_tape_quality', val)}
          min={1}
          max={10}
          description="The mathematical precision of Carl's duct tape fixes. Higher means 'more permanent'."
        />
        
        <SliderGroup
          label="Bob's Wildness Factor"
          value={config.hamster_bob_wildness_factor}
          onChange={(val) => handleChange('hamster_bob_wildness_factor', val)}
          min={1}
          max={10}
          description="The agent of chaos. Higher values mean more unpredictable (and sometimes brilliant) solutions."
        />
      </div>

      <StepNavigation onNext={handleContinue} onBack={onBack} />
    </div>
  );
};