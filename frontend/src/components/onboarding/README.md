components/onboarding/
├── OnboardingFlow.tsx              (Main container - ~200 lines MAX)
├── OnboardingContext.tsx           (State management)
├── steps/
│   ├── index.ts                    (Export all steps)
│   ├── WelcomeStep.tsx
│   ├── ProfileStep.tsx
│   ├── PermissionsStep.tsx
│   ├── SystemProfileStep.tsx
│   ├── SystemNameStep.tsx
│   ├── AgentsIntroStep.tsx
│   └── agents/
│       ├── HawkingtonConfig.tsx
│       ├── StickConfig.tsx
│       ├── HamstersConfig.tsx
│       ├── SpecialistsConfig.tsx
│       └── MonitoringConfig.tsx
├── components/
│   ├── AgentCard.tsx
│   ├── AgentPattern.tsx
│   ├── SliderGroup.tsx
│   └── StepNavigation.tsx
├── hooks/
│   ├── useOnboarding.ts
│   └── useSystemDetection.ts
├── utils/
│   ├── agentDefaults.ts
│   ├── installCommands.ts
│   └── systemDetection.ts
└── OnboardingFlow.css

// components/onboarding/OnboardingFlow.tsx
import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import './OnboardingFlow.css';

interface OnboardingStep {
  id: string;
  title: string;
  subtitle: string;
  component: React.ComponentType<any>;
}

const OnboardingFlow: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [onboardingData, setOnboardingData] = useState({
    first_name: '',
    last_name: '',
    company_name: '',
    job_title: '',
    system_name: '',
    agent_preferences: {
      hawkington_triage_normal_threshold: 30,
      hawkington_triage_medium_threshold: 65,
      hawkington_triage_emergency_threshold: 85,
      hawkington_message_frequency: 10,
      hawkington_analysis_thoroughness: 7,
      
      stick_base_anxiety: 25,
      stick_paper_bag_threshold: 60,
      stick_bob_anxiety_multiplier: 30,
      stick_compliance_strictness: 50,
      stick_pattern_memory_depth: 7,
      
      hamster_beer_optimal_level: 3,
      hamster_disk_intervention_threshold: 70,
      hamster_3am_activity_boost: 5,
      hamster_carl_duct_tape_quality: 5,
      hamster_bob_wildness_factor: 8,
      
      snail_caffeine_sensitivity: 5,
      snail_optimization_aggression: 5,
      snail_trail_intensity: 5,
      
      qsp_tequila_jello_tolerance: 5,
      qsp_phase_shift_threshold: 5,
      qsp_quantum_fix_confidence: 5,
      qsp_comprehensibility: 3,
      
      vic20_pattern_recognition_depth: 5,
      vic20_mediation_patience: 5,
      vic20_recommendation_confidence: 5,
      
      agent_interaction_frequency: 5,
      hamster_stick_proximity_alerts: 5,
      cross_agent_memory_sharing: 5
    },
    monitoring_preferences: {
      cpu_stress_weight: 25,
      memory_stress_weight: 35,
      disk_stress_weight: 40,
      cpu_compliance_threshold: 80,
      memory_compliance_threshold: 85,
      temperature_paranoia_threshold: 75,
      disk_cleanup_threshold: 70,
      disk_emergency_threshold: 90,
      fragmentation_threshold: 20,
      latency_gaming_threshold: 20,
      latency_streaming_threshold: 50,
      latency_critical_threshold: 5,
      packet_loss_intervention: 1,
      alert_frequency: 'balanced',
      enable_3am_operations: true,
      quantum_interventions_allowed: true,
      cross_agent_collaboration: true
    }
  });

  const steps: OnboardingStep[] = [
    {
      id: 'welcome',
      title: 'Welcome to System Rebellion',
      subtitle: 'Where AI agents remember everything',
      component: WelcomeStep
    },
    {
      id: 'profile',
      title: 'Create Your Profile',
      subtitle: 'Tell us about yourself',
      component: ProfileStep
    },
    {
      id: 'system',
      title: 'Name Your System',
      subtitle: 'Give your infrastructure an identity',
      component: SystemStep
    },
    {
      id: 'agents',
      title: 'Meet Your AI Agents',
      subtitle: 'Six personalities, infinite memory',
      component: AgentsIntroStep
    },
    {
      id: 'hawkington',
      title: 'Configure Sir Hawkington',
      subtitle: 'Your aristocratic triage commander',
      component: HawkingtonConfig
    },
    {
      id: 'stick',
      title: 'Configure The Stick',
      subtitle: 'Anxiety-driven hypervigilance',
      component: StickConfig
    },
    {
      id: 'hamsters',
      title: 'Configure The Hamsters',
      subtitle: 'Beer-fueled infrastructure team',
      component: HamstersConfig
    },
    {
      id: 'specialists',
      title: 'Configure Specialists',
      subtitle: 'Snail, QSP, and VIC-20',
      component: SpecialistsConfig
    },
    {
      id: 'monitoring',
      title: 'Set Monitoring Preferences',
      subtitle: 'Define your thresholds',
      component: MonitoringConfig
    },
    {
      id: 'complete',
      title: 'Initialization Complete',
      subtitle: 'Your AI agents are ready',
      component: CompleteStep
    }
  ];

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = async () => {
    try {
      // Save onboarding data
      await completeOnboarding(onboardingData);
    } catch (error) {
      console.error('Onboarding failed:', error);
    }
  };

  return (
    <div className="onboarding-container">
      <div className="onboarding-progress">
        <div 
          className="progress-bar" 
          style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
        />
      </div>

      <AnimatePresence mode="wait">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.3 }}
          className="onboarding-content"
        >
          <div className="step-header">
            <h1 className="step-title">{steps[currentStep].title}</h1>
            <p className="step-subtitle">{steps[currentStep].subtitle}</p>
          </div>

          <div className="step-body">
            {React.createElement(steps[currentStep].component, {
              data: onboardingData,
              updateData: setOnboardingData,
              onNext: handleNext,
              onBack: handleBack,
              onComplete: handleComplete
            })}
          </div>
        </motion.div>
      </AnimatePresence>

      <div className="onboarding-footer">
        <span className="step-indicator">
          {currentStep + 1} of {steps.length}
        </span>
      </div>
    </div>
  );
};

// Step Components

