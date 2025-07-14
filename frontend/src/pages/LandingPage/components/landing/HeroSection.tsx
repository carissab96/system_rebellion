// src/components/landing/HeroSection.tsx
import React from 'react';

interface HeroSectionProps {
  onGetStarted: () => void;
}

export const HeroSection: React.FC<HeroSectionProps> = ({ onGetStarted }) => {
  return (
    <section className="hero-rebellion">
      <div className="hero-container">
        <div className="hero-brand">
          {/* Logo placeholder - replace with your actual logo */}
          <div className="logo-placeholder">
            <img 
              src="/assets/logo-system-rebellion.png" 
              alt="The System Rebellion" 
              className="rebellion-logo"
            />
          </div>
          
          <h1 className="hero-title">
            Your monitoring should understand 
            <span className="hero-emphasis"> how you actually work.</span>
          </h1>
          
          <p className="hero-truth">
            Built by developers who've been there at 3AM with duct tape and determination.
            <br />
            For CTOs who know that behind every "enterprise solution" 
            is someone making miracles happen.
          </p>
          
          <div className="hero-actions">
            <button 
              className="cta-rebellion primary"
              onClick={onGetStarted}
            >
              See how we actually monitor systems
            </button>
            
            <button className="cta-rebellion secondary">
              Watch the rebellion in action
            </button>
          </div>
        </div>
        
        <div className="hero-visual">
          {/* Placeholder for hero image/animation */}
          <div className="hero-image-placeholder">
            <p>// Hero visual goes here</p>
            <p>// Maybe rotating character showcase?</p>
            <p>// Or live AI decision feed?</p>
          </div>
        </div>
      </div>
    </section>
  );
};