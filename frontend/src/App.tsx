// src/App.tsx
import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { useDispatch, useSelector } from 'react-redux'
import type { RootState } from './store/store'
import LandingPage from './pages/LandingPage'
import SignUpModal from './components/auth/SignUpModal'
import LoginModal from './components/auth/LoginModal'
import AgentTheater from './components/agent-theater/AgentTheater'
import { initializeAuth } from './store/slices/authSlice'
import { OnboardingFlow } from './components/onboarding/OnboardingFlow'

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
  const [isInitialized, setIsInitialized] = useState(false);
  const dispatch = useDispatch();
  const auth = useSelector((state: RootState) => state.auth);
  const { user, token, isAuthenticated } = auth;

  useEffect(() => {
    dispatch(initializeAuth());
    setIsInitialized(true); // Mark as initialized
  }, [dispatch]);

  // Show loading while initializing
  if (!isInitialized) {
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

          {/* Agent Theater - only accessible if authenticated and onboarded */}
          <Route 
            path="/agent-theater" 
            element={
              isAuthenticated && user && user.is_onboarded ? (
                <AgentTheater /> 
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />

          {/* Catch all - redirect to appropriate page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;