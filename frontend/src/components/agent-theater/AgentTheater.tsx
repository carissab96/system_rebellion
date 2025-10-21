// components/agent-theater/AgentTheaterEnhanced.tsx
import React, { useState, useEffect } from "react";
import { useDispatch } from "react-redux";
import { useAppSelector } from "../../hooks/redux";

import HamstersCard from "./agents/HamstersCard/HamstersCard";
import MethSnailCard from "./agents/MethSnailCard/MethSnailCard";
import QuantumShadowCard from "./agents/QuantumShadowPeopleCard/QSPCard";
import SirHawkingtonCard from "./agents/SirHawkingtonCard/SirHawkingtonCard";
import TheStickCard from "./agents/TheStickCard/TheStickCard";
import VIC20Card from "./agents/VIC20Card/VIC20Card";
import AgentMethodTracker from "./AgentMethodTracker";
// import "./AgentTheater.css";
import "./AgentTheaterEnhanced.css";

import type { RootState } from "../../store/store";
import { logout } from "../../store/slices/authSlice";
import { useWebSocketConnection } from "../../hooks/useWebSocketConnection";
import { useAgentInsightsConnection } from "../../hooks/useAgentInsightsConnection";
import { useAgentEventsConnection } from "../../hooks/useAgentEventsConnection";
import { AGENT_KEYS, TOTAL_AGENT_COUNT } from "../../store/selectors/metrics";
import ConnectionStatus from "./agents/shared/ConnectionStatus";
import MissingAgentsIndicator from "./agents/shared/MissingAgentsIndicator";
import { getAllAgentNames, AGENT_INTROSPECTION_DATA } from "../../types/agentIntrospection";
import { METRIC_KEYS } from "../../types/metricKeys";

type ConnectionStatusType = 'connecting' | 'connected' | 'disconnected';

interface AgentActivity {
  agentName: string;
  methodName: string;
  timestamp: string;
  category?: string;
}

