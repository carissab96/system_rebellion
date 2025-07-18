// components/AgentTheater/AgentTheater.tsx
import React from 'react';
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

export const AgentTheater: React.FC = () => {
  const { metricsData, connectionStatus, error, lastUpdate } = useAgentTheater();
  
  const activeAgentCount = Object.keys(metricsData || {}).length;
  const totalAgents = 6;
  
  return (
    <div className="agent-theater">
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
          isActive={!!metricsData?.sir_hawkington}
        />
        <MethSnailCard 
          data={metricsData?.meth_snail} 
          isActive={!!metricsData?.meth_snail}
        />
        <HamstersCard 
          data={metricsData?.hamsters} 
          isActive={!!metricsData?.hamsters}
        />
        <QuantumShadowCard 
          data={metricsData?.quantum_shadow} 
          isActive={!!metricsData?.quantum_shadow}
        />
        <TheStickCard 
          data={metricsData?.the_stick} 
          isActive={!!metricsData?.the_stick}
        />
        <VIC20Card 
          data={metricsData?.vic20_sage} 
          isActive={!!metricsData?.vic20_sage}
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