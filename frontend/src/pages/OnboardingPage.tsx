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
  
  // Check if user already has system profile information
  const hasSystemInfo = user?.profile && (
    user.profile.operating_system ||
    user.profile.os_version ||
    user.profile.cpu_cores ||
    user.profile.total_memory
  );
  
  // Redirect to dashboard if user has already completed system profile
  if (user && hasSystemInfo) {
    console.log("User already has system profile information, redirecting to dashboard");
    return <Navigate to="/dashboard" />;
  }
  
  return <Onboarding />;
};

export default OnboardingPage;