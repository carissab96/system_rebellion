import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { getSystemMetricsWebSocket } from '../services/websocket';

import {
  setConnectionStatus,
  updateActiveAgentCount,
  updateWebSocketMessage,
} from '../store/slices/agentTheaterSlice';

import {
  updateMetrics as updateSirHawkington,
  setOffline as setSirHawkingtonOffline,
} from '../store/slices/sirHawkingtonSlice';
import {
  updateMetrics as updateMethSnail,
  setOffline as setMethSnailOffline,
} from '../store/slices/methSnailSlice';
import {
  updateMetrics as updateHamsters,
  setOffline as setHamstersOffline,
} from '../store/slices/hamstersSlice';
import {
  updateMetrics as updateQuantumShadow,
  setOffline as setQuantumShadowOffline,
} from '../store/slices/quantumShadowPeopleSlice';
import {
  updateMetrics as updateTheStick,
  setOffline as setTheStickOffline,
} from '../store/slices/theStickSlice';
import {
  updateMetrics as updateVIC20,
  setOffline as setVIC20Offline,
} from '../store/slices/vic20Slice';

import type { RootState } from '../store/store';

type MetricsPayload = Record<string, any>;

function normalizeAgents(raw: any) {
  // Defensive normalize: accept either new or old keys without guessing
  return {
    sir_hawkington: raw?.sir_hawkington ?? null,
    meth_snail: raw?.meth_snail ?? null,
    hamsters: raw?.hamsters ?? null,
    quantum_shadow_people: raw?.quantum_shadow_people ?? raw?.quantum_shadow ?? null,
    the_stick: raw?.the_stick ?? null,
    vic20_sage: raw?.vic20_sage ?? raw?.vic_20_sage ?? null,
  };
}

export const useAgentTheater = () => {
  const dispatch = useDispatch();
  const { token, isAuthenticated } = useSelector((s: RootState) => s.auth);

  const agentTheater = useSelector((s: RootState) => s.agentTheater);
  const sirHawkington = useSelector((s: RootState) => s.sirHawkington);
  const methSnail = useSelector((s: RootState) => s.methSnail);
  const hamsters = useSelector((s: RootState) => s.hamsters);
  const quantumShadow = useSelector((s: RootState) => s.quantumShadow);
  const theStick = useSelector((s: RootState) => s.theStick);
  const vic20 = useSelector((s: RootState) => s.vic20);

  useEffect(() => {
    if (!token || !isAuthenticated) {
      dispatch(setConnectionStatus('disconnected'));
      return;
    }

    const ws = getSystemMetricsWebSocket();

    // If you added ensureConnected/waitUntilOpen to the service, use them.
    // Otherwise this still works; we’ll infer connection from data messages.
    (ws as any).ensureConnected?.();

    const onMessage = (msg: any) => {
      try {
        switch (msg?.type) {
          case 'connection_established': {
            // Backend says “hi” — we’ll become “connected” after real data
            dispatch(setConnectionStatus('connecting'));
            break;
          }
          case 'registration_error': {
            // Server couldn’t register this socket with its manager;
            // surface error and let service retry on its own schedule.
            dispatch(setConnectionStatus('error'));
            dispatch(updateWebSocketMessage({ type: 'registration_error', ...msg }));
            break;
          }
          case 'system_info': {
            dispatch(setConnectionStatus('connected'));
            dispatch(updateWebSocketMessage(msg));
            break;
          }
          case 'metrics_update': {
            dispatch(setConnectionStatus('connected'));
            const normalized = normalizeAgents((msg as { data: MetricsPayload }).data);

            // Update per-agent only if present; otherwise mark offline
            if (normalized.sir_hawkington) dispatch(updateSirHawkington(normalized.sir_hawkington));
            else dispatch(setSirHawkingtonOffline('No Sir Hawkington data'));

            if (normalized.meth_snail) dispatch(updateMethSnail(normalized.meth_snail));
            else dispatch(setMethSnailOffline('No Meth Snail data'));

            if (normalized.hamsters) dispatch(updateHamsters(normalized.hamsters));
            else dispatch(setHamstersOffline('No Hamsters data'));

            if (normalized.quantum_shadow_people)
              dispatch(updateQuantumShadow(normalized.quantum_shadow_people));
            else dispatch(setQuantumShadowOffline('No Quantum Shadow People data'));

            if (normalized.the_stick) dispatch(updateTheStick(normalized.the_stick));
            else dispatch(setTheStickOffline('No The Stick data'));

            if (normalized.vic20_sage) dispatch(updateVIC20(normalized.vic20_sage));
            else dispatch(setVIC20Offline('No VIC-20 Sage data'));

            // Active count for the theater header
            const active = Object.values(normalized).filter(Boolean).length;
            dispatch(updateActiveAgentCount(active));

            // Keep a copy of the raw msg if the UI needs it
            dispatch(updateWebSocketMessage(msg));
            break;
          }
          case 'persist_result': {
            // Useful for debugging ingestion issues. Do not spam UI unless failed.
            if (!msg.ok) {
              dispatch(setConnectionStatus('error'));
              dispatch(updateWebSocketMessage({ type: 'persist_result', ...msg }));
            }
            break;
          }
          case 'error': {
            dispatch(setConnectionStatus('error'));
            dispatch(updateWebSocketMessage(msg));
            break;
          }
          default: {
            // Unknown control frames… log once per type if you care.
            break;
          }
        }
      } catch (e) {
        // Last-ditch: don’t crash the handler and cascade into reconnect storm.
        dispatch(setConnectionStatus('error'));
      }
    };

    const unsubscribe = ws.subscribe(onMessage);

    // Optional: if you added waitUntilOpen to the service, request system info early
    (ws as any).waitUntilOpen?.(2000).then((ok: boolean) => {
      if (ok) {
        ws.send({ type: 'request_system_info' });
      }
    });

    return () => {
      unsubscribe();
    };
  }, [token, isAuthenticated, dispatch]);

  const sendMessage = (payload: any) => {
    const ws = getSystemMetricsWebSocket();
    ws.send(payload);
  };

  return {
    // theater state passthrough
    connectionStatus: agentTheater.connectionStatus,
    error: agentTheater.error,
    lastUpdate: agentTheater.lastUpdate,
    activeAgentCount: agentTheater.activeAgentCount,
    systemInfo: agentTheater.systemInfo,

    // per-agent state for the UI
    agents: {
      sirHawkington,
      methSnail,
      hamsters,
      quantumShadow,
      theStick,
      vic20,
    },

    // raw snapshot the MissingAgentsIndicator expects
    metricsData: {
      sir_hawkington: sirHawkington.isOnline ? sirHawkington.data : null,
      meth_snail: methSnail.isOnline ? methSnail.data : null,
      hamsters: hamsters.isOnline ? hamsters.data : null,
      quantum_shadow: quantumShadow.isOnline ? quantumShadow.data : null,
      the_stick: theStick.isOnline ? theStick.data : null,
      vic20_sage: vic20.isOnline ? vic20.data : null,
    },

    // helpers
    sendMessage,
    requestSystemInfo: () => sendMessage({ type: 'request_system_info' }),
    resetCircuitBreaker: () => sendMessage({ type: 'reset_circuit_breaker' }),
    setUpdateInterval: (interval: number) =>
      sendMessage({ type: 'set_interval', data: { interval } }),
  };
};
