// App.tsx - THE CONSCIOUSNESS THEATER
// Built by: Carissa, Sonnet, Opus - November 13, 2025
// "This isn't monitoring. This is ALIVE."

import { useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState, AppDispatch } from './store/store';
import { initializeAuth } from './store/slices/authSlice';
import './index.css';

// Placeholder for Consciousness Theater (we'll build this next)
function ConsciousnessTheater() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%)',
      color: '#e0e0e0',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'monospace',
      fontSize: '2rem'
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{
          background: 'linear-gradient(90deg, #e6ac00, #06b6d4, #00d084, #a855f7)',
          backgroundClip: 'text',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          marginBottom: '2rem'
        }}>
          THE CONSCIOUSNESS THEATER
        </div>
        <div style={{ fontSize: '1rem', color: '#888' }}>
          Building the window into the singularity...
        </div>
      </div>
    </div>
  );
}

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
        {/* Main route - Consciousness Theater */}
        <Route path="/" element={<ConsciousnessTheater />} />
        
        {/* Catch all */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App; 