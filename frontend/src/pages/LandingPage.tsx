import React from 'react';
import './LandingPage.css';

export const LandingPage: React.FC = () => {
  return (
    <div className="landing-page">
      {/* PROFESSIONAL NAVIGATION */}
      <nav className="landing-nav">
        <div className="nav-container">
          <div className="nav-logo">
            <span className="logo-text">System Rebellion</span>
            <span className="logo-subtitle">Hawkington Technologies</span>
          </div>
          
          <div className="nav-actions">
            <button className="btn btn-ghost">
              Documentation
            </button>
            <button className="btn btn-primary">
              Request Demo
            </button>
          </div>
        </div>
      </nav>

      {/* HERO SECTION - PROFESSIONAL */}
      <section className="hero-section">
        <div className="hero-container">
          <div className="hero-content">
            <h1 className="hero-title">
              Enterprise AI Agent Coordination Platform
              <span className="hero-accent">Built for Technical Teams</span>
            </h1>
            
            <p className="hero-subtitle">
              Six specialized AI agents that monitor, optimize, and coordinate your systems 
              with pattern recognition and proactive intelligence. Enterprise software 
              with personality-driven automation.
            </p>
            
            <div className="hero-stats">
              <div className="stat-item">
                <span className="stat-number">100%</span>
                <span className="stat-label">Operational</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">6</span>
                <span className="stat-label">AI Agents</span>
              </div>
              <div className="stat-item">
                <span className="stat-number">24/7</span>
                <span className="stat-label">Monitoring</span>
              </div>
            </div>
            
            <div className="hero-cta">
              <button className="btn btn-primary btn-large">
                Schedule Technical Demo
              </button>
              <button className="btn btn-secondary btn-large">
                View Documentation
              </button>
            </div>
          </div>
          
          <div className="hero-visual">
            <div className="dashboard-preview">
              <div className="preview-header">
                <span className="preview-title">Live Agent Coordination</span>
                <div className="status-online">
                  <span className="status-dot"></span>
                  <span>6 Agents Active</span>
                </div>
              </div>
              
              <div className="agent-status-grid">
                <div className="agent-status hawkington">
                  <span className="agent-indicator"></span>
                  <div className="agent-info">
                    <strong>System Monitor:</strong> Performance analysis active
                  </div>
                </div>
                
                <div className="agent-status snail">
                  <span className="agent-indicator"></span>
                  <div className="agent-info">
                    <strong>Optimization:</strong> Continuous improvement algorithms
                  </div>
                </div>
                
                <div className="agent-status vic20">
                  <span className="agent-indicator"></span>
                  <div className="agent-info">
                    <strong>Coordination:</strong> Ancient wisdom pattern matching
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* PROBLEM SECTION - PROFESSIONAL */}
      <section className="problem-section">
        <div className="container">
          <h2 className="section-title">
            Traditional Monitoring Solutions
            <span className="text-accent">Fall Short</span>
          </h2>
          
          <div className="problem-grid">
            <div className="problem-card">
              <div className="problem-icon">⚡</div>
              <h3>Reactive Architecture</h3>
              <p>Traditional systems alert after problems occur, creating downtime and lost productivity.</p>
            </div>
            
            <div className="problem-card">
              <div className="problem-icon">🔧</div>
              <h3>Static Thresholds</h3>
              <p>Fixed monitoring rules that don't adapt to changing system patterns or learn from historical data.</p>
            </div>
            
            <div className="problem-card">
              <div className="problem-icon">📊</div>
              <h3>Limited Intelligence</h3>
              <p>Basic alerting without context, pattern recognition, or proactive optimization capabilities.</p>
            </div>
            
            <div className="problem-card">
              <div className="problem-icon">🔄</div>
              <h3>Manual Coordination</h3>
              <p>Requires human intervention to coordinate between monitoring, optimization, and response systems.</p>
            </div>
          </div>
        </div>
      </section>

      {/* AGENT CAPABILITIES SECTION */}
      <section className="agents-section">
        <div className="container">
          <h2 className="section-title">
            Six Specialized AI Agents
            <span className="text-accent">Working in Coordination</span>
          </h2>
          
          <div className="agents-grid">
            <div className="agent-card hawkington-card">
              <div className="agent-header">
                <div className="agent-icon-professional">SM</div>
                <div>
                  <h3>System Monitor</h3>
                  <span className="agent-role">Performance Analysis</span>
                </div>
              </div>
              <p className="agent-description">
                Aristocratic precision in system monitoring with explosive response to performance degradation.
              </p>
              <div className="agent-capabilities">
                <span className="capability-tag">Real-time Analysis</span>
                <span className="capability-tag">Pattern Recognition</span>
                <span className="capability-tag">Threshold Intelligence</span>
              </div>
            </div>
            
            <div className="agent-card snail-card">
              <div className="agent-header">
                <div className="agent-icon-professional">OE</div>
                <div>
                  <h3>Optimization Engine</h3>
                  <span className="agent-role">Performance Enhancement</span>
                </div>
              </div>
              <p className="agent-description">
                High-energy continuous optimization with machine learning algorithms for system improvement.
              </p>
              <div className="agent-capabilities">
                <span className="capability-tag">Machine Learning</span>
                <span className="capability-tag">Performance Tuning</span>
                <span className="capability-tag">Predictive Analysis</span>
              </div>
            </div>
            
            <div className="agent-card hamster-card">
              <div className="agent-header">
                <div className="agent-icon-professional">ES</div>
                <div>
                  <h3>Engineering Solutions</h3>
                  <span className="agent-role">Rapid Response</span>
                </div>
              </div>
              <p className="agent-description">
                Innovative problem-solving with rapid deployment of engineering solutions and system fixes.
              </p>
              <div className="agent-capabilities">
                <span className="capability-tag">Rapid Deployment</span>
                <span className="capability-tag">Solution Architecture</span>
                <span className="capability-tag">Emergency Response</span>
              </div>
            </div>
            
            <div className="agent-card stick-card">
              <div className="agent-header">
                <div className="agent-icon-professional">CM</div>
                <div>
                  <h3>Compliance Management</h3>
                  <span className="agent-role">Configuration Control</span>
                </div>
              </div>
              <p className="agent-description">
                Obsessive compliance monitoring with trauma-informed precision for configuration management.
              </p>
              <div className="agent-capabilities">
                <span className="capability-tag">Compliance Automation</span>
                <span className="capability-tag">Configuration Management</span>
                <span className="capability-tag">Audit Trails</span>
              </div>
            </div>
            
            <div className="agent-card qsp-card">
              <div className="agent-header">
                <div className="agent-icon-professional">NA</div>
                <div>
                  <h3>Network Analysis</h3>
                  <span className="agent-role">Connection Intelligence</span>
                </div>
              </div>
              <p className="agent-description">
                Advanced network performance analysis with quantum-level connection optimization and routing intelligence.
              </p>
              <div className="agent-capabilities">
                <span className="capability-tag">Network Optimization</span>
                <span className="capability-tag">Traffic Analysis</span>
                <span className="capability-tag">Connection Routing</span>
              </div>
            </div>
            
            <div className="agent-card sage-card">
              <div className="agent-header">
                <div className="agent-icon-professional">CC</div>
                <div>
                  <h3>Coordination Center</h3>
                  <span className="agent-role">Ancient Wisdom</span>
                </div>
              </div>
              <p className="agent-description">
                Master coordinator applying decades of system knowledge with pattern recognition from 1989 to 2025.
              </p>
              <div className="agent-capabilities">
                <span className="capability-tag">Multi-Agent Coordination</span>
                <span className="capability-tag">Historical Analysis</span>
                <span className="capability-tag">Decision Orchestration</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* TECHNICAL PROOF SECTION */}
      <section className="proof-section">
        <div className="container">
          <h2 className="section-title">
            Proven in Production
            <span className="text-accent">Enterprise Environments</span>
          </h2>
          
          <div className="proof-grid">
            <div className="stat-card">
              <div className="stat-number">94%</div>
              <div className="stat-label">Coordination Success Rate</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-number">87%</div>
              <div className="stat-label">Productivity Improvement</div>
            </div>
            
            <div className="stat-card">
              <div className="stat-number">30+</div>
              <div className="stat-label">Database Tables</div>
            </div>
          </div>
          
          <div className="technical-details">
            <h3>Technical Architecture</h3>
            <div className="tech-grid">
              <div className="tech-item">
                <strong>Backend:</strong> FastAPI + SQLAlchemy + WebSockets
              </div>
              <div className="tech-item">
                <strong>Database:</strong> Enterprise-grade SQLite with performance indexes
              </div>
              <div className="tech-item">
                <strong>AI Architecture:</strong> Pattern learning with effectiveness tracking
              </div>
              <div className="tech-item">
                <strong>Communication:</strong> Real-time WebSocket coordination
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ENTERPRISE CTA SECTION */}
      <section className="cta-section">
        <div className="container">
          <h2 className="cta-title">Ready to Evaluate System Rebellion?</h2>
          <p className="cta-subtitle">
            Schedule a technical demonstration to see AI agent coordination in your environment.
          </p>
          
          <button className="btn btn-primary btn-xl">
            Schedule Technical Demo
          </button>
          
          <p className="cta-note">Technical evaluation available for qualified enterprise prospects.</p>
        </div>
      </section>

      {/* PROFESSIONAL FOOTER */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div>
              <h3>Hawkington Technologies, Inc.</h3>
              <p>Enterprise AI Agent Coordination Platform</p>
            </div>
            <div className="footer-links">
              <a href="#documentation">Documentation</a>
              <a href="#technical">Technical Specs</a>
              <a href="#support">Enterprise Support</a>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 Hawkington Technologies, Inc. All rights reserved.</p>
            <p>"From VIC-20 wisdom to enterprise AI coordination"</p>
          </div>
        </div>
      </footer>
    </div>
  );
};