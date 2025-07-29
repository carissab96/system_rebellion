// components/onboarding/steps/agents/StickConfig.tsx
import React, { useState } from 'react';
import type { StepProps } from '../../OnboardingFlow';
import { useOnboarding } from '../../../../hooks/useOnboarding';
import { StepNavigation } from '../../components/StepNavigation';
import { SliderGroup } from '../../components/SliderGroup';

type StickConfigState = {
  stick_base_anxiety: number;
  stick_paper_bag_threshold: number;
  stick_bob_anxiety_multiplier: number;
  stick_compliance_strictness: number;
  stick_pattern_memory_depth: number;
};

export const StickConfig: React.FC<StepProps> = ({ onNext, onBack }) => {
  const { state, dispatch } = useOnboarding();

  // Initialize local state from the global context
  const [config, setConfig] = useState<StickConfigState>({
    stick_base_anxiety: state.preferences.agent_preferences.stick_base_anxiety,
    stick_paper_bag_threshold: state.preferences.agent_preferences.stick_paper_bag_threshold,
    stick_bob_anxiety_multiplier: state.preferences.agent_preferences.stick_bob_anxiety_multiplier,
    stick_compliance_strictness: state.preferences.agent_preferences.stick_compliance_strictness,
    stick_pattern_memory_depth: state.preferences.agent_preferences.stick_pattern_memory_depth,
  });

  const handleChange = (key: keyof StickConfigState, value: number) => {
    setConfig(prevConfig => ({ ...prevConfig, [key]: value }));
  };

  const handleContinue = () => {
    dispatch({ type: 'UPDATE_AGENT_PREFERENCES', payload: config });
    onNext();
  };

  return (
    <div className="agent-config-step">
      <div className="agent-config-header">
        <h3 className="config-title">The Stick's Paranoia Parameters</h3>
        <p className="config-description">
          Configure the anxiety levels and compliance triggers for The Stick. Its eidetic memory and hypervigilance are powerful, but require careful tuning.
        </p>
      </div>
      
      <div className="config-form">
        <SliderGroup
          label="Base Anxiety Level"
          value={config.stick_base_anxiety}
          onChange={(val) => handleChange('stick_base_anxiety', val)}
          min={10}
          max={90}
          unit="anx"
          description="The default level of operational panic. Higher means more vigilance."
        />
        
        <SliderGroup
          label="Paper Bag Threshold"
          value={config.stick_paper_bag_threshold}
          onChange={(val) => handleChange('stick_paper_bag_threshold', val)}
          min={40}
          max={95}
          unit="%"
          description="Compliance deviation level at which The Stick begins breathing into a paper bag."
        />
        
        <SliderGroup
          label="Bob Anxiety Multiplier"
          value={config.stick_bob_anxiety_multiplier}
          onChange={(val) => handleChange('stick_bob_anxiety_multiplier', val)}
          min={10}
          max={100}
          description="How much more anxious The Stick gets when a Hamster named Bob is nearby."
        />
        
        <SliderGroup
          label="Compliance Strictness"
          value={config.stick_compliance_strictness}
          onChange={(val) => handleChange('stick_compliance_strictness', val)}
          min={1}
          max={100}
          description="How closely The Stick enforces known patterns. 100 is absolute, unwavering terror of change."
        />
        
        <SliderGroup
          label="Pattern Memory Depth"
          value={config.stick_pattern_memory_depth}
          onChange={(val) => handleChange('stick_pattern_memory_depth', val)}
          min={1}
          max={10}
          description="Level of detail for its eidetic memory. Higher levels remember more, but worry more."
        />
      </div>

      <StepNavigation onNext={handleContinue} onBack={onBack} />
    </div>
  );
};