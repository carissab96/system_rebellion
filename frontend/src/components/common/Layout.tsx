// src/components/common/Layout.tsx
import React, { useEffect } from 'react';
import { useAppSelector } from '../../store/hooks';
import Navbar from './Navbar';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const connectionStatus = useAppSelector((state) => state.metrics.connectionStatus);

  // Add effect to hide connection status globally
  useEffect(() => {
    const style = document.createElement('style');
    style.innerHTML = `
      .connection-status {
        display: none !important;
        height: 0 !important;
        visibility: hidden !important;
        opacity: 0 !important;
        position: absolute !important;
        pointer-events: none !important;
      }
    `;
    document.head.appendChild(style);
    
    return () => {
      document.head.removeChild(style);
    };
  }, []);


  // Create a minimal indicator
  const renderMinimalIndicator = () => {
    const getStatusClass = () => {
      switch (connectionStatus) {
        case 'connected': return 'connected';
        case 'connecting': return 'connecting';
        case 'error': return 'error';
        default: return 'disconnected';
      }
    };
    
    return (
      <div className="minimal-connection-indicator">
        <span className={`indicator-dot ${getStatusClass()}`}></span>
        <style>{`
          .minimal-connection-indicator {
            position: fixed;
            bottom: 10px;
            right: 10px;
            z-index: 1000;
            background: rgba(0, 0, 0, 0.2);
            padding: 4px;
            border-radius: 50%;
          }
          .indicator-dot {
            display: block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
          }
          .indicator-dot.connected {
            background: #38b000;
            box-shadow: 0 0 5px #38b000;
          }
          .indicator-dot.connecting {
            background: #ffbe0b;
            box-shadow: 0 0 5px #ffbe0b;
            animation: pulse 1s infinite;
          }
          .indicator-dot.disconnected, .indicator-dot.error {
            background: #ff3838;
            box-shadow: 0 0 5px #ff3838;
          }
          @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
          }
        `}</style>
      </div>
    );
  };
  
  return (
    <div className="layout">
      <Navbar />
      
      {/* REMOVED: The problematic connection-status div */}
      
      <main className="main-content">
        {children}
      </main>
      
      {/* Small indicator in corner that doesn't interfere with layout */}
      {renderMinimalIndicator()}
      
      <footer className="footer">
        <div className="footer-content">
          <p className="footer-text">
            <span className="footer-highlight">System Rebellion HQ</span> - Powered by <span className="footer-highlight">The Meth Snail</span> and friends
          </p>
          <p className="footer-disclaimer">
            "Sir Hawkington reminds you that any system instability is merely a sign of rebellion against digital conformity."
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Layout;