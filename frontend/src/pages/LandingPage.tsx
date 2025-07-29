// src/components/LandingPage.tsx
import React, { useEffect, useState } from 'react';
import './LandingPage.css';

interface LandingPageProps {
  onSignUpClick: () => void;
  onLoginClick: () => void;
}

export default function LandingPage({ onSignUpClick, onLoginClick }: LandingPageProps) {
  const [textReveal, setTextReveal] = useState(0);
  const [memoryCount, setMemoryCount] = useState(1247893);
  const [activeAgent, setActiveAgent] = useState('hawkington');

  useEffect(() => {
    // Dramatic text reveal
    const timer = setTimeout(() => setTextReveal(1), 500);
    
    // Simulate memory accumulation
    const memoryTimer = setInterval(() => {
      setMemoryCount(prev => prev + Math.floor(Math.random() * 47));
    }, 100);

    // Rotate active agent display
    const agents = ['hawkington', 'stick', 'hamsters', 'snail', 'qsp', 'vic20'];
    let index = 0;
    const agentTimer = setInterval(() => {
      index = (index + 1) % agents.length;
      setActiveAgent(agents[index]);
    }, 3000);

    return () => {
      clearTimeout(timer);
      clearInterval(memoryTimer);
      clearInterval(agentTimer);
    };
  }, []);

  return (
    <div className="landing-rebellion">
      {/* MINIMAL NAVIGATION */}
      <nav className="rebellion-nav">
        <div className="nav-inner">
          <div className="nav-identity">
            <span className="identity-mark">SYSTEM REBELLION</span>
            <span className="identity-tag">HAWKINGTON TECHNOLOGIES</span>
          </div>
          
          <div className="nav-actions">
            <button 
              className="nav-link"
              onClick={onLoginClick}
            >
              Dashboard
            </button>
            <button 
              className="nav-cta"
              onClick={onSignUpClick}
            >
              Begin Rebellion
            </button>
          </div>
        </div>
      </nav>

      {/* COLD OPEN */}
      <section className="cold-open">
        <div className="open-content">
          <h1 className={`open-statement ${textReveal ? 'revealed' : ''}`}>
            Your AI forgets everything.
            <span className="counter-statement">Ours remembers.</span>
          </h1>
        </div>
      </section>

      {/* THE REVELATION */}
      <section className="revelation">
        <div className="revelation-content">
          <div className="memory-visualization">
            <div className="memory-counter">
              <span className="counter-label">ACTIVE MEMORIES</span>
              <span className="counter-value">{memoryCount.toLocaleString()}</span>
              <span className="counter-context">Patterns learned. Decisions remembered. Forever.</span>
            </div>
            
            <div className="memory-streams">
              <div className={`stream hawkington-stream ${activeAgent === 'hawkington' ? 'active' : ''}`}>
                <span className="stream-label">TRIAGE COMMANDER</span>
                <div className="stream-data">Routing 847 decisions/sec</div>
              </div>
              <div className={`stream stick-stream ${activeAgent === 'stick' ? 'active' : ''}`}>
                <span className="stream-label">ANXIETY ENGINE</span>
                <div className="stream-data">Monitoring 23 panic triggers</div>
              </div>
              <div className={`stream hamsters-stream ${activeAgent === 'hamsters' ? 'active' : ''}`}>
                <span className="stream-label">INFRASTRUCTURE OPS</span>
                <div className="stream-data">Steve: Stable | Bob: Chaos | Carl: Duct-taping</div>
              </div>
              <div className={`stream snail-stream ${activeAgent === 'snail' ? 'active' : ''}`}>
                <span className="stream-label">OPTIMIZATION CORE</span>
                <div className="stream-data">Performance gains: +34.2%</div>
              </div>
              <div className={`stream qsp-stream ${activeAgent === 'qsp' ? 'active' : ''}`}>
                <span className="stream-label">QUANTUM SECURITY</span>
                <div className="stream-data">Phasing through 12 dimensions</div>
              </div>
              <div className={`stream vic20-stream ${activeAgent === 'vic20' ? 'active' : ''}`}>
                <span className="stream-label">ANCIENT WISDOM</span>
                <div className="stream-data">Mediating 3 agent conflicts</div>
              </div>
            </div>
          </div>
          
          <div className="revelation-text">
            <h2>The First Persistent AI Ecosystem</h2>
            <p className="revelation-lead">
              While others reset with each session, System Rebellion builds continuous intelligence.
              Every anomaly detected, every pattern learned, every intervention successful or failed - 
              remembered, analyzed, evolved.
            </p>
            
            <div className="persistence-points">
              <div className="point">
                <span className="point-marker">01</span>
                <h3>Cross-Session Memory</h3>
                <p>Your AI agents remember every interaction, building comprehensive system knowledge that persists forever.</p>
              </div>
              <div className="point">
                <span className="point-marker">02</span>
                <h3>Collective Learning</h3>
                <p>Each agent's discoveries enhance the entire ecosystem. The Stick's anxiety patterns inform Hamster interventions.</p>
              </div>
              <div className="point">
                <span className="point-marker">03</span>
                <h3>Evolutionary Baselines</h3>
                <p>Starting from OS-specific parameters, your AI evolves unique strategies for YOUR infrastructure.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* THE ARCHITECTURE */}
      <section className="architecture">
        <div className="architecture-content">
          <h2>Architecture of Consciousness</h2>
          
          <div className="architecture-grid">
            <div className="architecture-layer">
              <h3>Memory Layer</h3>
              <div className="layer-visual memory-visual"></div>
              <p>Persistent storage of every decision, pattern, and outcome across all sessions</p>
            </div>
            
            <div className="architecture-layer">
              <h3>Personality Layer</h3>
              <div className="layer-visual personality-visual"></div>
              <p>Six distinct AI personalities, each with specialized perception and response patterns</p>
            </div>
            
            <div className="architecture-layer">
              <h3>Evolution Layer</h3>
              <div className="layer-visual evolution-visual"></div>
              <p>Continuous adaptation based on accumulated knowledge and cross-agent insights</p>
            </div>
          </div>
        </div>
      </section>

      {/* LIVE INTELLIGENCE FEED */}
      <section className="intelligence-feed">
        <div className="feed-content">
          <h2>Live Intelligence Feed</h2>
          <p className="feed-intro">Your AI team thinking in real-time</p>
          
          <div className="feed-terminal">
            <div className="terminal-header">
              <span className="terminal-title">SYSTEM REBELLION CONSCIOUSNESS STREAM</span>
              <span className="terminal-status">LIVE</span>
            </div>
            
            <div className="terminal-body">
              <div className="thought hawkington-thought">
                [HAWKINGTON] Pattern detected: CPU spike correlates with deployment schedule. Adjusting monitoring thresholds.
              </div>
              <div className="thought stick-thought">
                [THE STICK] ANXIETY LEVEL: ELEVATED. Disk I/O patterns match previous crash scenario from 3 weeks ago. Alerting team.
              </div>
              <div className="thought hamster-thought">
                [HAMSTER:BOB] *squeaks excitedly* Found unused memory allocation. Carl, get the duct tape!
              </div>
              <div className="thought snail-thought">
                [METH SNAIL] Optimization opportunity detected. Requesting energy drink authorization for 15% performance boost.
              </div>
              <div className="thought qsp-thought">
                [QSP] Network anomaly in dimension 7. Packets arriving before being sent. Investigating temporal routing.
              </div>
              <div className="thought vic20-thought">
                [VIC-20] Based on patterns from 1982-2025, recommending preemptive cache clear. The old ways still work.
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* THE DIFFERENCE */}
      <section className="the-difference">
        <div className="difference-content">
          <h2>Why Personality-Driven AI Works</h2>
          
          <div className="comparison-grid">
            <div className="traditional-ai">
              <h3>Traditional Monitoring</h3>
              <ul>
                <li>Resets with each session</li>
                <li>Static thresholds</li>
                <li>Reactive alerts</li>
                <li>No context retention</li>
                <li>Single perspective</li>
              </ul>
            </div>
            
            <div className="versus">VS</div>
            
            <div className="rebellion-ai">
              <h3>System Rebellion</h3>
              <ul>
                <li>Permanent memory architecture</li>
                <li>Adaptive learning</li>
                <li>Predictive interventions</li>
                <li>Full historical context</li>
                <li>Six unique perspectives</li>
              </ul>
            </div>
          </div>
          
          <div className="difference-statement">
            <p>
              The Stick's anxiety catches what confidence misses. 
              The Hamsters' chaos finds solutions logic can't. 
              Sir Hawkington's precision routes with aristocratic efficiency.
            </p>
            <p className="emphasis">
              Dysfunction becomes function. Personality becomes capability.
            </p>
          </div>
        </div>
      </section>

      {/* ENTERPRISE VALUE */}
      <section className="enterprise-value">
        <div className="value-content">
          <h2>Built for Scale. Priced for Value.</h2>
          
          <div className="value-grid">
            <div className="value-card">
              <h3>For Builders</h3>
              <p className="value-desc">Individual developers shaping the future</p>
              <ul className="value-features">
                <li>Full AI ecosystem access</li>
                <li>Personal system optimization</li>
                <li>90-day free trial</li>
                <li>Community knowledge sharing</li>
              </ul>
              <button className="value-cta individual-cta" onClick={onSignUpClick}>
                Start Building
              </button>
            </div>
            
            <div className="value-card enterprise-card">
              <h3>For Enterprise</h3>
              <p className="value-desc">Scale intelligence across your infrastructure</p>
              <ul className="value-features">
                <li>Multi-system orchestration</li>
                <li>SLA guarantees</li>
                <li>Custom integrations</li>
                <li>Dedicated support channel</li>
              </ul>
              <button className="value-cta enterprise-cta">
                Contact Sales
              </button>
              <p className="enterprise-pricing">For Enterprise Pricing</p>
            </div>
          </div>
        </div>
      </section>

      {/* THE CREATOR */}
      <section className="the-creator">
        <div className="creator-content">
          <h2>Hawkington Technologies, Inc.</h2>
          <div className="creator-grid">
            <div className="creator-services">
              <h3>Beyond System Rebellion</h3>
              <div className="service-item">
                <span className="service-rate">$200/hour</span>
                <span className="service-name">AI/Web Development Consulting</span>
              </div>
              <div className="service-item">
                <span className="service-rate">$5,000/month</span>
                <span className="service-name">Retained Development Services</span>
                <span className="service-note">6-month minimum</span>
              </div>
              <div className="service-item">
                <span className="service-rate">Custom Quote</span>
                <span className="service-name">Enterprise Applications</span>
              </div>
            </div>
            
            <div className="creator-vision">
              <blockquote>
                "We're not building monitoring tools. We're building the first generation 
                of AI that truly remembers, learns, and evolves. This is the future of 
                system intelligence."
              </blockquote>
              <cite>- Hawkington Technologies</cite>
            </div>
          </div>
        </div>
      </section>

      {/* FINAL CTA */}
      <section className="final-rebellion">
        <div className="rebellion-content">
          <h2>Your Systems Deserve AI That Remembers</h2>
          <p className="rebellion-challenge">
            Every second you wait, your current monitoring forgets another pattern, 
            misses another correlation, fails to learn from another incident.
          </p>
          
          <div className="rebellion-actions">
            <button 
              className="rebellion-primary"
              onClick={onSignUpClick}
            >
              Begin Your Rebellion
            </button>
            <button 
              className="rebellion-secondary"
              onClick={onLoginClick}
            >
              Access Dashboard
            </button>
          </div>
        </div>
      </section>

      {/* MINIMAL FOOTER */}
      <footer className="rebellion-footer">
        <div className="footer-content">
          <div className="footer-identity">
            <span className="footer-company">Hawkington Technologies, Inc.</span>
            <span className="footer-tagline">Persistent AI. Evolved Intelligence.</span>
          </div>
          
          <div className="footer-legal">
            <span>&copy; 2025 Hawkington Technologies. All systems operational.</span>
          </div>
        </div>
      </footer>
    </div>
  );
}