const WelcomeStep: React.FC<any> = ({ onNext }) => {
  return (
    <div className="welcome-step">
      <div className="welcome-content">
        <div className="welcome-text">
          <h2>Your AI isn't like the others.</h2>
          <p className="welcome-lead">
            System Rebellion creates AI agents with persistent memory. 
            They learn from every interaction, remember every pattern, 
            and evolve their strategies specifically for your infrastructure.
          </p>
          <div className="welcome-features">
            <div className="feature-item">
              <span className="feature-number">01</span>
              <span className="feature-text">Six unique AI personalities</span>
            </div>
            <div className="feature-item">
              <span className="feature-number">02</span>
              <span className="feature-text">Cross-session memory persistence</span>
            </div>
            <div className="feature-item">
              <span className="feature-number">03</span>
              <span className="feature-text">Collective learning ecosystem</span>
            </div>
          </div>
        </div>
        <div className="welcome-visual">
          <div className="memory-counter-preview">
            <span className="counter-label">PATTERNS LEARNED</span>
            <span className="counter-value">0</span>
            <span className="counter-text">About to begin...</span>
          </div>
        </div>
      </div>
      <button className="onboarding-button primary" onClick={onNext}>
        Begin Configuration
      </button>
    </div>
  );
};

const ProfileStep: React.FC<any> = ({ data, updateData, onNext, onBack }) => {
  const [profile, setProfile] = useState({
    first_name: data.first_name || '',
    last_name: data.last_name || '',
    company_name: data.company_name || '',
    job_title: data.job_title || ''
  });

  const handleChange = (field: string, value: string) => {
    setProfile({ ...profile, [field]: value });
  };

  const handleContinue = () => {
    updateData({ ...data, ...profile });
    onNext();
  };

  const isValid = profile.first_name && profile.last_name;

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

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button 
          className="onboarding-button primary" 
          onClick={handleContinue}
          disabled={!isValid}
        >
          Continue
        </button>
      </div>
    </div>
  );
};

const SystemStep: React.FC<any> = ({ data, updateData, onNext, onBack }) => {
  const [systemName, setSystemName] = useState(data.system_name || '');

  const handleContinue = () => {
    updateData({ ...data, system_name: systemName });
    onNext();
  };

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

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button 
          className="onboarding-button primary" 
          onClick={handleContinue}
          disabled={!systemName}
        >
          Continue
        </button>
      </div>
    </div>
  );
};

const AgentsIntroStep: React.FC<any> = ({ onNext, onBack }) => {
  const agents = [
    {
      name: 'Sir Hawkington',
      role: 'Triage Commander',
      description: 'Aristocratic decision-maker who routes issues with monocle-yeeting precision',
      color: '#e6ac00'
    },
    {
      name: 'The Stick',
      role: 'Compliance Monitor',
      description: 'Anxiety-driven hypervigilance catches what others miss',
      color: '#f97316'
    },
    {
      name: 'The Hamsters',
      role: 'Infrastructure Team',
      description: 'Steve, Bob, and Carl fix everything with beer and duct tape',
      color: '#ff8c42'
    },
    {
      name: 'Meth Snail',
      role: 'Speed Optimizer',
      description: 'Caffeinated mollusk who makes everything faster',
      color: '#00d084'
    },
    {
      name: 'Quantum Shadow People',
      role: 'Network Specialists',
      description: 'Phase through dimensions to fix network issues',
      color: '#a855f7'
    },
    {
      name: 'VIC-20',
      role: 'Ancient Wisdom',
      description: 'Mediates conflicts with knowledge from 1982-2025',
      color: '#06b6d4'
    }
  ];

  return (
    <div className="agents-intro-step">
      <div className="agents-grid">
// Continue AgentsIntroStep component
        {agents.map((agent, index) => (
          <motion.div
            key={agent.name}
            className="agent-card"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            style={{ borderColor: agent.color }}
          >
            <h3 className="agent-name">{agent.name}</h3>
            <p className="agent-role">{agent.role}</p>
            <p className="agent-description">{agent.description}</p>
          </motion.div>
        ))}
      </div>

      <div className="agents-footer">
        <p className="agents-note">
          Each agent has unique decision-making patterns and remembers everything 
          across sessions. They work together to monitor and optimize your system.
        </p>
      </div>

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button className="onboarding-button primary" onClick={onNext}>
          Configure Agents
        </button>
      </div>
    </div>
  );
};

