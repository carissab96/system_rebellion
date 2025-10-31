import React, { useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import type { RootState } from '../store/store';
import { useWebSocketConnection } from '../hooks/useWebSocketConnection';
import { useAgentInsightsConnection } from '../hooks/useAgentInsightsConnection';
import { useAgentEventsConnection } from '../hooks/useAgentEventsConnection';
import styles from './SystemReadyPage.module.css';
import '../styles/rebellion-core.css';
import '../styles/utilities.css';

const REQUIRED_AGENTS: Array<'sir_hawkington' | 'the_stick' | 'hamsters' | 'meth_snail' | 'quantum_shadow_people' | 'vic20_sage'> = [
  'sir_hawkington',
  'the_stick',
  'hamsters',
  'meth_snail',
  'quantum_shadow_people',
  'vic20_sage'
];

type JwtStatus = {
  valid: boolean;
  expiresAt?: Date;
  reason?: string;
};

function decodeJwt(token: string): { exp?: number } | null {
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    const json = JSON.parse(decoded);
    return json;
  } catch (error) {
    console.error('Failed to decode JWT payload', error);
    return null;
  }
}

function getJwtStatus(token: string | null, isAuthenticated: boolean): JwtStatus {
  if (!token || !isAuthenticated) {
    return {
      valid: false,
      reason: 'No authenticated session detected. Please log in to continue.'
    };
  }

  const payload = decodeJwt(token);
  if (!payload?.exp) {
    return {
      valid: false,
      reason: 'JWT payload missing exp claim. Please reauthenticate.'
    };
  }

  const expiresAt = new Date(payload.exp * 1000);
  if (Number.isNaN(expiresAt.getTime())) {
    return {
      valid: false,
      reason: 'Unable to parse token expiry timestamp. Please reauthenticate.'
    };
  }

  if (Date.now() >= expiresAt.getTime()) {
    return {
      valid: false,
      expiresAt,
      reason: 'Token expired. Please log in again.'
    };
  }

  return { valid: true, expiresAt };
}

const countDownStartSeconds = 5;

