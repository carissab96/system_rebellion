// pages/LiveAgentTheaterPage.tsx
import React, { useState, useEffect, useRef } from 'react';
import { useAppSelector } from '../hooks/redux';
import { LiveAgentTheater } from '../components/agent-theater/LiveAgentTheater';
import { WebSocketService } from '../services/websocket';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

interface AgentData {
  [agentId: string]: any;
}

export const LiveAgentTheaterPage: React.FC = () => {
  const [agentData, setAgentData] = useState<AgentData>({});
  const [isConnecting, setIsConnecting] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const wsServiceRef = useRef<WebSocketService | null>(null);
  const updateTimerRef = useRef<NodeJS.Timeout | null>(null);
  const agentBufferRef = useRef<AgentData>({});
  
  const token = useAppSelector((state: any) => state.auth.token);

  // Debug: Log when component mounts
  useEffect(() => {
    console.log('🎭 LiveAgentTheaterPage mounted - YOU ARE ON THE NEW THEATER!');
    return () => console.log('🎭 LiveAgentTheaterPage unmounting');
  }, []);

  useEffect(() => {
    if (!token) {
      setError('Not authenticated');
      setIsConnecting(false);
      return;
    }

    // Initialize WebSocket service
    const wsService = WebSocketService.getInstance(WS_BASE_URL);
    wsServiceRef.current = wsService;

    const handleMessage = (data: any) => {
      console.log('📨 WebSocket message received:', data);

      // Handle metrics_update messages (contains agent data AND system metrics)
      if (data.type === 'metrics_update') {
        const systemMetrics = data.data || {};
        const agentData = data.agents || {};
        
        console.log('📊 System metrics:', systemMetrics);
        console.log('🌐 Network data:', systemMetrics.network);
        console.log('🤖 Agent data:', agentData);
        
        // Map system metrics to each agent's domain
        const mappedAgentData: AgentData = {
          // Hawkington gets CPU + triage data
          sir_hawkington: {
            status: 'active',
            cpu_usage: systemMetrics.cpu_usage,
            ...agentData.sir_hawkington
          },
          
          // Meth Snail gets Memory
          meth_snail: {
            status: 'active',
            memory_usage: systemMetrics.memory_usage,
            ...agentData.meth_snail
          },
          
          // Hamsters get Disk/Infrastructure
          hamsters: {
            status: 'active',
            disk_usage: systemMetrics.disk_usage,
            ...agentData.hamsters
          },
          
          // QSP get Network (full network data)
          quantum_shadow_people: {
            status: 'active',
            network_sent_rate: systemMetrics.network_sent_rate,
            network_recv_rate: systemMetrics.network_recv_rate,
            // Extract detailed network metrics
            connection_count: systemMetrics.network?.total_connections || 0,
            connection_stats: systemMetrics.network?.connection_stats || {},
            protocol_stats: systemMetrics.network?.protocol_stats || {},
            interfaces: systemMetrics.network?.interfaces || [],
            ...agentData.quantum_shadow_people
          },
          
          // The Stick gets EVERYTHING (hypervigilant)
          the_stick: {
            status: 'active',
            cpu_usage: systemMetrics.cpu_usage,
            memory_usage: systemMetrics.memory_usage,
            disk_usage: systemMetrics.disk_usage,
            ...agentData.the_stick
          },
          
          // VIC-20 gets all agent activity for mediation
          vic20_sage: {
            status: 'active',
            ...agentData.vic20_sage
          }
        };
        
        // Buffer the mapped agent data
        agentBufferRef.current = mappedAgentData;
      }

      // Handle connection established
      if (data.type === 'connection_established') {
        console.log('✅ WebSocket connected');
        setIsConnecting(false);
        setError(null);
      }

      // Handle errors
      if (data.type === 'error') {
        console.error('❌ WebSocket error:', data.message);
        setError(data.message);
      }
    };

    // Subscribe to WebSocket messages
    wsService.subscribe(handleMessage);

    // Connect to system-metrics WebSocket (includes agent data)
    const connectWebSocket = async () => {
      try {
        console.log('🔌 Connecting to WebSocket...');
        await wsService.ensureConnected('/api/ws/system-metrics');
        await wsService.waitUntilOpen(10000, 3, 2000);
        console.log('✅ WebSocket connection established');
      } catch (err: any) {
        console.error('❌ WebSocket connection failed:', err);
        setError(err.message || 'Failed to connect to WebSocket');
        setIsConnecting(false);
      }
    };

    connectWebSocket();

    // Update UI every 60 seconds with buffered data
    updateTimerRef.current = setInterval(() => {
      console.log('🔄 Updating UI with buffered agent data');
      setAgentData({ ...agentBufferRef.current });
    }, 60000); // 60 seconds

    // Also do an initial update after 2 seconds to show data quickly
    const initialUpdateTimer = setTimeout(() => {
      console.log('🔄 Initial UI update');
      setAgentData({ ...agentBufferRef.current });
    }, 2000);

    // Cleanup
    return () => {
      console.log('🧹 Cleaning up WebSocket connection');
      if (updateTimerRef.current) {
        clearInterval(updateTimerRef.current);
      }
      clearTimeout(initialUpdateTimer);
      wsService.unsubscribe(handleMessage);
      // WebSocketService keeps connection alive, no disconnect needed
    };
  }, [token]);

  // Loading state
  if (isConnecting) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'var(--rebellion-void)',
        color: 'var(--rebellion-text)',
        gap: 'var(--space-md)'
      }}>
        <div style={{
          width: '48px',
          height: '48px',
          border: '4px solid var(--rebellion-border)',
          borderTop: '4px solid var(--rebellion-cyan)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <p style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.875rem',
          textTransform: 'uppercase',
          letterSpacing: '0.05em'
        }}>
          Connecting to Agent Theater...
        </p>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: 'var(--rebellion-void)',
        color: 'var(--rebellion-text)',
        gap: 'var(--space-md)',
        padding: 'var(--space-lg)'
      }}>
        <div style={{
          padding: 'var(--space-lg)',
          background: 'var(--rebellion-surface)',
          border: '2px solid var(--error)',
          borderRadius: 'var(--radius-md)',
          maxWidth: '500px',
          textAlign: 'center'
        }}>
          <h2 style={{
            color: 'var(--error)',
            marginBottom: 'var(--space-md)',
            fontFamily: 'var(--font-mono)'
          }}>
            Connection Error
          </h2>
          <p style={{
            color: 'var(--rebellion-text)',
            marginBottom: 'var(--space-lg)'
          }}>
            {error}
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: 'var(--space-sm) var(--space-lg)',
              background: 'var(--rebellion-cyan)',
              color: 'var(--rebellion-void)',
              border: 'none',
              borderRadius: 'var(--radius-md)',
              fontFamily: 'var(--font-mono)',
              fontWeight: '600',
              cursor: 'pointer',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  // Main theater view
  return (
    <LiveAgentTheater
      agentData={agentData}
      onAgentClick={(agentId) => {
        console.log('🎭 Agent clicked:', agentId);
        // Future: Could open a detailed modal or navigate to agent detail page
      }}
    />
  );
};
