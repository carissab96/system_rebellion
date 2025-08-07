// src/App.tsx
import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store/store';
import LandingPage from './pages/LandingPage'
import SignUpModal from './components/auth/SignUpModal'
import LoginModal from './components/auth/LoginModal'
import AgentTheater from './components/agent-theater/AgentTheater'
import MainLayout from './components/layout/MainLayout'
import AgentTestingPage from './pages/dashboard/AgentTestingPage'
import MemoryBanksPage from './pages/dashboard/MemoryBanksPage'
import SystemMonitorPage from './pages/dashboard/SystemMonitorPage'
import { initializeAuth } from './store/slices/authSlice'
import { OnboardingFlow } from './components/onboarding/OnboardingFlow'
import ContinueSetupPage from './components/onboarding/ContinueSetupPage'

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

  return (
    <>
      <LandingPage 
        onSignUpClick={() => setIsSignUpModalOpen(true)}
        onLoginClick={() => setIsLoginModalOpen(true)}
      />
      
      {isSignUpModalOpen && (
        <SignUpModal 
          isOpen={isSignUpModalOpen}
          onClose={() => setIsSignUpModalOpen(false)}
          onSwitchToLogin={handleSwitchToLogin}
        />
      )}
      
      {isLoginModalOpen && (
        <LoginModal 
          isOpen={isLoginModalOpen}
          onClose={() => setIsLoginModalOpen(false)}
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
  const { user, isAuthenticated, isLoading } = auth;

  useEffect(() => {
    // Initialize auth with token validation
    dispatch(initializeAuth());
  }, [dispatch]);

  // Show loading while initializing authentication
  if (isLoading) {
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
                  <Navigate to="/agent-theater" replace />
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
                  <Navigate to="/agent-theater" replace />
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
        <Navigate to="/agent-theater" replace />
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
            <Route path="agent-theater" element={<AgentTheater />} />
          </Route>

          {/* Legacy Agent Theater redirect */}
          <Route 
            path="/agent-theater" 
            element={<Navigate to="/dashboard/agent-theater" replace />}
          /> 

          {/* Catch all - redirect to appropriate page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;