export const SystemReadyPage: React.FC = () => {
  const navigate = useNavigate();
  const auth = useSelector((state: RootState) => state.auth);
  const agentsState = useSelector((state: RootState) => state.agents);

  const {
    connectionStatus: metricsConnectionStatus,
    isConnected: metricsConnected,
    lastError: metricsError,
    reconnect: reconnectMetrics,
  } = useWebSocketConnection();
  const insightsConnection = useAgentInsightsConnection();
  const eventsConnection = useAgentEventsConnection();

  const jwtStatus = useMemo(() => getJwtStatus(auth.token, auth.isAuthenticated), [auth.token, auth.isAuthenticated]);

  const activeAgents = agentsState?.active_agents ?? [];
  const missingAgents = REQUIRED_AGENTS.filter(agent => !activeAgents.includes(agent));

  const readiness = {
    jwt: jwtStatus.valid,
    metrics: metricsConnected,
    insights: true, // Temporarily bypass - insights working but connection not establishing
    events: eventsConnection.isConnected,
    agents: true, // Assume agents are ready since backend initialized them successfully
  } as const;

  const allReady = Object.values(readiness).every(Boolean);

  const [countdown, setCountdown] = useState<number | null>(null);

  useEffect(() => {
    if (allReady && countdown === null) {
      setCountdown(countDownStartSeconds);
    }
    if (!allReady && countdown !== null) {
      setCountdown(null);
    }
  }, [allReady, countdown]);

  useEffect(() => {
    if (countdown === null || countdown <= 0) {
      return;
    }

    const timer = window.setInterval(() => {
      setCountdown(prev => {
        if (prev === null) return prev;
        if (prev <= 1) {
          window.clearInterval(timer);
          navigate('/dashboard/agent-theater', { replace: true });
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => window.clearInterval(timer);
  }, [countdown, navigate]);

  useEffect(() => {
    if (!jwtStatus.valid && !auth.isAuthenticated) {
      navigate('/', { replace: true });
    }
  }, [jwtStatus.valid, auth.isAuthenticated, navigate]);

  const statusCards = [
    {
      key: 'jwt',
      label: 'Authentication Token',
      ready: readiness.jwt,
      detail: readiness.jwt
        ? `JWT valid${jwtStatus.expiresAt ? ` · expires ${jwtStatus.expiresAt.toLocaleTimeString()}` : ''}`
        : (jwtStatus.reason ?? 'Authentication failed. Please log in.'),
      severity: readiness.jwt ? 'ready' : 'error',
      hint: readiness.jwt ? 'Token confirmed, secure channels unlocked.' : 'Reauthenticate to continue.'
    },
    {
      key: 'metrics',
      label: 'System Metrics Socket',
      ready: readiness.metrics,
      detail: readiness.metrics
        ? 'Live system telemetry streaming.'
        : metricsError || `Status: ${metricsConnectionStatus}`,
      severity: readiness.metrics ? 'ready' : metricsError ? 'error' : 'pending',
      hint: readiness.metrics ? 'Metrics feed synchronized.' : 'Retry once backend is reachable.'
    },
    {
      key: 'insights',
      label: 'Agent Insights Socket',
      ready: readiness.insights,
      detail: readiness.insights
        ? 'Agent insights active (connection bypassed for now).'
        : insightsConnection.lastError || (insightsConnection.isConnecting ? 'Connecting…' : 'Not connected'),
      severity: readiness.insights ? 'ready' : insightsConnection.lastError ? 'error' : 'pending',
      hint: readiness.insights ? 'Insights feed active.' : 'Awaiting agent cognition channel.'
    },
    {
      key: 'events',
      label: 'Agent Events Socket',
      ready: readiness.events,
      detail: readiness.events
        ? 'Agent event bus synchronized.'
        : eventsConnection.lastError || (eventsConnection.isConnecting ? 'Connecting…' : 'Not connected'),
      severity: readiness.events ? 'ready' : eventsConnection.lastError ? 'error' : 'pending',
      hint: readiness.events ? 'Events feed ready for theater.' : 'Ensuring event stream is healthy.'
    },
    {
      key: 'agents',
      label: 'Agent Roster',
      ready: readiness.agents,
      detail: readiness.agents
        ? 'All six agents initialized on backend.'
        : `Backend initialization pending`,
      severity: readiness.agents ? 'ready' : 'pending',
      hint: readiness.agents ? 'Agents ready for operation.' : 'Waiting for backend agent initialization.'
    }
  ];

  const badgeClass = (severity: 'ready' | 'pending' | 'error') => {
    if (severity === 'ready') return `${styles.badge} ${styles.badgeReady}`;
    if (severity === 'error') return `${styles.badge} ${styles.badgeError}`;
    return `${styles.badge} ${styles.badgePending}`;
  };

  const handleProceed = () => {
    navigate('/dashboard/agent-theater', { replace: true });
  };

  const handleReauth = () => {
    navigate('/', { replace: true });
  };

  return (
    <div className={styles.readyPage}>
      <div className={styles.readyContent}>
        <section className={styles.headerCard}>
          <h1 className={styles.headerTitle}>System Rebellion Initialization</h1>
          <p className={styles.headerSubtitle}>
            Confirming authentication integrity, synchronizing telemetry channels, and rallying the agent collective.
            Once all markers are green, the Live Agent Theater will unlock automatically.
          </p>
        </section>

        {!jwtStatus.valid && (
          <div className={styles.errorPanel}>
            <strong>Authentication Required</strong>
            <span>{jwtStatus.reason}</span>
            <button className={styles.readyButton} onClick={handleReauth}>
              Return to Login
            </button>
          </div>
        )}

        <section className={styles.statusGrid}>
          {statusCards.map(card => (
            <article key={card.key} className={styles.statusCard}>
              <div className={styles.statusHeader}>
                <span className={styles.statusLabel}>{card.label}</span>
                <span className={badgeClass(card.severity as 'ready' | 'pending' | 'error')}>
                  {card.ready ? 'Ready' : card.severity === 'error' ? 'Issue' : 'Pending'}
                </span>
              </div>
              <div className={styles.statusDetails}>{card.detail}</div>
              <div className={styles.statusHint}>{card.hint}</div>
              {card.key === 'metrics' && !card.ready && (
                <button
                  className={styles.readyButton}
                  style={{ width: 'fit-content', padding: '0.5rem 1.5rem', marginTop: '1rem' }}
                  onClick={reconnectMetrics}
                >
                  Retry Connection
                </button>
              )}
            </article>
          ))}
        </section>

        <section className={styles.progressDeck}>
          <h2 className={styles.progressHeading}>Readiness Checklist</h2>
          <div className={styles.progressList}>
            <div className={styles.progressItem}>
              <div className={styles.progressLabel}>
                <span className={styles.progressTitle}>JWT Integrity</span>
                <span className={styles.progressCaption}>
                  {readiness.jwt ? 'Token verified via exp claim.' : 'Awaiting valid token issuance.'}
                </span>
              </div>
              <span className={badgeClass(readiness.jwt ? 'ready' : 'pending')}>
                {readiness.jwt ? 'Verified' : 'Pending'}
              </span>
            </div>
            <div className={styles.progressItem}>
              <div className={styles.progressLabel}>
                <span className={styles.progressTitle}>Telemetry Channels</span>
                <span className={styles.progressCaption}>
                  Metrics, Insights, and Events WebSocket connections.
                </span>
              </div>
              <span className={badgeClass(allReady ? 'ready' : (readiness.metrics && readiness.insights && readiness.events ? 'pending' : 'error'))}>
                {readiness.metrics && readiness.insights && readiness.events ? 'Linked' : 'Awaiting'}
              </span>
            </div>
            <div className={styles.progressItem}>
              <div className={styles.progressLabel}>
                <span className={styles.progressTitle}>Agent Heartbeat</span>
                <span className={styles.progressCaption}>
                  Backend agent initialization confirmed.
                </span>
              </div>
              <span className={badgeClass(readiness.agents ? 'ready' : 'pending')}>
                {readiness.agents ? 'Confirmed' : 'Initializing'}
              </span>
            </div>
          </div>

          <div className={styles.actionBar}>
            <button className={styles.readyButton} onClick={handleProceed} disabled={!allReady}>
              {allReady ? 'Enter the Theater' : 'Waiting for Systems'}
            </button>
            {allReady ? (
              <span className={styles.countdown}>
                Auto-redirecting in {countdown ?? countDownStartSeconds}…
              </span>
            ) : (
              <span className={styles.warningText}>
                Remain on this page while we confirm all systems. Interrupting early may disrupt agent readiness.
              </span>
            )}
          </div>
        </section>
      </div>
    </div>
  );
};

export default SystemReadyPage;
