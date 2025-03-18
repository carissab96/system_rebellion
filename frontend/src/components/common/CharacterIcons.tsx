import React from 'react';
import './CharacterIcons.css';

// Character icon SVG components
export const SirHawkington: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={`character-icon ${className || ''}`} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="45" fill="#1a0458" />
    <circle cx="50" cy="40" r="25" fill="#242b42" />
    <ellipse cx="50" cy="70" rx="15" ry="10" fill="#242b42" />
    <circle cx="40" cy="35" r="5" fill="#00f5d4" />
    <circle cx="60" cy="35" r="5" fill="#00f5d4" />
    <circle cx="40" cy="35" r="2" fill="#000" />
    <circle cx="60" cy="35" r="2" fill="#000" />
    <path d="M45 50 Q50 55 55 50" stroke="#00f5d4" strokeWidth="2" fill="none" />
    <circle cx="65" cy="30" r="10" fill="none" stroke="#00f5d4" strokeWidth="2" />
    <path d="M65 20 L65 40" stroke="#00f5d4" strokeWidth="2" />
    <path d="M30 25 Q40 15 50 25" stroke="#00f5d4" strokeWidth="2" fill="none" />
  </svg>
);

export const MethSnail: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={`character-icon ${className || ''}`} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <path d="M20 60 Q30 30 60 40 Q80 45 80 60 Q80 80 60 80 Q30 80 20 60 Z" fill="#e9009b" />
    <path d="M60 40 Q70 30 80 40 Q90 50 80 60" fill="none" stroke="#00f5d4" strokeWidth="2" />
    <circle cx="35" cy="50" r="5" fill="#00f5d4" />
    <circle cx="35" cy="50" r="2" fill="#000" />
    <circle cx="45" cy="50" r="5" fill="#00f5d4" />
    <circle cx="45" cy="50" r="2" fill="#000" />
    <path d="M30 65 Q40 70 50 65" stroke="#00f5d4" strokeWidth="2" fill="none" />
    <path d="M70 45 L75 35 M70 45 L65 35" stroke="#00f5d4" strokeWidth="2" />
    <path d="M20 60 Q10 70 15 80 Q20 85 30 80" fill="none" stroke="#00f5d4" strokeWidth="2" />
  </svg>
);

export const Hamster: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={`character-icon ${className || ''}`} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <circle cx="50" cy="50" r="30" fill="#02b5fc" />
    <circle cx="40" cy="40" r="5" fill="#00f5d4" />
    <circle cx="60" cy="40" r="5" fill="#00f5d4" />
    <circle cx="40" cy="40" r="2" fill="#000" />
    <circle cx="60" cy="40" r="2" fill="#000" />
    <ellipse cx="50" cy="55" rx="5" ry="3" fill="#00f5d4" />
    <path d="M35 30 L25 20 M65 30 L75 20" stroke="#00f5d4" strokeWidth="2" />
    <path d="M40 65 Q50 70 60 65" fill="none" stroke="#00f5d4" strokeWidth="2" />
    <path d="M20 50 Q10 40 15 30 Q20 25 30 30" fill="none" stroke="#3333ff" strokeWidth="2" strokeDasharray="2,2" />
    <path d="M80 50 Q90 40 85 30 Q80 25 70 30" fill="none" stroke="#3333ff" strokeWidth="2" strokeDasharray="2,2" />
  </svg>
);

export const TheStick: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={`character-icon ${className || ''}`} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <path d="M40 20 L60 20 L55 80 L45 80 Z" fill="#00f5a3" />
    <circle cx="40" cy="35" r="5" fill="#1a0458" />
    <circle cx="60" cy="35" r="5" fill="#1a0458" />
    <circle cx="40" cy="35" r="2" fill="#00f5d4" />
    <circle cx="60" cy="35" r="2" fill="#00f5d4" />
    <path d="M45 50 Q50 55 55 50" stroke="#1a0458" strokeWidth="2" fill="none" />
    <path d="M30 30 Q20 25 25 15 Q30 10 35 15" fill="none" stroke="#00f5d4" strokeWidth="1" />
    <path d="M70 30 Q80 25 75 15 Q70 10 65 15" fill="none" stroke="#00f5d4" strokeWidth="1" />
  </svg>
);

