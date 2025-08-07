// components/layout/MainLayout.tsx
import React, { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { useSelector, useDispatch } from 'react-redux';
import type { RootState } from '../../store/store';
import { logout } from '../../store/slices/authSlice';
import './MainLayout.css';

interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  description: string;
}

const navigationItems: NavigationItem[] = [
  {
    id: 'agent-testing',
    label: 'Agent Testing',
    icon: '🧪',
    path: '/dashboard/agent-testing',
    description: 'Test and monitor AI agent behaviors'
  },
  {
    id: 'memory-banks',
    label: 'Memory Banks',
    icon: '🧠',
    path: '/dashboard/memory-banks',
    description: 'Visualize agent memory and learning'
  },
  {
    id: 'system-monitor',
    label: 'System Monitor',
    icon: '📊',
    path: '/dashboard/system-monitor',
    description: 'Real-time system metrics and health'
  },
  {
    id: 'agent-theater',
    label: 'Agent Theater',
    icon: '🎭',
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
            <span className="logo-icon">⚡</span>
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
              <span className="nav-icon">{item.icon}</span>
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
            <span className="user-icon">👤</span>
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
            <span className="logout-icon">🚪</span>
            {!sidebarCollapsed && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="main-content">
        <div className="content-header">
          <div className="breadcrumb">
            <span className="breadcrumb-home">🏠</span>
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
