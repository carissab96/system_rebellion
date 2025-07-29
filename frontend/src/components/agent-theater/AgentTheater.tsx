// components/agent-theater/AgentTheater.tsx
import React, { useEffect, useState } from 'react';
import { useAgentTheater } from '../../hooks/useAgentTheater';
import SirHawkingtonCard from '../../components/agent-theater/agents/SirHawingtonCard/SirHawkingtonCard.tsx';
import MethSnailCard from '../../components/agent-theater/agents/MethSnailCard/MethSnailCard.tsx';
import HamstersCard from '../../components/agent-theater/agents/HamstersCard/HamstersCard.tsx';
import QuantumShadowCard from '../../components/agent-theater/agents/QuantumShadowPeopleCard/QSPCard.tsx';
import TheStickCard from '../../components/agent-theater/agents/TheStickCard/TheStickCard.tsx';
import VIC20Card from '../../components/agent-theater/agents/VIC20Card/VIC20Card.tsx';
import ConnectionStatus from '../../components/agent-theater/agents/shared/ConnectionStatus';
import { MissingAgentsIndicator } from '../../components/agent-theater/agents/shared/MissingAgentsIndicator';
import './AgentTheater.css';
import { useDispatch, useSelector } from 'react-redux';
import type { RootState } from '../../store/store';
import { logout } from '../../store/slices/authSlice.ts';

export const AgentTheater: React.FC = () => {
  const { metricsData, connectionStatus, error, lastUpdate } = useAgentTheater();
  console.log('AgentTheater Debug:', {
    metricsData,
    connectionStatus,
    error,
    lastUpdate
  });
  const activeAgentCount = Object.keys(metricsData || {}).length;
  const totalAgents = 6;
  const dispatch = useDispatch();
  const auth = useSelector((state: RootState) => state.auth);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  
  const handleLogout = () => {
    dispatch(logout());
  };
  useEffect(() => {
    const testBackend = async () => {
      try {
        console.log('Testing backend connectivitiy...');
        const response = await fetch('/api/auth/csrf_token');
        console.log('backend CSRF test:', response.status);
      } catch (error) {
        console.error('Error testing backend:', error);
      }
    }
    testBackend();
  }, []);
  
  return (
    <div className="agent-theater">
      <nav className="theater-nav">
        <div className="nav-left">
          <button
            onClick={() => window.location.href = '/'}
            className="logo-button"
            >System Rebellion</button>
        </div>
        <div className="nav-right">
          <div className="profile-dropdown">
            <button
              onClick={() => setShowProfileMenu(!showProfileMenu)}
              className="profile-button"
              >{auth.user?.first_Name}</button>
            {showProfileMenu && (
              <div className="dropdown-menu">
                <button onClick={() => console.log('Settings')}>Settings</button>
                <button onClick={() => console.log('Profile')}>Profile</button>
                <hr />
                <button onClick={handleLogout} className="logout-btn">
                  Logout</button>
              </div>
            )}
          </div>
        </div>
      </nav>
      <div className="theater-header">
        <div className="theater-title-section">
          <h1 className="theater-title">Agent Theater</h1>
          <div className="theater-subtitle">
            Real-time AI Agent Performance Dashboard
          </div>
        </div>
        
        <div className="theater-status">
          <ConnectionStatus 
            status={connectionStatus} 
            error={error} 
            lastUpdate={lastUpdate}
            metricsData={metricsData}
                />
          <div className="agent-count">
            <span className="active-count">{activeAgentCount}</span>
            <span className="total-count">/{totalAgents}</span>
            <span className="count-label">Agents Active</span>
          </div>
        </div>
      </div>
      
      <div className="theater-grid">
        <SirHawkingtonCard 
          data={metricsData?.sir_hawkington} 
          is_active={!!metricsData?.sir_hawkington}
        />
        <MethSnailCard 
          data={metricsData?.meth_snail} 
          is_active={!!metricsData?.meth_snail}
        />
        <HamstersCard 
          data={metricsData?.hamsters} 
          is_active={!!metricsData?.hamsters}
        />
        <QuantumShadowCard 
          data={metricsData?.quantum_shadow} 
          is_active={!!metricsData?.quantum_shadow}
        />
        <TheStickCard 
          data={metricsData?.the_stick} 
          is_active={!!metricsData?.the_stick}
        />
        <VIC20Card 
          data={metricsData?.vic20_sage} 
          is_active={!!metricsData?.vic20_sage}
        />
      </div>
      
      {activeAgentCount < totalAgents && (
        <MissingAgentsIndicator 
          metricsData={metricsData} 
          connectionStatus={connectionStatus}
        />
      )}
    </div>
  );
};
export default AgentTheater;