export const QuantumShadowPerson: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={`character-icon ${className || ''}`} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <path d="M30 30 L70 30 L60 80 L40 80 Z" fill="#3333ff" fillOpacity="0.7" />
    <circle cx="40" cy="45" r="5" fill="#00f5d4" />
    <circle cx="60" cy="45" r="5" fill="#00f5d4" />
    <path d="M30 30 Q50 10 70 30" fill="none" stroke="#00f5d4" strokeWidth="2" strokeDasharray="3,3" />
    <path d="M40 60 Q50 65 60 60" stroke="#00f5d4" strokeWidth="2" fill="none" strokeDasharray="2,2" />
    <path d="M25 50 L15 40 M75 50 L85 40" stroke="#00f5d4" strokeWidth="1" strokeDasharray="1,1" />
  </svg>
);

export const VIC20: React.FC<{ className?: string }> = ({ className }) => (
  <svg className={`character-icon ${className || ''}`} viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <rect x="20" y="30" width="60" height="40" rx="5" fill="#242b42" />
    <rect x="25" y="35" width="50" height="15" rx="2" fill="#1a0458" />
    <rect x="30" y="55" width="10" height="10" rx="1" fill="#e9009b" />
    <rect x="45" y="55" width="10" height="10" rx="1" fill="#00f5a3" />
    <rect x="60" y="55" width="10" height="10" rx="1" fill="#02b5fc" />
    <path d="M35 40 L40 40 L40 45 L35 45 Z" fill="#00f5d4" />
    <path d="M45 40 L50 40 L50 45 L45 45 Z" fill="#00f5d4" />
    <path d="M55 40 L65 40 L65 45 L55 45 Z" fill="#00f5d4" />
    <text x="30" y="43" fontSize="5" fill="#00f5d4">VIC-20</text>
  </svg>
);

// Character avatar selection component
interface CharacterAvatarSelectorProps {
  selectedAvatar: string;
  onSelect: (avatar: string) => void;
}

export const CharacterAvatarSelector: React.FC<CharacterAvatarSelectorProps> = ({ 
  selectedAvatar, 
  onSelect 
}) => {
  const characters = [
    { id: 'sir-hawkington', name: 'Sir Hawkington', component: <SirHawkington /> },
    { id: 'meth-snail', name: 'The Meth Snail', component: <MethSnail /> },
    { id: 'hamster', name: 'Hamster', component: <Hamster /> },
    { id: 'the-stick', name: 'The Stick', component: <TheStick /> },
    { id: 'quantum-shadow', name: 'Quantum Shadow Person', component: <QuantumShadowPerson /> },
    { id: 'vic-20', name: 'VIC-20', component: <VIC20 /> },
  ];

  return (
    <div className="character-avatar-selector">
      <h3>Choose Your Avatar</h3>
      <div className="avatar-grid">
        {characters.map((character) => (
          <div 
            key={character.id}
            className={`avatar-option ${selectedAvatar === character.id ? 'selected' : ''}`}
            onClick={() => onSelect(character.id)}
          >
            {character.component}
            <span className="avatar-name">{character.name}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Function to get character component by ID
export const getCharacterById = (id: string): React.ReactNode => {
  switch (id) {
    case 'sir-hawkington':
      return <SirHawkington />;
    case 'meth-snail':
      return <MethSnail />;
    case 'quantum-hamster':
      return <Hamster />;
    case 'the-stick':
      return <TheStick />;
    case 'quantum-shadow':
      return <QuantumShadowPerson />;
    case 'vic-20':
      return <VIC20 />;
    default:
      return <SirHawkington />;
  }
};

export default {
  SirHawkington,
  MethSnail,
  Hamster,
  TheStick,
  QuantumShadowPerson,
  VIC20,
  CharacterAvatarSelector,
  getCharacterById
};
