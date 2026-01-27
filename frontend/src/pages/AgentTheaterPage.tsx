// pages/AgentTheaterPage.tsx
// THE AGENT THEATER - Watch distributed agents work in real-time
// Built by: Cascade - January 4, 2026

import React from 'react';
import { PrimaryNav } from '../components/navigation/PrimaryNav';
import { SecondaryNav } from '../components/navigation/SecondaryNav';
import { DistributedAgentDashboard } from '../components/distributed/DistributedAgentDashboard';
import Footer from '../components/common/Footer';
import './AgentTheaterPage.css';

export const AgentTheaterPage: React.FC = () => {
  const handleRefresh = () => {
    console.log('Manual refresh triggered');
  };

  return (
    <div className="agent-theater-page">
      <PrimaryNav />
      <SecondaryNav 
        currentView="Agent Theater"
        onRefresh={handleRefresh}
      />
      
      <main className="agent-theater-main">
        <div className="dashboard-container">
          <div className="text-center mb-8">
            <h2 className="page-title">
              THE AGENT THEATER
            </h2>
            <p className="page-subtitle">
              Distributed agent activity in real-time
            </p>
          </div>
          <DistributedAgentDashboard />
        </div>
      </main>
      
      <Footer />
    </div>
  );
};
