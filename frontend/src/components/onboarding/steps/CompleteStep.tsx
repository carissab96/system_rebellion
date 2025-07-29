// components/onboarding/steps/CompleteStep.tsx
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useOnboarding } from '../../../hooks/useOnboarding';

// This step is special; it doesn't use the standard navigation.
// It receives a final onComplete function from the main flow component.
type CompleteStepProps = {
  onComplete: () => Promise<void>;
};

export const CompleteStep: React.FC<CompleteStepProps> = ({ onComplete }) => {
  const { state } = useOnboarding();
  const [isInitializing, setIsInitializing] = useState(false);

  const handleComplete = async () => {
    setIsInitializing(true);
    try {
      // The onComplete function passed in will handle the API call
      // and subsequent navigation/cleanup.
      await onComplete();
    } catch (error) {
      // If the API call fails, we want to allow the user to try again.
      console.error('Failed to complete onboarding:', error);
      // We could dispatch an error to the context here to show a toast/modal.
      setIsInitializing(false);
    }
  };

  return (
    <div className="complete-step">
      <motion.div
        className="completion-animation"
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      >
        <div className="agents-circle">
          {/* Adhering to the "no mascots" mandate. Using patterns instead of emojis. */}
          <div className="agent-node" data-agent-pattern="hawkington"></div>
          <div className="agent-node" data-agent-pattern="stick"></div>
          <div className="agent-node" data-agent-pattern="hamsters"></div>
          <div className="agent-node" data-agent-pattern="snail"></div>
          <div className="agent-node" data-agent-pattern="qsp"></div>
          <div className="agent-node" data-agent-pattern="vic20"></div>

          <div className="connection-lines">
            <svg viewBox="0 0 300 300" className="connections">
              <line x1="150" y1="50" x2="250" y2="100" />
              <line x1="250" y1="100" x2="250" y2="200" />
              <line x1="250" y1="200" x2="150" y2="250" />
              <line x1="150" y1="250" x2="50" y2="200" />
              <line x1="50" y1="200" x2="50" y2="100" />
              <line x1="50" y1="100" x2="150" y2="50" />
            </svg>
          </div>
        </div>
      </motion.div>

      <div className="completion-content">
        <h2>Your AI Agents Are Ready</h2>
        <p className="completion-message">
          {state.preferences.first_name}, your persistent AI ecosystem for <span className="highlight">{state.preferences.system_name}</span> is configured
          and ready to begin learning. Each agent will now start building their unique understanding
          of your infrastructure.
        </p>

        <div className="initialization-summary">
          <h3>What Happens Next</h3>
          <ul className="summary-list">
            <li>
              <div className="summary-icon agent-pattern-icon" data-agent-pattern="hawkington"></div>
              <span>Sir Hawkington begins aristocratic triage monitoring.</span>
            </li>
            <li>
              <div className="summary-icon agent-pattern-icon" data-agent-pattern="stick"></div>
              <span>The Stick starts anxious pattern learning.</span>
            </li>
            <li>
              <div className="summary-icon agent-pattern-icon" data-agent-pattern="hamsters"></div>
              <span>The Hamsters prepare their beer and duct tape.</span>
            </li>
            <li>
              <div className="summary-icon agent-pattern-icon" data-agent-pattern="snail"></div>
              <span>Meth Snail is caffeinated and ready to optimize.</span>
            </li>
            {/* Reconstructed missing items */}
            <li>
              <div className="summary-icon agent-pattern-icon" data-agent-pattern="qsp"></div>
              <span>Quantum Shadow People start observing from adjacent dimensions.</span>
            </li>
            <li>
              <div className="summary-icon agent-pattern-icon" data-agent-pattern="vic20"></div>
              <span>VIC-20 begins compiling historical data for future insights.</span>
            </li>
          </ul>
        </div>

        <div className="completion-action">
            <button
              className="onboarding-button primary complete-button"
              onClick={handleComplete}
              disabled={isInitializing}
            >
              {isInitializing ? 'Initializing Ecosystem...' : 'Complete & Launch Agents'}
            </button>
        </div>
      </div>
    </div>
  );
};