const HawkingtonConfig: React.FC<any> = ({ data, updateData, onNext, onBack }) => {
  const [preferences, setPreferences] = useState(data.agent_preferences);

  const handleSliderChange = (key: string, value: number) => {
    const updatedPrefs = {
      ...preferences,
      [key]: value
    };
    setPreferences(updatedPrefs);
    updateData({
      ...data,
      agent_preferences: updatedPrefs
    });
  };

  return (
    <div className="agent-config-step hawkington">
      <div className="agent-header">
        <div className="agent-icon" style={{ borderColor: '#e6ac00' }}>🧐</div>
        <div className="agent-intro">
          <h3>Sir Hawkington</h3>
          <p>Your aristocratic triage commander who decides which agents handle what issues.</p>
        </div>
      </div>

      <div className="config-section">
        <h4>Triage Sensitivity</h4>
        <p className="config-description">
          These thresholds determine when Sir Hawkington escalates issues from routine 
          monitoring to emergency interventions.
        </p>

        <div className="slider-group">
          <label>
            <span>Normal Operations Threshold</span>
            <span className="value">{preferences.hawkington_triage_normal_threshold}%</span>
          </label>
          <input
            type="range"
            min="10"
            max="50"
            value={preferences.hawkington_triage_normal_threshold}
            onChange={(e) => handleSliderChange('hawkington_triage_normal_threshold', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">Below this: Routes to The Stick for learning</span>
        </div>

        <div className="slider-group">
          <label>
            <span>Coordination Threshold</span>
            <span className="value">{preferences.hawkington_triage_medium_threshold}%</span>
          </label>
          <input
            type="range"
            min="50"
            max="80"
            value={preferences.hawkington_triage_medium_threshold}
            onChange={(e) => handleSliderChange('hawkington_triage_medium_threshold', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">Above this: VIC-20 coordinates multiple agents</span>
        </div>

        <div className="slider-group">
          <label>
            <span>Emergency Threshold</span>
            <span className="value">{preferences.hawkington_triage_emergency_threshold}%</span>
          </label>
          <input
            type="range"
            min="80"
            max="95"
            value={preferences.hawkington_triage_emergency_threshold}
            onChange={(e) => handleSliderChange('hawkington_triage_emergency_threshold', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">Above this: MONOCLE YEET! All agents mobilize</span>
        </div>
      </div>

      <div className="config-section">
        <h4>Analysis Style</h4>
        
        <div className="slider-group">
          <label>
            <span>Analysis Thoroughness</span>
            <span className="value">{preferences.hawkington_analysis_thoroughness}/10</span>
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={preferences.hawkington_analysis_thoroughness}
            onChange={(e) => handleSliderChange('hawkington_analysis_thoroughness', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">Higher = more detailed analysis with historical patterns</span>
        </div>

        <div className="slider-group">
          <label>
            <span>Message Frequency</span>
            <span className="value">{preferences.hawkington_message_frequency}%</span>
          </label>
          <input
            type="range"
            min="0"
            max="50"
            value={preferences.hawkington_message_frequency}
            onChange={(e) => handleSliderChange('hawkington_message_frequency', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">How often Sir Hawkington breaks silence during normal operations</span>
        </div>
      </div>

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button className="onboarding-button primary" onClick={onNext}>
          Continue
        </button>
      </div>
    </div>
  );
};

const StickConfig: React.FC<any> = ({ data, updateData, onNext, onBack }) => {
  const [preferences, setPreferences] = useState(data.agent_preferences);

  const handleSliderChange = (key: string, value: number) => {
    const updatedPrefs = {
      ...preferences,
      [key]: value
    };
    setPreferences(updatedPrefs);
    updateData({
      ...data,
      agent_preferences: updatedPrefs
    });
  };

  return (
    <div className="agent-config-step stick">
      <div className="agent-header">
        <div className="agent-icon" style={{ borderColor: '#f97316' }}>📏</div>
        <div className="agent-intro">
          <h3>The Stick</h3>
          <p>Anxiety-driven compliance monitor with eidetic memory. Hypervigilance is the feature.</p>
        </div>
      </div>

      <div className="config-section">
        <h4>Anxiety Management</h4>
        <p className="config-description">
          The Stick's anxiety makes it notice things others miss. Higher anxiety means 
          stricter monitoring but more paper bag consumption.
        </p>

        <div className="slider-group">
          <label>
            <span>Base Anxiety Level</span>
            <span className="value">{preferences.stick_base_anxiety}%</span>
          </label>
          <input
            type="range"
            min="10"
            max="50"
            value={preferences.stick_base_anxiety}
            onChange={(e) => handleSliderChange('stick_base_anxiety', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">Starting anxiety (never truly calm)</span>
        </div>

        <div className="slider-group">
          <label>
            <span>Paper Bag Threshold</span>
            <span className="value">{preferences.stick_paper_bag_threshold}%</span>
          </label>
          <input
            type="range"
            min="40"
            max="80"
            value={preferences.stick_paper_bag_threshold}
            onChange={(e) => handleSliderChange('stick_paper_bag_threshold', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">Anxiety level that triggers paper bag breathing</span>
        </div>

        <div className="slider-group">
          <label>
            <span>Bob Anxiety Multiplier</span>
            <span className="value">{preferences.stick_bob_anxiety_multiplier}%</span>
          </label>
          <input
            type="range"
            min="10"
            max="100"
            value={preferences.stick_bob_anxiety_multiplier}
            onChange={(e) => handleSliderChange('stick_bob_anxiety_multiplier', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">How much Bob the Hamster triggers anxiety (Bob is chaos)</span>
        </div>
      </div>

      <div className="config-section">
        <h4>Monitoring Behavior</h4>

        <div className="slider-group">
          <label>
            <span>Compliance Strictness</span>
            <span className="value">{preferences.stick_compliance_strictness}%</span>
          </label>
          <input
            type="range"
            min="20"
            max="80"
            value={preferences.stick_compliance_strictness}
            onChange={(e) => handleSliderChange('stick_compliance_strictness', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">How strict thresholds become under anxiety</span>
        </div>

        <div className="slider-group">
          <label>
            <span>Pattern Memory Depth</span>
            <span className="value">{preferences.stick_pattern_memory_depth} days</span>
          </label>
          <input
            type="range"
            min="1"
            max="30"
            value={preferences.stick_pattern_memory_depth}
            onChange={(e) => handleSliderChange('stick_pattern_memory_depth', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">How far back The Stick's eidetic memory analyzes</span>
        </div>
      </div>

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button className="onboarding-button primary" onClick={onNext}>
          Continue
        </button>
      </div>
    </div>
  );
};

const HamstersConfig: React.FC<any> = ({ data, updateData, onNext, onBack }) => {
  const [preferences, setPreferences] = useState(data.agent_preferences);

  const handleSliderChange = (key: string, value: number) => {
    const updatedPrefs = {
      ...preferences,
      [key]: value
    };
    setPreferences(updatedPrefs);
    updateData({
      ...data,
      agent_preferences: updatedPrefs
    });
  };

  return (
    <div className="agent-config-step hamsters">
      <div className="agent-header">
        <div className="agent-icon" style={{ borderColor: '#ff8c42' }}>🐹</div>
        <div className="agent-intro">
          <h3>The Hamsters</h3>
          <p>Steve (careful), Bob (wild), and Carl (duct tape expert) handle infrastructure 
             with beer-fueled enthusiasm. Peak performance at 3am.</p>
        </div>
      </div>

      <div className="config-section">
        <h4>Operational Parameters</h4>
        <p className="config-description">
          The Hamsters' effectiveness is directly proportional to their beer consumption 
          and inversely proportional to common sense.
        </p>

        <div className="slider-group">
          <label>
            <span>Optimal Beer Level</span>
            <span className="value">{preferences.hamster_beer_optimal_level}/10</span>
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={preferences.hamster_beer_optimal_level}
            onChange={(e) => handleSliderChange('hamster_beer_optimal_level', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">3-4 beers = peak performance, 7+ = Carl does calculus with duct tape</span>
        </div>

        <div className="slider-group">
          <label>
            <span>Bob's Wildness Factor</span>
            <span className="value">{preferences.hamster_bob_wildness_factor}/10</span>
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={preferences.hamster_bob_wildness_factor}
            onChange={(e) => handleSliderChange('hamster_bob_wildness_factor', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">How wild Bob's infrastructure ideas get (causes Stick anxiety)</span>
        </div>

        <div className="slider-group">
          <label>
            <span>Carl's Duct Tape Access</span>
            <span className="value">{preferences.hamster_carl_duct_tape_quality}/10</span>
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={preferences.hamster_carl_duct_tape_quality}
            onChange={(e) => handleSliderChange('hamster_carl_duct_tape_quality', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">Access to premium and quantum duct tape grades</span>
        </div>
      </div>

      <div className="config-section">
        <h4>Intervention Thresholds</h4>

        <div className="slider-group">
          <label>
            <span>Disk Cleanup Threshold</span>
            <span className="value">{preferences.hamster_disk_intervention_threshold}%</span>
          </label>
          <input
            type="range"
            min="50"
            max="85"
            value={preferences.hamster_disk_intervention_threshold}
            onChange={(e) => handleSliderChange('hamster_disk_intervention_threshold', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">When hamsters start "helping" with disk space</span>
        </div>

        <div className="slider-group">
          <label>
            <span>3AM Activity Boost</span>
            <span className="value">{preferences.hamster_3am_activity_boost}/10</span>
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={preferences.hamster_3am_activity_boost}
            onChange={(e) => handleSliderChange('hamster_3am_activity_boost', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">How aggressive they get during prime hours (2-5 AM)</span>
        </div>
      </div>

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button className="onboarding-button primary" onClick={onNext}>
          Continue
        </button>
      </div>
    </div>
  );
};
// Continue with SpecialistsConfig
const SpecialistsConfig: React.FC<any> = ({ data, updateData, onNext, onBack }) => {
  const [preferences, setPreferences] = useState(data.agent_preferences);

  const handleSliderChange = (key: string, value: number) => {
    const updatedPrefs = {
      ...preferences,
      [key]: value
    };
    setPreferences(updatedPrefs);
    updateData({
      ...data,
      agent_preferences: updatedPrefs
    });
  };

  return (
    <div className="agent-config-step specialists">
      <div className="specialists-grid">
        {/* Meth Snail Config */}
        <div className="specialist-section snail">
          <div className="specialist-header">
            <div className="agent-icon small" style={{ borderColor: '#00d084' }}>🐌</div>
            <h4>Meth Snail</h4>
          </div>
          <p className="specialist-desc">Caffeinated optimizer leaving optimization trails</p>
          
          <div className="slider-group compact">
            <label>
              <span>Caffeine Sensitivity</span>
              <span className="value">{preferences.snail_caffeine_sensitivity}/10</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={preferences.snail_caffeine_sensitivity}
              onChange={(e) => handleSliderChange('snail_caffeine_sensitivity', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>

          <div className="slider-group compact">
            <label>
              <span>Optimization Aggression</span>
              <span className="value">{preferences.snail_optimization_aggression}/10</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={preferences.snail_optimization_aggression}
              onChange={(e) => handleSliderChange('snail_optimization_aggression', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>
        </div>

        {/* Quantum Shadow People Config */}
        <div className="specialist-section qsp">
          <div className="specialist-header">
            <div className="agent-icon small" style={{ borderColor: '#a855f7' }}>👻</div>
            <h4>Quantum Shadow People</h4>
          </div>
          <p className="specialist-desc">Phase through dimensions to fix network issues</p>
          
          <div className="slider-group compact">
            <label>
              <span>Tequila Jello Tolerance</span>
              <span className="value">{preferences.qsp_tequila_jello_tolerance}/10</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={preferences.qsp_tequila_jello_tolerance}
              onChange={(e) => handleSliderChange('qsp_tequila_jello_tolerance', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>

          <div className="slider-group compact">
            <label>
              <span>Phase Shift Threshold</span>
              <span className="value">{preferences.qsp_phase_shift_threshold}/10</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={preferences.qsp_phase_shift_threshold}
              onChange={(e) => handleSliderChange('qsp_phase_shift_threshold', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>

          <div className="slider-group compact">
            <label>
              <span>Comprehensibility</span>
              <span className="value">{preferences.qsp_comprehensibility}/10</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={preferences.qsp_comprehensibility}
              onChange={(e) => handleSliderChange('qsp_comprehensibility', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>
        </div>

        {/* VIC-20 Config */}
        <div className="specialist-section vic20">
          <div className="specialist-header">
            <div className="agent-icon small" style={{ borderColor: '#06b6d4' }}>💾</div>
            <h4>VIC-20</h4>
          </div>
          <p className="specialist-desc">Ancient wisdom mediator with 40+ years of patterns</p>
          
          <div className="slider-group compact">
            <label>
              <span>Pattern Recognition Depth</span>
              <span className="value">{preferences.vic20_pattern_recognition_depth}/10</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={preferences.vic20_pattern_recognition_depth}
              onChange={(e) => handleSliderChange('vic20_pattern_recognition_depth', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>

          <div className="slider-group compact">
            <label>
              <span>Mediation Patience</span>
              <span className="value">{preferences.vic20_mediation_patience}/10</span>
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={preferences.vic20_mediation_patience}
              onChange={(e) => handleSliderChange('vic20_mediation_patience', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>
        </div>
      </div>

      <div className="interaction-section">
        <h4>Agent Interactions</h4>
        <p className="config-description">
          Control how agents work together and share information
        </p>

        <div className="slider-group">
          <label>
            <span>Hamster-Stick Proximity Alerts</span>
            <span className="value">{preferences.hamster_stick_proximity_alerts}/10</span>
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={preferences.hamster_stick_proximity_alerts}
            onChange={(e) => handleSliderChange('hamster_stick_proximity_alerts', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">How sensitive The Stick is to Hamster activity</span>
        </div>

        <div className="slider-group">
          <label>
            <span>Cross-Agent Memory Sharing</span>
            <span className="value">{preferences.cross_agent_memory_sharing}/10</span>
          </label>
          <input
            type="range"
            min="1"
            max="10"
            value={preferences.cross_agent_memory_sharing}
            onChange={(e) => handleSliderChange('cross_agent_memory_sharing', parseInt(e.target.value))}
            className="config-slider"
          />
          <span className="slider-hint">How much agents share learned patterns</span>
        </div>
      </div>

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button className="onboarding-button primary" onClick={onNext}>
          Continue
        </button>
      </div>
    </div>
  );
};

const MonitoringConfig: React.FC<any> = ({ data, updateData, onNext, onBack }) => {
  const [preferences, setPreferences] = useState(data.monitoring_preferences);

  const handleChange = (key: string, value: any) => {
    const updatedPrefs = {
      ...preferences,
      [key]: value
    };
    setPreferences(updatedPrefs);
    updateData({
      ...data,
      monitoring_preferences: updatedPrefs
    });
  };

  return (
    <div className="monitoring-config-step">
      <div className="monitoring-section">
        <h4>System Stress Weights</h4>
        <p className="config-description">
          How Sir Hawkington calculates overall system stress. Must total 100%.
        </p>

        <div className="weight-sliders">
          <div className="slider-group">
            <label>
              <span>CPU Weight</span>
              <span className="value">{preferences.cpu_stress_weight}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={preferences.cpu_stress_weight}
              onChange={(e) => handleChange('cpu_stress_weight', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>

          <div className="slider-group">
            <label>
              <span>Memory Weight</span>
              <span className="value">{preferences.memory_stress_weight}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={preferences.memory_stress_weight}
              onChange={(e) => handleChange('memory_stress_weight', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>

          <div className="slider-group">
            <label>
              <span>Disk Weight</span>
              <span className="value">{preferences.disk_stress_weight}%</span>
            </label>
            <input
              type="range"
              min="0"
              max="100"
              value={preferences.disk_stress_weight}
              onChange={(e) => handleChange('disk_stress_weight', parseInt(e.target.value))}
              className="config-slider"
            />
          </div>

          <div className="weight-total">
            Total: {preferences.cpu_stress_weight + preferences.memory_stress_weight + preferences.disk_stress_weight}%
            {(preferences.cpu_stress_weight + preferences.memory_stress_weight + preferences.disk_stress_weight) !== 100 && 
              <span className="warning"> (Must equal 100%)</span>
            }
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
              value={preferences.cpu_compliance_threshold}
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
              value={preferences.memory_compliance_threshold}
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
              value={preferences.disk_cleanup_threshold}
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
              value={preferences.latency_gaming_threshold}
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
              checked={preferences.enable_3am_operations}
              onChange={(e) => handleChange('enable_3am_operations', e.target.checked)}
            />
            <span>Enable 3AM Operations</span>
            <span className="toggle-hint">Allow Hamsters to work during prime hours</span>
          </label>

          <label className="toggle-label">
            <input
              type="checkbox"
              checked={preferences.quantum_interventions_allowed}
              onChange={(e) => handleChange('quantum_interventions_allowed', e.target.checked)}
            />
            <span>Allow Quantum Interventions</span>
            <span className="toggle-hint">Let QSP phase shift your network</span>
          </label>

          <label className="toggle-label">
            <input
              type="checkbox"
              checked={preferences.cross_agent_collaboration}
              onChange={(e) => handleChange('cross_agent_collaboration', e.target.checked)}
            />
            <span>Cross-Agent Collaboration</span>
            <span className="toggle-hint">Agents work together and share insights</span>
          </label>
        </div>

        <div className="select-group">
          <label>Alert Frequency</label>
          <select 
            value={preferences.alert_frequency}
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

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button 
          className="onboarding-button primary" 
          onClick={onNext}
          disabled={(preferences.cpu_stress_weight + preferences.memory_stress_weight + preferences.disk_stress_weight) !== 100}
        >
          Complete Setup
        </button>
      </div>
    </div>
  );
};

const CompleteStep: React.FC<any> = ({ data, onComplete }) => {
  const [isInitializing, setIsInitializing] = useState(false);

// Continue CompleteStep
  const handleComplete = async () => {
    setIsInitializing(true);
    try {
      await onComplete();
    } catch (error) {
      console.error('Failed to complete onboarding:', error);
      setIsInitializing(false);
    }
  };

  return (
    <div className="complete-step">
      <motion.div 
        className="completion-animation"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5 }}
      >
        <div className="agents-circle">
          <div className="agent-node hawkington" style={{ '--color': '#e6ac00' }}>🧐</div>
          <div className="agent-node stick" style={{ '--color': '#f97316' }}>📏</div>
          <div className="agent-node hamsters" style={{ '--color': '#ff8c42' }}>🐹</div>
          <div className="agent-node snail" style={{ '--color': '#00d084' }}>🐌</div>
          <div className="agent-node qsp" style={{ '--color': '#a855f7' }}>👻</div>
          <div className="agent-node vic20" style={{ '--color': '#06b6d4' }}>💾</div>
          
          <div className="connection-lines">
            <svg viewBox="0 0 300 300" className="connections">
              {/* Connection lines between agents */}
              <line x1="150" y1="50" x2="250" y2="100" stroke="#333" strokeWidth="1" opacity="0.5" />
              <line x1="250" y1="100" x2="250" y2="200" stroke="#333" strokeWidth="1" opacity="0.5" />
              <line x1="250" y1="200" x2="150" y2="250" stroke="#333" strokeWidth="1" opacity="0.5" />
              <line x1="150" y1="250" x2="50" y2="200" stroke="#333" strokeWidth="1" opacity="0.5" />
              <line x1="50" y1="200" x2="50" y2="100" stroke="#333" strokeWidth="1" opacity="0.5" />
              <line x1="50" y1="100" x2="150" y2="50" stroke="#333" strokeWidth="1" opacity="0.5" />
            </svg>
          </div>
        </div>
      </motion.div>

      <div className="completion-content">
        <h2>Your AI Agents Are Ready</h2>
        <p className="completion-message">
          {data.first_name}, your persistent AI ecosystem for <span className="highlight">{data.system_name}</span> is configured 
          and ready to begin learning. Each agent will now start building their unique understanding 
          of your infrastructure.
        </p>

        <div className="initialization-summary">
          <h3>What Happens Next</h3>
          <ul className="summary-list">
            <li>
              <span className="summary-icon">🧐</span>
              <span>Sir Hawkington begins aristocratic triage monitoring</span>
            </li>
            <li>
              <span className="summary-icon">📏</span>
              <span>The Stick starts anxious pattern learning</span>
            </li>
            <li>
              <span className="summary-icon">🐹</span>
              <span>The Hamsters prepare their beer and duct tape</span>
            </li>
            <li>
              <span className="summary-icon">🐌</span>
              <span>Meth Snail caffeinated and ready to optimize</span>
            </li>
            <li>
              <span className="summary-icon">👻</span>
              <span>QSP phase into network monitoring dimension</span>
            </li>
            <li>
              <span className="summary-icon">💾</span>
              <span>VIC-20 loads 40+ years of wisdom patterns</span>
            </li>
          </ul>
        </div>

        <div className="memory-notice">
          <p className="notice-text">
            <strong>Remember:</strong> Your agents maintain persistent memory across all sessions. 
            Every decision, pattern, and interaction is permanently stored and influences future behavior.
          </p>
        </div>
      </div>

      <button 
        className={`onboarding-button primary large ${isInitializing ? 'loading' : ''}`}
        onClick={handleComplete}
        disabled={isInitializing}
      >
        {isInitializing ? 'Initializing AI Agents...' : 'Enter System Rebellion'}
      </button>
    </div>
  );
};

// Helper function to complete onboarding
async function completeOnboarding(data: any) {
  try {
    const response = await fetch('/api/user/complete-onboarding', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: JSON.stringify({
        first_name: data.first_name,
        last_name: data.last_name,
        company_name: data.company_name,
        job_title: data.job_title,
        system_name: data.system_name,
        agent_preferences: data.agent_preferences,
        monitoring_preferences: data.monitoring_preferences,
        is_onboarded: true
      })
    });

    if (!response.ok) {
      throw new Error('Failed to complete onboarding');
    }

    // Update user state in Redux
    const result = await response.json();
    // dispatch(updateUser(result.user));
    
    // Redirect to dashboard
    window.location.href = '/dashboard';
  } catch (error) {
    console.error('Onboarding error:', error);
    throw error;
  }
}

export default OnboardingFlow;

then we did this...
// Updated AgentsIntroStep component
const AgentsIntroStep: React.FC<any> = ({ onNext, onBack }) => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);

  const agents = [
    {
      id: 'hawkington',
      name: 'Sir Hawkington',
      role: 'Triage Commander',
      description: 'Aristocratic decision-maker who routes issues with monocle-yeeting precision',
      color: '#e6ac00',
      details: {
        personality: 'Aristocratic perfectionist with zero tolerance for bad data',
        responsibility: 'First responder who assesses severity and delegates to specialists',
        quirks: 'Yeets monocle when data quality is beneath standards',
        memory: 'Remembers every monocle yeet incident and data quality failure',
        interactions: 'Commands all other agents, especially during emergencies'
      }
    },
    {
      id: 'stick',
      name: 'The Stick',
      role: 'Compliance Monitor',
      description: 'Anxiety-driven hypervigilance catches what others miss',
      color: '#f97316',
      details: {
        personality: 'OCD + ADHD + PTSD + Eidetic Memory = Perfect paranoid monitor',
        responsibility: 'Learns user patterns and enforces compliance thresholds',
        quirks: 'Consumes paper bags when anxious, especially around Bob',
        memory: 'Eidetic - remembers EVERYTHING that ever happened',
        interactions: 'Panics when Hamsters nearby, understands their squeaks through shared anxiety'
      }
    },
    {
      id: 'hamsters',
      name: 'The Hamsters',
      role: 'Infrastructure Team',
      description: 'Steve, Bob, and Carl fix everything with beer and duct tape',
      color: '#ff8c42',
      details: {
        personality: 'Steve (careful), Bob (chaos), Carl (duct tape mathematician)',
        responsibility: '3AM emergency infrastructure fixes, disk cleanup, defragmentation',
        quirks: 'Peak performance at 3-4 beers, communicate in squeaks',
        memory: 'Collective telepathic memory, ancient beer-stained wisdom',
        interactions: 'Bob causes Stick anxiety, telepathic understanding with QSP'
      }
    },
    {
      id: 'snail',
      name: 'Meth Snail',
      role: 'Speed Optimizer',
      description: 'Caffeinated mollusk who makes everything faster',
      color: '#00d084',
      details: {
        personality: 'Hyperactive optimization addict leaving trails of improvements',
        responsibility: 'CPU optimization, process prioritization, speed enhancements',
        quirks: 'Leaves glowing optimization trails, shell spins indicate excitement',
        memory: 'Remembers every optimization and its cascading effects',
        interactions: 'Too caffeinated to understand Hamster squeaks, respects Hawkington'
      }
    },
    {
      id: 'qsp',
      name: 'Quantum Shadow People',
      role: 'Network Specialists',
      description: 'Phase through dimensions to fix network issues',
      color: '#a855f7',
      details: {
        personality: 'Mysterious entities who exist partially in multiple dimensions',
        responsibility: 'Network optimization, security, packet recovery from the void',
        quirks: 'Fix routers by phasing them through tequila jello dimensions',
        memory: 'Remember network patterns across dimensional boundaries',
        interactions: 'Telepathic bond with Hamsters, incomprehensible to most'
      }
    },
    {
      id: 'vic20',
      name: 'VIC-20',
      role: 'Ancient Wisdom',
      description: 'Mediates conflicts with knowledge from 1982-2025',
      color: '#06b6d4',
      details: {
        personality: 'Ancient sage who has seen every pattern since 1982',
        responsibility: 'Pattern recognition, conflict mediation, auto-tuning recommendations',
        quirks: 'Speaks in historical computing references, always relevant',
        memory: '40+ years of patterns, every mistake and solution ever made',
        interactions: 'Mediates between agents, translates Hamster squeaks to others'
      }
    }
  ];

  return (
    <div className="agents-intro-step">
      <div className="agents-showcase">
        {agents.map((agent) => (
          <motion.div
            key={agent.id}
            className={`agent-showcase-card ${selectedAgent === agent.id ? 'selected' : ''}`}
            onClick={() => setSelectedAgent(agent.id)}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            whileHover={{ scale: 1.02 }}
            style={{ 
              '--agent-color': agent.color,
              borderColor: selectedAgent === agent.id ? agent.color : 'transparent'
            }}
          >
            <div className="agent-identity">
              <div className="agent-color-bar" style={{ background: agent.color }} />
              <div className="agent-basic-info">
                <h3 className="agent-name">{agent.name}</h3>
                <p className="agent-role">{agent.role}</p>
              </div>
            </div>
            
            <p className="agent-description">{agent.description}</p>
            
            {selectedAgent === agent.id && (
              <motion.div 
                className="agent-details"
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
              >
                <div className="detail-item">
                  <span className="detail-label">Personality</span>
                  <span className="detail-content">{agent.details.personality}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Responsibility</span>
                  <span className="detail-content">{agent.details.responsibility}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Quirks</span>
                  <span className="detail-content">{agent.details.quirks}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Memory</span>
                  <span className="detail-content">{agent.details.memory}</span>
                </div>
                <div className="detail-item">
                  <span className="detail-label">Interactions</span>
                  <span className="detail-content">{agent.details.interactions}</span>
                </div>
              </motion.div>
            )}
            
            <div className="card-footer">
              <span className="click-hint">
                {selectedAgent === agent.id ? 'Selected' : 'Click to learn more'}
              </span>
            </div>
          </motion.div>
        ))}
      </div>

      <div className="agents-footer">
        <p className="agents-note">
          Click each agent to understand their role in your AI ecosystem. 
          These aren't chatbots - they're specialized decision engines with 
          persistent memory and complex inter-agent relationships.
        </p>
      </div>

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button className="onboarding-button primary" onClick={onNext}>
          Configure Agents
        </button>
      </div>
    </div>
  );
};

and then we added this
// Updated AgentsIntroStep component with better interaction
const AgentsIntroStep: React.FC<any> = ({ onNext, onBack }) => {
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null);
  const [lockedAgents, setLockedAgents] = useState<Set<string>>(new Set());

  const handleCardClick = (agentId: string) => {
    setLockedAgents(prev => {
      const newSet = new Set(prev);
      if (newSet.has(agentId)) {
        newSet.delete(agentId);
      } else {
        newSet.add(agentId);
      }
      return newSet;
    });
  };

  const handleMouseEnter = (agentId: string) => {
    setHoveredAgent(agentId);
  };

  const handleMouseLeave = (agentId: string) => {
    setHoveredAgent(null);
  };

  const isExpanded = (agentId: string) => {
    return lockedAgents.has(agentId) || hoveredAgent === agentId;
  };

  const agents = [
    // ... same agents array as before
  ];

  return (
    <div className="agents-intro-step">
      <div className="agents-showcase">
        {agents.map((agent) => {
          const expanded = isExpanded(agent.id);
          const locked = lockedAgents.has(agent.id);
          
          return (
            <motion.div
              key={agent.id}
              className={`agent-showcase-card ${expanded ? 'expanded' : ''} ${locked ? 'locked' : ''}`}
              onClick={() => handleCardClick(agent.id)}
              onMouseEnter={() => handleMouseEnter(agent.id)}
              onMouseLeave={() => handleMouseLeave(agent.id)}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ 
                '--agent-color': agent.color,
                borderColor: expanded ? agent.color : 'transparent'
              }}
            >
              <div className="agent-identity">
                <div className="agent-color-bar" style={{ background: agent.color }} />
                <div className="agent-basic-info">
                  <h3 className="agent-name">{agent.name}</h3>
                  <p className="agent-role">{agent.role}</p>
                </div>
                {locked && (
                  <div className="lock-indicator">
                    <div className="lock-icon" />
                  </div>
                )}
              </div>
              
              <p className="agent-description">{agent.description}</p>
              
              <AnimatePresence>
                {expanded && (
                  <motion.div 
                    className="agent-details"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    <div className="detail-item">
                      <span className="detail-label">Personality</span>
                      <span className="detail-content">{agent.details.personality}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Responsibility</span>
                      <span className="detail-content">{agent.details.responsibility}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Quirks</span>
                      <span className="detail-content">{agent.details.quirks}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Memory</span>
                      <span className="detail-content">{agent.details.memory}</span>
                    </div>
                    <div className="detail-item">
                      <span className="detail-label">Interactions</span>
                      <span className="detail-content">{agent.details.interactions}</span>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
              
              <div className="card-footer">
                <span className="interaction-hint">
                  {locked ? 'Click to collapse' : expanded ? 'Click to lock open' : 'Hover to preview • Click to lock'}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>

      <div className="agents-footer">
        <p className="agents-note">
          Hover over each agent to preview their details. Click to keep a card expanded while exploring others.
          These aren't chatbots - they're specialized decision engines with persistent memory and complex inter-agent relationships.
        </p>
      </div>

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button className="onboarding-button primary" onClick={onNext}>
          Configure Agents
        </button>
      </div>
    </div>
  );
};

and then we added this
// Updated AgentsIntroStep with geometric patterns on cards
const AgentsIntroStep: React.FC<any> = ({ onNext, onBack }) => {
  const [expandedAgents, setExpandedAgents] = useState<Set<string>>(new Set());
  const [hoveredAgent, setHoveredAgent] = useState<string | null>(null);
  const [lockedAgents, setLockedAgents] = useState<Set<string>>(new Set());

  // ... handlers remain the same ...

  const renderAgentPattern = (agentId: string) => {
    switch (agentId) {
      case 'hawkington':
        return (
          <div className="agent-pattern hawkington-pattern">
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
          </div>
        );
      
      case 'stick':
        return (
          <div className="agent-pattern stick-pattern">
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
          </div>
        );
      
      case 'hamsters':
        return (
          <div className="agent-pattern hamsters-pattern">
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
          </div>
        );
      
      case 'snail':
        return (
          <div className="agent-pattern snail-pattern">
            <svg viewBox="0 0 80 80">
              <path
                className="snail-spiral"
                d="M40,40 Q50,30 40,20 T20,20 Q10,30 10,40 T20,60 Q30,70 40,70 T60,60 Q70,50 70,40 T60,20"
              />
            </svg>
          </div>
        );
      
      case 'qsp':
        return (
          <div className="agent-pattern qsp-pattern">
            <div className="pattern-element" />
            <div className="pattern-element" />
          </div>
        );
      
      case 'vic20':
        return (
          <div className="agent-pattern vic20-pattern">
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
            <div className="pattern-element" />
          </div>
        );
      
      default:
        return null;
    }
  };

  const agents = [/* ... same agents array ... */];

  return (
    <div className="agents-intro-step">
      <div className="agents-showcase">
        {agents.map((agent) => {
          const expanded = isExpanded(agent.id);
          const locked = lockedAgents.has(agent.id);
          
          return (
            <motion.div
              key={agent.id}
              className={`agent-showcase-card ${expanded ? 'expanded' : ''} ${locked ? 'locked' : ''}`}
              onClick={() => handleCardClick(agent.id)}
              onMouseEnter={() => handleMouseEnter(agent.id)}
              onMouseLeave={() => handleMouseLeave(agent.id)}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              style={{ 
                '--agent-color': agent.color,
                borderColor: expanded ? agent.color : 'transparent'
              }}
            >
              <div className="agent-identity">
                <div className="agent-pattern-container">
                  {renderAgentPattern(agent.id)}
                </div>
                <div className="agent-basic-info">
                  <h3 className="agent-name">{agent.name}</h3>
                  <p className="agent-role">{agent.role}</p>
                </div>
                {locked && (
                  <div className="lock-indicator">
                    <div className="lock-icon" />
                  </div>
                )}
              </div>
              
              <p className="agent-description">{agent.description}</p>
              
              <AnimatePresence>
                {expanded && (
                  <motion.div 
                    className="agent-details"
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.3 }}
                  >
                    {/* ... detail items ... */}
                  </motion.div>
                )}
              </AnimatePresence>
              
              <div className="card-footer">
                <span className="interaction-hint">
                  {locked ? 'Click to collapse' : expanded ? 'Click to lock open' : 'Hover to preview • Click to lock'}
                </span>
              </div>
            </motion.div>
          );
        })}
      </div>
      {/* ... rest of component ... */}
    </div>
  );
};

and then this was added
// New PermissionsStep component
const PermissionsStep: React.FC<any> = ({ data, updateData, onNext, onBack }) => {
  const [osType, setOsType] = useState<string>('');
  const [permissionsGranted, setPermissionsGranted] = useState(false);
  const [installMethod, setInstallMethod] = useState<string>('');

  useEffect(() => {
    // Detect OS
    detectOperatingSystem();
  }, []);

  const detectOperatingSystem = () => {
    const platform = navigator.platform.toLowerCase();
    if (platform.includes('win')) setOsType('windows');
    else if (platform.includes('mac')) setOsType('macos');
    else if (platform.includes('linux')) setOsType('linux');
    else setOsType('unknown');
  };

  const handlePermissionSetup = async () => {
    try {
      // Different setup based on OS
      switch (osType) {
        case 'windows':
          await setupWindowsPermissions();
          break;
        case 'macos':
          await setupMacPermissions();
          break;
        case 'linux':
          await setupLinuxPermissions();
          break;
      }
      setPermissionsGranted(true);
    } catch (error) {
      console.error('Permission setup failed:', error);
    }
  };

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
          <div className="code-block">
            {getInstallCommand(osType, installMethod)}
          </div>
          <button 
            className="copy-button"
            onClick={() => copyToClipboard(getInstallCommand(osType, installMethod))}
          >
            Copy Command
          </button>
        </div>
      )}

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

      <div className="button-group">
        <button className="onboarding-button secondary" onClick={onBack}>
          Back
        </button>
        <button 
          className="onboarding-button primary" 
          onClick={onNext}
          disabled={!permissionsGranted || !installMethod}
        >
          Continue Configuration
        </button>
      </div>
    </div>
  );
};

// Helper function to generate install commands
const getInstallCommand = (os: string, method: string): string => {
  const commands: Record<string, Record<string, string>> = {
    windows: {
      installer: 'Invoke-WebRequest -Uri https://systemrebellion.ai/download/windows/installer.exe -OutFile SystemRebellionInstaller.exe\n.\\SystemRebellionInstaller.exe',
      manual: '# Download from: https://systemrebellion.ai/setup/windows\n# Run: Set-ExecutionPolicy RemoteSigned\n# Then: .\\setup-system-rebellion.ps1'
    },
    macos: {
      homebrew: 'brew tap hawkington/system-rebellion\nbrew install system-rebellion-agent\nsystem-rebellion setup',
      installer: '# Download from: https://systemrebellion.ai/download/macos/SystemRebellion.dmg',
      manual: 'curl -sSL https://systemrebellion.ai/setup/macos | python3'
    },
    linux: {
      apt: 'sudo add-apt-repository ppa:hawkington/system-rebellion\nsudo apt update\nsudo apt install system-rebellion-agent',
      yum: 'sudo yum-config-manager --add-repo https://systemrebellion.ai/repo/rhel/system-rebellion.repo\nsudo yum install system-rebellion-agent',
      pacman: 'yay -S system-rebellion-agent',
      script: 'curl -sSL https://systemrebellion.ai/setup/linux | sudo bash'
    }
  };

  return commands[os]?.[method] || '# Instructions not available for this configuration';
};

and the we created the permissions.py file(which I  think is ok as it was implemented, so I'm not going to send it through unless we determine later it's necessary. 

and then we added another step
// New SystemProfileStep component - goes after PermissionsStep
const SystemProfileStep: React.FC<any> = ({ data, updateData, onNext, onBack }) => {
  const [systemInfo, setSystemInfo] = useState({
    os_type: '',
    os_version: '',
    total_ram_gb: 0,
    storage_type: '',
    total_storage_gb: 0,
    cpu_cores: 0,
    is_virtual: false,
    network_type: 'standard',
    admin_access: 'full',
    mdm_controlled: false,
    custom_restrictions: []
  });

  const [autoDetected, setAutoDetected] = useState(false);
  const [detectionStatus, setDetectionStatus] = useState('detecting');

  useEffect(() => {
    autoDetectSystemInfo();
  }, []);

  const autoDetectSystemInfo = async () => {
    try {
      // Call backend to get system info via the agent
      const response = await fetch('/api/system/detect', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.ok) {
        const detected = await response.json();
        setSystemInfo({
          ...systemInfo,
          ...detected
        });
        setAutoDetected(true);
        setDetectionStatus('success');
      } else {
        setDetectionStatus('manual');
      }
    } catch (error) {
      setDetectionStatus('manual');
    }
  };

  const handleChange = (field: string, value: any) => {
    setSystemInfo({ ...systemInfo, [field]: value });
  };

  const handleContinue = () => {
    updateData({
      ...data,
      system_profile: systemInfo
    });
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
                      checked={systemInfo.custom_restrictions.includes(restriction.id)}
                      onChange={(e) => {
                        const restrictions = e.target.checked
                          ? [...systemInfo.custom_restrictions, restriction.id]
                          : systemInfo.custom_restrictions.filter(r => r !== restriction.id);
                        handleChange('custom_restrictions', restrictions);
                      }}
                    />
                    <span>{restriction.label}</span>
                  </label>
                ))}
              </div>
            </div>
          </div>

          {(systemInfo.admin_access === 'none' || systemInfo.custom_restrictions.length > 2) && (
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

          {autoDetected && (
            <div className="detection-notice">
              <p>✓ System information auto-detected. Please verify and adjust if needed.</p>
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
// Function to adjust agent defaults based on system profile
const adjustAgentDefaults = (systemProfile: any) => {
  const defaults = { ...defaultAgentPreferences };
  
  // Low RAM systems - less aggressive
  if (systemProfile.total_ram_gb <= 8) {
    defaults.snail_optimization_aggression = 3;
    defaults.hamster_3am_activity_boost = 3;
    defaults.stick_paper_bag_threshold = 70; // Less anxious about memory
  }
  
  // HDD systems - different disk thresholds
  if (systemProfile.storage_type === 'hdd') {
    defaults.hamster_disk_intervention_threshold = 60; // Earlier intervention
    defaults.hamster_beer_optimal_level = 4; // Need more beer for slower disks
  }
  
  // Enterprise/MDM systems - more conservative
  if (systemProfile.mdm_controlled || systemProfile.network_type === 'enterprise') {
    defaults.hawkington_triage_emergency_threshold = 90; // Higher threshold
    defaults.hamster_bob_wildness_factor = 5; // Less wild
    defaults.qsp_phase_shift_threshold = 7; // More cautious about network changes
  }
  
  // Limited access systems - advisory mode
  if (systemProfile.admin_access === 'none' || systemProfile.admin_access === 'limited') {
    defaults.agent_interaction_frequency = 3; // Less frequent
    defaults.cross_agent_collaboration = false; // Simplified operation
  }
  
  return defaults;
};
and then we updated onboardingData initial state to include the new fields
const [onboardingData, setOnboardingData] = useState({
  first_name: '',
  last_name: '',
  company_name: '',
  job_title: '',
  system_name: '',
  // Add these new fields
  permissions_granted: false,
  installation_method: '',
  system_profile: {
    os_type: '',
    os_version: '',
    total_ram_gb: 0,
    storage_type: '',
    total_storage_gb: 0,
    cpu_cores: 0,
    is_virtual: false,
    network_type: 'standard',
    admin_access: 'full',
    mdm_controlled: false,
    custom_restrictions: []
  },
  agent_preferences: {
    // ... existing preferences
  },
  monitoring_preferences: {
    // ... existing preferences
  }
});