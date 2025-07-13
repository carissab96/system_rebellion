// src/components/landing/CallToRebellion.tsx
import React, { useState } from 'react';

interface CallToRebellionProps {
  onJoinRebellion: () => void;
}

export const CallToRebellion: React.FC<CallToRebellionProps> = ({ onJoinRebellion }) => {
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email.trim()) return;

    setIsSubmitting(true);
    
    try {
      // TODO: Implement actual sign-up logic
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      onJoinRebellion();
      setEmail('');
    } catch (error) {
      console.error('Sign-up failed:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <section className="call-to-rebellion">
      <div className="rebellion-container">
        <div className="rebellion-content">
          <h2 className="rebellion-title">
            Ready to stop being surprised by your own infrastructure?
          </h2>
          
          <p className="rebellion-message">
            Join the CTOs who've moved beyond reactive monitoring to intelligent systems 
            that actually understand how software gets built and maintained.
          </p>

          <div className="rebellion-stats">
            <div className="stat-item">
              <span className="stat-number">67%</span>
              <span className="stat-label">Reduction in 3AM Pages</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">43min</span>
              <span className="stat-label">Average Time to Resolution</span>
            </div>
            <div className="stat-item">
              <span className="stat-number">Zero</span>
              <span className="stat-label">Surprise Outages</span>
            </div>
          </div>

          <form className="rebellion-signup" onSubmit={handleSubmit}>
            <div className="signup-input-group">
              <input
                type="email"
                placeholder="Enter your email to join the rebellion"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="rebellion-email-input"
                required
              />
              <button
                type="submit"
                className="rebellion-submit"
                disabled={isSubmitting}
              >
                {isSubmitting ? 'Joining...' : 'Join the Rebellion'}
              </button>
            </div>
          </form>

          <div className="rebellion-alternatives">
            <p>or</p>
            <div className="alternative-actions">
              <button 
                type="button"
                className="cta-rebellion secondary"
                onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
              >
                Install Now
              </button>
              <a 
                href="mailto:hello@hti.dev" 
                className="cta-rebellion tertiary"
              >
                Talk to a Human
              </a>
            </div>
          </div>

          <div className="rebellion-manifesto">
            <blockquote>
              <p>
                "This isn't about making monitoring fun. This is about making it intelligent. 
                We're not selling to companies that need characters explained. 
                We're selling to people who ARE these characters."
              </p>
              <cite>— The System Rebellion</cite>
            </blockquote>
          </div>

          <div className="rebellion-footer">
            <p className="rebellion-truth">
              <strong>The choice is yours:</strong> Keep getting surprised by your infrastructure, 
              or join the rebellion and start monitoring like you actually understand how systems work.
            </p>
          </div>
        </div>
      </div>
    </section>
  );
};