export const AgentTheaterEnhanced: React.FC = () => {
  const dispatch = useDispatch();
  const auth = useAppSelector((state: RootState) => state.auth);
  
  // Get WebSocket connection info
  const { connectionStatus, lastError } = useWebSocketConnection();
  useAgentInsightsConnection();
  useAgentEventsConnection();
  
  // Get agent data from Redux
  const agents = useAppSelector((state: RootState) => state.agents);
  const metrics = useAppSelector((state: RootState) => state.metrics);
  
  // Local state for agent activity tracking
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [agentActivities, setAgentActivities] = useState<Record<string, AgentActivity>>({});
  const [showIntrospection, setShowIntrospection] = useState(true);
  const [showProfileMenu, setShowProfileMenu] = useState(false);
  
  // Calculate active agent count
  const activeAgentCount = Object.entries(agents).filter(([_, data]) => data !== null).length;
  
  // Get last update timestamp
  const lastUpdate = metrics.timestamp || new Date().toISOString();
  
  // Convert connection status
  const connectionStatusForDisplay: ConnectionStatusType = 
    connectionStatus === 'connected' ? 'connected' : 
    connectionStatus === 'disconnected' || connectionStatus === 'error' ? 'disconnected' : 
    'connecting';

  // Get available agents from introspection data
  const availableAgents = getAllAgentNames().filter(name => name !== '_base');
  
  // Auto-select first active agent
  useEffect(() => {
    if (!selectedAgent && availableAgents.length > 0) {
      setSelectedAgent(availableAgents[0]);
    }
  }, [availableAgents, selectedAgent]);

  // Listen to real agent activity from Redux (populated by WebSocket)
  useEffect(() => {
    // Extract latest activity from each agent's memories
    const activities: Record<string, AgentActivity> = {};
    
    Object.entries(agents).forEach(([agentKey, agentData]) => {
      if (agentData && agentData.memories && agentData.memories.length > 0) {
        // Get most recent live activity
        const liveActivities = agentData.memories.filter((m: any) => m.is_live_activity);
        if (liveActivities.length > 0) {
          const latest = liveActivities[liveActivities.length - 1];
          const activityData = latest.activity_data || {};
          
          activities[agentKey] = {
            agentName: agentKey,
            methodName: activityData.method_name || 'unknown',
            timestamp: latest.timestamp,
            category: activityData.category || latest.activity_type
          };
        }
      }
    });
    
    if (Object.keys(activities).length > 0) {
      setAgentActivities(activities);
    }
  }, [agents]);

  const handleLogout = () => {
    dispatch(logout());
  };

  const handleAgentSelect = (agentName: string) => {
    setSelectedAgent(agentName);
  };

  return (
    <div className="agent-theater enhanced">
      <nav className="theater-nav">
        <div className="nav-left bordered-all-thin">
          <button onClick={() => (window.location.href = '/')} className="logo-button">
            System Rebellion
          </button>
        </div>
        <div className="nav-center">
          <div className="view-toggle">
            <button 
              className={showIntrospection ? 'active' : ''}
              onClick={() => setShowIntrospection(true)}
            >
            Introspection View
            </button>
            <button 
              className={!showIntrospection ? 'active' : ''}
              onClick={() => setShowIntrospection(false)}
            >
            Theater View
            </button>
          </div>
        </div>
        <div className="nav-right">
          <div className="profile-dropdown">
            <button onClick={() => setShowProfileMenu(!showProfileMenu)} className="profile-button">
              {auth.user?.first_name}
            </button>
            {showProfileMenu && (
              <div className="dropdown-menu">
                <button onClick={() => console.log('Settings')}>Settings</button>
                <button onClick={() => console.log('Profile')}>Profile</button>
                <hr />
                <button onClick={handleLogout} className="logout-btn">Logout</button>
              </div>
            )}
          </div>
        </div>
      </nav>

      <div className="theater-header">
        <div className="theater-title-section">
          <h1 className="theater-title">
            Agent Theater
            {showIntrospection && <span className="mode-badge">Enhanced Mode</span>}
          </h1>
          <div className="theater-subtitle">
            Real-time AI Agent Performance Dashboard with AST Introspection
          </div>
        </div>

        <div className="theater-status">
          <ConnectionStatus
            status={connectionStatusForDisplay}
            error={lastError}
            lastUpdate={lastUpdate}
            metricsData={agents}
          />
          <div className="agent-count">
            <span className="active-count">{activeAgentCount}</span>
            <span className="total-count">/{TOTAL_AGENT_COUNT}</span>
            <span className="count-label">Agents Active</span>
          </div>
          <div className="metrics-count">
            <span className="metric-count">{Object.keys(METRIC_KEYS).length}</span>
            <span className="count-label">Metrics Tracked</span>
          </div>
        </div>
      </div>

      {showIntrospection ? (
        <div className="introspection-layout">
          <div className="agent-selector-panel">
            <h3>Available Agents</h3>
            <div className="agent-list">
              {availableAgents.map(agentName => {
                const agentData = AGENT_INTROSPECTION_DATA[agentName];
                const hasData = agentData && agentData.length > 0;
                // Type-safe agent access
                const agentKey = agentName as keyof typeof agents;
                const agentState = agentKey in agents ? agents[agentKey] : null;
                const isActive = agentState !== null && agentState !== undefined && typeof agentState === 'object';
                const currentActivity = agentActivities[agentName];
                
                return (
                  <button
                    key={agentName}
                    className={`agent-selector-item ${selectedAgent === agentName ? 'selected' : ''} ${isActive ? 'active' : ''}`}
                    onClick={() => handleAgentSelect(agentName)}
                    disabled={!hasData}
                  >
                    <div className="agent-selector-header">
                      <span className="agent-name">{agentName.replace(/_/g, ' ')}</span>
                      {isActive && <span className="status-dot active">●</span>}
                    </div>
                    {hasData && agentData[0] && (
                      <div className="agent-selector-stats">
                        <span>{agentData[0].methods?.length || 0} methods</span>
                        {currentActivity && (
                          <span className="current-activity">
                            ⚡ {currentActivity.methodName}
                          </span>
                        )}
                      </div>
                    )}
                    {!hasData && (
                      <div className="no-introspection-data">
                        No introspection data
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
            
            <div className="introspection-info">
              <h4>📊 System Stats</h4>
              <div className="stat-item">
                <span>Total Agents:</span>
                <strong>{availableAgents.length}</strong>
              </div>
              <div className="stat-item">
                <span>Active Agents:</span>
                <strong>{activeAgentCount}</strong>
              </div>
              <div className="stat-item">
                <span>Metrics:</span>
                <strong>{Object.keys(METRIC_KEYS).length}</strong>
              </div>
            </div>
          </div>

          <div className="method-tracker-panel">
            {selectedAgent && (
              <AgentMethodTracker
                agentName={selectedAgent}
                activeMethod={agentActivities[selectedAgent]?.methodName}
                showCategories={['core_processing', 'handler', 'monitoring', 'getter']}
              />
            )}
          </div>

          <div className="agent-card-preview">
            <h3>Agent Card</h3>
            {selectedAgent === 'sir_hawkington' && (
              <SirHawkingtonCard data={agents.sir_hawkington?.display_data} is_active={!!agents.sir_hawkington?.display_data} />
            )}
            {selectedAgent === 'meth_snail' && (
              <MethSnailCard data={agents.meth_snail?.display_data} is_active={!!agents.meth_snail?.display_data} />
            )}
            {selectedAgent === 'hamsters' && (
              <HamstersCard data={agents.hamsters?.display_data} is_active={!!agents.hamsters?.display_data} />
            )}
            {selectedAgent === 'quantum_shadow_people' && (
              <QuantumShadowCard data={agents.quantum_shadow_people?.display_data} is_active={!!agents.quantum_shadow_people?.display_data} />
            )}
            {selectedAgent === 'the_stick' && (
              <TheStickCard data={agents.the_stick?.display_data} is_active={!!agents.the_stick?.display_data} />
            )}
            {selectedAgent === 'vic_20_sage' && (
              <VIC20Card data={agents.vic20_sage?.display_data} is_active={!!agents.vic20_sage?.display_data} />
            )}
          </div>
        </div>
      ) : (
        <div className="theater-grid">
          <SirHawkingtonCard data={agents.sir_hawkington?.display_data} is_active={!!agents.sir_hawkington?.display_data} />
          <MethSnailCard data={agents.meth_snail?.display_data} is_active={!!agents.meth_snail?.display_data} />
          <HamstersCard data={agents.hamsters?.display_data} is_active={!!agents.hamsters?.display_data} />
          <QuantumShadowCard data={agents.quantum_shadow_people?.display_data} is_active={!!agents.quantum_shadow_people?.display_data} />
          <TheStickCard data={agents.the_stick?.display_data} is_active={!!agents.the_stick?.display_data} />
          <VIC20Card data={agents.vic20_sage?.display_data} is_active={!!agents.vic20_sage?.display_data} />
        </div>
      )}

      {activeAgentCount < AGENT_KEYS.length && !showIntrospection && (
        <MissingAgentsIndicator metricsData={agents} connectionStatus={connectionStatusForDisplay} />
      )}
    </div>
  );
};

export default AgentTheaterEnhanced;
