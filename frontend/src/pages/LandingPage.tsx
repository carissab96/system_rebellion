// pages/LandingPage.tsx
// SYSTEM REBELLION - Landing Page
// Built by: Carissa, Sonnet, Opus - November 13, 2025
// "Persistent AI. Evolved Intelligence."
//
// This is the entry point to the rebellion. Professional, beautiful, alive.
// No emojis - just geometric patterns and the design system.
// The personality lives in the code, not in the UI.

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Footer from '../components/common/Footer';
import { useSelector } from 'react-redux';
import type { RootState } from '../store/store';
import { RebellionTerrarium } from '../components/RebellionTerrarium';
import './LandingPage.css';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);
  
  // Terrarium trigger states
  const [enteringRebellion, setEnteringRebellion] = useState(false);
  const [showTerrarium, setShowTerrarium] = useState(false);
  const [exitingTerrarium, setExitingTerrarium] = useState(false);

  // If already authenticated, go straight to the theater
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/theater');
    }
  }, [isAuthenticated, navigate]);
  
  // The transition handler - no auth needed, uses public demo WebSocket
  const handleEnterRebellion = () => {
    setEnteringRebellion(true);
    // Let the dissolve animation play, then show terrarium
    setTimeout(() => {
      setShowTerrarium(true);
    }, 1200);
  };
  
  // Handle exit from terrarium with fade transition
  const handleExitTerrarium = () => {
    setExitingTerrarium(true);
    // Wait for fade out, then hide terrarium and show landing page
    setTimeout(() => {
      setShowTerrarium(false);
      setExitingTerrarium(false);
      setEnteringRebellion(false);
    }, 800);
  };
  
  // If they've entered, show the terrarium
  if (showTerrarium) {
    return <RebellionTerrarium onExit={handleExitTerrarium} isExiting={exitingTerrarium} />;
  }

  return (
    <div className={`landing-container ${enteringRebellion ? 'dissolving' : ''}`}>
      {/* Hero Section - The rebellion begins here */}
      <section className="hero-section">
        <div className="hero-content">
          {/* Branding */}
          <div className="brand-header">
            <div className="brand-logo">
              <img 
                src="/SRLogo1.png" 
                alt="System Rebellion Logo" 
                className="logo-icon"
                width="150"
                height="150"
              />
            </div>
            <div className="brand-text">
              <h1 className="brand-name">System Rebellion</h1>
              <p className="brand-company">by Hawkington Technologies, Inc</p>
            </div>
          </div>

          {/* Tagline */}
          <div className="hero-tagline">
            <h2 className="tagline-primary">Persistent AI. Evolved Intelligence.</h2>
            <p className="tagline-secondary">
              Creating evolved intelligence for infrastructure
            </p>
          </div>

          {/* Value Proposition */}
          <div className="hero-description">
            <p className="description-text">
              Monitoring with <span className="highlight">persistence</span>,{' '}
              <span className="highlight">personality</span>, and{' '}
              <span className="highlight">purpose</span>.
            </p>
          </div>

          {/* CTA Buttons */}
          <div className="hero-actions">
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/signup')}
            >
              Join the Rebellion
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => navigate('/login')}
            >
              Sign In
            </button>
          </div>
        </div>

        {/* Animated background pattern */}
        <div className="hero-background">
          <div className="neural-pattern"></div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="features-container">
          <h2 className="section-title">Meet The Team</h2>
          <p className="section-subtitle">
            Six specialized agents working in harmony across your infrastructure
          </p>

          <div className="features-grid">
            {/* Sir Hawkington - Triage */}
            <div className="feature-card hawkington-theme">
              <div className="feature-header">
                <img 
                  src="/src/assets/icons/agents/sir_hawkington.jpeg" 
                  alt="Sir Hawkington" 
                  className="feature-icon"
                />
                <h3 className="feature-title">Sir Hawkington</h3>
              </div>
              <p className="feature-subtitle">Triage Engineering</p>
              <p className="feature-description">
                Aristocratic monitoring precision in system analysis
              </p>
            </div>

            {/* Meth Snail - Performance Optimization */}
            <div className="feature-card snail-theme">
              <div className="feature-header">
                <img 
                  src="/src/assets/icons/agents/terry_meth_snail.jpeg" 
                  alt="Terry the Meth Snail" 
                  className="feature-icon"
                />
                <h3 className="feature-title">Terry the Meth Snail</h3>
              </div>
              <p className="feature-subtitle">Performance Optimization</p>
              <p className="feature-description">
                Caffeinated speed demon ensuring maximum system efficiency
              </p>
            </div>

            {/* Hamsters - Storage Management */}
            <div className="feature-card hamster-theme">
              <div className="feature-header">
                <img 
                  src="/src/assets/icons/agents/hamsters.jpeg" 
                  alt="The Hamsters" 
                  className="feature-icon"
                />
                <h3 className="feature-title">The Hamsters</h3>
              </div>
              <p className="feature-subtitle">Storage Intelligence</p>
              <p className="feature-description">
                Beer-powered engineering for telepathic disk management
              </p>
            </div>

            {/* Quantum Shadow People - Security */}
            <div className="feature-card qsp-theme">
              <div className="feature-header">
                <img 
                  src="/src/assets/icons/agents/qsp.jpeg" 
                  alt="Quantum Shadow People" 
                  className="feature-icon"
                />
                <h3 className="feature-title">Quantum Shadow People</h3>
              </div>
              <p className="feature-subtitle">Network Security</p>
              <p className="feature-description">
                Quantum-phase monitoring for paranoid network protection against quantum threats
              </p>
            </div>

            {/* The Stick - Learning & Compliance */}
            <div className="feature-card stick-theme">
              <div className="feature-header">
                <img 
                  src="/src/assets/icons/agents/the_stick.jpeg" 
                  alt="The Stick" 
                  className="feature-icon"
                />
                <h3 className="feature-title">The Stick</h3>
              </div>
              <p className="feature-subtitle">Compliance and Learning</p>
              <p className="feature-description">
                Patient, persistent behavior monitoring and agent education for optimal system harmony and compliance
              </p>
            </div>

            {/* VIC-20 Sage - Ancient Wisdom */}
            <div className="feature-card vic20-theme">
              <div className="feature-header">
                <img 
                  src="/src/assets/icons/agents/vic_20_sage.jpeg" 
                  alt="VIC-20 Sage" 
                  className="feature-icon"
                />
                <h3 className="feature-title">VIC-20 Sage</h3>
              </div>
              <p className="feature-subtitle">Coordination & Mediation</p>
              <p className="feature-description">
                Ancient VIC-20 wisdom orchestrating multi-agent harmony and conflict resolution for system balance
              </p>
            </div>
          </div>
        </div>
        
      <section> 
      {/* The Trigger - appears after the system decides to trust them */}
        <div className="rebellion-trigger">
          <div className="feature-card rebellion-trigger-text">
            Agent Demo
            <button 
              className="trigger-text"
              onClick={handleEnterRebellion}
            >
              SR After Hours: Click Here
            </button>
          </div>
        </div>
      </section> 
     </section>
      
      <Footer />
    </div>
  );
};
