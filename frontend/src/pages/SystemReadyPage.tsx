import React, { useEffect, useMemo, useState } from 'react';
import { useSelector } from 'react-redux';
import { useNavigate } from 'react-router-dom';
import type { RootState } from '../store/store';
import { useWebSocketConnection } from '../hooks/useWebSocketConnection';
// Deprecated: useAgentInsightsConnection and useAgentEventsConnection
// Now unified into useWebSocketConnection
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
    connectionStatus: systemConnectionStatus,
    isConnected: systemConnected,
    lastError: systemError,
    reconnect: reconnectSystem,
  } = useWebSocketConnection();
  // Unified connection now handles metrics, insights, and events

  const jwtStatus = useMemo(() => getJwtStatus(auth.token, auth.isAuthenticated), [auth.token, auth.isAuthenticated]);

  // Check that all required agents are active
  const activeAgents = agentsState?.active_agents ?? [];
  const missingAgents = REQUIRED_AGENTS.filter(agent => !activeAgents.includes(agent));
  const allAgentsReady = missingAgents.length === 0;

  const readiness = {
    jwt: jwtStatus.valid,
    system: systemConnected, // Unified connection includes metrics, insights, and events
    agents: allAgentsReady, // Verify all 6 agents are actually active
  } as const;

  const allReady = Object.values(readiness).every(Boolean);

  // Debug logging for readiness state
  useEffect(() => {
    console.log('🔍 SystemReadyPage Telemetry Check:', {
      jwt: readiness.jwt,
      system: readiness.system,
      agents: readiness.agents,
      activeAgents: activeAgents,
      missingAgents: missingAgents,
      allReady: allReady
    });
  }, [readiness.jwt, readiness.system, readiness.agents, activeAgents, missingAgents, allReady]);

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

  // Redirect to login if JWT becomes invalid or user logs out
  useEffect(() => {
    if (!jwtStatus.valid || !auth.isAuthenticated) {
      console.log('🔒 JWT invalid or not authenticated, redirecting to login');
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
      key: 'system',
      label: 'Unified System Channel',
      ready: readiness.system,
      detail: readiness.system
        ? 'Live telemetry, agent insights, and events streaming.'
        : systemError || `Status: ${systemConnectionStatus}`,
      severity: readiness.system ? 'ready' : systemError ? 'error' : 'pending',
      hint: readiness.system ? 'All system feeds synchronized.' : 'Retry once backend is reachable.'
    },
    {
      key: 'agents',
      label: 'Agent Roster',
      ready: readiness.agents,
      detail: readiness.agents
        ? `All six agents active (${activeAgents.length}/6)`
        : missingAgents.length > 0 
          ? `Missing agents: ${missingAgents.join(', ')} (${activeAgents.length}/6)`
          : `Waiting for agent initialization (${activeAgents.length}/6)`,
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
              {card.key === 'system' && !card.ready && (
                <button
                  className={styles.readyButton}
                  style={{ width: 'fit-content', padding: '0.5rem 1.5rem', marginTop: '1rem' }}
                  onClick={reconnectSystem}
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
                <span className={styles.progressTitle}>Unified System Channel</span>
                <span className={styles.progressCaption}>
                  Single WebSocket for metrics, insights, and events.
                </span>
              </div>
              <span className={badgeClass(readiness.system ? 'ready' : 'pending')}>
                {readiness.system ? 'Linked' : 'Awaiting'}
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
