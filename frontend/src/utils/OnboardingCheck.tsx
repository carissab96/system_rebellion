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

    // Only check onboarding status if user is authenticated and not already on the onboarding page
    if (isAuthenticated && !isLoading && location.pathname !== '/onboarding') {
      // Check if we have user data
      if (!user) {
        console.log('No user data available, checking auth status again...');
        dispatch(checkAuthStatus());
        return;
      }

      // IMPORTANT: For existing users, only redirect to onboarding if needs_onboarding is EXPLICITLY true
      // This ensures users who have completed onboarding go straight to dashboard
      const needsOnboarding = user.needs_onboarding === true;
      
      // Additional check: If the user has system info already, they shouldn't need onboarding
      const hasSystemInfo = !!(user.operating_system || user.os_version || user.cpu_cores || user.total_memory);
      
      console.log('Checking onboarding status:', { 
        user, 
        needs_onboarding: user.needs_onboarding,
        needsOnboarding,
        hasSystemInfo,
        currentPath: location.pathname 
      });
      
      // Only redirect to onboarding if explicitly needed AND user doesn't have system info
      if (needsOnboarding && !hasSystemInfo) {
        console.log('User needs onboarding and has no system info, redirecting to /onboarding');
        navigate('/onboarding', { replace: true });
      } else {
        // If user has system info but needs_onboarding is still true, fix it
        if (needsOnboarding && hasSystemInfo) {
          console.log('User has system info but needs_onboarding is true - this should be fixed');
          // We'll let them continue to their destination, the backend will fix this on next profile update
        }
        
        // If user is on the home page or login page after authentication, redirect to dashboard
        if (location.pathname === '/' || location.pathname === '/login') {
          console.log('Authenticated user on home/login page, redirecting to dashboard');
          navigate('/dashboard', { replace: true });
        } else {
          console.log('User does not need onboarding, continuing to requested page');
          setCheckComplete(true);
        }
      }
    } else if (isAuthenticated && !isLoading && location.pathname === '/onboarding') {
      // If we're on the onboarding page, check if the user actually needs onboarding
      if (user && user.needs_onboarding === false) {
        console.log('User does not need onboarding but is on onboarding page, redirecting to dashboard');
        navigate('/dashboard', { replace: true });
      } else {
        console.log('User is on onboarding page and needs onboarding, allowing...');
        setCheckComplete(true);
      }
    } else if (!isAuthenticated && !isLoading) {
      // If not authenticated and not loading, redirect to login
      console.log('User is not authenticated, redirecting to login');
      navigate('/login', { replace: true });
    } else if (isLoading) {
      // Still loading, wait for auth status to be determined
      console.log('Auth status is loading...');
    } else {
      console.log('Default case - setting checkComplete to true');
      setCheckComplete(true);
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
