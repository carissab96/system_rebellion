// src/components/onboarding/hooks/useOnboarding.ts (or wherever you placed it)
import { useContext } from 'react';
import { OnboardingContext, type OnboardingContextType } from '../components/onboarding/OnboardingContext';

/**
 * Custom hook to consume the OnboardingContext.
 * This provides type-safe access to the onboarding state and dispatch function.
 * 
 * @returns {OnboardingContextType} The onboarding context value with state and dispatch
 * @throws {Error} If used outside of an OnboardingProvider
 */
const useOnboarding = (): OnboardingContextType => {
  const context = useContext(OnboardingContext);
  
  if (context === undefined) {
    throw new Error('useOnboarding must be used within an OnboardingProvider');
  }
  
  return context;
};

export { useOnboarding };