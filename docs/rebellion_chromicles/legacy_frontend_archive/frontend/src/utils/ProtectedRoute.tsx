// frontend/src/utils/ProtectedRoute.tsx
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppSelector, useAppDispatch } from '../store/hooks';
import { checkAuthStatus } from '../store/slices/authSlice';

export interface ProtectedRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
  children, 
  redirectTo = '/login' 
}) => {
  const { isAuthenticated, isLoading } = useAppSelector(state => state.auth);
  const dispatch = useAppDispatch();
  const navigate = useNavigate();

  useEffect(() => {
    // Only check auth if not already authenticated and not loading
    if (!isAuthenticated && !isLoading) {
      console.log('🧙‍♂️ The Stick: Protected route checking authentication...');
      dispatch(checkAuthStatus()).catch(error => {
        console.error('🚨 Auth check failed in protected route:', error);
      });
    }
  }, [isAuthenticated, isLoading, dispatch]);

  // Handle redirection when auth status is determined
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      console.log('🧙‍♂️ The Stick: Not authenticated, redirecting to', redirectTo);
      navigate(redirectTo, { replace: true });
    }
  }, [isAuthenticated, isLoading, navigate, redirectTo]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '2rem'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #3498db',
          borderRadius: '50%',
          animation: 'spin 1.5s linear infinite',
          marginBottom: '1rem'
        }}></div>
        <p>Sir Hawkington is verifying your credentials...</p>
        <style>{
          `@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }`
        }</style>
      </div>
    );
  }

  // Render children only if authenticated
  return isAuthenticated ? <>{children}</> : null;
};

export default ProtectedRoute;