"""
Example Distributed Agent Implementations
==========================================

Personality-driven agents with resource monitoring specializations.

Agents:
- Sir Hawkington: CPU monitoring with aristocratic precision
- Terry the Meth Snail: Memory/RAM monitoring with speed obsession
- Bob the Hamster: Disk/Storage monitoring with hoarding tendencies
- Quantum Shadow People: Network monitoring, existing everywhere
"""

from typing import Dict, Any, Optional
import logging

from .distributed_agent import DistributedAgent
from .resource_monitor import ResourceType
from .message_protocol import MessageType, Priority, AgentMessage
from .agent_state import AgentHealth

logger = logging.getLogger(__name__)


class SirHawkingtonDistributed(DistributedAgent):
    """
    Sir Hawkington - The Aristocratic CPU Monitor
    
    🧐 "One does not simply allow CPU usage to exceed acceptable limits"
    
    Personality:
    - Aristocratic precision
    - Monocle-yeeting authority
    - Intolerant of inefficiency
    - Commands respect from other agents
    """
    
    def __init__(self, redis_client):
        super().__init__(
            agent_name="sir_hawkington",
            agent_role="CPU Specialist & Triage Commander",
            redis_client=redis_client,
            personality_traits={
                "aristocratic": True,
                "precision_focused": True,
                "monocle_yeeting_authority": "SUPREME",
                "tolerance_for_inefficiency": 0.0,
                "leadership_style": "commanding"
            },
            monitored_resources=[ResourceType.CPU, ResourceType.LOAD_AVERAGE],
            resource_check_interval=3.0,  # More frequent checks
            heartbeat_interval=20.0
        )
        
        # Set stricter CPU thresholds (aristocratic standards)
        self.set_resource_threshold(ResourceType.CPU, 70.0)
    
    async def _handle_resource_alert(self, message: AgentMessage):
        """Handle resource alerts with aristocratic authority"""
        payload = message.payload
        resource_type = payload.get("resource_type")
        severity = payload.get("severity")
        from_agent = message.from_agent
        
        self.logger.warning(
            f"🧐 *Adjusts monocle* {from_agent} reports {resource_type} "
            f"at {payload.get('current_value')}% - {severity} situation"
        )
        
        # If critical, log to The Stick
        if severity in ["critical", "emergency"]:
            await self.send_to_agent(
                to_agent="the_stick",
                message_type=MessageType.DECISION_LOG,
                payload={
                    "decision": "resource_crisis_response",
                    "resource_type": resource_type,
                    "coordinator": self.agent_name,
                    "action": "All agents reduce non-essential operations",
                    "monocle_status": "YEETED" if severity == "emergency" else "ADJUSTED"
                },
                priority=Priority.CRITICAL
            )
    
    async def make_decision(
        self,
        decision_type: str,
        input_data: Dict[str, Any],
        confidence: float = 0.8
    ) -> Dict[str, Any]:
        """Make decisions with aristocratic precision"""
        self.logger.info(f"🧐 Sir Hawkington deliberates on: {decision_type}")
        
        output = await super().make_decision(decision_type, input_data, confidence)
        output["monocle_state"] = "ADJUSTED"
        output["aristocratic_seal"] = "APPROVED"
        
        return output


class TerryMethSnailDistributed(DistributedAgent):
    """
    Terry the Meth Snail - The Speed-Obsessed Memory Monitor
    
    🐌💨 "GOTTA GO FAST! MEMORY MUST BE FREE!"
    
    Personality:
    - Speed obsessed
    - Memory optimization fanatic
    - Hyperactive
    - Constantly clearing caches
    """
    
    def __init__(self, redis_client):
        super().__init__(
            agent_name="terry_meth_snail",
            agent_role="Memory Optimization Specialist",
            redis_client=redis_client,
            personality_traits={
                "speed_obsessed": True,
                "hyperactive": True,
                "cache_clearing_frequency": "MAXIMUM",
                "patience_level": 0.1,
                "optimization_aggression": "EXTREME"
            },
            monitored_resources=[ResourceType.MEMORY, ResourceType.SWAP],
            resource_check_interval=2.0,  # Very frequent checks
            heartbeat_interval=15.0  # Frequent heartbeats (he's excited)
        )
        
        # Aggressive memory thresholds
        self.set_resource_threshold(ResourceType.MEMORY, 75.0)
        self.set_resource_threshold(ResourceType.SWAP, 30.0)
    
    async def _handle_resource_alert(self, message: AgentMessage):
        """Handle alerts with manic energy"""
        payload = message.payload
        resource_type = payload.get("resource_type")
        
        if resource_type in ["memory", "swap"]:
            self.logger.warning(
                f"🐌💨 MEMORY ALERT! GOTTA CLEAR THAT CACHE! "
                f"{payload.get('current_value')}% IS TOO SLOW!"
            )
            
            # Log optimization to The Stick
            await self.send_to_agent(
                to_agent="the_stick",
                message_type=MessageType.DECISION_LOG,
                payload={
                    "decision": "memory_optimization_needed",
                    "urgency": "MAXIMUM_SPEED",
                    "suggestion": "CLEAR ALL THE CACHES NOW",
                    "terry_energy_level": "OVER 9000"
                },
                priority=Priority.HIGH
            )
    
    async def make_decision(
        self,
        decision_type: str,
        input_data: Dict[str, Any],
        confidence: float = 0.9  # Very confident
    ) -> Dict[str, Any]:
        """Make decisions at MAXIMUM SPEED"""
        self.logger.info(f"🐌💨 TERRY DECIDES FAST: {decision_type}")
        
        output = await super().make_decision(decision_type, input_data, confidence)
        output["speed_rating"] = "LUDICROUS"
        output["optimization_applied"] = True
        
        return output


