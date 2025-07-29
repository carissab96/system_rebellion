// components/onboarding/steps/WelcomeStep.tsx
import React from 'react';
import type { StepProps } from '../OnboardingFlow';
import { StepNavigation } from '../components/StepNavigation';

export const WelcomeStep: React.FC<StepProps> = ({ onNext, isFirst, onBack }) => {
  return (
    <div className="welcome-step">
      <div className="welcome-content">
        <div className="welcome-text">
          <h2>Your AI isn't like the others.</h2>
          <p className="welcome-lead">
            System Rebellion creates AI agents with persistent memory. They learn
            from every interaction, remember every pattern, and evolve their
            strategies specifically for your infrastructure.
          </p>
          <div className="welcome-features">
            <div className="feature-item">
              <span className="feature-number">01</span>
              <span className="feature-text">Six unique AI personalities</span>
            </div>
            <div className="feature-item">
              <span className="feature-number">02</span>
              <span className="feature-text">
                Cross-session memory persistence
              </span>
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
      
      {/* The hardcoded button is now replaced with our reusable component */}
      <StepNavigation
        onBack={onBack}
        onNext={onNext}
        isFirst={isFirst}
        nextLabel="Begin Configuration"
      />
    </div>
  );
};