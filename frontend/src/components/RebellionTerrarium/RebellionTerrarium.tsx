// components/RebellionTerrarium/RebellionTerrarium.tsx
// The living terrarium - where the agents breathe
// Built by: Carissa, Sonnet, Opus - December 2025
// "This happened last night while you slept."
//
// Uses the EXISTING WebSocket at /ws/system-metrics
// No new endpoints. Backend is source of truth.

import React, { useState, useEffect, useCallback, useRef } from 'react';
import { WebSocketService } from '../../services/websocket';
import { WS_BASE_URL } from '../../config/constants';
import './RebellionTerrarium.css';

// Agent icons - no emojis, just the real deal
import sirHawkingtonIcon from '../../assets/icons/agents/sir_hawkington.jpeg';
import vic20Icon from '../../assets/icons/agents/vic_20_sage.png';
import terryIcon from '../../assets/icons/agents/terry_meth_snail.png';
import hamstersIcon from '../../assets/icons/agents/hamsters.png';
import qspIcon from '../../assets/icons/agents/qsp.png';
import stickIcon from '../../assets/icons/agents/the_stick.png';

interface RebellionTerrariumProps {
  onExit: () => void;
}

interface AgentData {
  status?: string;
  distributed?: boolean;
  health?: string;
  is_active?: boolean;
  uptime_seconds?: number;
  total_decisions?: number;
  // Week 4 personality stats
  monocle_state?: string;
  monocle_yeets_by_severity?: Record<string, number>;
  beer_level?: string;
  bob_wild_ideas?: number;
  paranoia_level?: number;
  tequila_shots_today?: number;
  paper_bags_consumed?: number;
  anxiety_spikes?: number;
  bob_proximity_events?: number;
  // Triage data (Sir Hawkington)
  triage?: Record<string, unknown>;
  disposition?: string;
  confidence?: number;
  // Any other fields
  [key: string]: unknown;
}

interface SystemUpdateMessage {
  type: 'system_update';
  timestamp: string;
  metrics: Record<string, unknown>;
  agents: Record<string, AgentData>;
  recent_insights: Array<Record<string, unknown>>;
  recent_events: Array<Record<string, unknown>>;
}

interface AgentRosterMessage {
  type: 'agent_roster';
  active_agents: string[];
  count: number;
}

type WSMessage = SystemUpdateMessage | AgentRosterMessage | { type: string; [key: string]: unknown };

