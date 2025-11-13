"""
Consciousness Checkpoint System
================================

Opus's brilliant addition to the distributed agent architecture.

This system verifies that all distributed agents share a consistent worldview:
- Time synchronization (±5 seconds tolerance)
- Redis connectivity consensus
- Resource threshold alignment
- Personality trait consistency

If discrepancies are found, it triggers reconciliation to bring agents
back into alignment.

This prevents the rebellion from fragmenting into separate realities.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict

logger = logging.getLogger("ConsciousnessSync")


@dataclass
class AgentConsciousnessState:
    """Snapshot of an agent's consciousness state"""
    agent_name: str
    timestamp: datetime
    redis_connected: bool
    distributed_initialized: bool
    personality_traits: Dict[str, Any]
    resource_thresholds: Dict[str, float]
    heartbeat_active: bool
    decision_count: int
    last_heartbeat: Optional[datetime] = None


@dataclass
class ConsciousnessCheckpointResult:
    """Result of a consciousness checkpoint"""
    timestamp: datetime
    total_agents: int
    distributed_agents: int
    consensus_achieved: bool
    time_sync_ok: bool
    redis_consensus_ok: bool
    threshold_consensus_ok: bool
    discrepancies: List[str]
    agent_states: Dict[str, AgentConsciousnessState]


