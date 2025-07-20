// src/components/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useAppSelector } from '../hooks/redux';
import type { RootState } from '../store/store';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiresAdmin?: boolean;
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ 
    children, 
    requiresAdmin = false 
  }) => {
    const { isAuthenticated, user } = useAppSelector((state: RootState) => state.auth);
    const location = useLocation();
  
    if (!isAuthenticated) {
      return <Navigate to="/login" state={{ from: location }} replace />;
    }
  
    if (requiresAdmin && !user?.isAdmin) {
      return <Navigate to="/unauthorized" replace />;
    }
  
    return <>{children}</>;
  };
  