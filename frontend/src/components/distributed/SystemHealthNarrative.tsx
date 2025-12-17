import { useEffect, useState } from 'react';
import { useSelector } from 'react-redux';
import { selectRecentCommunications } from '../../store/slices/communicationSlice';
import { Clock } from 'lucide-react';

/**
 * System Health Narrative - Transform Real Agent Logs into Story Format
 * 
 * CRITICAL RULE: All narratives generated from ACTUAL agent logs, decisions, and events.
 * NO fake data, NO placeholder text, NO simulated stories.
 * 
 * Data Sources:
 * - Agent insights from emit_agent_insight (real decisions and actions)
 * - Agent logs from WebSocketLogHandler (real backend events)
 * - Communication messages (real agent-to-agent coordination)
 */

interface NarrativeEvent {
  timestamp: string;
  agent: string;
  narrative: string;
  severity: 'info' | 'warning' | 'critical';
  category: 'decision' | 'action' | 'coordination' | 'system';
}

const AGENT_DISPLAY_NAMES: Record<string, string> = {
  sir_hawkington: 'Sir Hawkington',
  vic20_sage: 'VIC-20 Sage',
  meth_snail: 'Terry',
  the_stick: 'The Stick',
  hamsters: 'The Hamsters',
  quantum_shadow_people: 'QSP',
};

