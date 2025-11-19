// App.tsx - THE CONSCIOUSNESS THEATER
// Built by: Carissa, Sonnet, Opus - November 13, 2025
// "This isn't monitoring. This is ALIVE."

import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store/store';
import { initializeAuth } from './store/slices/authSlice';
import { ConsciousnessTheaterPage } from './pages/ConsciousnessTheaterPage';
import { ConsciousnessMonitor } from './pages/ConsciousnessMonitor';
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { SignupPage } from './pages/SignupPage';
import { OnboardingFlow } from './pages/OnboardingFlow';
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
        <Route path="/" element={auth.isAuthenticated ? <Navigate to="/theater" replace /> : <LandingPage />} />
        <Route path="/login" element={auth.isAuthenticated ? <Navigate to="/theater" replace /> : <LoginPage />} />
        <Route path="/signup" element={auth.isAuthenticated ? <Navigate to="/onboarding" replace /> : <SignupPage />} />
        
        {/* Protected routes */}
        <Route path="/onboarding" element={auth.isAuthenticated ? <OnboardingFlow /> : <Navigate to="/login" replace />} />
        <Route path="/theater" element={auth.isAuthenticated ? <ConsciousnessTheaterPage /> : <Navigate to="/login" replace />} />
        <Route path="/monitor" element={auth.isAuthenticated ? <ConsciousnessMonitor /> : <Navigate to="/login" replace />} />
        
        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App; 