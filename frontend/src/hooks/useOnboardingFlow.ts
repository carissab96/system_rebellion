import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';


import useOnboarding from '../components/onboarding/OnboardingContext';
import clearSavedProgress from '../components/onboarding/OnboardingContext';
import apiService from '../services/api';

interface UseOnboardingFlowProps {
  totalSteps: number;
  onComplete?: () => void;
}

export const useOnboardingFlow = ({ totalSteps, onComplete }: UseOnboardingFlowProps) => {
  const { state, dispatch } = useOnboarding();
  const { currentStep } = state;
  const navigate = useNavigate();
  const [isCompleting, setIsCompleting] = useState(false);
  const [completionError, setCompletionError] = useState<string | null>(null);
  const [showExitConfirm, setShowExitConfirm] = useState(false);

  const goToStep = useCallback((step: number) => {
    if (step >= 1 && step <= totalSteps) {
      dispatch({ type: 'GO_TO_STEP', payload: step });
    }
  }, [dispatch, totalSteps]);

  const goToNext = useCallback(() => {
    if (currentStep < totalSteps) {
      goToStep(currentStep + 1);
    }
  }, [currentStep, totalSteps, goToStep]);

  const goToPrevious = useCallback(() => {
    if (currentStep > 1) {
      goToStep(currentStep - 1);
    }
  }, [currentStep, goToStep]);

  const handleSaveAndExit = useCallback(() => {
    // Progress is auto-saved by the context
    navigate('/');
  }, [navigate]);

  const handleExitConfirmation = useCallback(() => {
    setShowExitConfirm(true);
  }, []);

  const handleCancelExit = useCallback(() => {
    setShowExitConfirm(false);
  }, []);

  const handleCompleteOnboarding = useCallback(async () => {
    if (isCompleting) return;
    
    setIsCompleting(true);
    setCompletionError(null);

    try {
      await apiService.completeOnboarding(state);
      // Clear saved progress on successful completion
      clearSavedProgress();
      
      if (onComplete) {
        onComplete();
      } else {
        navigate('/AgentTheater');
      }
    } catch (error: any) {
      console.error('Failed to complete onboarding:', error);
      setCompletionError(
        error.response?.data?.detail || 
        error.message || 
        'Failed to complete onboarding. Please try again.'
      );
    } finally {
      setIsCompleting(false);
    }
  }, [isCompleting, state, navigate, onComplete]);



  return {
    currentStep,
    totalSteps,
    isFirstStep: currentStep === 1,
    isLastStep: currentStep === totalSteps,
    isCompleting,
    completionError,
    showExitConfirm,
    goToStep,
    goToNext,
    goToPrevious,
    handleSaveAndExit,
    handleExitConfirmation,
    handleCancelExit,
    handleCompleteOnboarding,
  };
};
