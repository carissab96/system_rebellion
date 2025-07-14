// src/data/characters.ts
import { Character } from '../types/characters-types';

export const sirHawkington: Character = {
  id: 'sir-hawkington',
  name: 'Strategic Analysis',
  role: 'System Architect & Decision Engine',
  reality: "That's you trying to architect something properly while everything's on fire",
  capability: 'Real-time system intelligence that thinks like you do',
  image: '/assets/characters/sir-hawkington.png',
  colors: {
    primary: '#6366f1',
    secondary: '#818cf8',
    background: '#312e81',
  },
};

export const methSnail: Character = {
  id: 'meth-snail',
  name: 'Optimization Expert',
  role: 'Optimization Engine',
  reality: "That's you at 2AM optimizing queries with energy drinks",
  capability: 'Continuous optimization that never sleeps',
  image: '/assets/characters/meth-snail.png',
  colors: {
    primary: '#10b981',
    secondary: '#34d399',
    background: '#047857',
  },
};

export const hamsters: Character = {
  id: 'hamsters',
  name: 'Rapid Response',
  role: 'Redneck Engineering Team',
  reality: "That's your team making miracles happen with whatever's available in the supply closet",
  capability: '3AM problem-solving that actually works',
  image: '/assets/characters/hamsters.png',
  colors: {
    primary: '#ff8c00',
    secondary: '#4169e1',
    background: '#654321',
  },
};

export const theStick: Character = {
  id: 'the-stick',
  name: 'Anxiety-ridden Compliance Expert',
  role: 'Configuration Officer',
  reality: "That's you having PTSD from configuration nightmares",
  capability: 'Obsessive compliance monitoring that never misses anything',
  image: '/assets/characters/the-stick.png',
  colors: {
    primary: '#f59e0b',
    secondary: '#facc15',
    background: '#374151',
  },
};

export const quantumShadowPeople: Character = {
  id: 'quantum-shadow-people',
  name: 'Quantum Network Intelligence Experts',
  role: 'Connection Specialists',
  reality: "That's the mysterious interdimensional beings that control the network connection. They phase in and out of our dimension as and when they're needed.",
  capability: 'Quantum-level connection analysis and monitoring',
  image: '/assets/characters/quantum-shadows.png',
  colors: {
    primary: '#8b5cf6',
    secondary: '#14b8a6',
    background: '#1e293b',
  },
};

export const theSage: Character = {
  id: 'the-sage',
  name: 'VIC-20 - 8 bit Wisdom in Green Phosphor',
  role: 'Historical Analytics',
  reality: "That's the old-timer who's seen every possible failure mode",
  capability: 'Decades of accumulated system knowledge and pattern recognition',
  image: '/assets/characters/the-sage.png',
  colors: {
    primary: '#355e3b',
    secondary: '#ffbf00',
    background: '#2d4a32',
  },
};

// Export all characters as an array
export const allCharacters: Character[] = [
  sirHawkington,
  methSnail,
  hamsters,
  theStick,
  quantumShadowPeople,
  theSage,
];

// Export main team (the ones with completed images)
export const mainTeam: Character[] = [
  sirHawkington,
  methSnail,
  hamsters,
  theStick,
  quantumShadowPeople,
  theSage,
];