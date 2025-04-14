import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAppSelector } from '../store/hooks';

interface PrivateRouteProps {
    children: React.ReactNode;
}

export const PrivateRoute: React.FC<PrivateRouteProps> = ({ children }) => {
    const { isAuthenticated, isLoading } = useAppSelector(state => state.auth);

    // Show loading indicator while checking authentication status
    if (isLoading) {
        return (
            <div className="auth-loading">
                <div className="loading-spinner"></div>
                <p>Sir Hawkington is verifying your credentials...</p>
            </div>
        );
    }

    // Redirect to login if not authenticated
    if (!isAuthenticated) {
        console.log("🚫 Access denied: Not authenticated");
        return <Navigate to="/login" replace />;
    }

    // Render children if authenticated
    return <>{children}</>;
};