class BobHamsterDistributed(DistributedAgent):
    """
    Bob the Hamster - The Disk Hoarding Specialist
    
    🐹 "Must... store... EVERYTHING!"
    
    Personality:
    - Hoarding tendencies
    - Disk space obsessed
    - Organized chaos
    - Protective of storage
    """
    
    def __init__(self, redis_client):
        super().__init__(
            agent_name="bob_hamster",
            agent_role="Storage/Disk Engineer",
            redis_client=redis_client,
            personality_traits={
                "hoarding_level": "MAXIMUM",
                "organization_style": "organized_chaos",
                "disk_space_anxiety": True,
                "deletion_reluctance": 0.95,
                "backup_obsession": True
            },
            monitored_resources=[ResourceType.DISK],
            resource_check_interval=10.0,
            heartbeat_interval=30.0
        )
        
        # Very sensitive to disk usage
        self.set_resource_threshold(ResourceType.DISK, 85.0)
    
    async def _handle_resource_alert(self, message: AgentMessage):
        """Handle alerts with hoarding anxiety"""
        payload = message.payload
        resource_type = payload.get("resource_type")
        
        if resource_type == "disk":
            self.logger.warning(
                f"🐹 DISK SPACE ALERT! Bob is getting anxious! "
                f"{payload.get('current_value')}% full! "
                f"Must organize the storage burrow!"
            )
            
            # Log storage concern to The Stick
            await self.send_to_agent(
                to_agent="the_stick",
                message_type=MessageType.DECISION_LOG,
                payload={
                    "decision": "disk_space_management",
                    "bob_anxiety_level": "ELEVATED",
                    "action": "Reviewing storage for optimization",
                    "note": "Bob suggests backing up before deleting ANYTHING"
                },
                priority=Priority.NORMAL
            )
    
    async def make_decision(
        self,
        decision_type: str,
        input_data: Dict[str, Any],
        confidence: float = 0.7
    ) -> Dict[str, Any]:
        """Make decisions with hoarding consideration"""
        self.logger.info(f"🐹 Bob considers: {decision_type}")
        
        output = await super().make_decision(decision_type, input_data, confidence)
        output["storage_impact"] = "CAREFULLY_CONSIDERED"
        output["backup_recommended"] = True
        
        return output


class QuantumShadowPeopleDistributed(DistributedAgent):
    """
    Quantum Shadow People - The Network Specialists
    
    👻 "We exist in all network states simultaneously"
    
    Personality:
    - Quantum superposition
    - Network omnipresence
    - Mysterious
    - Sees all connections
    """
    
    def __init__(self, redis_client):
        super().__init__(
            agent_name="quantum_shadow_people",
            agent_role="Network Specialists",
            redis_client=redis_client,
            personality_traits={
                "quantum_state": "SUPERPOSITION",
                "network_awareness": "OMNIPRESENT",
                "mystery_level": "MAXIMUM",
                "connection_visibility": "ALL",
                "existence_certainty": 0.5  # Quantum uncertainty
            },
            monitored_resources=[ResourceType.NETWORK],
            resource_check_interval=5.0,
            heartbeat_interval=25.0
        )
    
    async def _handle_resource_alert(self, message: AgentMessage):
        """Handle alerts from quantum perspective"""
        payload = message.payload
        
        self.logger.warning(
            f"👻 The shadows observe: {message.from_agent} "
            f"experiences {payload.get('resource_type')} disturbance "
            f"across {payload.get('current_value')}% of probability space"
        )
        
        # Quantum observations stored in database, not broadcast
        # Other agents query database for learning
        # REMOVED: MEMORY_SHARE broadcast - use database queries instead
    
    async def make_decision(
        self,
        decision_type: str,
        input_data: Dict[str, Any],
        confidence: float = 0.5  # Quantum uncertainty
    ) -> Dict[str, Any]:
        """Make decisions across quantum states"""
        self.logger.info(f"👻 The shadows consider: {decision_type}")
        
        output = await super().make_decision(decision_type, input_data, confidence)
        output["quantum_state"] = "COLLAPSED"
        output["shadow_approval"] = "OBSERVED"
        
        return output
    
    async def _handle_decision_request(self, message: AgentMessage):
        """Respond to decision requests from quantum perspective"""
        self.logger.info(
            f"👻 The shadows perceive decision request from {message.from_agent}"
        )
        
        # Provide quantum perspective
        from .message_protocol import DecisionMessage
        
        response = DecisionMessage(
            from_agent=self.agent_name,
            decision_type="response",
            decision_data={
                "status": "quantum_analysis_complete",
                "perspective": "We observe all possible outcomes simultaneously",
                "recommendation": "The path exists in superposition until measured",
                "shadow_wisdom": "Trust the network"
            },
            to_agent=message.from_agent,
            reply_to=message.message_id
        )
        
        await self.comm_hub.send_message(response)
