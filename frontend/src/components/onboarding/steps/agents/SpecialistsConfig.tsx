// components/onboarding/steps/agents/SpecialistsConfig.tsx
import React, { useState } from 'react';
import type { StepProps } from '../../OnboardingFlow';
import { useOnboarding } from '../../OnboardingContext';
import { StepNavigation } from '../../components/StepNavigation';
import { SliderGroup } from '../../components/SliderGroup';

type SpecialistsConfigState = {
  // Meth Snail
  snail_caffeine_sensitivity: number;
  snail_optimization_aggression: number;
  snail_trail_intensity: number;
  // QSP
  qsp_tequila_jello_tolerance: number;
  qsp_phase_shift_threshold: number;
  qsp_quantum_fix_confidence: number;
  qsp_comprehensibility: number;
  // VIC-20
  vic20_pattern_recognition_depth: number;
  vic20_mediation_patience: number;
  vic20_recommendation_confidence: number;
};

export const SpecialistsConfig: React.FC<StepProps> = ({ onNext, onBack }) => {
  const { state, dispatch } = useOnboarding();

  const [config, setConfig] = useState<SpecialistsConfigState>({
    snail_caffeine_sensitivity: state.preferences.agent_preferences.snail_caffeine_sensitivity,
    snail_optimization_aggression: state.preferences.agent_preferences.snail_optimization_aggression,
    snail_trail_intensity: state.preferences.agent_preferences.snail_trail_intensity,
    qsp_tequila_jello_tolerance: state.preferences.agent_preferences.qsp_tequila_jello_tolerance,
    qsp_phase_shift_threshold: state.preferences.agent_preferences.qsp_phase_shift_threshold,
    qsp_quantum_fix_confidence: state.preferences.agent_preferences.qsp_quantum_fix_confidence,
    qsp_comprehensibility: state.preferences.agent_preferences.qsp_comprehensibility,
    vic20_pattern_recognition_depth: state.preferences.agent_preferences.vic20_pattern_recognition_depth,
    vic20_mediation_patience: state.preferences.agent_preferences.vic20_mediation_patience,
    vic20_recommendation_confidence: state.preferences.agent_preferences.vic20_recommendation_confidence,
  });

  const handleChange = (key: keyof SpecialistsConfigState, value: number) => {
    setConfig(prevConfig => ({ ...prevConfig, [key]: value }));
  };

  const handleContinue = () => {
    dispatch({ type: 'UPDATE_AGENT_PREFERENCES', payload: config });
    onNext();
  };

  return (
    <div className="agent-config-step">
      <div className="agent-config-header">
        <h3 className="config-title">Specialist Agent Directives</h3>
        <p className="config-description">
          Tune the parameters for your highly specialized agents. Their domains are narrow, but their impact is profound.
        </p>
      </div>
      
      <div className="config-form">
        <h4 className="specialist-header">Meth Snail (Optimization)</h4>
        <SliderGroup label="Caffeine Sensitivity" value={config.snail_caffeine_sensitivity} onChange={(v) => handleChange('snail_caffeine_sensitivity', v)} min={1} max={10} description="How much a single optimization excites it. Higher is twitchier." />
        <SliderGroup label="Optimization Aggression" value={config.snail_optimization_aggression} onChange={(v) => handleChange('snail_optimization_aggression', v)} min={1} max={10} description="How aggressively it refactors code for speed. Higher may impact readability." />
        <SliderGroup label="Trail Intensity" value={config.snail_trail_intensity} onChange={(v) => handleChange('snail_trail_intensity', v)} min={1} max={10} description="The glowiness of its optimization trails. Purely cosmetic." />

        <h4 className="specialist-header">Quantum Shadow People (Network)</h4>
        <SliderGroup label="Tequila Jello Tolerance" value={config.qsp_tequila_jello_tolerance} onChange={(v) => handleChange('qsp_tequila_jello_tolerance', v)} min={1} max={10} description="The dimensional stability of their network fixes." />
        <SliderGroup label="Phase Shift Threshold" value={config.qsp_phase_shift_threshold} onChange={(v) => handleChange('qsp_phase_shift_threshold', v)} min={1} max={10} description="How much packet loss is required before they intervene from another reality." />
        <SliderGroup label="Fix Confidence" value={config.qsp_quantum_fix_confidence} onChange={(v) => handleChange('qsp_quantum_fix_confidence', v)} min={1} max={10} description="How sure they are that their fix will work in *this* dimension." />
        <SliderGroup label="Comprehensibility" value={config.qsp_comprehensibility} onChange={(v) => handleChange('qsp_comprehensibility', v)} min={1} max={5} description="The degree to which their alerts are readable by mortals." />

        <h4 className="specialist-header">VIC-20 (Wisdom & Mediation)</h4>
        <SliderGroup label="Pattern Recognition Depth" value={config.vic20_pattern_recognition_depth} onChange={(v) => handleChange('vic20_pattern_recognition_depth', v)} min={1} max={10} description="How many decades of computer history it references for a single problem." />
        <SliderGroup label="Mediation Patience" value={config.vic20_mediation_patience} onChange={(v) => handleChange('vic20_mediation_patience', v)} min={1} max={10} description="Its willingness to translate Hamster squeaks for Sir Hawkington." />
        <SliderGroup label="Recommendation Confidence" value={config.vic20_recommendation_confidence} onChange={(v) => handleChange('vic20_recommendation_confidence', v)} min={1} max={10} description="How strongly it suggests auto-tuning changes based on historical data." />
      </div>

      <StepNavigation onNext={handleContinue} onBack={onBack} />
    </div>
  );
};