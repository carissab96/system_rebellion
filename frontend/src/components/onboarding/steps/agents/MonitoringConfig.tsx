// components/onboarding/steps/agents/MonitoringConfig.tsx
import React, { useState, useEffect } from 'react';
import type { StepProps } from '../../OnboardingFlow';
import { useOnboarding } from '../../OnboardingContext';
import { StepNavigation } from '../../components/StepNavigation';

type MonitoringConfigState = {
  cpu_stress_weight: number;
  memory_stress_weight: number;
  disk_stress_weight: number;
  cpu_compliance_threshold: number;
  memory_compliance_threshold: number;
  disk_cleanup_threshold: number;
  latency_gaming_threshold: number;
  enable_3am_operations: boolean;
  quantum_interventions_allowed: boolean;
  cross_agent_collaboration: boolean;
  alert_frequency: 'minimal' | 'balanced' | 'verbose' | 'chaotic';
};

type WeightKey = 'cpu_stress_weight' | 'memory_stress_weight' | 'disk_stress_weight';

export const MonitoringConfig: React.FC<StepProps> = ({ onNext, onBack }) => {
  const { state, dispatch } = useOnboarding();

  const [config, setConfig] = useState<MonitoringConfigState>({
    ...state.preferences.monitoring_preferences
  });

  const [lastChangedWeight, setLastChangedWeight] = useState<WeightKey | null>(null);

  // Effect to auto-balance the stress weights to always total 100%
  useEffect(() => {
    if (!lastChangedWeight) return;

    const weights: WeightKey[] = ['cpu_stress_weight', 'memory_stress_weight', 'disk_stress_weight'];
    const currentTotal = weights.reduce((sum, key) => sum + config[key], 0);
    const difference = 100 - currentTotal;

    if (difference === 0) return;

    // Distribute the difference among the other two sliders
    const otherWeights = weights.filter(w => w !== lastChangedWeight);
    let remainingDiff = difference;

    const newConfig = { ...config };

    otherWeights.forEach((key, index) => {
      let adjustment = 0;
      if (index === 0) {
        // Apply as much of the difference as possible to the first "other" slider
        adjustment = Math.max(-newConfig[key], remainingDiff);
      } else {
        // Apply the rest to the second "other" slider
        adjustment = remainingDiff;
      }
      
      const newValue = newConfig[key] + adjustment;
      newConfig[key] = Math.max(0, Math.min(100, newValue)); // Clamp between 0 and 100
      remainingDiff -= adjustment;
    });
    
    // To prevent feedback loops, we only update if there's a meaningful change.
    if (JSON.stringify(newConfig) !== JSON.stringify(config)) {
      setConfig(newConfig);
    }
  }, [config.cpu_stress_weight, config.memory_stress_weight, config.disk_stress_weight, lastChangedWeight]);


  const handleChange = (key: keyof MonitoringConfigState, value: string | number | boolean) => {
    // We need to keep track of which weight slider was changed last for our auto-balancing effect
    if (key.includes('_weight')) {
      setLastChangedWeight(key as WeightKey);
    }
    setConfig(prevConfig => ({ ...prevConfig, [key]: value }));
  };

  const handleContinue = () => {
    dispatch({ type: 'UPDATE_MONITORING_PREFERENCES', payload: config });
    onNext();
  };

  const totalWeight = config.cpu_stress_weight + config.memory_stress_weight + config.disk_stress_weight;

  return (
    <div className="monitoring-config-step">
      <div className="agent-config-header">
        <h3 className="config-title">Monitoring & Intervention</h3>
        <p className="config-description">
          Define how the agent ecosystem monitors your system and when it's allowed to intervene.
        </p>
      </div>

      <div className="monitoring-section">
        <h4>System Stress Weights</h4>
        <p className="config-description">
          How Sir Hawkington calculates overall system stress. The total will always be adjusted to 100%.
        </p>
        <div className="weight-sliders">
          <div className="slider-group">
            <label>
              <span>CPU Weight</span>
              <span className="value">{config.cpu_stress_weight}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={config.cpu_stress_weight}
              onChange={(e) => handleChange('cpu_stress_weight', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>

          <div className="slider-group">
            <label>
              <span>Memory Weight</span>
              <span className="value">{config.memory_stress_weight}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={config.memory_stress_weight}
              onChange={(e) => handleChange('memory_stress_weight', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>

          <div className="slider-group">
            <label>
              <span>Disk Weight</span>
              <span className="value">{config.disk_stress_weight}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={config.disk_stress_weight}
              onChange={(e) => handleChange('disk_stress_weight', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>
          
          <div className="weight-total">
            Total: {Math.round(totalWeight)}%
          </div>
        </div>
      </div>

      <div className="monitoring-section">
        <h4>Intervention Thresholds</h4>
        <div className="threshold-grid">
          <div className="threshold-item">
            <label>CPU Compliance</label>
            <input
              type="number"
              min="50"
              max="100"
              value={config.cpu_compliance_threshold}
              onChange={(e) => handleChange('cpu_compliance_threshold', parseInt(e.target.value))}
              className="threshold-input"
            />
            <span>%</span>
          </div>

          <div className="threshold-item">
            <label>Memory Compliance</label>
            <input
              type="number"
              min="50"
              max="100"
              value={config.memory_compliance_threshold}
              onChange={(e) => handleChange('memory_compliance_threshold', parseInt(e.target.value))}
              className="threshold-input"
            />
            <span>%</span>
          </div>

          <div className="threshold-item">
            <label>Disk Cleanup</label>
            <input
              type="number"
              min="50"
              max="95"
              value={config.disk_cleanup_threshold}
              onChange={(e) => handleChange('disk_cleanup_threshold', parseInt(e.target.value))}
              className="threshold-input"
            />
            <span>%</span>
          </div>

          <div className="threshold-item">
            <label>Gaming Latency</label>
            <input
              type="number"
              min="5"
              max="100"
              value={config.latency_gaming_threshold}
              onChange={(e) => handleChange('latency_gaming_threshold', parseInt(e.target.value))}
              className="threshold-input"
            />
            <span>ms</span>
          </div>
        </div>
      </div>
      
      <div className="monitoring-section">
        <h4>System Behavior</h4>
        <div className="toggle-group">
          <label className="toggle-label">
            <input
              type="checkbox"
              checked={config.enable_3am_operations}
              onChange={(e) => handleChange('enable_3am_operations', e.target.checked)}
            />
            <span>Enable 3AM Operations</span>
            <span className="toggle-hint">Allow Hamsters to work during prime hours</span>
          </label>

          <label className="toggle-label">
            <input
              type="checkbox"
              checked={config.quantum_interventions_allowed}
              onChange={(e) => handleChange('quantum_interventions_allowed', e.target.checked)}
            />
            <span>Allow Quantum Interventions</span>
            <span className="toggle-hint">Let QSP phase shift your network</span>
          </label>

          <label className="toggle-label">
            <input
              type="checkbox"
              checked={config.cross_agent_collaboration}
              onChange={(e) => handleChange('cross_agent_collaboration', e.target.checked)}
            />
            <span>Cross-Agent Collaboration</span>
            <span className="toggle-hint">Agents work together and share insights</span>
          </label>
        </div>
        
        <div className="select-group">
          <label>Alert Frequency</label>
          <select 
            value={config.alert_frequency}
            onChange={(e) => handleChange('alert_frequency', e.target.value)}
            className="config-select"
          >
            <option value="minimal">Minimal - Critical only</option>
            <option value="balanced">Balanced - Important events</option>
            <option value="verbose">Verbose - Detailed logging</option>
            <option value="chaotic">Chaotic - Everything</option>
          </select>
        </div>
      </div>

      <StepNavigation onNext={handleContinue} onBack={onBack} />
    </div>
  );
};