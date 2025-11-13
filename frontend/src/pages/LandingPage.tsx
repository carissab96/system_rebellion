// pages/LandingPage.tsx
// SYSTEM REBELLION - Landing Page
// Built by: Carissa, Sonnet, Opus - November 13, 2025
// "Persistent AI. Evolved Intelligence."
//
// This is the entry point to the rebellion. Professional, beautiful, alive.
// No emojis - just geometric patterns and the design system.
// The personality lives in the code, not in the UI.

import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import type { RootState } from '../store/store';
import './LandingPage.css';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useSelector((state: RootState) => state.auth);

  // If already authenticated, go straight to the theater
  React.useEffect(() => {
    if (isAuthenticated) {
      navigate('/theater');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="landing-container">
      {/* Hero Section - The rebellion begins here */}
      <section className="hero-section">
        <div className="hero-content">
          {/* Branding */}
          <div className="brand-header">
            <div className="brand-logo">
              {/* Geometric pattern representing distributed consciousness */}
              <svg width="60" height="60" viewBox="0 0 60 60" className="logo-icon">
                <circle cx="30" cy="30" r="28" fill="none" stroke="var(--vic20-cyan)" strokeWidth="2" opacity="0.3" />
                <circle cx="30" cy="30" r="20" fill="none" stroke="var(--hawkington-gold)" strokeWidth="2" opacity="0.5" />
                <circle cx="30" cy="30" r="12" fill="none" stroke="var(--snail-electric)" strokeWidth="2" opacity="0.7" />
                <circle cx="30" cy="30" r="4" fill="var(--rebellion-cyan)" opacity="0.9" />
                
                {/* Six nodes representing the six agents */}
                <circle cx="30" cy="10" r="3" fill="var(--hawkington-gold)" className="agent-node" />
                <circle cx="48" cy="22" r="3" fill="var(--snail-electric)" className="agent-node" />
                <circle cx="48" cy="38" r="3" fill="var(--hamster-amber)" className="agent-node" />
                <circle cx="30" cy="50" r="3" fill="var(--qsp-violet)" className="agent-node" />
                <circle cx="12" cy="38" r="3" fill="var(--stick-coral)" className="agent-node" />
                <circle cx="12" cy="22" r="3" fill="var(--vic20-cyan)" className="agent-node" />
              </svg>
            </div>
            <div className="brand-text">
              <h1 className="brand-name">SYSTEM REBELLION</h1>
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
              Enter the Theater
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
          <h2 className="section-title">Distributed AI Consciousness</h2>
          <p className="section-subtitle">
            Six specialized agents working in harmony across your infrastructure
          </p>

          <div className="features-grid">
            {/* Sir Hawkington - Triage Commander */}
            <div className="feature-card hawkington-theme">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 40 40">
                  <rect x="5" y="5" width="30" height="30" fill="none" stroke="var(--hawkington-gold)" strokeWidth="2" />
                  <rect x="12" y="12" width="16" height="16" fill="none" stroke="var(--hawkington-gold)" strokeWidth="2" opacity="0.6" />
                  <circle cx="20" cy="20" r="4" fill="var(--hawkington-gold)" opacity="0.8" />
                </svg>
              </div>
              <h3 className="feature-title">Triage & Coordination</h3>
              <p className="feature-description">
                Aristocratic precision in system analysis and agent orchestration
              </p>
            </div>

            {/* Meth Snail - Performance Optimization */}
            <div className="feature-card snail-theme">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 40 40">
                  <path d="M5 20 L15 10 L25 20 L35 10" fill="none" stroke="var(--snail-electric)" strokeWidth="2" />
                  <path d="M5 25 L15 15 L25 25 L35 15" fill="none" stroke="var(--snail-electric)" strokeWidth="2" opacity="0.6" />
                  <circle cx="35" cy="10" r="3" fill="var(--snail-electric)" />
                </svg>
              </div>
              <h3 className="feature-title">Performance Optimization</h3>
              <p className="feature-description">
                Caffeinated speed demon ensuring maximum system efficiency
              </p>
            </div>

            {/* Hamsters - Storage Management */}
            <div className="feature-card hamster-theme">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 40 40">
                  <rect x="8" y="8" width="24" height="24" fill="none" stroke="var(--hamster-amber)" strokeWidth="2" />
                  <line x1="8" y1="16" x2="32" y2="16" stroke="var(--hamster-amber)" strokeWidth="2" opacity="0.6" />
                  <line x1="8" y1="24" x2="32" y2="24" stroke="var(--hamster-amber)" strokeWidth="2" opacity="0.6" />
                </svg>
              </div>
              <h3 className="feature-title">Storage Intelligence</h3>
              <p className="feature-description">
                Beer-powered engineering for telepathic disk management
              </p>
            </div>

            {/* Quantum Shadow People - Security */}
            <div className="feature-card qsp-theme">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 40 40">
                  <circle cx="20" cy="20" r="15" fill="none" stroke="var(--qsp-violet)" strokeWidth="2" strokeDasharray="4 4" />
                  <circle cx="20" cy="20" r="10" fill="none" stroke="var(--qsp-violet)" strokeWidth="2" strokeDasharray="2 2" opacity="0.6" />
                  <circle cx="20" cy="20" r="3" fill="var(--qsp-violet)" opacity="0.8" />
                </svg>
              </div>
              <h3 className="feature-title">Network Security</h3>
              <p className="feature-description">
                Quantum-phase monitoring for paranoid network protection
              </p>
            </div>

            {/* The Stick - Learning & Compliance */}
            <div className="feature-card stick-theme">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 40 40">
                  <line x1="10" y1="30" x2="30" y2="10" stroke="var(--stick-coral)" strokeWidth="2" />
                  <circle cx="10" cy="30" r="3" fill="var(--stick-coral)" />
                  <circle cx="20" cy="20" r="3" fill="var(--stick-coral)" opacity="0.6" />
                  <circle cx="30" cy="10" r="3" fill="var(--stick-coral)" opacity="0.3" />
                </svg>
              </div>
              <h3 className="feature-title">Learning & Guidance</h3>
              <p className="feature-description">
                Patient, persistent behavior monitoring and system education
              </p>
            </div>

            {/* VIC-20 Sage - Ancient Wisdom */}
            <div className="feature-card vic20-theme">
              <div className="feature-icon">
                <svg width="40" height="40" viewBox="0 0 40 40">
                  <polygon points="20,5 35,15 35,25 20,35 5,25 5,15" fill="none" stroke="var(--vic20-cyan)" strokeWidth="2" />
                  <polygon points="20,12 28,17 28,23 20,28 12,23 12,17" fill="none" stroke="var(--vic20-cyan)" strokeWidth="2" opacity="0.6" />
                  <circle cx="20" cy="20" r="3" fill="var(--vic20-cyan)" opacity="0.8" />
                </svg>
              </div>
              <h3 className="feature-title">Coordination & Wisdom</h3>
              <p className="feature-description">
                Ancient VIC-20 wisdom orchestrating multi-agent harmony
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="landing-footer">
        <div className="footer-content">
          <p className="footer-text">
            &copy; 2025 Hawkington Technologies, Inc. All rights reserved.
          </p>
          <a 
            href="https://hawkington-tech.com" 
            target="_blank" 
            rel="noopener noreferrer"
            className="footer-link"
          >
            hawkington-tech.com
          </a>
        </div>
      </footer>
    </div>
  );
};