export function SystemHealthNarrative() {
  const recentCommunications = useSelector(selectRecentCommunications);
  const [narrativeEvents, setNarrativeEvents] = useState<NarrativeEvent[]>([]);

  useEffect(() => {
    // Transform real agent communications into narrative events
    const events: NarrativeEvent[] = recentCommunications
      .slice(0, 20) // Last 20 real events
      .map(comm => {
        const agentName = AGENT_DISPLAY_NAMES[comm.from_agent] || comm.from_agent;
        const timestamp = comm.timestamp || new Date().toISOString();
        
        // Generate narrative from REAL message data
        let narrative = '';
        let severity: 'info' | 'warning' | 'critical' = 'info';
        let category: 'decision' | 'action' | 'coordination' | 'system' = 'system';

        // Parse real agent_insight messages
        if (comm.message_type === 'agent_insight') {
          const action = comm.action || '';
          const reasoning = comm.reasoning || '';
          const context = comm.context || {};

          // Hawkington's triage actions (REAL)
          if (action === 'route_normal_operations' || action === 'triage_decision') {
            category = 'decision';
            severity = context.severity === 'critical' ? 'critical' : 'warning';
            narrative = reasoning || `${agentName} triaged ${context.resource_type || 'system'} alert`;
          }
          
          // Terry's cache clear actions (REAL)
          else if (action === 'cache_clear_executed') {
            category = 'action';
            severity = context.followed_vic20 ? 'info' : 'warning';
            narrative = context.followed_vic20
              ? `${agentName} executed cache clear following VIC-20's recommendation for ${context.resource_type}`
              : `${agentName} overrode VIC-20 and executed emergency cache clear - GOTTA GO FAST!`;
          } else if (action === 'cache_clear_success') {
            category = 'action';
            severity = 'info';
            const freed = context.memory_freed_mb?.toFixed(1) || '0';
            const improvement = context.improvement_percent?.toFixed(1) || '0';
            narrative = `${agentName} freed ${freed}MB of memory (${improvement}% improvement)`;
          }
          
          // VIC-20's coordination (REAL)
          else if (action === 'coordinate_specialist') {
            category = 'coordination';
            severity = context.severity === 'high' || context.severity === 'critical' ? 'critical' : 'warning';
            narrative = `${agentName} routed ${context.resource_type} alert to ${context.specialist} - ${context.recommendation}`;
          }
          
          // The Stick's anxiety events (REAL)
          else if (action === 'paper_bag_consumed') {
            category = 'system';
            severity = 'warning';
            narrative = `${agentName} consumed paper bag due to ${context.reason} (${context.bags_remaining} remaining)`;
          }
          
          // Hamsters disk cleanup (REAL)
          else if (action === 'disk_cleanup_executed' || action === 'disk_cleanup_success') {
            category = 'action';
            severity = 'info';
            if (action === 'disk_cleanup_success') {
              const freed = context.disk_freed_mb?.toFixed(1) || '0';
              narrative = `${agentName} freed ${freed}MB of disk space`;
            } else {
              narrative = reasoning || `${agentName} executing disk cleanup`;
            }
          }
          
          // QSP security scans (REAL)
          else if (action === 'security_scan_executed' || action === 'security_scan_success') {
            category = 'action';
            severity = 'warning';
            if (action === 'security_scan_success') {
              const reduced = context.connections_reduced || 0;
              narrative = `${agentName} secured network - ${reduced} connections reduced`;
            } else {
              narrative = reasoning || `${agentName} executing security lockdown`;
            }
          }
          
          // Generic insight - use reasoning if available
          else if (reasoning) {
            category = 'decision';
            narrative = reasoning;
          }
          // Last resort fallback
          else if (action) {
            category = 'decision';
            narrative = `${agentName} performed ${action}`;
          }
        }
        
        // Parse real agent_log messages
        else if (comm.message_type === 'agent_log') {
          category = 'system';
          const level = comm.level || 'info';
          severity = level === 'error' ? 'critical' : level === 'warning' ? 'warning' : 'info';
          narrative = comm.message || comm.summary || 'System event';
        }
        
        // Parse real coordination messages
        else if (comm.message_type === 'COORDINATION_REQUEST') {
          category = 'coordination';
          severity = 'warning';
          narrative = `${agentName} requested coordination with ${comm.to_agent}`;
        }
        
        // Parse real triage decisions
        else if (comm.message_type === 'TRIAGE_ALERT') {
          category = 'decision';
          severity = 'critical';
          narrative = `${agentName} issued triage alert to ${comm.to_agent}`;
        }
        
        // Fallback: use summary if available (still real data)
        else if (comm.summary) {
          narrative = typeof comm.summary === 'string' 
            ? comm.summary 
            : JSON.stringify(comm.summary);
        }

        // Only return events with actual narrative content
        if (narrative) {
          return {
            timestamp,
            agent: agentName,
            narrative,
            severity,
            category,
          };
        }
        return null;
      })
      .filter((event): event is NarrativeEvent => event !== null);

    setNarrativeEvents(events);
  }, [recentCommunications]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'text-red-400';
      case 'warning': return 'text-yellow-400';
      case 'info': return 'text-cyan-400';
      default: return 'text-slate-300';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'decision': return '🧠';
      case 'action': return '⚡';
      case 'coordination': return '🤝';
      case 'system': return '⚙️';
      default: return '📝';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      const diffSecs = Math.floor(diffMs / 1000);
      
      if (diffSecs < 60) return `${diffSecs}s ago`;
      if (diffSecs < 3600) return `${Math.floor(diffSecs / 60)}m ago`;
      if (diffSecs < 86400) return `${Math.floor(diffSecs / 3600)}h ago`;
      return date.toLocaleTimeString();
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="w-full bg-slate-900/50 backdrop-blur-sm rounded-lg border border-slate-700/50 p-4">
      <div className="flex items-center gap-2 mb-4">
        <Clock className="w-5 h-5 text-cyan-400" />
        <h3 className="text-lg font-semibold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-400">
          System Health Narrative
        </h3>
        <span className="text-xs text-slate-500 ml-auto">
          Real-time agent story • {narrativeEvents.length} events
        </span>
      </div>

      <div className="space-y-2 max-h-96 overflow-y-auto">
        {narrativeEvents.length === 0 ? (
          <div className="text-center text-slate-500 py-8">
            Waiting for agent activity...
          </div>
        ) : (
          narrativeEvents.map((event, idx) => (
            <div
              key={`${event.timestamp}-${idx}`}
              className="bg-slate-800/50 rounded p-3 border-l-2 border-slate-600 hover:border-cyan-500 transition-colors"
              style={{
                borderLeftColor: event.severity === 'critical' ? '#f87171' : 
                                 event.severity === 'warning' ? '#fbbf24' : '#22d3ee'
              }}
            >
              <div className="flex items-start gap-2">
                <span className="text-lg flex-shrink-0">{getCategoryIcon(event.category)}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold text-slate-400">{event.agent}</span>
                    <span className="text-xs text-slate-600">•</span>
                    <span className="text-xs text-slate-500">{formatTimestamp(event.timestamp)}</span>
                  </div>
                  <p className={`text-sm ${getSeverityColor(event.severity)}`}>
                    {event.narrative}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
