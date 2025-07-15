// src/App.tsx
import { useState } from 'react'
import { LandingPage } from './pages/LandingPage'
import './index.css'
import { SignUpModal } from './components/auth/SignUpModal'
import { LoginModal } from './components/auth/LoginModal'
import './LoginModal.css';
import './SignUpModal.css';
import type { User } from './types/auth'
import { ProfileDropdown } from './components/navigation/ProfileDropdown'
import './ProfileDropdown.css';

function App() {
  const [isSignUpModalOpen, setIsSignUpModalOpen] = useState(false);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [user, setUser] = useState<User | null>(null);

  return (
    <div className="App">
      <LandingPage />
      <SignUpModal 
        isOpen={isSignUpModalOpen}
        onClose={() => setIsSignUpModalOpen(false)}
        onSuccess={() => setIsLoginModalOpen(true)}
      />
      <LoginModal 
        isOpen={isLoginModalOpen}
        onClose={() => setIsLoginModalOpen(false)}
        onSuccess={() => setIsLoginModalOpen(false)}
        onSwitchToSignUp={() => setIsSignUpModalOpen(true)}
      />
      <ProfileDropdown 
        user={user}
        onSignUp={() => setIsSignUpModalOpen(true)}
        onLogin={() => setIsLoginModalOpen(true)}
        onLogout={() => setUser(null)}
      />
    </div>
  )
}

export default App



// import { useState } from 'react'
// import './index.css'

// function App() {
//   const [count, setCount] = useState(0)

//   return (
//     <div className="rebellion-container">
//       <header style={{ padding: '2rem 0' }}>
//         <h1 className="vic20-text vic20-glow">
//           🖥️ SYSTEM REBELLION - FRONTEND RENAISSANCE
//         </h1>
//         <p className="rebellion-text" style={{ marginTop: '0.5rem' }}>
//           Enterprise Software That Doesn't Suck! - Hawkington Technologies, Inc.
//         </p>
//       </header>

//       <div className="rebellion-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
//         {/* Sir Hawkington Preview */}
//         <div className="rebellion-card hawkington-panel">
//           <h3 className="hawkington-text">🧐 Sir Hawkington Von Monitorious III</h3>
//           <p style={{ marginTop: '0.5rem' }}>
//             Distinguished monitoring with aristocratic precision
//           </p>
//           <span className="hawkington-badge">ARISTOCRATIC</span>
//         </div>

//         {/* Meth Snail Preview */}
//         <div className="rebellion-card snail-panel">
//           <h3 className="snail-text snail-pulse">🐌💨 Meth Snail</h3>
//           <p style={{ marginTop: '0.5rem' }}>
//             Caffeinated optimization engine
//           </p>
//           <span className="snail-text" style={{ fontSize: '0.875rem' }}>ENERGY LEVEL: MAXIMUM</span>
//         </div>

//         {/* Hamsters Preview */}
//         <div className="rebellion-card hamster-panel">
//           <h3 className="hamster-text">🐹🍺 The Hamsters</h3>
//           <p style={{ marginTop: '0.5rem' }}>
//             Beer-powered engineering solutions
//           </p>
//           <span className="hamster-text" style={{ fontSize: '0.875rem' }}>BEER LEVEL: FULL</span>
//         </div>

//         {/* QSP Preview */}
//         <div className="rebellion-card qsp-panel">
//           <h3 className="qsp-text qsp-fade">👻 Quantum Shadow People</h3>
//           <p style={{ marginTop: '0.5rem' }}>
//             Mysterious network optimization
//           </p>
//           <span className="qsp-text" style={{ fontSize: '0.875rem' }}>PHASING: ACTIVE</span>
//         </div>

//         {/* The Stick Preview */}
//         <div className="rebellion-card stick-panel">
//           <h3 className="stick-text">📏 The Stick</h3>
//           <p style={{ marginTop: '0.5rem' }}>
//             Trauma-aware compliance mastery
//           </p>
//           <span className="stick-text" style={{ fontSize: '0.875rem' }}>PAPER BAG: READY</span>
//         </div>

//         {/* VIC-20 Sage Preview */}
//         <div className="rebellion-card vic20-panel coordination-active">
//           <h3 className="vic20-text vic20-glow">🖥️ VIC-20 Sage</h3>
//           <p style={{ marginTop: '0.5rem' }}>
//             Ancient wisdom coordination master
//           </p>
//           <span className="vic20-text" style={{ fontSize: '0.875rem' }}>WISDOM: 1989→2025</span>
//         </div>
//       </div>

//       <div className="rebellion-card" style={{ marginTop: '2rem' }}>
//         <h2 className="vic20-text">🔥 Rebellion Design System Active</h2>
//         <p style={{ marginTop: '1rem' }}>
//           Custom CSS architecture showcasing agent personalities without faces.
//           Each agent has distinct typography, colors, and micro-interactions.
//         </p>
//         <button 
//           className="rebellion-card"
//           style={{ 
//             background: 'var(--vic20-cyan)', 
//             color: 'var(--rebellion-void)',
//             border: 'none',
//             padding: '0.75rem 1.5rem',
//             borderRadius: 'var(--radius-md)',
//             fontWeight: '600',
//             cursor: 'pointer',
//             marginTop: '1rem'
//           }}
//           onClick={() => setCount(count + 1)}
//         >
//           Test Counter: {count}
//         </button>
//       </div>
//     </div>
//   )
// }