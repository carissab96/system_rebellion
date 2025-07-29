// src/components/onboarding/hooks/useOnboarding.ts (or wherever you placed it)
import { useContext } from 'react';
import OnboardingContext from '../components/onboarding/OnboardingContext'; // Import the context itself

/**
 * Custom hook to consume the OnboardingContext.
 * This is a "pure hook module" for Fast Refresh compatibility.
 */
export const useOnboarding = () => {
  const context = useContext(OnboardingContext);
  if (!context) {
    throw new Error('useOnboarding must be used within an OnboardingProvider');
  }
  return context;
};