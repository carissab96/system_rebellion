// src/App.tsx
import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import OnboardingPage from './pages/OnboardingPage'
import SignUpModal from './components/auth/SignUpModal'
import LoginModal from './components/auth/LoginModal'
import type { User } from './types/auth'

// Import CSS files from correct locations
// import './index.css'
// import './styles/rebellion-core.css'
// import './styles/agent-personalities.css'
// import './styles/common-components.css'
// import './components/auth/LoginModal.css'
// import './components/auth/SignUpModal.css'
// import './components/navigation/ProfileDropdown.css'

function App() {
  const [isSignUpModalOpen, setIsSignUpModalOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [authToken, setAuthToken] = useState<string | null>(null);

  // Initialize auth state from localStorage
  useEffect(() => {
    const savedToken = localStorage.getItem('auth_token');
    const savedUser = localStorage.getItem('user_data');
    
    if (savedToken && savedUser) {
      setAuthToken(savedToken);
      setUser(JSON.parse(savedUser));
    }
  }, []);

  // Handle successful SignUp - redirect to onboarding
  const handleSignUpSuccess = (userData: User, token: string) => {
    setUser(userData);
    setAuthToken(token);
    setIsSignUpModalOpen(false);
    
    // Store in localStorage for persistence
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user_data', JSON.stringify(userData));
  };

  // Handle successful Login - redirect based on onboarding status
  const handleLoginSuccess = (userData: User, token: string) => {
    setUser(userData);
    setAuthToken(token);
    setIsLoginModalOpen(false);
    
    // Store in localStorage for persistence
    localStorage.setItem('auth_token', token);
    localStorage.setItem('user_data', JSON.stringify(userData));
  };

  // Handle onboarding completion
  const handleOnboardingComplete = (updatedUser: User) => {
    setUser(updatedUser);
    localStorage.setItem('user_data', JSON.stringify(updatedUser));
  };

  // Handle logout
  const handleLogout = () => {
    setUser(null);
    setAuthToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  };

  // Modal switching
  const handleSwitchToSignUp = () => {
    setIsLoginModalOpen(false);
    setIsSignUpModalOpen(true);
  };

  const handleSwitchToLogin = () => {
    setIsSignUpModalOpen(false);
    setIsLoginModalOpen(true);
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Landing Page - only show if not authenticated */}
          <Route 
            path="/" 
            element={
              user ? (
                user.isOnboarded ? (
                  <Navigate to="/dashboard" replace />
                ) : (
                  <Navigate to="/onboarding" replace />
                )
              ) : (
                <LandingPage 
                  onSignUpClick={() => setIsSignUpModalOpen(true)}
                  onLoginClick={() => setIsLoginModalOpen(true)}
                />
              )
            } 
          />

          {/* Onboarding - only accessible if authenticated but not onboarded */}
          <Route 
            path="/onboarding" 
            element={
              user ? (
                !user.isOnboarded ? (
                  <OnboardingPage 
                    user={user}
                    token={authToken!}
                    onComplete={handleOnboardingComplete}
                  />
                ) : (
                  <Navigate to="/dashboard" replace />
                )
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />

          {/* Dashboard - placeholder for now */}
          <Route 
            path="/dashboard" 
            element={
              user && user.isOnboarded ? (
                <div className="dashboard-placeholder">
                  <h1>Dashboard Coming Soon!</h1>
                  <p>Welcome, {user.firstName}!</p>
                  <button onClick={handleLogout}>Logout</button>
                </div>
              ) : (
                <Navigate to="/" replace />
              )
            } 
          />

          {/* Catch all - redirect to appropriate page */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        {/* Auth Modals - only show on landing page */}
        {!user && (
          <>
            {isSignUpModalOpen && (
              <SignUpModal 
                isOpen={isSignUpModalOpen}
                onClose={() => setIsSignUpModalOpen(false)}
                onSuccess={handleSignUpSuccess}
                onSwitchToLogin={handleSwitchToLogin}
              />
            )}
            
            {isLoginModalOpen && (
              <LoginModal 
                isOpen={isLoginModalOpen}
                onClose={() => setIsLoginModalOpen(false)}
                onSuccess = {handleLoginSuccess}
                onSwitchToSignUp={handleSwitchToSignUp}
              />
            )}
          </>
        )}
      </div>
    </Router>
  )
}

export default App