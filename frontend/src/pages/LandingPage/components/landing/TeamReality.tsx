// src/components/landing/TeamReality.tsx
import React from 'react';
import { CharacterCard } from '../ui/CharacterCard';
import { mainTeam } from '../../../../data/characters-data';

export const TeamReality: React.FC = () => {
  return (
    <section className="team-reality">
      <div className="team-container">
        <h2 className="team-title">
          Every development team has these people. 
          <span className="team-emphasis">Now your monitoring does too.</span>
        </h2>
        
        <div className="character-grid">
          {mainTeam.map((character) => (
            <CharacterCard 
              key={character.id} 
              character={character} 
            />
          ))}
        </div>
        
        <p className="team-truth">
          We don't pretend development is clean and corporate.
          <br />
          We build monitoring for people who actually ship software.
        </p>
      </div>
    </section>
  );
};