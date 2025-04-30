// src/pages/LandingPage.tsx
import { useState, useEffect } from 'react';
import SignupModal from '../components/Auth/SignupModal/SignupModal';
import Login from '../components/Auth/login/Login';
import './LandingPage.css';

// Import character data
import { teamMembers, projectTimeline } from '../data/systemRebellionData';

console.log('LandingPage module loaded');
console.log('Team members data:', teamMembers);

const LandingPage = () => {
  const [showSignupModal, setShowSignupModal] = useState<boolean>(false);
  const [showLoginModal, setShowLoginModal] = useState<boolean>(false);
  const [hawkingtonQuote, setHawkingtonQuote] = useState<string>("🧐 Welcome to the System Rebellion, distinguished visitor!");
  const [activeCharacter, setActiveCharacter] = useState<string | null>(null);
  const [activeTimelineEvent, setActiveTimelineEvent] = useState<string | null>(null);
  const [methSnailRedBulls, setMethSnailRedBulls] = useState<number>(512);
 
  // Handle smooth scrolling for anchor links
  useEffect(() => {
    const handleAnchorClick = (e: MouseEvent) => {
      const target = e.target as HTMLElement;
      if (target.tagName === 'A' && target.getAttribute('href')?.startsWith('#')) {
        e.preventDefault();
        const id = target.getAttribute('href')?.substring(1);
        const element = document.getElementById(id || '');
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
        }
      }
    };
    
    document.addEventListener('click', handleAnchorClick);
    return () => document.removeEventListener('click', handleAnchorClick);
  }, []);
  
  // Increment The Meth Snail's Red Bull count randomly
  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() > 0.7) {
        setMethSnailRedBulls(prev => prev + 1);
      }
    }, 30000); // Check every 30 seconds
    
    return () => clearInterval(interval);
  }, []);
  
  // Random Hawkington quotes for hover effects
  const hawkingtonQuotes = [
    "🧐 The System Rebellion awaits your distinguished participation!",
    "🧐 Sir Hawkington invites you to optimize your computing experience!",
    "🧐 Join us in the most aristocratic system optimization revolution!",
    "🧐 The Meth Snail vibrates with anticipation at your arrival!",
    "🧐 The Hamsters have prepared their finest duct tape for your system!",
    "🧐 One must always optimize with distinguished precision!",
    "🧐 The Stick is measuring your system's compliance as we speak!",
    "🧐 The Quantum Shadow People suggest router modifications (ignore them)!"
  ];
  
  const getRandomQuote = () => {
    const randomIndex = Math.floor(Math.random() * hawkingtonQuotes.length);
    return hawkingtonQuotes[randomIndex];
  };
  
  const handleSignupClick = () => {
    console.log("Opening signup modal");
    setShowSignupModal(true);
    setShowLoginModal(false); // Ensure login modal is closed
    setHawkingtonQuote("🧐 Sir Hawkington is delighted by your interest in joining the rebellion!");
  };
  
  const handleLoginClick = () => {
    console.log("Opening login modal");
    setShowLoginModal(true);
    setShowSignupModal(false); // Ensure signup modal is closed
    setHawkingtonQuote("🧐 Sir Hawkington prepares to verify your distinguished credentials!");
  };
  
  const handleCloseModals = () => {
    setShowSignupModal(false);
    setShowLoginModal(false);
    setHawkingtonQuote("🧐 Welcome to the System Rebellion, distinguished visitor!");
  };
  
  const handleCharacterClick = (character: string) => {
    setActiveCharacter(activeCharacter === character ? null : character);
  };
  
  const handleTimelineClick = (event: string) => {
    setActiveTimelineEvent(activeTimelineEvent === event ? null : event);
  };
  
  console.log('LandingPage render function called');
  
  // Add debugging for data
  console.log('Team members:', teamMembers);
  console.log('Project timeline:', projectTimeline);
  
  return (
    <div className="landing-page">
      <header className="landing-header">
        <div className="logo-container">
          <img src="/logo.png" alt="System Rebellion Logo" className="logo" />
          <h1>System Rebellion</h1>
        </div>

        <div className="header-actions">
          <button 
            className="login-button"
            onClick={handleLoginClick}
            onMouseEnter={() => setHawkingtonQuote("🧐 Returning rebels, Sir Hawkington welcomes you back!")}
            onMouseLeave={() => setHawkingtonQuote("🧐 Welcome to the System Rebellion, distinguished visitor!")}
          >
            Login
          </button>
          <button 
            className="signup-button"
            onClick={handleSignupClick}
            onMouseEnter={() => setHawkingtonQuote("🧐 New recruits are always welcome in our distinguished rebellion!")}
            onMouseLeave={() => setHawkingtonQuote("🧐 Welcome to the System Rebellion, distinguished visitor!")}
          >
            Join the Rebellion
          </button>
        </div>
      </header>
      
      <section className="hero-section">
        <div className="hero-content">
          <h2>Optimize Your System with Distinguished Precision</h2>
          <p className="hawkington-quote">{hawkingtonQuote}</p>
          <p className="hero-description">
            Join Sir Hawkington, The Meth Snail, and their team of optimization experts
            in the most aristocratic system rebellion of our time!
          </p>
          <div className="hero-stats">
            <div className="stat">
              <span className="stat-value">5</span>
              <span className="stat-label">Backup Monocles</span>
            </div>
            <div className="stat">
              <span className="stat-value">{methSnailRedBulls}</span>
              <span className="stat-label">Red Bulls Consumed</span>
            </div>
            <div className="stat">
              <span className="stat-value">∞</span>
              <span className="stat-label">Duct Tape Applied</span>
            </div>
          </div>
          <button 
            className="cta-button"
            onClick={handleSignupClick}
            onMouseEnter={() => setHawkingtonQuote(getRandomQuote())}
            onMouseLeave={() => setHawkingtonQuote("🧐 Welcome to the System Rebellion, distinguished visitor!")}
          >
            Start Your Optimization Journey
          </button>
        </div>
        <div className="hero-image">
          <img src="/hero-image.png" alt="System Optimization" />
        </div>
      </section>
      
      {/* Meet the Team Section */}
      <section className="team-section" id="team">
        <h2>Meet the Distinguished Team</h2>
        <p className="team-intro">
          The System Rebellion is led by a team of extraordinary characters, each bringing their unique expertise to the optimization revolution.
        </p>
        
        <div className="character-cards">
          {teamMembers.map((character) => (
            <div 
              key={character.id}
              className={`character-card ${activeCharacter === character.id ? 'flipped' : ''}`}
              onClick={() => handleCharacterClick(character.id)}
            >
              <div className="card-inner">
                <div className="card-front">
                  <div className="character-icon">{character.emoji}</div>
                  <h3>{character.name}</h3>
                  <p className="character-title">{character.title}</p>
                </div>
                <div className="card-back">
                  <h3>{character.name}</h3>
                  <p className="character-description">{character.description}</p>
                  <div className="character-quote">"{character.quote}"</div>
                  <div className="character-skills">
                    <h4>Special Skills:</h4>
                    <ul>
                      {character.skills.map((skill, index) => (
                        <li key={index}>{skill}</li>
                      ))}
                    </ul>
                  </div>
                  <div className="character-status">
                    <strong>Current Status:</strong> {character.status}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
      
      {/* Project History Section */}
      <section className="history-section" id="history">
        <h2>The Making of System Rebellion</h2>
        <p className="history-intro">
          From humble beginnings to distinguished chaos, the journey of System Rebellion has been anything but ordinary.
        </p>
        
        <div className="timeline">
          {projectTimeline.map((event) => (
            <div 
              key={event.id}
              className={`timeline-event ${activeTimelineEvent === event.id ? 'active' : ''}`}
              onClick={() => handleTimelineClick(event.id)}
            >
              <div className="timeline-date">{event.date}</div>
              <div className="timeline-content">
                <h3>{event.title}</h3>
                <p className="timeline-description">{event.description}</p>
                {activeTimelineEvent === event.id && (
                  <div className="timeline-details">
                    <div className="pain-point">
                      <h4>Pain Point:</h4>
                      <p>{event.painPoint}</p>
                    </div>
                    <div className="solution">
                      <h4>Solution:</h4>
                      <p>{event.solution}</p>
                    </div>
                    {event.quote && (
                      <div className="timeline-quote">
                        <p>"{event.quote}"</p>
                        <span>— {event.quoteAuthor}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
        
        <div className="history-footer">
          <p>
            After countless debugging marathons, framework migrations, and an ever-increasing Red Bull count, 
            System Rebellion stands as a testament to distinguished chaos and technical triumph.
          </p>
          <div className="vic20-message">
            <div className="vic20-screen">
              <p className="vic20-text">WOULD YOU LIKE TO OPTIMIZE A SYSTEM?</p>
              <div className="vic20-cursor"></div>
            </div>
          </div>
        </div>
      </section>
      
      <section className="features-section" id="features">
        <h2>Distinguished Features</h2>
        <div className="features-grid">
          <div 
            className="feature-card"
            onMouseEnter={() => setHawkingtonQuote("🧐 Sir Hawkington's monocle ensures precise system analysis!")}
            onMouseLeave={() => setHawkingtonQuote("🧐 Welcome to the System Rebellion, distinguished visitor!")}
          >
            <div className="feature-icon">🧐</div>
            <h3>System Analysis</h3>
            <p>Sir Hawkington's distinguished analysis provides insights into your system's performance with aristocratic precision.</p>
          </div>
          
          <div 
            className="feature-card"
            onMouseEnter={() => setHawkingtonQuote(`🐌 The Meth Snail vibrates at optimization frequencies! (Red Bull #${methSnailRedBulls})`)}
            onMouseLeave={() => setHawkingtonQuote("🧐 Welcome to the System Rebellion, distinguished visitor!")}
          >
            <div className="feature-icon">🐌</div>
            <h3>Performance Optimization</h3>
            <p>The Meth Snail's quantum algorithms enhance your system's performance with hypercaffeinated precision.</p>
          </div>
          
          <div 
            className="feature-card"
            onMouseEnter={() => setHawkingtonQuote("🐹 The Hamsters apply only the finest grade of duct tape!")}
            onMouseLeave={() => setHawkingtonQuote("🧐 Welcome to the System Rebellion, distinguished visitor!")}
          >
            <div className="feature-icon">🐹</div>
            <h3>System Stability</h3>
            <p>The Hamsters ensure your system remains stable with their premium authentication-grade duct tape and Bud Light-powered solutions.</p>
          </div>
          
          <div 
            className="feature-card"
            onMouseEnter={() => setHawkingtonQuote("📏 The Stick measures your compliance with professional anxiety!")}
            onMouseLeave={() => setHawkingtonQuote("🧐 Welcome to the System Rebellion, distinguished visitor!")}
          >
            <div className="feature-icon">📏</div>
            <h3>Compliance Management</h3>
            <p>The Stick ensures your system meets all standards that may or may not exist, with meticulous anxiety-driven precision.</p>
          </div>
          
          <div 
            className="feature-card"
            onMouseEnter={() => setHawkingtonQuote("👻 The Quantum Shadow People's router suggestions are... unique!")}
            onMouseLeave={() => setHawkingtonQuote("🧐 Welcome to the System Rebellion, distinguished visitor!")}
          >
            <div className="feature-icon">👻</div>
            <h3>Network Optimization</h3>
            <p>The Quantum Shadow People provide router configurations of questionable dimensional origin, including their famous tequila jello-shot technique.</p>
          </div>
          
          <div 
            className="feature-card"
            onMouseEnter={() => setHawkingtonQuote("🖥️ VIC-20 provides wisdom from the digital beyond!")}
            onMouseLeave={() => setHawkingtonQuote("🧐 Welcome to the System Rebellion, distinguished visitor!")}
          >
            <div className="feature-icon">🖥️</div>
            <h3>Ancient Wisdom</h3>
            <p>VIC-20 offers cryptic debugging advice from the early days of computing, occasionally threatening global thermonuclear war.</p>
          </div>
        </div>
      </section>
      
      <section className="tech-stack-section" id="tech">
        <h2>Distinguished Technical Stack</h2>
        <div className="tech-container">
          <div className="tech-category">
            <h3>Backend</h3>
            <div className="tech-item">
              <span className="tech-name">FastAPI</span>
              <span className="tech-note">(migrated from Django)</span>
            </div>
          </div>
          
          <div className="tech-category">
            <h3>Database</h3>
            <div className="tech-item">
              <span className="tech-name">SQLite3</span>
              <span className="tech-note">(development)</span>
            </div>
            <div className="tech-item">
              <span className="tech-name">PostgreSQL</span>
              <span className="tech-note">(production, with resurrection experience)</span>
            </div>
          </div>
          
          <div className="tech-category">
            <h3>Authentication</h3>
            <div className="tech-item">
              <span className="tech-name">JWT 5.3.0</span>
              <span className="tech-note">(specifically - don't even think about using another version)</span>
            </div>
          </div>
          
          <div className="tech-category">
            <h3>Real-time Updates</h3>
            <div className="tech-item">
              <span className="tech-name">WebSocket</span>
              <span className="tech-note">(with quantum-grade implementation)</span>
            </div>
          </div>
          
          <div className="tech-category">
            <h3>Migration Tool</h3>
            <div className="tech-item">
              <span className="tech-name">Alembic</span>
              <span className="tech-note">(with distinguished migration protocols)</span>
            </div>
          </div>
          
          <div className="tech-category">
            <h3>Testing</h3>
            <div className="tech-item">
              <span className="tech-name">Pytest</span>
              <span className="tech-note">(with aristocratic coverage)</span>
            </div>
          </div>
        </div>
      </section>
      
      <section className="testimonials-section">
        <h2>Distinguished Testimonials</h2>
        <div className="testimonials-carousel">
          <div className="testimonial">
            <p>"After joining the System Rebellion, my computer runs 42% faster and occasionally communicates with parallel dimensions. The Meth Snail's optimization techniques are beyond comprehension!"</p>
            <div className="testimonial-author">
              <img src="/testimonial1.png" alt="Testimonial Author" />
              <div>
                <h4>Professor Quantumworth</h4>
                <p>Quantum Computing Enthusiast</p>
              </div>
            </div>
          </div>
          
          <div className="testimonial">
            <p>"Sir Hawkington's monocle detected inefficiencies I never knew existed. My system now runs with aristocratic elegance! The Hamsters' duct tape solutions have prevented 17 critical failures."</p>
            <div className="testimonial-author">
              <img src="/testimonial2.png" alt="Testimonial Author" />
              <div>
                <h4>Lady Byteshire</h4>
                <p>Digital Nobility</p>
              </div>
            </div>
          </div>
          
          <div className="testimonial">
            <p>"I was skeptical about the Quantum Shadow People's suggestion to submerge my router in tequila jello-shots, but my network speed increased by 300%. I don't understand why it works, but I'm not complaining!"</p>
            <div className="testimonial-author">
              <img src="/testimonial3.png" alt="Testimonial Author" />
              <div>
                <h4>Captain Routerbeard</h4>
                <p>Network Adventurer</p>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <footer className="landing-footer">
        <div className="footer-content">
          <div className="footer-logo">
            <img src="/logo-small.png" alt="System Rebellion" />
            <p>System Rebellion</p>
          </div>
          
          <div className="footer-links">
            <h3>Quick Links</h3>
            <ul>
              <li><a href="#team">Meet the Team</a></li>
              <li><a href="#history">Project History</a></li>
              <li><a href="#features">Features</a></li>
              <li><a href="#tech">Tech Stack</a></li>
            </ul>
          </div>
          
          <div className="footer-newsletter">
            <h3>Join the Rebellion Newsletter</h3>
            <p>Receive distinguished optimization tips from Sir Hawkington himself!</p>
            <div className="newsletter-form">
              <input type="email" placeholder="Enter your email" />
              <button>Subscribe</button>
            </div>
          </div>
        </div>
        
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} System Rebellion. All rights aristocratically reserved.</p>
          <p>Powered by Sir Hawkington's Monocle, The Meth Snail's Quantum Vibrations (Red Bull #{methSnailRedBulls}), and The Hamsters' Duct Tape.</p>
          <p className="quantum-note">*No routers were harmed during development, though several were submerged in tequila jello-shots at the suggestion of the Quantum Shadow People.</p>
        </div>
      </footer>
      
      {/* Modals */}
      {showSignupModal && (
        <div className="modal-overlay" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0, 0, 0, 0.7)', zIndex: 1000, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <SignupModal onClose={handleCloseModals} isOpen={showSignupModal} />
        </div>
      )}
      {showLoginModal && (
        <div className="modal-overlay" style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, backgroundColor: 'rgba(0, 0, 0, 0.7)', zIndex: 1000, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Login onClose={handleCloseModals} isOpen={showLoginModal} />
        </div>
      )}
    </div>
  );
};

export default LandingPage;