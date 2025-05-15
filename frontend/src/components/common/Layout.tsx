import React, { useCallback } from 'react';
import { useAppSelector, useAppDispatch } from '../../store/hooks';
import { setConnectionStatus } from '../../store/slices/metricsSlice';
import { useToast } from './Toast';
import Navbar from './Navbar';
import './Layout.css';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const connectionStatus = useAppSelector((state) => state.metrics.connectionStatus);
  const dispatch = useAppDispatch();
  const toast = useToast();

  const handleReconnect = useCallback(async () => {
    try {
      dispatch(setConnectionStatus('connecting'));
      // Add any additional reconnection logic here
      toast.success('Reconnecting...', 'Attempting to reestablish WebSocket connection');
    } catch (error) {
      console.error('Reconnection error:', error);
      toast.error('Reconnection failed', 'Failed to reconnect to WebSocket');
    }
  }, [dispatch, toast]);

  const getStatusColor = () => {
    switch (connectionStatus) {
      case 'connected':
        return 'status-connected';
      case 'connecting':
        return 'status-connecting';
      case 'error':
        return 'status-error';
      default:
        return 'status-disconnected';
    }
  };
  return (
    <div className="layout">
      <Navbar />
      <div className="connection-status">
        <div className={`status-indicator ${getStatusColor()}`}></div>
        <span className="status-text">WebSocket: {connectionStatus || 'disconnected'}</span>
        {connectionStatus !== 'connected' && (
          <button onClick={handleReconnect} className="reconnect-button">
            Reconnect
          </button>
        )}
      </div>
      <main className="main-content">
        {children}
      </main>
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