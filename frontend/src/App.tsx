// src/App.tsx
import { useState, useEffect, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store/store';
import LandingPage from './pages/LandingPage'
import SignUpModal from './components/auth/SignUpModal'
import LoginModal from './components/auth/LoginModal'
// OLD: import AgentTheater from './components/agent-theater/AgentTheater'
import { LiveAgentTheaterPage } from './pages/LiveAgentTheaterPage'
// import AgentTheaterOld from './components/agent-theater/AgentTheater'
import MainLayout from './components/layout/MainLayout'
import AgentTestingPage from './pages/dashboard/AgentTestingPage'
import MemoryBanksPage from './pages/dashboard/MemoryBanksPage'
import { SystemMonitorPage } from './pages/dashboard/SystemMonitorPage'
import { initializeAuth } from './store/slices/authSlice'
import { OnboardingFlow } from './components/onboarding/OnboardingFlow'
import ContinueSetupPage from './components/onboarding/ContinueSetupPage'
import './index.css'
// Landing page with modal state management
function LandingPageWithModals() {
  const [isSignUpModalOpen, setIsSignUpModalOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);



  const handleSwitchToSignUp = () => {
    setIsLoginModalOpen(false);
    setIsSignUpModalOpen(true);
  };

  const handleSwitchToLogin = () => {
    setIsSignUpModalOpen(false);
    setIsLoginModalOpen(true);
  };

  const handleLoginClick = useCallback((e?: React.MouseEvent) => {
    e?.preventDefault();
    e?.stopPropagation();
    setIsLoginModalOpen(true);
  }, []);

  const handleLoginClose = useCallback(() => {
    setIsLoginModalOpen(false);
  }, []);

  const handleSignUpClose = useCallback(() => {
    setIsSignUpModalOpen(false);
  }, []);

  return (
    <>
      <LandingPage 
        onSignUpClick={() => setIsSignUpModalOpen(true)}
        onLoginClick={handleLoginClick}
      />
      
      {isSignUpModalOpen && (
        <SignUpModal 
          isOpen={isSignUpModalOpen}
          onClose={handleSignUpClose}
          onSwitchToLogin={handleSwitchToLogin}
        />
      )}
      
      {isLoginModalOpen && (
        <LoginModal 
          isOpen={isLoginModalOpen}
          onClose={handleLoginClose}
          onSwitchToSignUp={handleSwitchToSignUp}
          // ❌ REMOVED onSuccess - LoginModal should handle Redux internally
        />
      )}
    </>
  );
}

// Main App component
function App() {
  const dispatch = useDispatch<AppDispatch>();
  const auth = useSelector((state: RootState) => state.auth);
  const { user, isAuthenticated, isInitializing } = auth;

  useEffect(() => {
    // Initialize auth with token validation
    dispatch(initializeAuth());
  }, [dispatch]);  

  // Show loading while initializing authentication
  if (isInitializing) {
    return <div className="app-loading">Initializing System Rebellion...</div>;
  }
  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Landing Page - only show if not authenticated */}
          <Route 
            path="/" 
            element={
              isAuthenticated && user ? (
                user.is_onboarded ? (
                  <Navigate to="/dashboard/agent-theater" replace />
                ) : (
                  <Navigate to="/onboarding" replace />
                )
              ) : (
                <LandingPageWithModals />
              )
            } 
          />

          {/* Onboarding - only accessible if authenticated but not onboarded */}
          <Route 
            path="/onboarding" 
            element={
              isAuthenticated && user ? (
                !user.is_onboarded ? (
                  <OnboardingFlow /> 
                ) : (
                  <Navigate to="/dashboard/agent-theater" replace />
                )
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />
          {/* Continue Setup - for users with saved progress */}
<Route 
  path="/continue-setup" 
  element={
    isAuthenticated && user ? (
      !user.is_onboarded ? (
        <ContinueSetupPage /> 
      ) : (
        <Navigate to="/dashboard/agent-theater" replace />
      )
    ) : (
      <Navigate to="/" replace />
    )
  }   
/>
          {/* Dashboard - only accessible if authenticated and onboarded */}
          <Route 
            path="/dashboard/*" 
            element={
              isAuthenticated && user && user.is_onboarded ? (
                <MainLayout />
              ) : (
                <Navigate to="/" replace />
              )
            }
          >
            {/* Dashboard sub-routes */}
            <Route index element={<Navigate to="/dashboard/agent-testing" replace />} />
            <Route path="agent-testing" element={<AgentTestingPage />} />
            <Route path="memory-banks" element={<MemoryBanksPage />} />
            <Route path="system-monitor" element={<SystemMonitorPage />} />
            <Route path="agent-theater" element={<LiveAgentTheaterPage />} />
            {/* <Route path="agent-theater-old" element={<AgentTheaterOld />} /> */}
          </Route>

          {/* Catch all - redirect to appropriate page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App; 