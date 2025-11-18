"""
Cross-Agent Coordination System for System Rebellion

Enables multiple agents to work together on system-wide issues:
- Resource negotiation (who can help best?)
- Conflict resolution (prevent stepping on each other)
- Coordinated responses (team-based problem solving)
- Priority management (critical agents first)

Week 4 Task 4.4
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any, Callable
from enum import Enum
from dataclasses import dataclass, field
import uuid

logger = logging.getLogger(__name__)


class CoordinationPriority(str, Enum):
    """Priority levels for coordination requests"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class ResourceType(str, Enum):
    """Resource types for coordination"""
    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    NETWORK = "network"


class CoordinationStatus(str, Enum):
    """Status of coordination request"""
    PENDING = "pending"
    NEGOTIATING = "negotiating"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class AgentCapability:
    """What an agent can do to help"""
    agent_name: str
    resource_type: ResourceType
    estimated_improvement: float  # Percentage improvement they can provide
    confidence: float  # 0-1, how confident they are
    estimated_duration: float  # Seconds
    action_name: str  # Name of action they'll take
    
    def get_score(self) -> float:
        """Calculate capability score for ranking"""
        # Higher improvement and confidence = better score
        return self.estimated_improvement * self.confidence


@dataclass
class CoordinationRequest:
    """Request for coordinated action"""
    request_id: str
    resource_type: ResourceType
    current_value: float
    threshold: float
    priority: CoordinationPriority
    requesting_agent: str
    
    # Response tracking
    status: CoordinationStatus = CoordinationStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    
    # Negotiation results
    capabilities: List[AgentCapability] = field(default_factory=list)
    selected_agents: List[str] = field(default_factory=list)
    execution_plan: List[Dict[str, Any]] = field(default_factory=list)
    
    # Results
    completed_at: Optional[datetime] = None
    final_value: Optional[float] = None
    total_improvement: Optional[float] = None
    
    def is_expired(self, timeout_seconds: int = 300) -> bool:
        """Check if request has expired"""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > timeout_seconds
    
    def get_best_capabilities(self, limit: int = 3) -> List[AgentCapability]:
        """Get top N capabilities by score"""
        sorted_caps = sorted(self.capabilities, key=lambda c: c.get_score(), reverse=True)
        return sorted_caps[:limit]


@dataclass
class AgentLock:
    """Lock to prevent agent conflicts"""
    agent_name: str
    resource_type: ResourceType
    locked_by: str  # Request ID
    locked_at: datetime
    expires_at: datetime
    
    def is_expired(self) -> bool:
        """Check if lock has expired"""
        return datetime.now() > self.expires_at


