"""
Agent State Persistence System
===============================

Manages agent state across restarts, crashes, and network changes.
Agents maintain continuous existence through Redis-backed state storage.

Key Features:
- Persistent personality traits
- Decision history tracking
- Resource monitoring state
- Learning progress preservation
- Crash recovery
"""

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional, List
import json
import logging
from enum import Enum

from .message_protocol import RedisKeys

logger = logging.getLogger(__name__)


class AgentHealth(Enum):
    """Agent health status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    CRITICAL = "critical"
    OFFLINE = "offline"
    STARTING = "starting"
    SHUTTING_DOWN = "shutting_down"


@dataclass
class AgentState:
    """
    Complete state snapshot of an agent.
    
    This is persisted to Redis and restored on agent restart,
    ensuring continuous existence and memory across failures.
    """
    # Identity
    agent_name: str
    agent_role: str
    personality_traits: Dict[str, Any] = field(default_factory=dict)
    
    # Status
    health: AgentHealth = AgentHealth.STARTING
    is_active: bool = True
    last_heartbeat: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Lifecycle
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_restart: Optional[str] = None
    restart_count: int = 0
    uptime_seconds: float = 0.0
    
    # Performance metrics
    total_decisions: int = 0
    total_messages_sent: int = 0
    total_messages_received: int = 0
    error_count: int = 0
    last_error: Optional[str] = None
    
    # Resource monitoring state
    monitored_resources: Dict[str, Any] = field(default_factory=dict)
    resource_thresholds: Dict[str, float] = field(default_factory=dict)
    last_resource_check: Optional[str] = None
    
    # Decision state
    current_decision_context: Optional[Dict[str, Any]] = None
    pending_decisions: List[str] = field(default_factory=list)
    
    # Learning state
    learned_patterns: Dict[str, Any] = field(default_factory=dict)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    
    # Network state
    connected_agents: List[str] = field(default_factory=list)
    subscribed_channels: List[str] = field(default_factory=list)
    
    # Custom agent-specific state
    custom_state: Dict[str, Any] = field(default_factory=dict)
    
    def to_json(self) -> str:
        """Serialize state to JSON"""
        data = asdict(self)
        data['health'] = self.health.value
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'AgentState':
        """Deserialize state from JSON"""
        data = json.loads(json_str)
        data['health'] = AgentHealth(data['health'])
        return cls(**data)
    
    def update_heartbeat(self):
        """Update last heartbeat timestamp"""
        self.last_heartbeat = datetime.now(timezone.utc).isoformat()
    
    def calculate_uptime(self) -> float:
        """Calculate current uptime in seconds"""
        started = datetime.fromisoformat(self.started_at)
        now = datetime.now(timezone.utc)
        return (now - started).total_seconds()
    
    def is_healthy(self) -> bool:
        """Check if agent is in healthy state"""
        return self.health in [AgentHealth.HEALTHY, AgentHealth.DEGRADED]
    
    def mark_error(self, error_msg: str):
        """Record an error"""
        self.error_count += 1
        self.last_error = error_msg
        if self.error_count > 10:
            self.health = AgentHealth.CRITICAL


@dataclass
class DecisionRecord:
    """
    Record of a single agent decision.
    
    Stored in Redis sorted sets for efficient time-based queries.
    """
    decision_id: str
    agent_name: str
    decision_type: str  # What kind of decision (required field, no default)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    
    # Decision details
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    
    # Context
    triggered_by: Optional[str] = None  # What caused this decision
    confidence: float = 0.5
    
    # Triage-specific fields (Task 3.3)
    triage_severity: Optional[str] = None  # normal, medium, high, critical, emergency
    triage_routing: Optional[str] = None  # stick_direct, vic20_coordination, vic20_emergency, cpu_specialist
    coordination_id: Optional[str] = None  # Link to coordination activities
    
    # Outcome tracking
    was_successful: Optional[bool] = None
    outcome_notes: Optional[str] = None
    
    # Related decisions
    related_decisions: List[str] = field(default_factory=list)
    
    def to_json(self) -> str:
        """Serialize to JSON"""
        return json.dumps(asdict(self))
    
    @classmethod
    def from_json(cls, json_str: str) -> 'DecisionRecord':
        """Deserialize from JSON"""
        return cls(**json.loads(json_str))
    
    def get_score(self) -> float:
        """Get timestamp as score for sorted set"""
        dt = datetime.fromisoformat(self.timestamp)
        return dt.timestamp()


class AgentStateManager:
    """
    Manages agent state persistence in Redis.
    
    Handles:
    - State snapshots and restoration
    - Decision history tracking
    - Resource monitoring state
    - Crash recovery
    """
    
    def __init__(self, redis_client, agent_name: str):
        """
        Initialize state manager.
        
        Args:
            redis_client: Redis client instance
            agent_name: Name of the agent this manager handles
        """
        self.redis = redis_client
        self.agent_name = agent_name
        self.logger = logging.getLogger(f"StateManager.{agent_name}")
        self._state_cache: Optional[AgentState] = None
    
    async def save_state(self, state: AgentState) -> bool:
        """
        Save agent state to Redis.
        
        Args:
            state: AgentState to persist
            
        Returns:
            True if successful
        """
        try:
            key = RedisKeys.agent_state(self.agent_name)
            await self.redis.set(key, state.to_json())
            await self.redis.expire(key, 86400 * 7)  # 7 day TTL
            self._state_cache = state
            self.logger.debug(f"Saved state for {self.agent_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to save state: {e}")
            return False
    
    async def load_state(self) -> Optional[AgentState]:
        """
        Load agent state from Redis.
        
        Returns:
            AgentState if found, None otherwise
        """
        try:
            key = RedisKeys.agent_state(self.agent_name)
            data = await self.redis.get(key)
            if data:
                state = AgentState.from_json(data)
                self._state_cache = state
                self.logger.info(f"Loaded state for {self.agent_name} (uptime: {state.calculate_uptime():.0f}s)")
                return state
            return None
        except Exception as e:
            self.logger.error(f"Failed to load state: {e}")
            return None
    
    async def create_initial_state(
        self,
        agent_role: str,
        personality_traits: Dict[str, Any],
        resource_thresholds: Optional[Dict[str, float]] = None
    ) -> AgentState:
        """
        Create initial state for a new agent.
        
        Args:
            agent_role: Role description
            personality_traits: Agent personality configuration
            resource_thresholds: Resource monitoring thresholds
            
        Returns:
            New AgentState
        """
        state = AgentState(
            agent_name=self.agent_name,
            agent_role=agent_role,
            personality_traits=personality_traits,
            resource_thresholds=resource_thresholds or {},
            health=AgentHealth.STARTING
        )
        await self.save_state(state)
        return state
    
    async def record_decision(self, decision: DecisionRecord) -> bool:
        """
        Record a decision in the agent's history.
        
        Decisions are stored in a Redis sorted set, scored by timestamp.
        
        Args:
            decision: DecisionRecord to store
            
        Returns:
            True if successful
        """
        try:
            key = RedisKeys.agent_history(self.agent_name)
            score = decision.get_score()
            await self.redis.zadd(key, {decision.to_json(): score})
            
            # Keep only last 10,000 decisions
            await self.redis.zremrangebyrank(key, 0, -10001)
            
            # Update state
            if self._state_cache:
                self._state_cache.total_decisions += 1
                await self.save_state(self._state_cache)
            
            self.logger.debug(f"Recorded decision {decision.decision_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to record decision: {e}")
            return False
    
    async def get_recent_decisions(
        self,
        count: int = 10,
        since: Optional[datetime] = None
    ) -> List[DecisionRecord]:
        """
        Get recent decisions from history.
        
        Args:
            count: Maximum number of decisions to return
            since: Optional datetime to filter decisions after
            
        Returns:
            List of DecisionRecords, newest first
        """
        try:
            key = RedisKeys.agent_history(self.agent_name)
            
            if since:
                min_score = since.timestamp()
                results = await self.redis.zrangebyscore(
                    key, min_score, '+inf', start=0, num=count
                )
            else:
                # Get most recent
                results = await self.redis.zrevrange(key, 0, count - 1)
            
            decisions = [DecisionRecord.from_json(r) for r in results]
            return decisions
        except Exception as e:
            self.logger.error(f"Failed to get recent decisions: {e}")
            raise  # Don't hide failures with empty list
    
    async def get_decisions_by_severity(
        self,
        severity: str,
        count: int = 50,
        since: Optional[datetime] = None
    ) -> List[DecisionRecord]:
        """
        Get decisions filtered by triage severity (Task 3.3).
        
        Args:
            severity: Triage severity (normal, medium, high, critical, emergency)
            count: Maximum number of decisions to return
            since: Optional datetime to filter decisions after
            
        Returns:
            List of DecisionRecords matching severity, newest first
        """
        try:
            # Get more decisions than requested to filter
            all_decisions = await self.get_recent_decisions(count=count * 2, since=since)
            
            # Filter by severity
            filtered = [
                d for d in all_decisions 
                if d.triage_severity and d.triage_severity.lower() == severity.lower()
            ]
            
            return filtered[:count]
        except Exception as e:
            self.logger.error(f"Failed to get decisions by severity: {e}")
            return []
    
    async def get_decisions_by_routing(
        self,
        routing: str,
        count: int = 50,
        since: Optional[datetime] = None
    ) -> List[DecisionRecord]:
        """
        Get decisions filtered by triage routing (Task 3.3).
        
        Args:
            routing: Triage routing type (stick_direct, vic20_coordination, etc.)
            count: Maximum number of decisions to return
            since: Optional datetime to filter decisions after
            
        Returns:
            List of DecisionRecords matching routing, newest first
        """
        try:
            # Get more decisions than requested to filter
            all_decisions = await self.get_recent_decisions(count=count * 2, since=since)
            
            # Filter by routing
            filtered = [
                d for d in all_decisions 
                if d.triage_routing and d.triage_routing.lower() == routing.lower()
            ]
            
            return filtered[:count]
        except Exception as e:
            self.logger.error(f"Failed to get decisions by routing: {e}")
            return []
    
    async def get_coordination_decisions(
        self,
        coordination_id: str
    ) -> List[DecisionRecord]:
        """
        Get all decisions related to a specific coordination activity (Task 3.3).
        
        Args:
            coordination_id: Coordination ID to filter by
            
        Returns:
            List of DecisionRecords for this coordination
        """
        try:
            # Get recent decisions (coordination usually happens quickly)
            all_decisions = await self.get_recent_decisions(count=100)
            
            # Filter by coordination_id
            filtered = [
                d for d in all_decisions 
                if d.coordination_id == coordination_id
            ]
            
            return filtered
        except Exception as e:
            self.logger.error(f"Failed to get coordination decisions: {e}")
            return []
    
    async def update_metrics(
        self,
        messages_sent: int = 0,
        messages_received: int = 0,
        errors: int = 0
    ):
        """Update agent metrics in state"""
        if self._state_cache:
            self._state_cache.total_messages_sent += messages_sent
            self._state_cache.total_messages_received += messages_received
            self._state_cache.error_count += errors
            self._state_cache.uptime_seconds = self._state_cache.calculate_uptime()
            await self.save_state(self._state_cache)
    
    async def update_health(self, health: AgentHealth):
        """Update agent health status"""
        if self._state_cache:
            self._state_cache.health = health
            self._state_cache.update_heartbeat()
            await self.save_state(self._state_cache)
    
    async def mark_restart(self):
        """Mark agent as restarted"""
        if self._state_cache:
            self._state_cache.restart_count += 1
            self._state_cache.last_restart = datetime.now(timezone.utc).isoformat()
            self._state_cache.started_at = datetime.now(timezone.utc).isoformat()
            await self.save_state(self._state_cache)
    
    async def cleanup(self):
        """Clean up old data"""
        try:
            # Remove decisions older than 30 days
            key = RedisKeys.agent_history(self.agent_name)
            cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).timestamp()
            await self.redis.zremrangebyscore(key, '-inf', cutoff)
            self.logger.info(f"Cleaned up old decisions for {self.agent_name}")
        except Exception as e:
            self.logger.error(f"Cleanup failed: {e}")