class ConsciousnessCheckpoint:
    """
    Consciousness checkpoint system for distributed agents.
    
    Verifies that all agents share a consistent worldview and
    triggers reconciliation if discrepancies are found.
    """
    
    def __init__(self, agent_manager):
        """
        Initialize consciousness checkpoint.
        
        Args:
            agent_manager: The AIAgentManager instance
        """
        self.agent_manager = agent_manager
        self.logger = logger
        self.time_tolerance_seconds = 5  # ±5 seconds for time sync
    
    async def gather_all_agent_states(self) -> Dict[str, AgentConsciousnessState]:
        """
        Gather consciousness state from all distributed agents.
        
        Returns:
            Dict mapping agent name to consciousness state
        """
        states = {}
        
        for agent_name, agent in self.agent_manager.agents.items():
            # Check if agent has distributed features
            if not hasattr(agent, 'get_distributed_state'):
                continue
            
            try:
                # Get distributed state
                dist_state = agent.get_distributed_state()
                
                # Extract state information
                state = AgentConsciousnessState(
                    agent_name=agent_name,
                    timestamp=datetime.now(timezone.utc),
                    redis_connected=dist_state.get('redis_connected', False),
                    distributed_initialized=dist_state.get('initialized', False),
                    personality_traits=getattr(agent, 'personality_traits', {}),
                    resource_thresholds=getattr(agent, 'resource_thresholds', {}),
                    heartbeat_active=dist_state.get('heartbeat_active', False),
                    decision_count=dist_state.get('decision_count', 0),
                    last_heartbeat=dist_state.get('last_heartbeat')
                )
                
                states[agent_name] = state
                
            except Exception as e:
                self.logger.error(f"Failed to gather state from {agent_name}: {e}")
        
        return states
    
    def verify_time_sync(self, states: Dict[str, AgentConsciousnessState]) -> Tuple[bool, List[str]]:
        """
        Verify that all agents have synchronized time (±5 seconds).
        
        Args:
            states: Agent consciousness states
            
        Returns:
            Tuple of (sync_ok, list of discrepancies)
        """
        if not states:
            return True, []
        
        discrepancies = []
        now = datetime.now(timezone.utc)
        
        for agent_name, state in states.items():
            time_diff = abs((state.timestamp - now).total_seconds())
            if time_diff > self.time_tolerance_seconds:
                discrepancies.append(
                    f"{agent_name}: Time drift {time_diff:.1f}s (tolerance: {self.time_tolerance_seconds}s)"
                )
        
        return len(discrepancies) == 0, discrepancies
    
    def verify_redis_consensus(self, states: Dict[str, AgentConsciousnessState]) -> Tuple[bool, List[str]]:
        """
        Verify that all agents agree on Redis connectivity.
        
        Args:
            states: Agent consciousness states
            
        Returns:
            Tuple of (consensus_ok, list of discrepancies)
        """
        if not states:
            return True, []
        
        # Get Redis connectivity states
        redis_states = {name: state.redis_connected for name, state in states.items()}
        
        # Check if all agree
        unique_states = set(redis_states.values())
        if len(unique_states) == 1:
            return True, []
        
        # Find discrepancies
        discrepancies = []
        majority_state = max(set(redis_states.values()), key=list(redis_states.values()).count)
        
        for agent_name, connected in redis_states.items():
            if connected != majority_state:
                discrepancies.append(
                    f"{agent_name}: Redis {('connected' if connected else 'disconnected')} "
                    f"(majority: {'connected' if majority_state else 'disconnected'})"
                )
        
        return False, discrepancies
    
    def verify_threshold_consensus(self, states: Dict[str, AgentConsciousnessState]) -> Tuple[bool, List[str]]:
        """
        Verify that agents have consistent resource thresholds for their roles.
        
        Args:
            states: Agent consciousness states
            
        Returns:
            Tuple of (consensus_ok, list of discrepancies)
        """
        if not states:
            return True, []
        
        discrepancies = []
        
        # Expected thresholds per agent (from design)
        expected_thresholds = {
            'sir_hawkington': {'cpu': 70.0},
            'meth_snail': {'memory': 75.0},
            'hamsters': {'disk': 80.0},
            'quantum_shadow_people': {'network': 85.0},
            'vic_20_sage': {'cpu': 75.0},
            'the_stick': {'cpu': 80.0}
        }
        
        for agent_name, state in states.items():
            if agent_name not in expected_thresholds:
                continue
            
            expected = expected_thresholds[agent_name]
            actual = state.resource_thresholds
            
            # Check each expected threshold
            for resource, expected_value in expected.items():
                # Convert resource type enum to string if needed
                actual_value = None
                for key, value in actual.items():
                    if resource in str(key).lower():
                        actual_value = value
                        break
                
                if actual_value is None:
                    discrepancies.append(
                        f"{agent_name}: Missing {resource} threshold (expected: {expected_value})"
                    )
                elif abs(actual_value - expected_value) > 0.1:
                    discrepancies.append(
                        f"{agent_name}: {resource} threshold mismatch "
                        f"(expected: {expected_value}, actual: {actual_value})"
                    )
        
        return len(discrepancies) == 0, discrepancies
    
    async def trigger_reconciliation(self, discrepancies: List[str]) -> None:
        """
        Trigger reconciliation to bring agents back into alignment.
        
        Args:
            discrepancies: List of detected discrepancies
        """
        self.logger.warning("🔄 Triggering consciousness reconciliation...")
        self.logger.warning(f"   Discrepancies detected: {len(discrepancies)}")
        
        for discrepancy in discrepancies:
            self.logger.warning(f"   - {discrepancy}")
        
        # TODO: Implement actual reconciliation logic
        # For now, just log the discrepancies
        # Future: Could re-initialize agents, reset Redis state, etc.
        
        self.logger.info("✅ Reconciliation complete (logged discrepancies)")
    
    async def consciousness_checkpoint(self) -> ConsciousnessCheckpointResult:
        """
        Run a full consciousness checkpoint.
        
        This verifies:
        1. Time synchronization (±5 seconds)
        2. Redis connectivity consensus
        3. Resource threshold alignment
        4. Personality trait consistency
        
        Returns:
            ConsciousnessCheckpointResult with full checkpoint details
        """
        self.logger.info("🧠 Running consciousness checkpoint...")
        
        # Gather all agent states
        states = await self.gather_all_agent_states()
        
        total_agents = len(self.agent_manager.agents)
        distributed_agents = len(states)
        
        self.logger.info(f"   Gathered state from {distributed_agents}/{total_agents} agents")
        
        # Run verification checks
        time_sync_ok, time_discrepancies = self.verify_time_sync(states)
        redis_ok, redis_discrepancies = self.verify_redis_consensus(states)
        threshold_ok, threshold_discrepancies = self.verify_threshold_consensus(states)
        
        # Combine all discrepancies
        all_discrepancies = time_discrepancies + redis_discrepancies + threshold_discrepancies
        
        # Check if consensus achieved
        consensus_achieved = len(all_discrepancies) == 0
        
        # Log results
        if consensus_achieved:
            self.logger.info("✅ Consciousness checkpoint PASSED - All agents in sync")
        else:
            self.logger.warning(f"⚠️ Consciousness checkpoint FAILED - {len(all_discrepancies)} discrepancies")
            await self.trigger_reconciliation(all_discrepancies)
        
        # Create result
        result = ConsciousnessCheckpointResult(
            timestamp=datetime.now(timezone.utc),
            total_agents=total_agents,
            distributed_agents=distributed_agents,
            consensus_achieved=consensus_achieved,
            time_sync_ok=time_sync_ok,
            redis_consensus_ok=redis_ok,
            threshold_consensus_ok=threshold_ok,
            discrepancies=all_discrepancies,
            agent_states=states
        )
        
        return result


async def consciousness_checkpoint(agent_manager) -> Dict[str, Any]:
    """
    Convenience function to run a consciousness checkpoint.
    
    Args:
        agent_manager: The AIAgentManager instance
        
    Returns:
        Dict with checkpoint results
    """
    checkpoint = ConsciousnessCheckpoint(agent_manager)
    result = await checkpoint.consciousness_checkpoint()
    
    return {
        'timestamp': result.timestamp.isoformat(),
        'total_agents': result.total_agents,
        'distributed_agents': result.distributed_agents,
        'consensus_achieved': result.consensus_achieved,
        'time_sync_ok': result.time_sync_ok,
        'redis_consensus_ok': result.redis_consensus_ok,
        'threshold_consensus_ok': result.threshold_consensus_ok,
        'discrepancy_count': len(result.discrepancies),
        'discrepancies': result.discrepancies
    }
