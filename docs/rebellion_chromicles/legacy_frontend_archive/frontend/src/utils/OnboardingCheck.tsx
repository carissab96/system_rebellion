import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { checkAuthStatus } from '../store/slices/authSlice';

interface OnboardingCheckProps {
  children: React.ReactNode;
}

/**
 * A component that checks if a user needs to complete onboarding
 * and redirects them to the onboarding page if necessary.
 * Otherwise, it renders the children.
 */
const OnboardingCheck: React.FC<OnboardingCheckProps> = ({ children }) => {
  const { user, isAuthenticated, isLoading } = useAppSelector(state => state.auth);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const location = useLocation();
  const [checkComplete, setCheckComplete] = useState(false);

  useEffect(() => {
    // If auth status is not determined yet, check it
    if (!isAuthenticated && !isLoading) {
      console.log('Auth status not determined, checking...');
      dispatch(checkAuthStatus());
      return;
    }

    console.log('OnboardingCheck - Auth state:', { 
      isAuthenticated, 
      isLoading, 
      user, 
      pathname: location.pathname 
    });

    // Only proceed if we have authentication status and it's not loading
    if (!isLoading) {
      // If authenticated, handle redirection based on user state
      if (isAuthenticated) {
        // Check if we have user data
        if (!user) {
          console.log('No user data available, checking auth status again...');
          dispatch(checkAuthStatus());
          return;
        }

        // If user is on login page or home page, always redirect to dashboard
        if (location.pathname === '/' || location.pathname === '/login') {
          console.log('Authenticated user on home/login page, redirecting to dashboard');
          navigate('/dashboard', { replace: true });
          return;
        }

        // Check if user needs onboarding
        // IMPORTANT: Only redirect to onboarding if needs_onboarding is EXPLICITLY true
        // AND user doesn't have system info
        const hasSystemInfo = !!(user.operating_system || user.os_version || user.cpu_cores || user.total_memory);
        
        // Default to NOT needing onboarding unless explicitly set to true
        const needsOnboarding = user.needs_onboarding === true && !hasSystemInfo;
        
        console.log('Checking onboarding status:', { 
          user, 
          needs_onboarding: user.needs_onboarding,
          hasSystemInfo,
          needsOnboarding,
          currentPath: location.pathname 
        });
        
        // Handle onboarding redirection
        if (needsOnboarding && location.pathname !== '/onboarding') {
          // User needs onboarding and is not on the onboarding page
          console.log('User needs onboarding, redirecting to /onboarding');
          navigate('/onboarding', { replace: true });
        } else if (!needsOnboarding && location.pathname === '/onboarding') {
          // User doesn't need onboarding but is on the onboarding page
          console.log('User does not need onboarding but is on onboarding page, redirecting to dashboard');
          navigate('/dashboard', { replace: true });
        } else {
          // User is on the correct page based on their onboarding status
          console.log('User is on the correct page, rendering children');
          setCheckComplete(true);
        }
      } else {
        // Not authenticated, redirect to login unless already there
        if (location.pathname !== '/login') {
          console.log('User is not authenticated, redirecting to login');
          navigate('/login', { replace: true });
        } else {
          console.log('User is on login page and not authenticated, allowing...');
          setCheckComplete(true);
        }
      }
    }
  }, [isAuthenticated, isLoading, user, navigate, location.pathname, dispatch]);

  // If we're still loading or checking, show a loading indicator
  if (isLoading || !checkComplete) {
    return <div className="loading">Loading...</div>;
  }

  // Render the children once all checks are complete
  return <>{children}</>;
};

export default OnboardingCheck;