class CoordinationManager:
    """
    Manages cross-agent coordination for system-wide issues.
    
    Features:
    - Resource negotiation (agents bid on helping)
    - Conflict prevention (locks to avoid collisions)
    - Coordinated execution (sequential or parallel)
    - Priority management (critical requests first)
    """
    
    def __init__(self):
        self.active_requests: Dict[str, CoordinationRequest] = {}
        self.agent_locks: Dict[Tuple[str, ResourceType], AgentLock] = {}
        self.agent_capabilities: Dict[str, Callable] = {}
        
        # Configuration
        self.negotiation_timeout = 5.0  # Seconds to wait for bids
        self.lock_duration = 60.0  # Seconds a lock lasts
        self.max_parallel_agents = 3  # Max agents working simultaneously
        
        # Statistics
        self.total_coordinations = 0
        self.successful_coordinations = 0
        self.failed_coordinations = 0
    
    def register_agent_capability(
        self,
        agent_name: str,
        capability_callback: Callable
    ):
        """
        Register an agent's capability to respond to coordination requests.
        
        Args:
            agent_name: Name of the agent
            capability_callback: Async function that returns AgentCapability
                                Signature: async def callback(resource_type, current_value) -> AgentCapability
        """
        self.agent_capabilities[agent_name] = capability_callback
        logger.info(f"🤝 Registered coordination capability for {agent_name}")
    
    async def request_coordination(
        self,
        resource_type: ResourceType,
        current_value: float,
        threshold: float,
        priority: CoordinationPriority,
        requesting_agent: str
    ) -> str:
        """
        Request coordinated help from other agents.
        
        Args:
            resource_type: Resource needing help
            current_value: Current resource value
            threshold: Threshold that was exceeded
            priority: Priority level
            requesting_agent: Agent requesting help
        
        Returns:
            Request ID
        """
        request_id = str(uuid.uuid4())
        
        request = CoordinationRequest(
            request_id=request_id,
            resource_type=resource_type,
            current_value=current_value,
            threshold=threshold,
            priority=priority,
            requesting_agent=requesting_agent
        )
        
        self.active_requests[request_id] = request
        self.total_coordinations += 1
        
        logger.info(
            f"🤝 Coordination requested by {requesting_agent}: "
            f"{resource_type.upper()} at {current_value:.1f}% "
            f"(priority: {priority})"
        )
        
        # Start coordination workflow
        asyncio.create_task(self._coordinate_response(request_id))
        
        return request_id
    
    async def _coordinate_response(self, request_id: str):
        """
        Coordinate response to a request.
        
        Workflow:
        1. Negotiate - collect bids from agents
        2. Select - choose best agents
        3. Lock - acquire locks to prevent conflicts
        4. Execute - run actions in order
        5. Complete - record results
        """
        request = self.active_requests.get(request_id)
        if not request:
            return
        
        try:
            # Phase 1: Negotiate
            request.status = CoordinationStatus.NEGOTIATING
            await self._negotiate_capabilities(request)
            
            if not request.capabilities:
                logger.warning(f"🤝 No agents available to help with {request_id}")
                request.status = CoordinationStatus.FAILED
                self.failed_coordinations += 1
                return
            
            # Phase 2: Select best agents
            selected_capabilities = request.get_best_capabilities(
                limit=self.max_parallel_agents
            )
            
            if not selected_capabilities:
                logger.warning(f"🤝 No suitable agents found for {request_id}")
                request.status = CoordinationStatus.FAILED
                self.failed_coordinations += 1
                return
            
            request.selected_agents = [cap.agent_name for cap in selected_capabilities]
            
            logger.info(
                f"🤝 Selected agents for {request_id}: "
                f"{', '.join(request.selected_agents)}"
            )
            
            # Phase 3: Acquire locks
            locks_acquired = await self._acquire_locks(request, selected_capabilities)
            
            if not locks_acquired:
                logger.warning(f"🤝 Could not acquire locks for {request_id}")
                request.status = CoordinationStatus.FAILED
                self.failed_coordinations += 1
                return
            
            # Phase 4: Execute coordinated actions
            request.status = CoordinationStatus.EXECUTING
            success = await self._execute_coordinated_actions(request, selected_capabilities)
            
            # Phase 5: Complete
            if success:
                request.status = CoordinationStatus.COMPLETED
                request.completed_at = datetime.now()
                self.successful_coordinations += 1
                logger.info(f"🤝✅ Coordination {request_id} completed successfully!")
            else:
                request.status = CoordinationStatus.FAILED
                self.failed_coordinations += 1
                logger.error(f"🤝❌ Coordination {request_id} failed")
            
        except Exception as e:
            logger.error(f"🤝💥 Coordination {request_id} error: {e}")
            request.status = CoordinationStatus.FAILED
            self.failed_coordinations += 1
        
        finally:
            # Release locks
            await self._release_locks(request)
    
    async def _negotiate_capabilities(self, request: CoordinationRequest):
        """
        Negotiate with agents to see who can help.
        
        Broadcasts request and collects bids from agents.
        """
        logger.info(f"🤝 Negotiating capabilities for {request.request_id}")
        
        # Collect bids from all registered agents
        tasks = []
        for agent_name, callback in self.agent_capabilities.items():
            # Don't ask the requesting agent
            if agent_name == request.requesting_agent:
                continue
            
            # Check if agent is locked
            if self._is_agent_locked(agent_name, request.resource_type):
                continue
            
            # Request capability
            task = self._get_agent_capability(
                agent_name,
                callback,
                request.resource_type,
                request.current_value
            )
            tasks.append(task)
        
        # Wait for responses with timeout
        try:
            capabilities = await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=self.negotiation_timeout
            )
            
            # Filter out errors and None responses
            valid_capabilities = [
                cap for cap in capabilities
                if isinstance(cap, AgentCapability)
            ]
            
            request.capabilities = valid_capabilities
            
            logger.info(
                f"🤝 Received {len(valid_capabilities)} capability bids "
                f"for {request.request_id}"
            )
            
        except asyncio.TimeoutError:
            logger.warning(f"🤝 Negotiation timeout for {request.request_id}")
    
    async def _get_agent_capability(
        self,
        agent_name: str,
        callback: Callable,
        resource_type: ResourceType,
        current_value: float
    ) -> Optional[AgentCapability]:
        """Get capability from a single agent"""
        try:
            capability = await callback(resource_type, current_value)
            if capability:
                logger.debug(
                    f"🤝 {agent_name} bid: {capability.estimated_improvement:.1f}% "
                    f"improvement (confidence: {capability.confidence:.0%})"
                )
            return capability
        except Exception as e:
            logger.error(f"🤝 Error getting capability from {agent_name}: {e}")
            return None
    
    def _is_agent_locked(self, agent_name: str, resource_type: ResourceType) -> bool:
        """Check if agent is locked for this resource"""
        key = (agent_name, resource_type)
        
        if key not in self.agent_locks:
            return False
        
        lock = self.agent_locks[key]
        
        # Check if lock expired
        if lock.is_expired():
            del self.agent_locks[key]
            return False
        
        return True
    
    async def _acquire_locks(
        self,
        request: CoordinationRequest,
        capabilities: List[AgentCapability]
    ) -> bool:
        """
        Acquire locks for selected agents.
        
        Returns True if all locks acquired, False otherwise.
        """
        acquired_locks = []
        
        try:
            for capability in capabilities:
                key = (capability.agent_name, request.resource_type)
                
                # Check if already locked
                if self._is_agent_locked(capability.agent_name, request.resource_type):
                    logger.warning(
                        f"🤝 {capability.agent_name} is locked, cannot acquire"
                    )
                    # Release any locks we acquired
                    for lock_key in acquired_locks:
                        del self.agent_locks[lock_key]
                    return False
                
                # Acquire lock
                lock = AgentLock(
                    agent_name=capability.agent_name,
                    resource_type=request.resource_type,
                    locked_by=request.request_id,
                    locked_at=datetime.now(),
                    expires_at=datetime.now() + timedelta(seconds=self.lock_duration)
                )
                
                self.agent_locks[key] = lock
                acquired_locks.append(key)
                
                logger.debug(f"🤝🔒 Locked {capability.agent_name} for {request.request_id}")
            
            return True
            
        except Exception as e:
            logger.error(f"🤝 Error acquiring locks: {e}")
            # Release any locks we acquired
            for lock_key in acquired_locks:
                if lock_key in self.agent_locks:
                    del self.agent_locks[lock_key]
            return False
    
    async def _release_locks(self, request: CoordinationRequest):
        """Release all locks for this request"""
        released = 0
        
        for key, lock in list(self.agent_locks.items()):
            if lock.locked_by == request.request_id:
                del self.agent_locks[key]
                released += 1
                logger.debug(f"🤝🔓 Released lock for {lock.agent_name}")
        
        if released > 0:
            logger.info(f"🤝 Released {released} locks for {request.request_id}")
    
    async def _execute_coordinated_actions(
        self,
        request: CoordinationRequest,
        capabilities: List[AgentCapability]
    ) -> bool:
        """
        Execute coordinated actions.
        
        For now, executes sequentially. Could be parallel in future.
        """
        logger.info(
            f"🤝 Executing coordinated actions for {request.request_id}: "
            f"{len(capabilities)} agents"
        )
        
        total_improvement = 0.0
        
        for capability in capabilities:
            logger.info(
                f"🤝 {capability.agent_name} executing {capability.action_name} "
                f"(expected: {capability.estimated_improvement:.1f}% improvement)"
            )
            
            # TODO: Actually execute the action
            # For now, simulate with sleep
            await asyncio.sleep(0.5)
            
            # Record in execution plan
            request.execution_plan.append({
                "agent": capability.agent_name,
                "action": capability.action_name,
                "estimated_improvement": capability.estimated_improvement,
                "timestamp": datetime.now().isoformat()
            })
            
            total_improvement += capability.estimated_improvement
        
        request.total_improvement = total_improvement
        request.final_value = request.current_value - total_improvement
        
        logger.info(
            f"🤝 Coordinated actions complete: "
            f"{request.current_value:.1f}% → {request.final_value:.1f}% "
            f"({total_improvement:.1f}% improvement)"
        )
        
        return True
    
    def get_request_status(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a coordination request"""
        request = self.active_requests.get(request_id)
        
        if not request:
            return None
        
        return {
            "request_id": request.request_id,
            "status": request.status.value,
            "resource_type": request.resource_type.value,
            "priority": request.priority.value,
            "requesting_agent": request.requesting_agent,
            "selected_agents": request.selected_agents,
            "total_improvement": request.total_improvement,
            "created_at": request.created_at.isoformat(),
            "completed_at": request.completed_at.isoformat() if request.completed_at else None
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get coordination statistics"""
        active_count = sum(
            1 for r in self.active_requests.values()
            if r.status in [CoordinationStatus.PENDING, CoordinationStatus.NEGOTIATING, CoordinationStatus.EXECUTING]
        )
        
        success_rate = (
            self.successful_coordinations / self.total_coordinations
            if self.total_coordinations > 0 else 0.0
        )
        
        return {
            "total_coordinations": self.total_coordinations,
            "successful": self.successful_coordinations,
            "failed": self.failed_coordinations,
            "success_rate": success_rate,
            "active_requests": active_count,
            "active_locks": len(self.agent_locks),
            "registered_agents": len(self.agent_capabilities)
        }


# Global singleton
_coordination_manager: Optional[CoordinationManager] = None


def get_coordination_manager() -> CoordinationManager:
    """Get or create the global coordination manager"""
    global _coordination_manager
    if _coordination_manager is None:
        _coordination_manager = CoordinationManager()
    return _coordination_manager
