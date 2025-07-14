// src/types/characters.ts
export interface Character {
    id: string;
    name: string;
    role: string;
    reality: string;
    capability: string;
    image: string;
    colors: {
      primary: string;
      secondary: string;
      background: string;
    };
  }
  
  export interface CharacterCardProps {
    character: Character;
    className?: string;
  }