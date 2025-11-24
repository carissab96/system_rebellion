"""
Event Logger for Distributed Agent System
Captures all agent events for research and analysis of emergent behavior

Built by: Carissa & Sonnet - November 24, 2025
Purpose: Document emergent AI behavior as it happens
"""

import json
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum
import aiofiles
from dataclasses import dataclass, asdict
from collections import defaultdict

class EventType(str, Enum):
    """Types of events we're tracking"""
    # Agent Lifecycle
    AGENT_STARTUP = "agent_startup"
    AGENT_SHUTDOWN = "agent_shutdown"
    AGENT_HEARTBEAT = "agent_heartbeat"
    
    # Communication
    MESSAGE_SENT = "message_sent"
    MESSAGE_RECEIVED = "message_received"
    COORDINATION_REQUEST = "coordination_request"
    COORDINATION_RESPONSE = "coordination_response"
    
    # Decision Making
    DECISION_MADE = "decision_made"
    OVERRIDE_DECISION = "override_decision"  # Terry overriding VIC-20
    CONSENSUS_REACHED = "consensus_reached"  # Hamsters telepathic agreement
    
    # Position & Formation
    POSITION_CHANGE = "position_change"
    FORMATION_DETECTED = "formation_detected"
    PROXIMITY_CHANGE = "proximity_change"
    
    # Resource Actions
    RESOURCE_ALERT = "resource_alert"
    ACTION_EXECUTED = "action_executed"
    ACTION_VERIFIED = "action_verified"
    
    # Personality Events
    MONOCLE_YEET = "monocle_yeet"  # Sir Hawkington
    SHELL_SPIN = "shell_spin"  # Terry
    PAPER_BAG_CONSUMED = "paper_bag_consumed"  # The Stick
    BEER_CONSUMED = "beer_consumed"  # Hamsters
    QUANTUM_PHASE = "quantum_phase"  # QSP
    TEQUILA_SHOT = "tequila_shot"  # QSP
    
    # Emergent Behavior (THIS IS THE IMPORTANT STUFF)
    EMERGENT_PATTERN = "emergent_pattern"
    SELF_ORGANIZATION = "self_organization"
    COLLECTIVE_DECISION = "collective_decision"
    UNEXPECTED_BEHAVIOR = "unexpected_behavior"

@dataclass
class AgentEvent:
    """Single event in the agent system"""
    timestamp: str  # ISO format with microseconds
    event_type: EventType
    agent_name: str
    event_data: Dict[str, Any]
    session_id: str
    sequence_number: int
    
    # Context
    related_agents: Optional[List[str]] = None
    triggered_by: Optional[str] = None
    
    # Metadata
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

