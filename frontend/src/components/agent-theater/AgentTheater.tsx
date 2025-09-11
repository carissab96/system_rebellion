// components/agent-theater/AgentTheater.tsx
import React, { useMemo, useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import HamstersCard from '../../components/agent-theater/agents/HamstersCard/HamstersCard.tsx';
import MethSnailCard from '../../components/agent-theater/agents/MethSnailCard/MethSnailCard.tsx';
import QuantumShadowCard from '../../components/agent-theater/agents/QuantumShadowPeopleCard/QSPCard.tsx';
import ConnectionStatus from '../../components/agent-theater/agents/shared/ConnectionStatus';
import { MissingAgentsIndicator } from '../../components/agent-theater/agents/shared/MissingAgentsIndicator';
import SirHawkingtonCard from '../../components/agent-theater/agents/SirHawingtonCard/SirHawkingtonCard.tsx';
import TheStickCard from '../../components/agent-theater/agents/TheStickCard/TheStickCard.tsx';
import VIC20Card from '../../components/agent-theater/agents/VIC20Card/VIC20Card.tsx';
import './AgentTheater.css';

import type { RootState } from '../../store/store';
import { logout } from '../../store/slices/authSlice.ts';

// Use the ingestion hook that dispatches to Redux.
// If your hook file is `useSystemMetricWebSocket.ts`, keep the singular name below.
import { useSystemMetricsWebSocket } from '../../hooks/useSystemMetricsWebSocket.ts';

import { AGENT_KEYS } from '../../store/slices/metricsSlice.ts'

export const AgentTheater: React.FC = () => {
  useSystemMetricsWebSocket({}); // spins up the socket and dispatches setAllAgents etc.

  const dispatch = useDispatch();

  // Single source of truth: the metrics slice
  const {
    agents,
    connectionStatus,
    error,
    lastUpdate,
    activeAgentCount,
  } = useSelector((s: RootState) => s.metrics);

  const auth = useSelector((s: RootState) => s.auth);
  const [showProfileMenu, setShowProfileMenu] = useState(false);

  // optional backend ping in dev
  useEffect(() => {
    if (import.meta.env?.MODE !== 'development') return;
    (async () => {
      try {
        const res = await fetch('/api/auth/csrf_token');
        console.log('backend CSRF test:', res.status);
      } catch (e) {
        console.error('Backend connectivity check failed:', e);
      }
    })();
  }, []);

  const handleLogout = () => dispatch(logout());

  return (
    <div className="agent-theater">
      <nav className="theater-nav">
        <div className="nav-left">
          <button onClick={() => (window.location.href = '/')} className="logo-button">
            System Rebellion
          </button>
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
          <h1 className="theater-title">Agent Theater</h1>
          <div className="theater-subtitle">Real-time AI Agent Performance Dashboard</div>
        </div>

        <div className="theater-status">
          <ConnectionStatus
            status={connectionStatus}
            error={error}
            lastUpdate={lastUpdate}
            metricsData={agents}
          />
          <div className="agent-count">
            <span className="active-count">{activeAgentCount}</span>
            <span className="total-count">/{AGENT_KEYS.length}</span>
            <span className="count-label">Agents Active</span>
          </div>
        </div>
      </div>

      <div className="theater-grid">
        <SirHawkingtonCard data={agents.sir_hawkington} is_active={!!agents.sir_hawkington} />
        <MethSnailCard      data={agents.meth_snail}     is_active={!!agents.meth_snail} />
        <HamstersCard       data={agents.hamsters}       is_active={!!agents.hamsters} />
        <QuantumShadowCard  data={agents.quantum_shadow} is_active={!!agents.quantum_shadow} />
        <TheStickCard       data={agents.the_stick}      is_active={!!agents.the_stick} />
        <VIC20Card          data={agents.vic20_sage}     is_active={!!agents.vic20_sage} />
      </div>

      {activeAgentCount < AGENT_KEYS.length && (
        <MissingAgentsIndicator metricsData={agents} connectionStatus={connectionStatus} />
      )}
    </div>
  );
};

export default AgentTheater;