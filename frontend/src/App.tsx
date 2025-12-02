// App.tsx - SYSTEM REBELLION
// Built by: Carissa & Dell-Sonnet - November 20, 2025
// "Evolved Intelligence. Actually Intelligent."

import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store/store';
import { initializeAuth } from './store/slices/authSlice';
import { ObservatoryPage } from './pages/ObservatoryPage';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { OnboardingFlow } from './pages/OnboardingFlow';
import AgentMonitorPage from './pages/AgentMonitorPage';
import './index.css';

function App() {
  const dispatch = useDispatch<AppDispatch>();
  const auth = useSelector((state: RootState) => state.auth);
  const { isInitializing } = auth;

  useEffect(() => {
    // Initialize auth with token validation
    dispatch(initializeAuth());
  }, [dispatch]);

  // Show loading while initializing
  if (isInitializing) {
    return (
      <div style={{
        minHeight: '100vh',
        background: '#0a0a0a',
        color: '#00d084',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontFamily: 'monospace'
      }}>
        Initializing System Rebellion...
      </div>
    );
  }

  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/" element={auth.isAuthenticated ? <Navigate to="/observatory" replace /> : <LandingPage />} />
        <Route path="/login" element={auth.isAuthenticated ? <Navigate to="/observatory" replace /> : <LoginPage />} />
        <Route path="/signup" element={auth.isAuthenticated ? <Navigate to="/onboarding" replace /> : <SignupPage />} />
        
        {/* Protected routes */}
        <Route path="/onboarding" element={auth.isAuthenticated ? <OnboardingFlow /> : <Navigate to="/login" replace />} />
        <Route path="/observatory" element={auth.isAuthenticated ? <ObservatoryPage /> : <Navigate to="/login" replace />} />
        <Route path="/agent-monitor" element={auth.isAuthenticated ? <AgentMonitorPage /> : <Navigate to="/login" replace />} />
        
        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App; 