// pages/LiveAgentTheaterPage.tsx
import React, { useState, useEffect, useRef } from 'react';
import { useAppSelector } from '../hooks/redux';
import { LiveAgentTheater } from '../components/agent-theater/LiveAgentTheater';
import { WebSocketService } from '../services/websocket';
import type { AgentDecision } from '../components/agent-theater/AgentItelligenceOverlay';

const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

interface AgentData {
  [agentId: string]: any;
}

const DEFAULT_AGENTS: AgentData = {
  sir_hawkington: null,
  the_stick: null,
  hamsters: null,
  meth_snail: null,
  quantum_shadow_people: null,
  vic20_sage: null
};

const normalizeConfidence = (value: unknown): number => {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return 65;
  }
  if (value <= 1) {
    return Math.round(value * 100);
  }
  return Math.round(Math.min(value, 100));
};

const statusFromIndicators = (
  severity?: string,
  result?: Record<string, any>
): AgentDecision['status'] => {
  const resultStatus = typeof result?.status === 'string' ? result.status.toLowerCase() : '';
  if (['complete', 'completed', 'done', 'success'].includes(resultStatus)) {
    return 'complete';
  }
  if (['executing', 'running', 'in_progress', 'active'].includes(resultStatus)) {
    return 'executing';
  }

  const sev = typeof severity === 'string' ? severity.toLowerCase() : '';
  if (sev === 'emergency' || sev === 'high') {
    return 'executing';
  }

  return 'analyzing';
};

const routingToAction = (routing?: string): string => {
  switch ((routing || '').toLowerCase()) {
    case 'vic20_emergency':
      return 'Coordinating emergency response with VIC-20';
    case 'vic20_coordination':
      return 'Coordinating specialist response via VIC-20';
    case 'stick_direct':
      return 'Routing to The Stick for compliance monitoring';
    case 'cpu_specialist':
      return 'Engaging CPU specialist routines';
    default:
      return 'Maintaining situational awareness';
  }
};

const buildAgentDecision = (
  agentId: string,
  insight: Record<string, any> | undefined,
  systemMetrics: Record<string, any>
): AgentDecision | null => {
  const safeInsight = insight || {};

  const fallbackDecision = (
    trigger: string,
    analysis: string,
    action: string,
    impact: string,
    options: {
      status?: AgentDecision['status'];
      confidence?: number;
    } = {}
  ): AgentDecision => ({
    trigger,
    analysis,
    action,
    impact,
    confidence: normalizeConfidence(options.confidence ?? safeInsight.confidence),
    status: options.status ?? 'analyzing'
  });

  switch (agentId) {
    case 'sir_hawkington': {
      const triage = safeInsight.triage ?? {};
      if (!Object.keys(triage).length && !safeInsight.disposition && !safeInsight.routed_by) {
        return null;
      }

      const stressScore = triage?.hawkington_decision?.metrics?.stress_score;
      const severity = triage?.severity ?? safeInsight.disposition;
      const decisionStatus = statusFromIndicators(severity, safeInsight.result);

      const trigger = typeof stressScore === 'number'
        ? `Stress score ${stressScore.toFixed(2)}`
        : `CPU load ${Number(systemMetrics.cpu_usage ?? 0).toFixed(1)}%`;

      const analysis = triage?.reasoning ?? 'Orchestrating system triage response.';
      const action = routingToAction(triage?.routing);
      const impact = triage?.monocle_yeeted
        ? 'Monocle yeeted! Emergency protocols engaged.'
        : `Disposition: ${(safeInsight.disposition || severity || 'normal').toString().toUpperCase()}`;

      return {
        trigger,
        analysis,
        action,
        impact,
        confidence: normalizeConfidence(triage?.confidence ?? safeInsight.confidence),
        status: decisionStatus
      };
    }

    case 'meth_snail': {
      const result = safeInsight.result;
      const memoryUsage = Number(safeInsight.memory_usage ?? systemMetrics.memory_usage);
      if (!result && (memoryUsage === 0 || Number.isNaN(memoryUsage))) {
        return null;
      }

      const trigger = result?.trigger
        || (Number.isFinite(memoryUsage) ? `Memory usage at ${memoryUsage.toFixed(1)}%` : 'Monitoring memory optimizations');
      const analysis = result?.analysis || 'Evaluating memory pressure and optimization opportunities.';
      const action = result?.action || 'Optimizing allocation and cache compaction routines.';
      const impact = result?.impact || 'Improves response times and prevents swap storms.';

      return fallbackDecision(trigger, analysis, action, impact, {
        status: statusFromIndicators(undefined, result),
        confidence: result?.confidence
      });
    }

    case 'hamsters': {
      const result = safeInsight.result;
      const diskUsage = Number(safeInsight.disk_usage ?? systemMetrics.disk_usage);
      if (!result && (diskUsage === 0 || Number.isNaN(diskUsage))) {
        return null;
      }

      const trigger = result?.trigger
        || (Number.isFinite(diskUsage) ? `Disk utilization at ${diskUsage.toFixed(1)}%` : 'Monitoring infrastructure status');
      const analysis = result?.analysis || 'Assessing infrastructure workload across hamster squad.';
      const action = result?.action || "Dispatching Steve, Bob, and Carl for infrastructure maintenance.";
      const impact = result?.impact || 'Prevents outages and keeps infrastructure stable.';

      return fallbackDecision(trigger, analysis, action, impact, {
        status: statusFromIndicators(undefined, result),
        confidence: result?.confidence
      });
    }

    case 'the_stick': {
      const result = safeInsight.result;
      if (!result && !safeInsight.anxiety_level && !safeInsight.patterns_detected) {
        return null;
      }

      const trigger = result?.trigger || `Anxiety level ${safeInsight.anxiety_level || 'CALM'}`;
      const analysis = result?.analysis || 'Scanning for compliance anomalies and pattern drift.';
      const action = result?.action || 'Issuing compliance audit and watch protocols.';
      const impact = result?.impact || `Patterns logged: ${safeInsight.patterns_detected ?? 0}`;

      return fallbackDecision(trigger, analysis, action, impact, {
        status: statusFromIndicators(safeInsight.anxiety_level, result),
        confidence: result?.confidence
      });
    }

    case 'quantum_shadow_people': {
      const result = safeInsight.result;
      const totalRate = Number(systemMetrics.network_sent_rate || 0) + Number(systemMetrics.network_recv_rate || 0);
      if (!result && totalRate === 0) {
        return null;
      }

      const kbRate = totalRate / 1024;
      const trigger = result?.trigger || `Network throughput ${kbRate.toFixed(0)} KB/s`;
      const analysis = result?.analysis || 'Tracing packet anomalies across dimensional links.';
      const action = result?.action || 'Rebalancing routes through quantum relays.';
      const impact = result?.impact || 'Maintains network integrity across realities.';

      return fallbackDecision(trigger, analysis, action, impact, {
        status: statusFromIndicators(undefined, result),
        confidence: result?.confidence
      });
    }

    case 'vic20_sage': {
      const plan = safeInsight.plan;
      const result = safeInsight.result;
      if (!plan && !result) {
        return null;
      }

      const trigger = result?.trigger || plan?.trigger || 'Coordinating cross-agent mediation';
      const analysis = result?.analysis || plan?.analysis || 'Synthesizing historical patterns to guide agents.';
      const action = result?.action || plan?.action || 'Drafting mediation protocol and recommendations.';
      const impact = result?.impact || plan?.impact || 'Ensures multi-agent response stays aligned with historical lessons.';

      return fallbackDecision(trigger, analysis, action, impact, {
        status: statusFromIndicators(undefined, result || { status: plan?.status }),
        confidence: result?.confidence ?? plan?.confidence
      });
    }

    default:
      return null;
  }
};