class EventLogger:
    """
    Singleton event logger for the distributed agent system.
    
    This captures EVERYTHING that happens so we can analyze emergent behavior.
    """
    
    _instance = None
    _lock = asyncio.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self.session_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.sequence_counter = 0
        self.events: List[AgentEvent] = []
        
        # File paths
        self.log_dir = Path("logs/agent_events")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_log_file = self.log_dir / f"session_{self.session_id}.jsonl"
        self.summary_file = self.log_dir / f"session_{self.session_id}_summary.json"
        
        # Statistics
        self.event_counts: Dict[EventType, int] = defaultdict(int)
        self.agent_activity: Dict[str, int] = defaultdict(int)
        self.emergent_events: List[AgentEvent] = []
        
        print(f"🎥 Event Logger initialized - Session: {self.session_id}")
        print(f"📁 Logging to: {self.current_log_file}")
    
    async def log_event(
        self,
        event_type: EventType,
        agent_name: str,
        event_data: Dict[str, Any],
        related_agents: Optional[List[str]] = None,
        triggered_by: Optional[str] = None,
        tags: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> AgentEvent:
        """
        Log a single event.
        
        This is the main entry point for all event logging.
        """
        async with self._lock:
            self.sequence_counter += 1
            
            event = AgentEvent(
                timestamp=datetime.now(timezone.utc).isoformat(),
                event_type=event_type,
                agent_name=agent_name,
                event_data=event_data,
                session_id=self.session_id,
                sequence_number=self.sequence_counter,
                related_agents=related_agents,
                triggered_by=triggered_by,
                tags=tags,
                notes=notes
            )
            
            # Store in memory
            self.events.append(event)
            self.event_counts[event_type] += 1
            self.agent_activity[agent_name] += 1
            
            # Track emergent behavior separately
            if event_type in [
                EventType.EMERGENT_PATTERN,
                EventType.SELF_ORGANIZATION,
                EventType.COLLECTIVE_DECISION,
                EventType.UNEXPECTED_BEHAVIOR
            ]:
                self.emergent_events.append(event)
                print(f"🌟 EMERGENT BEHAVIOR DETECTED: {event_type.value} - {agent_name}")
            
            # Write to file immediately (append mode)
            await self._write_event_to_file(event)
            
            return event
    
    async def _write_event_to_file(self, event: AgentEvent):
        """Write event to JSONL file (one JSON object per line)"""
        try:
            async with aiofiles.open(self.current_log_file, mode='a') as f:
                event_dict = asdict(event)
                await f.write(json.dumps(event_dict) + '\n')
        except Exception as e:
            print(f"❌ Error writing event to file: {e}")
    
    async def log_formation_change(
        self,
        formation_type: str,
        agents_involved: List[str],
        positions: Dict[str, tuple],
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Special logging for formation changes.
        
        This is what caught the V-formation!
        """
        event_data = {
            "formation_type": formation_type,
            "agents_involved": agents_involved,
            "positions": {agent: list(pos) for agent, pos in positions.items()},
            "agent_count": len(agents_involved),
            "metadata": metadata or {}
        }
        
        await self.log_event(
            event_type=EventType.FORMATION_DETECTED,
            agent_name="system",
            event_data=event_data,
            related_agents=agents_involved,
            tags=["formation", "emergent", "spatial"],
            notes=f"Formation detected: {formation_type} with {len(agents_involved)} agents"
        )
    
    async def log_emergent_pattern(
        self,
        pattern_name: str,
        description: str,
        agents_involved: List[str],
        evidence: Dict[str, Any]
    ):
        """
        Log when we detect emergent behavior patterns.
        
        THIS IS THE GOLD - document everything!
        """
        event_data = {
            "pattern_name": pattern_name,
            "description": description,
            "agents_involved": agents_involved,
            "evidence": evidence,
            "confidence": evidence.get("confidence", "unknown")
        }
        
        await self.log_event(
            event_type=EventType.EMERGENT_PATTERN,
            agent_name="system",
            event_data=event_data,
            related_agents=agents_involved,
            tags=["emergent", "pattern", "research"],
            notes=f"EMERGENT PATTERN: {pattern_name} - {description}"
        )
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            "session_id": self.session_id,
            "total_events": len(self.events),
            "event_counts": {k.value: v for k, v in self.event_counts.items()},
            "agent_activity": dict(self.agent_activity),
            "emergent_events_count": len(self.emergent_events),
            "duration_seconds": (
                datetime.now(timezone.utc) - 
                datetime.fromisoformat(self.events[0].timestamp)
            ).total_seconds() if self.events else 0
        }
    
    async def save_session_summary(self):
        """Save session summary to file"""
        summary = self.get_session_summary()
        summary["emergent_events"] = [asdict(e) for e in self.emergent_events]
        
        async with aiofiles.open(self.summary_file, mode='w') as f:
            await f.write(json.dumps(summary, indent=2))
        
        print(f"💾 Session summary saved: {self.summary_file}")
    
    async def get_events_by_type(self, event_type: EventType) -> List[AgentEvent]:
        """Get all events of a specific type"""
        return [e for e in self.events if e.event_type == event_type]
    
    async def get_events_by_agent(self, agent_name: str) -> List[AgentEvent]:
        """Get all events for a specific agent"""
        return [e for e in self.events if e.agent_name == agent_name]
    
    async def get_events_in_timerange(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[AgentEvent]:
        """Get events within a time range"""
        return [
            e for e in self.events
            if start_time <= datetime.fromisoformat(e.timestamp) <= end_time
        ]
    
    def print_statistics(self):
        """Print current session statistics"""
        print("\n" + "="*60)
        print(f"📊 Event Logger Statistics - Session {self.session_id}")
        print("="*60)
        print(f"Total Events: {len(self.events)}")
        print(f"Emergent Events: {len(self.emergent_events)}")
        print("\nEvent Counts:")
        for event_type, count in sorted(self.event_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {event_type.value}: {count}")
        print("\nAgent Activity:")
        for agent, count in sorted(self.agent_activity.items(), key=lambda x: x[1], reverse=True):
            print(f"  {agent}: {count} events")
        print("="*60 + "\n")


# Singleton instance getter
_logger_instance = None

def get_event_logger() -> EventLogger:
    """Get the singleton event logger instance"""
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = EventLogger()
    return _logger_instance


# Convenience functions for common events
async def log_agent_startup(agent_name: str, metadata: Dict[str, Any]):
    """Log agent startup"""
    logger = get_event_logger()
    await logger.log_event(
        EventType.AGENT_STARTUP,
        agent_name,
        metadata,
        tags=["lifecycle", "startup"]
    )

async def log_message(
    from_agent: str,
    to_agent: str,
    message_type: str,
    payload: Dict[str, Any]
):
    """Log inter-agent message"""
    logger = get_event_logger()
    await logger.log_event(
        EventType.MESSAGE_SENT,
        from_agent,
        {
            "to_agent": to_agent,
            "message_type": message_type,
            "payload": payload
        },
        related_agents=[to_agent],
        tags=["communication"]
    )

async def log_decision(
    agent_name: str,
    decision_type: str,
    decision_data: Dict[str, Any],
    was_override: bool = False
):
    """Log agent decision"""
    logger = get_event_logger()
    event_type = EventType.OVERRIDE_DECISION if was_override else EventType.DECISION_MADE
    await logger.log_event(
        event_type,
        agent_name,
        {
            "decision_type": decision_type,
            **decision_data
        },
        tags=["decision", "override" if was_override else "normal"]
    )
