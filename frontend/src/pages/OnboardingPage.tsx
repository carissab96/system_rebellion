// src/pages/OnboardingPage.tsx
import { useSelector } from 'react-redux';
import { Navigate } from 'react-router-dom';
import Onboarding from '../components/onboarding/onboarding';
import { RootState } from '../store/store';

const OnboardingPage = () => {
  const { isAuthenticated, user } = useSelector((state: RootState) => state.auth);
  
  // Redirect to login if not authenticated
  if (!isAuthenticated) {
    return <Navigate to="/login" />;
  }
  
  // Redirect to dashboard if user has already completed onboarding
  if (user && !user.needs_onboarding) {
    return <Navigate to="/dashboard" />;
  }
  
  return <Onboarding />;
};

export default OnboardingPage;