const mapAgentsPayload = (
  systemMetrics: Record<string, any>,
  incomingAgentData: Record<string, any>
): AgentData => {
  const getInsight = (id: string) => (incomingAgentData?.[id] ? { ...incomingAgentData[id] } : {});

  const mapped: AgentData = {
    sir_hawkington: {
      status: 'active',
      cpu_usage: systemMetrics.cpu_usage,
      ...getInsight('sir_hawkington'),
      intelligence: {
        decision: buildAgentDecision('sir_hawkington', getInsight('sir_hawkington'), systemMetrics)
      }
    },
    meth_snail: {
      status: 'active',
      memory_usage: systemMetrics.memory_usage,
      ...getInsight('meth_snail'),
      intelligence: {
        decision: buildAgentDecision('meth_snail', getInsight('meth_snail'), systemMetrics)
      }
    },
    hamsters: {
      status: 'active',
      disk_usage: systemMetrics.disk_usage,
      ...getInsight('hamsters'),
      intelligence: {
        decision: buildAgentDecision('hamsters', getInsight('hamsters'), systemMetrics)
      }
    },
    quantum_shadow_people: {
      status: 'active',
      network_sent_rate: systemMetrics.network_sent_rate,
      network_recv_rate: systemMetrics.network_recv_rate,
      connection_count: systemMetrics.network?.total_connections || 0,
      connection_stats: systemMetrics.network?.connection_stats || {},
      protocol_stats: systemMetrics.network?.protocol_stats || {},
      interfaces: systemMetrics.network?.interfaces || [],
      ...getInsight('quantum_shadow_people'),
      intelligence: {
        decision: buildAgentDecision('quantum_shadow_people', getInsight('quantum_shadow_people'), systemMetrics)
      }
    },
    the_stick: {
      status: 'active',
      cpu_usage: systemMetrics.cpu_usage,
      memory_usage: systemMetrics.memory_usage,
      disk_usage: systemMetrics.disk_usage,
      ...getInsight('the_stick'),
      intelligence: {
        decision: buildAgentDecision('the_stick', getInsight('the_stick'), systemMetrics)
      }
    },
    vic20_sage: {
      status: 'active',
      ...getInsight('vic20_sage'),
      intelligence: {
        decision: buildAgentDecision('vic20_sage', getInsight('vic20_sage'), systemMetrics)
      }
    }
  };

  return {
    ...DEFAULT_AGENTS,
    ...mapped
  };
};

export const LiveAgentTheaterPage: React.FC = () => {
  const [agentData, setAgentData] = useState<AgentData>({ ...DEFAULT_AGENTS });
  const [isConnecting, setIsConnecting] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const wsServiceRef = useRef<WebSocketService | null>(null);
  const updateTimerRef = useRef<NodeJS.Timeout | null>(null);
  const agentBufferRef = useRef<AgentData>({ ...DEFAULT_AGENTS });
  
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
        const incomingAgentData = data.agents || {};
        
        console.log('📊 System metrics:', systemMetrics);
        console.log('🌐 Network data:', systemMetrics.network);
        console.log('🤖 Agent insights payload:', incomingAgentData);

        const mappedAgentData = mapAgentsPayload(systemMetrics, incomingAgentData);
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
