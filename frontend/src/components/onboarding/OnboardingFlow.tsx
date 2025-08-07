/* eslint-disable no-console */
//new version at at 28 Jul 2025 22.42:11
// components/onboarding/OnboardingFlow.tsx
import React, { useState, useEffect, useRef } from 'react';

import type { AxiosError } from 'axios';
import { motion, AnimatePresence } from 'framer-motion';

import { useNavigate } from 'react-router-dom';

// Import our final, robust apiService;
import { useAppDispatch } from '../../hooks/redux';
import { useOnboarding } from '../../hooks/useOnboarding';
import { completeOnboarding } from '../../store/slices/authSlice';

import { ProgressBar } from './components/ProgressBar';
import OnboardingProvider from './OnboardingContext';
import styles from './OnboardingFlow.module.css';
import { steps } from './steps';
import AgentPreviewModal from './utils/AgentPreviewModal';

interface StepProps {
  onNext: () => void;
  onBack: () => void;
  onComplete: () => void;
  isFirst: boolean;
  isLast: boolean;
  isCompleting: boolean;
  completionError: string | null;
  nextLabel: string;
  backLabel: string;
  onSaveAndExit?: () => void;
  onSaveAndContinue?: () => void;
  onExit?: () => void;
}

const OnboardingFlowContent: React.FC = () => {
  const { 
    state, 
    dispatch, 
    showSaveModal, 
    setShowSaveModal,
    saveAndExit,
    exitWithoutSaving,
    saveProgress,
    clearSavedProgress,
    isProgressSaved,
    savedAt,
    startPreviewMode
  } = useOnboarding();
  
  const { currentStep } = state;
  const navigate = useNavigate();
  const authDispatch = useAppDispatch();
  const [isCompleting, setIsCompleting] = useState(false);
  const [completionError, setCompletionError] = useState<string | null>(null);
  const [showResumeNotice, setShowResumeNotice] = useState(false);
  const prevStepRef = useRef<number>(currentStep);
  useEffect(() => {
    if (currentStep > 1 && currentStep !== prevStepRef.current) {
      saveProgress(); //context handles the actual saving
      prevStepRef.current = currentStep;
    }
  }, [currentStep, saveProgress]);
  
  const currentStepInfo = steps[currentStep - 1];
  const { component: CurrentStepComponent, title, subtitle } = currentStepInfo;
  const totalSteps = steps.length;

  const handleNext = () => dispatch({ type: 'NEXT_STEP' });
  const handleBack = () => dispatch({ type: 'PREVIOUS_STEP' });

  const handleComplete = async () => {
    if (isCompleting) return;
    setIsCompleting(true);
    setCompletionError(null);

    try {
      const onboardingData = {
        first_name: state.profile.first_name,
        last_name: state.profile.last_name,
        company_name: state.profile.company_name,
        job_title: state.profile.job_title,
        system_name: state.system.system_name,
        system_profile: state.system.system_profile,
        permissions_granted: state.system.permissions_granted,
        installation_method: state.system.installation_method,
        agent_preferences: state.preferences.agent_preferences,
        monitoring_preferences: state.preferences.monitoring_preferences,
        is_onboarded: true
      };
      await authDispatch(completeOnboarding(onboardingData)).unwrap();;
      
      await clearSavedProgress();

      navigate('/agent-theater');
    } catch (err: any) {
      const error = err as AxiosError<any>;
      const errorMessage = error.response?.data?.detail || 'A server error occurred. Please try again.';
      setCompletionError(errorMessage);
    } finally {
      setIsCompleting(false);
    }
  };

  const handleSaveAndContinue = () => {
    saveProgress();
    // You could show a toast notification here
    console.log('Progress saved manually');
  };

  const handleCancelSetup = () => {
    setShowSaveModal(true);
  };

  const handleSelectAgent = (agentId: string) => {
    // Start preview mode with selected agent
    startPreviewMode(agentId);
    setShowSaveModal(false);
  };



  return (
    <div className={styles.onboardingFlow}>
      {/* Resume Notice */}
      {showResumeNotice && (
        <div className="alert alert-info mb-3" style={{ position: 'relative' }}>
          <strong>Welcome back!</strong> Your progress has been restored from {savedAt ? new Date(savedAt).toLocaleString() : 'your last session'}.
          <button 
            onClick={() => setShowResumeNotice(false)}
            style={{ position: 'absolute', right: '0.5rem', top: '0.5rem', background: 'none', border: 'none', fontSize: '1.2rem', cursor: 'pointer' }}
          >
            ×
          </button>
        </div>
      )}

      <div className={`${styles.onboardingCard} card`}>
        {/* Progress Bar */}
        <div className="card-body">
          <ProgressBar totalSteps={totalSteps} currentStep={currentStep} />
        </div>

        {/* Header with Cancel Button */}
        <header className={`${styles.stepHeader} card-header`}>
          <div className="d-flex justify-between align-center">
            <div>
              <h1 className="card-title">{title}</h1>
              <p className="card-subtitle mt-1">{subtitle}</p>
            </div>
            
            {/* Cancel Setup Button - Only show after Welcome step */}
            {currentStep > 1 && (
              <div className="d-flex align-center gap-2">
                {isProgressSaved && (
                  <span className="text-xs text-dim">
                    Saved {savedAt ? new Date(savedAt).toLocaleTimeString() : 'recently'}
                  </span>
                )}
                <button 
                  className="btn btn-ghost btn-sm"
                  onClick={() => setShowSaveModal(true)}
                  title="Cancel setup and save progress"
                >
                  Cancel Setup
                </button>
              </div>
            )}
          </div>
        </header>
      
        {/* Step Content */}
        <main className={`${styles.contentArea} card-body`}>
          <AnimatePresence mode="wait">
            <motion.div key={currentStep} className="slide-in-up">
              <CurrentStepComponent
                onNext={handleNext}
                onBack={handleBack}
                onComplete={handleComplete}
                isFirst={currentStep === 1}
                isLast={currentStep === totalSteps}
                isCompleting={isCompleting}
                nextLabel="Next"
                backLabel="Back"
                completionError={completionError}
                onSaveAndContinue={handleSaveAndContinue}
                onExit={handleCancelSetup}
              />
            </motion.div>
          </AnimatePresence>
        </main>

        {/* Optional: Footer with save status */}
        {currentStep > 1 && (
          <footer className="card-footer text-center">
            <small className="text-dim">
              {isProgressSaved ? (
                <>Progress automatically saved • Step {currentStep} of {totalSteps}</>
              ) : (
                <>Step {currentStep} of {totalSteps}</>
              )}
            </small>
          </footer>
        )}
      </div>

      {/* Save Progress Modal */}
      {showSaveModal && (
        <AgentPreviewModal
          isOpen={showSaveModal}
          onClose={() => setShowSaveModal(false)}
          onSelectAgent={handleSelectAgent}
          onSaveAndContinueLater={saveAndExit}
          onStartOver={exitWithoutSaving}
        />
      )}
    </div>
  );
};

// The main export wraps everything in the provider
export const OnboardingFlow: React.FC = () => {
  return (
    <OnboardingProvider>
      <OnboardingFlowContent />
    </OnboardingProvider>
  );
};

export type { StepProps };