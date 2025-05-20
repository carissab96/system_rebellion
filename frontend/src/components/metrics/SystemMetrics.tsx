// frontend/src/components/metrics/SystemMetrics.tsx
import React, { useState } from 'react';
import NetworkMetric from './NetworkMetrics/NetworkMetric';
import CPUMetric from './CPU/CPUMetric';
import { MemoryMetric } from './memory/MemoryMetric';
import { DiskMetric } from './disk/DiskMetric';
import { useAppSelector } from '../../store/hooks';
import './SystemMetrics.css'; 

const SystemMetrics: React.FC = () => {
  // State for active tab
  const [activeTab, setActiveTab] = useState('cpu');
  
  // Get current connection status for minimal indicator
  const { connectionStatus } = useAppSelector(state => state.metrics);
  
  return (
    <div className="system-metrics">
      {/* Add a small, styled connection indicator */}
      <div className="metrics-connection-status">
        <span 
          className={`connection-dot ${connectionStatus === 'connected' ? 'connected' : 
                                      connectionStatus === 'connecting' ? 'connecting' : 
                                      'disconnected'}`}
        ></span>
        <span className="connection-text">{connectionStatus}</span>
      </div>
      
      {/* Hide any other connection status components */}
      <style>{`
        .connection-status:not(.metrics-connection-status) {
          display: none !important;
        }
        
        .metrics-connection-status {
          position: absolute;
          top: 10px;
          right: 10px;
          display: flex;
          align-items: center;
          gap: 5px;
          background: rgba(0, 0, 0, 0.1);
          padding: 4px 10px;
          border-radius: 20px;
          font-size: 0.7rem;
          z-index: 10;
        }
        
        .connection-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
        }
        
        .connection-dot.connected {
          background: #38b000;
          box-shadow: 0 0 5px #38b000;
        }
        
        .connection-dot.connecting {
          background: #ffbe0b;
          box-shadow: 0 0 5px #ffbe0b;
          animation: pulse 1s infinite;
        }
        
        .connection-dot.disconnected {
          background: #ff3838;
          box-shadow: 0 0 5px #ff3838;
        }
        
        .connection-text {
          text-transform: capitalize;
          color: #333333;
        }
        
        @keyframes pulse {
          0% { opacity: 0.6; }
          50% { opacity: 1; }
          100% { opacity: 0.6; }
        }
        
        /* Tab Styling */
        .system-metrics-tabs {
          display: flex;
          border-bottom: 2px solid var(--border-color, #dee2e6);
          margin-bottom: 1.5rem;
          padding: 0 1rem;
        }
        
        .system-metrics-tab {
          padding: 0.75rem 1.5rem;
          cursor: pointer;
          font-weight: 600;
          color: var(--text-secondary, #555);
          border-bottom: 3px solid transparent;
          margin-bottom: -2px;
          transition: all 0.2s ease;
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .system-metrics-tab:hover {
          color: var(--primary, #3a86ff);
        }
        
        .system-metrics-tab.active {
          color: var(--primary, #3a86ff);
          border-bottom: 3px solid var(--primary, #3a86ff);
        }
        
        .tab-content-area {
          padding: 1rem;
          min-height: 400px;
        }
        
        .tab-icon {
          font-size: 1.2rem;
        }
      `}</style>
      
      {/* System Metrics Tabs */}
      <div className="system-metrics-tabs">
        <div 
          className={`system-metrics-tab ${activeTab === 'cpu' ? 'active' : ''}`}
          onClick={() => setActiveTab('cpu')}
        >
          <span className="tab-icon">💻</span> CPU
        </div>
        <div 
          className={`system-metrics-tab ${activeTab === 'memory' ? 'active' : ''}`}
          onClick={() => setActiveTab('memory')}
        >
          <span className="tab-icon">🧠</span> Memory
        </div>
        <div 
          className={`system-metrics-tab ${activeTab === 'disk' ? 'active' : ''}`}
          onClick={() => setActiveTab('disk')}
        >
          <span className="tab-icon">💽</span> Disk
        </div>
        <div 
          className={`system-metrics-tab ${activeTab === 'network' ? 'active' : ''}`}
          onClick={() => setActiveTab('network')}
        >
          <span className="tab-icon">🌐</span> Network
        </div>
      </div>
      
      {/* Tab Content */}
      <div className="tab-content-area">
        {activeTab === 'cpu' && <CPUMetric compact={false} />}
        {activeTab === 'memory' && <MemoryMetric compact={false} />}
        {activeTab === 'disk' && <DiskMetric compact={false} />}
        {activeTab === 'network' && <NetworkMetric compact={false} showTabs={false} />}
      </div>
    </div>
  );
};

export default SystemMetrics;