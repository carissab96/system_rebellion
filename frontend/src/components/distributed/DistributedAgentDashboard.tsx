// components/distributed/DistributedAgentDashboard.tsx
// THE AGENT THEATER - Watch agents work in real-time
// Not a boring dashboard. A living, breathing performance.

import React, { useState, useEffect } from 'react';
import { useDistributedAgents } from '../../hooks/useDistributedAgents';
import { Radio, Sparkles, Heart, Zap as Lightning } from 'lucide-react';

interface ActivityLog {
  id: string;
  agent: string;
  action: string;
  timestamp: Date;
  color: string;
}

export const DistributedAgentDashboard: React.FC = () => {
  const { agents, loading, error } = useDistributedAgents();
  const [activityLog, setActivityLog] = useState<ActivityLog[]>([]);
  const [prevAgentStates, setPrevAgentStates] = useState<Map<string, any>>(new Map());

  // Watch for agent activity changes and log them
  useEffect(() => {
    agents.forEach(agent => {
      const prev = prevAgentStates.get(agent.agent_name);
      const dist = agent.distributed;
      
      if (!prev || !dist) return;

      // Detect new messages sent
      if (dist.total_messages_sent > (prev.messages_sent || 0)) {
        const count = dist.total_messages_sent - (prev.messages_sent || 0);
        addActivity(agent.agent_name, `📡 Broadcast ${count} message${count > 1 ? 's' : ''} to Redis`, getAgentColor(agent.agent_name));
      }

      // Detect new decisions
      if (agent.total_decisions > (prev.decisions || 0)) {
        const count = agent.total_decisions - (prev.decisions || 0);
        addActivity(agent.agent_name, `🧠 Made ${count} decision${count > 1 ? 's' : ''}`, getAgentColor(agent.agent_name));
      }

      // Detect health changes
      if (agent.health !== prev.health) {
        addActivity(agent.agent_name, `💓 Health: ${prev.health} → ${agent.health}`, getAgentColor(agent.agent_name));
      }
    });

    // Update previous states
    const newStates = new Map();
    agents.forEach(agent => {
      newStates.set(agent.agent_name, {
        messages_sent: agent.distributed?.total_messages_sent || 0,
        decisions: agent.total_decisions || 0,
        health: agent.health
      });
    });
    setPrevAgentStates(newStates);
  }, [agents]);

  const getAgentColor = (agentName: string): string => {
    // BACKEND IS SOURCE OF TRUTH - Use exact agent_name from API
    const colors: Record<string, string> = {
      'sir_hawkington': '#e6ac00',      // Hawkington gold
      'vic_20_sage': '#06b6d4',         // VIC-20 cyan
      'meth_snail': '#00d084',          // Terry's electric green (backend uses meth_snail)
      'the_stick': '#f97316',           // Stick coral
      'hamsters': '#ff8c42',            // Hamster amber (backend uses hamsters, not bob_hamster)
      'quantum_shadow_people': '#a855f7' // QSP violet
    };
    return colors[agentName] || '#ffffff';
  };

  const addActivity = (agent: string, action: string, color: string) => {
    const newActivity: ActivityLog = {
      id: `${Date.now()}-${Math.random()}`,
      agent,
      action,
      timestamp: new Date(),
      color
    };
    setActivityLog(prev => [newActivity, ...prev].slice(0, 50)); // Keep last 50
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-cyan-400 animate-pulse text-xl">🎭 Raising the curtain...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500 rounded-lg p-6 text-center">
        <p className="text-red-400 text-2xl mb-2">💥 THE SHOW MUST NOT GO ON</p>
        <p className="text-red-300">{error}</p>
        <p className="text-red-400 text-sm mt-2">No fallbacks. Fix it or fail it.</p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* THE STAGE - Agent performers */}
      <div className="lg:col-span-2 space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <Sparkles className="w-6 h-6 text-purple-400" />
          <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
            THE STAGE
          </h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {agents.map(agent => (
            <AgentPerformer key={agent.agent_name} agent={agent} />
          ))}
        </div>
      </div>

      {/* LIVE FEED - Activity stream */}
      <div className="space-y-4">
        <div className="flex items-center gap-3 mb-4">
          <Radio className="w-6 h-6 text-green-400 animate-pulse" />
          <h3 className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-green-400 to-cyan-400">
            LIVE FEED
          </h3>
        </div>

        <div className="bg-black/40 border border-green-500/30 rounded-lg p-4 h-[600px] overflow-y-auto space-y-2">
          {activityLog.length === 0 ? (
            <div className="text-slate-500 text-center py-8">
              Waiting for agent activity...
            </div>
          ) : (
            activityLog.map(log => (
              <div 
                key={log.id}
                className="bg-slate-900/50 border-l-4 p-3 rounded animate-fade-in"
                style={{ borderLeftColor: log.color }}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <div className="font-semibold" style={{ color: log.color }}>
                      {log.agent}
                    </div>
                    <div className="text-sm text-slate-300">{log.action}</div>
                  </div>
                  <div className="text-xs text-slate-500">
                    {log.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

interface AgentPerformerProps {
  agent: any;
}

const AgentPerformer: React.FC<AgentPerformerProps> = ({ agent }) => {
  const dist = agent.distributed || {};
  
  const healthColors: Record<string, string> = {
    'starting': 'text-yellow-400 border-yellow-500/30',
    'healthy': 'text-green-400 border-green-500/30',
    'degraded': 'text-orange-400 border-orange-500/30',
    'critical': 'text-red-400 border-red-500/30',
    'shutting_down': 'text-gray-400 border-gray-500/30'
  };
  
  const healthColor = healthColors[agent.health] || 'text-slate-400 border-slate-500/30';

  const formatUptime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  return (
    <div className={`bg-slate-800/50 border rounded-lg p-4 ${healthColor}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="text-lg font-semibold text-white">{agent.agent_name}</h3>
          <p className="text-xs text-slate-400">{agent.agent_type}</p>
        </div>
        <div className="flex items-center gap-2">
          <Heart className={`w-5 h-5 ${agent.is_active ? 'text-green-400 animate-pulse' : 'text-gray-400'}`} fill={agent.is_active ? 'currentColor' : 'none'} />
          <span className={`text-xs font-medium ${healthColor}`}>
            {agent.health}
          </span>
        </div>
      </div>

      {/* Distributed Stats */}
      {dist.distributed_enabled && (
        <div className="space-y-2 mb-3">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Uptime</span>
            <span className="text-cyan-400 font-mono">
              {formatUptime(agent.uptime_seconds || 0)}
            </span>
          </div>
          
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Decisions</span>
            <span className="text-green-400 font-mono">{agent.total_decisions || 0}</span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Messages Sent</span>
            <span className="text-purple-400 font-mono">{dist.messages_sent || 0}</span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Messages Received</span>
            <span className="text-blue-400 font-mono">{dist.messages_received || 0}</span>
          </div>

          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-400">Restarts</span>
            <span className="text-amber-400 font-mono">{dist.restart_count || 0}</span>
          </div>
        </div>
      )}

      {/* Week 4 Systems */}
      {agent.week4_systems && (
        <div className="border-t border-slate-700 pt-3 space-y-2">
          {agent.week4_systems.monocle_state && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-amber-400">🧐</span>
              <span className="text-slate-300">{agent.week4_systems.monocle_state}</span>
            </div>
          )}
          
          {agent.week4_systems.beer_level && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-amber-400">🍺</span>
              <span className="text-slate-300">{agent.week4_systems.beer_level}</span>
            </div>
          )}
          
          {agent.week4_systems.paranoia_level && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-purple-400">👻</span>
              <span className="text-slate-300">{agent.week4_systems.paranoia_level}</span>
            </div>
          )}

          {agent.week4_systems.bob_detection && (
            <div className="flex items-center gap-2 text-xs">
              <span className="text-orange-400">📋</span>
              <span className="text-slate-300">
                {agent.week4_systems.bob_detection.paper_bags_consumed} bags consumed
              </span>
            </div>
          )}
        </div>
      )}

      {/* Performance Indicator */}
      {dist.resource_monitoring_active && (
        <div className="mt-3 flex items-center gap-2 text-xs">
          <Lightning className="w-3 h-3 text-yellow-400" />
          <span className="text-yellow-400">⚡ Performing</span>
        </div>
      )}
    </div>
  );
};
