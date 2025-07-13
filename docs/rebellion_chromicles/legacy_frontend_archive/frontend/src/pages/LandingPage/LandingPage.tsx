// src/pages/LandingPage.tsx
import React from 'react';
import { HeroSection } from './components/landing/HeroSection';
import { IntelligenceProof } from './components/landing/IntelligenceProof';
import { InstallationSimple } from './components/landing/InstallationSimple';
import { CallToRebellion } from './components/landing/CallToRebellion';
import { RealWorldExample } from './components/ui/RealWorldExample';
import { RebelButton } from './components/ui/RebelButton';
import { CharacterCard } from './components/ui/CharacterCard';
import { mainTeam } from '../../data/characters-data';
import './landing-page.css';
import '../../styles/landing.css';

export const LandingPage: React.FC = () => {
  const handleGetStarted = () => {
    // Scroll to installation or open sign-up
    document.getElementById('installation')?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleJoinRebellion = () => {
    // Handle sign-up/contact
    console.log('Ready to join the rebellion!');
  };

  return (
    <div className="landing-page">
      <HeroSection onGetStarted={handleGetStarted} />
      <IntelligenceProof />
      <InstallationSimple />
      <CallToRebellion onJoinRebellion={handleJoinRebellion} />
      <RealWorldExample title={''} scenario={''} traditionalOutput={''} htiOutput={''} />
      <RebelButton children={undefined} onClick={handleJoinRebellion} />
      <CharacterCard character={mainTeam[0]} />
      <CharacterCard character={mainTeam[1]} />
      <CharacterCard character={mainTeam[2]} />
      <CharacterCard character={mainTeam[3]} />
      <CharacterCard character={mainTeam[4]} />
      <CharacterCard character={mainTeam[5]} />
    </div>
  );
};
export default LandingPage;