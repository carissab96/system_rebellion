// src/components/ui/CharacterCard.tsx
import React from 'react';
import { Character } from '../../../../types/characters-types';

interface CharacterCardProps {
  character: Character;
  className?: string;
}

export const CharacterCard: React.FC<CharacterCardProps> = ({ 
  character, 
  className = '' 
}) => {
  return (
    <div 
      className={`character-card ${className}`}
      style={{
        '--char-primary': character.colors.primary,
        '--char-secondary': character.colors.secondary,
        '--char-bg': character.colors.background,
      } as React.CSSProperties}
    >
      <div className="character-image">
        <img 
          src={character.image} 
          alt={character.name}
          loading="lazy"
        />
      </div>
      
      <div className="character-content">
        <h3 className="character-name">{character.name}</h3>
        <p className="character-role">{character.role}</p>
        <p className="character-reality">"{character.reality}"</p>
        <p className="character-capability">{character.capability}</p>
      </div>
    </div>
  );
};