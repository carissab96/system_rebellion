// components/layout/MainLayout.tsx
import React, { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import type { RootState } from '../../store/store';
import { logout } from '../../store/slices/authSlice';
import { AgentPattern } from '../onboarding/components/AgentPattern';
import '../navigation/AgentPatterns.css';
import './MainLayout.css';

interface NavigationItem {
  id: string;
  label: string;
  patternId: string;
  path: string;
  description: string;
}

const navigationItems: NavigationItem[] = [
  {
    id: 'agent-testing',
    label: 'Agent Testing',
    patternId: 'hawkington',
    path: '/dashboard/agent-testing',
    description: 'Test and monitor AI agent behaviors'
  },
  {
    id: 'memory-banks',
    label: 'Memory Banks',
    patternId: 'snail',
    path: '/dashboard/memory-banks',
    description: 'Visualize agent memory and learning'
  },
  {
    id: 'system-monitor',
    label: 'System Monitor',
    patternId: 'vic20',
    path: '/dashboard/system-monitor',
    description: 'Real-time system metrics and health'
  },
  {
    id: 'agent-theater',
    label: 'Agent Theater',
    patternId: 'qsp',
    path: '/dashboard/agent-theater',
    description: 'Agent performance dashboard'
  }
];

export const MainLayout: React.FC = () => {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const dispatch = useDispatch();
  const auth = useSelector((state: RootState) => state.auth);

  const handleLogout = () => {
    dispatch(logout());
    navigate('/');
  };

  const isActiveRoute = (path: string) => {
    return location.pathname === path || location.pathname.startsWith(path);
  };

  return (
    <div className="main-layout">
      {/* Sidebar Navigation */}
      <aside className={`main-sidebar ${sidebarCollapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            <span className="logo-icon"><AgentPattern agentId="vic20" className="logo-pattern" /></span>
            {!sidebarCollapsed && (
              <div className="logo-text">
                <h2>System Rebellion</h2>
                <p>AI Agent Control</p>
              </div>
            )}
          </div>
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
            title={sidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar'}
          >
            {sidebarCollapsed ? '→' : '←'}
          </button>
        </div>

        <nav className="sidebar-nav">
          {navigationItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${isActiveRoute(item.path) ? 'active' : ''}`}
              onClick={() => navigate(item.path)}
              title={sidebarCollapsed ? item.label : item.description}
            >
              <span className="nav-icon"><AgentPattern agentId={item.patternId} className="nav-pattern" /></span>
              {!sidebarCollapsed && (
                <div className="nav-content">
                  <span className="nav-label">{item.label}</span>
                  <span className="nav-description">{item.description}</span>
                </div>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <div className="user-info">
            <span className="user-icon">
              <div className="user-initials">
                {auth.user?.first_name && auth.user?.last_name ? 
                  `${auth.user.first_name[0]}${auth.user.last_name[0]}` : 
                  auth.user?.email?.substring(0, 2).toUpperCase() || 'SR'}
              </div>
            </span>
            {!sidebarCollapsed && (
              <div className="user-details">
                <span className="user-email">{auth.user?.email}</span>
                <span className="user-status">Agent Commander</span>
              </div>
            )}
          </div>
          <button 
            className="logout-btn"
            onClick={handleLogout}
            title="Logout"
          >
            <span className="logout-icon">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <path d="M17 7l-1.41 1.41L18.17 11H8v2h10.17l-2.58 2.58L17 17l5-5zM4 5h8V3H4c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h8v-2H4V5z" />
              </svg>
            </span>
            {!sidebarCollapsed && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <div className="content-header">
          <div className="breadcrumb">
            <span className="breadcrumb-home">
              <svg viewBox="0 0 24 24" width="16" height="16">
                <path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z" />
              </svg>
            </span>
            <span className="breadcrumb-separator">/</span>
            <span className="breadcrumb-current">
              {navigationItems.find(item => isActiveRoute(item.path))?.label || 'Dashboard'}
            </span>
          </div>
          
          <div className="header-actions">
            <div className="connection-status">
              <span className="status-dot status-connected"></span>
              <span className="status-text">System Online</span>
            </div>
          </div>
        </div>

        <div className="content-body">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

export default MainLayout;