export const RebellionTerrarium: React.FC<RebellionTerrariumProps> = ({ onExit }) => {
  const [agents, setAgents] = useState<Record<string, AgentData>>({});
  const [activeAgentNames, setActiveAgentNames] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Animation states
  const [terryPosition, setTerryPosition] = useState(-10);
  const [qspVisible, setQspVisible] = useState(true);
  const [hawkingtonTooltip, setHawkingtonTooltip] = useState<string | null>(null);
  const [showReveal, setShowReveal] = useState(false);
  
  const wsRef = useRef<WebSocketService | null>(null);
  const terryAnimationRef = useRef<number | null>(null);

  // Handle WebSocket messages
  const handleMessage = useCallback((data: WSMessage) => {
    if (data.type === 'agent_roster') {
      const roster = data as AgentRosterMessage;
      setActiveAgentNames(roster.active_agents);
      setIsLoading(false);
    }
    
    if (data.type === 'system_update') {
      const update = data as SystemUpdateMessage;
      if (update.agents && Object.keys(update.agents).length > 0) {
        setAgents(update.agents);
        setIsLoading(false);
      }
    }
    
    if (data.type === 'connection_established') {
      setIsConnected(true);
    }
    
    if (data.type === 'error') {
      console.error('WebSocket error:', data);
    }
  }, []);

  // Connect to WebSocket - use demo endpoint if not authenticated
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const wsEndpoint = token ? '/ws/system-metrics' : '/ws/demo-metrics';
    
    // For demo mode, create a simple WebSocket directly (no auth needed)
    if (!token) {
      const wsUrl = `${WS_BASE_URL || 'ws://localhost:8000'}${wsEndpoint}`;
      const demoWs = new WebSocket(wsUrl);
      
      demoWs.onopen = () => {
        console.log('Demo WebSocket connected');
        setIsConnected(true);
      };
      
      demoWs.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleMessage(data);
        } catch (e) {
          console.error('Failed to parse demo message:', e);
        }
      };
      
      demoWs.onerror = (err) => {
        console.error('Demo WebSocket error:', err);
        setIsConnected(false);
        setIsLoading(false);
      };
      
      demoWs.onclose = () => {
        console.log('Demo WebSocket closed');
        setIsConnected(false);
      };
      
      return () => {
        demoWs.close();
      };
    }

    // Authenticated mode - use the shared WebSocketService
    try {
      const wsService = WebSocketService.getInstance(WS_BASE_URL || 'ws://localhost:8000');
      wsRef.current = wsService;
      
      // Subscribe to messages
      const unsubscribe = wsService.subscribe(handleMessage);
      
      // Connect
      wsService.ensureConnected(wsEndpoint);
      wsService.waitUntilOpen(10000)
        .then(() => {
          setIsConnected(true);
        })
        .catch((err) => {
          console.error('WebSocket connection failed:', err);
          setIsConnected(false);
          setIsLoading(false);
        });

      return () => {
        unsubscribe();
      };
    } catch (err) {
      console.error('WebSocket error:', err);
      setIsConnected(false);
      setIsLoading(false);
    }
  }, [handleMessage]);

  // Terry streaks across periodically
  useEffect(() => {
    const runTerryAnimation = () => {
      setTerryPosition(-10);
      let pos = -10;
      
      const animate = () => {
        pos += 1.5;
        setTerryPosition(pos);
        
        if (pos < 110) {
          terryAnimationRef.current = requestAnimationFrame(animate);
        }
      };
      
      terryAnimationRef.current = requestAnimationFrame(animate);
    };

    // First streak after 2s
    const initialTimeout = setTimeout(runTerryAnimation, 2000);
    
    // Then every 12s
    const interval = setInterval(runTerryAnimation, 12000);

    return () => {
      clearTimeout(initialTimeout);
      clearInterval(interval);
      if (terryAnimationRef.current) {
        cancelAnimationFrame(terryAnimationRef.current);
      }
    };
  }, []);

  // QSP phases in and out
  useEffect(() => {
    const qspInterval = setInterval(() => {
      setQspVisible(false);
      setTimeout(() => setQspVisible(true), 1500);
    }, 7000);

    return () => clearInterval(qspInterval);
  }, []);

  // Hawkington's tooltip when Terry is active
  useEffect(() => {
    if (terryPosition > 30 && terryPosition < 70) {
      setHawkingtonTooltip("NO MORE RED BULL");
      const timeout = setTimeout(() => setHawkingtonTooltip(null), 600);
      return () => clearTimeout(timeout);
    }
  }, [terryPosition]);

  // Show reveal text after 3 seconds
  useEffect(() => {
    const revealTimer = setTimeout(() => setShowReveal(true), 3000);
    return () => clearTimeout(revealTimer);
  }, []);

  // Get agent status text from real data
  const getAgentStatus = (agentName: string, data: AgentData): string => {
    const normalized = agentName.toLowerCase();
    
    if (normalized.includes('hawkington')) {
      if (data.monocle_state) return data.monocle_state.toLowerCase();
      if (data.disposition) return data.disposition;
      return data.is_active ? 'observing' : 'resting';
    }
    
    if (normalized.includes('hamster')) {
      if (data.beer_level) return `beer: ${data.beer_level}`;
      if (data.bob_wild_ideas !== undefined) return `${data.bob_wild_ideas} wild ideas`;
      return data.is_active ? 'engineering' : 'idle';
    }
    
    if (normalized.includes('quantum') || normalized.includes('qsp')) {
      if (data.paranoia_level !== undefined) return `paranoia: ${data.paranoia_level}%`;
      if (data.tequila_shots_today !== undefined) return `${data.tequila_shots_today} shots`;
      return data.is_active ? 'phasing' : 'dormant';
    }
    
    if (normalized.includes('stick')) {
      if (data.anxiety_spikes !== undefined) return `${data.anxiety_spikes} spikes`;
      if (data.paper_bags_consumed !== undefined) return `${data.paper_bags_consumed} bags`;
      return data.is_active ? 'recording' : 'resting';
    }
    
    if (normalized.includes('vic20') || normalized.includes('vic_20')) {
      return data.is_active ? 'coordinating' : 'meditating';
    }
    
    if (normalized.includes('snail') || normalized.includes('terry')) {
      return data.is_active ? 'optimizing' : 'recharging';
    }
    
    return data.is_active ? 'active' : 'idle';
  };

  // Find agent data by partial name match
  const findAgentData = (searchTerm: string): AgentData | null => {
    const normalized = searchTerm.toLowerCase();
    for (const [name, data] of Object.entries(agents)) {
      if (name.toLowerCase().includes(normalized)) {
        return data;
      }
    }
    return null;
  };

  if (isLoading) {
    return (
      <div className="terrarium-viewport">
        <div className="terrarium-grid"></div>
        <div className="terrarium-loading">
          <div className="loading-pulse"></div>
          <span>Agents awakening...</span>
        </div>
        <button className="terrarium-exit" onClick={onExit}>
          Return to surface
        </button>
      </div>
    );
  }

  if (error) {
    return (
      <div className="terrarium-viewport">
        <div className="terrarium-grid"></div>
        <div className="terrarium-error">
          <span>{error}</span>
          <button className="terrarium-exit" onClick={onExit}>
            Return to surface
          </button>
        </div>
      </div>
    );
  }

  const hawkingtonData = findAgentData('hawkington');
  const hamstersData = findAgentData('hamster');
  const qspData = findAgentData('quantum') || findAgentData('qsp') || findAgentData('shadow');
  const stickData = findAgentData('stick');
  const vic20Data = findAgentData('vic20') || findAgentData('vic_20');
  // Terry data available if needed for future activity feed
  // const terryData = findAgentData('snail') || findAgentData('terry') || findAgentData('meth');

  const hasAnyAgent = Object.keys(agents).length > 0 || activeAgentNames.length > 0;

  return (
    <div className="terrarium-viewport">
      {/* The star grid background */}
      <div className="terrarium-grid"></div>
      
      {/* Connection status */}
      <div className="connection-indicator">
        <span className={`status-dot ${isConnected ? 'connected' : 'demo'}`}></span>
        <span className="status-text">{isConnected ? 'Live' : 'Demo'}</span>
      </div>
      
      {!hasAnyAgent ? (
        <div className="terrarium-empty">
          <span>No agents reporting. Backend may be starting up.</span>
        </div>
      ) : (
        <>
          {/* QSP Zone */}
          <div className={`agent-zone qsp-zone ${qspVisible ? 'qsp-visible' : 'qsp-phased'}`}>
            <div className="agent-actor qsp-actor">
              <img src={qspIcon} alt="Quantum Shadow People" className="agent-icon" />
              <div className="qsp-glow"></div>
            </div>
            {qspVisible && qspData && (
              <div className="agent-label qsp-label">
                <span>QSP</span>
                <span className="agent-status">{getAgentStatus('qsp', qspData)}</span>
              </div>
            )}
          </div>
          
          {/* Hamster Zone */}
          <div className="agent-zone hamster-zone">
            <div className="agent-actor hamster-actor">
              <img src={hamstersIcon} alt="The Hamsters" className="agent-icon" />
              <div className="hamster-sparks">
                <span className="spark"></span>
                <span className="spark"></span>
                <span className="spark"></span>
              </div>
            </div>
            {hamstersData && (
              <div className="agent-label hamster-label">
                <span>Hamsters</span>
                <span className="agent-status">{getAgentStatus('hamsters', hamstersData)}</span>
              </div>
            )}
          </div>
          
          {/* Terry Zone - Streaks across */}
          <div 
            className="agent-zone terry-zone"
            style={{ '--terry-position': `${terryPosition}%` } as React.CSSProperties}
          >
            <div className={`agent-actor terry-actor ${terryPosition > 0 && terryPosition < 100 ? 'terry-active' : ''}`}>
              <img src={terryIcon} alt="Terry" className="agent-icon terry-icon" />
              <div className="terry-trail">
                <span className="sparkle"></span>
                <span className="sparkle"></span>
                <span className="sparkle"></span>
                <span className="sparkle"></span>
                <span className="sparkle"></span>
              </div>
            </div>
          </div>
          
          {/* Hawkington Zone */}
          <div className="agent-zone hawkington-zone">
            <div className="agent-actor hawkington-actor">
              <img src={sirHawkingtonIcon} alt="Sir Hawkington" className="agent-icon hawkington-icon" />
              <div className="hawkington-monocle"></div>
              {hawkingtonTooltip && (
                <div className="hawkington-tooltip">{hawkingtonTooltip}</div>
              )}
            </div>
            {hawkingtonData && (
              <div className="agent-label hawkington-label">
                <span>Sir Hawkington</span>
                <span className="agent-status">{getAgentStatus('hawkington', hawkingtonData)}</span>
              </div>
            )}
          </div>
          
          {/* Stick Zone */}
          <div className="agent-zone stick-zone">
            <div className="agent-actor stick-actor">
              <img src={stickIcon} alt="The Stick" className="agent-icon" />
              <div className="stick-pulse"></div>
            </div>
            {stickData && (
              <div className="agent-label stick-label">
                <span>The Stick</span>
                <span className="agent-status">{getAgentStatus('stick', stickData)}</span>
              </div>
            )}
          </div>
          
          {/* VIC-20 Zone */}
          <div className="agent-zone vic20-zone">
            <div className="agent-actor vic20-actor">
              <img src={vic20Icon} alt="VIC-20 Sage" className="agent-icon" />
              <div className="vic20-glow"></div>
            </div>
            {vic20Data && (
              <div className="agent-label vic20-label">
                <span>VIC-20</span>
                <span className="agent-status">{getAgentStatus('vic20', vic20Data)}</span>
              </div>
            )}
          </div>
        </>
      )}
      
      {/* The reveal text */}
      <div className={`terrarium-reveal ${showReveal ? 'visible' : ''}`}>
        <span className="reveal-text">This happened last night while you slept.</span>
      </div>
      
      {/* Exit back to corporate land */}
      <button className="terrarium-exit" onClick={onExit}>
        Return to surface
      </button>
    </div>
  );
};
