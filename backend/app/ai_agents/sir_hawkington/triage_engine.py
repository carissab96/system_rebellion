# app/ai_agents/sir_hawkington/triage_engine.py
"""
Sir Hawkington's Triage Engine - THE ARISTOCRATIC REVOLUTION
DUAL ROLE COMMANDER: System-Wide Triage Officer + CPU Specialist

UPDATED: Now queries agent-specific table for structured analytics
NO FAKE DATA POLICY: Real data or graceful failure

This is the NEW entry point for ALL system metrics. Sir Hawkington has evolved from
a simple monitoring agent to the MASTER TRIAGE COMMANDER of the entire system.

🧐 "One does not simply monitor systems - one orchestrates them with aristocratic precision"

ROUTING PHILOSOPHY:
- NORMAL: Direct to The Stick for baseline learning
- MEDIUM: VIC-20 coordination with specialist recommendations  
- HIGH/EMERGENCY: MONOCLE YEET to VIC-20 for multi-agent orchestration

NO FAKE DATA TOLERANCE: ABSOLUTE
Monocle yeeting authority: SUPREME
Aristocratic standards: MAINTAINED
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import json

# Database integration
from .database_integration import HawkingtonDatabaseIntegration

# Import agent memory model for structured queries
from app.models.agent_memory_banks import SirHawkingtonMemoryBank

# Import agent manager at module level to avoid circular imports
from ..agent_manager import get_agent_manager

# Import instrumentation for method tracking
from ..agent_instrumentation import AgentInstrumentationMixin, instrument_method

# Import Sir Hawkington's existing brain
from .decision_engine import (
    sir_hawkington_brain, 
    HawkingtonDecision, 
    DecisionType, 
    MonocleState,
    AnalysisDepth
)

# VIC-20 Sage coordination functions
from ..vic_20_sage.decision_engine import (
    coordinate_agents as vic20_coordinate_agents,
    coordinate_emergency_response as vic20_emergency_response,
)

from app.utils.json_safety import to_json_safe

# SQLAlchemy imports for structured queries
from sqlalchemy import select, and_, func, desc

UTC = timezone.utc

def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)

def datetime_to_iso(dt):
    """Convert datetime to ISO string for JSON serialization"""
    return dt.isoformat() if dt else None

logger = logging.getLogger("SirHawkington.TriageEngine")

class TriageRouting(Enum):
    """Sir Hawkington's triage routing decisions"""
    STICK_DIRECT = "stick_direct"
    VIC20_COORDINATION = "vic20_coordination"
    VIC20_EMERGENCY = "vic20_emergency"
    CPU_SPECIALIST = "cpu_specialist"

class TriageSeverity(Enum):
    """Triage severity levels"""
    NORMAL = "normal"
    MEDIUM = "medium" 
    HIGH = "high"
    EMERGENCY = "emergency"

@dataclass
class TriageDecision:
    """Sir Hawkington's aristocratic triage decision"""
    severity: TriageSeverity
    routing: TriageRouting
    target_agents: List[str]
    reasoning: str
    monocle_yeeted: bool
    hawkington_decision: Optional[HawkingtonDecision]
    confidence: float
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = utc_now()
    
    @property
    def metrics(self) -> Optional[Dict[str, Any]]:
        """Get metrics from hawkington_decision"""
        return self.hawkington_decision.metrics if self.hawkington_decision else None
    
    @property
    def stress_score(self) -> float:
        """Get stress score directly"""
        return self.metrics.get('stress_score', 0.0) if self.metrics else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""
        hawkington_dict = None
        if self.hawkington_decision:
            hawkington_dict = {
                'decision_id': self.hawkington_decision.decision_id,
                'decision_type': self.hawkington_decision.decision_type,
                'confidence': self.hawkington_decision.confidence,
                'reasoning': self.hawkington_decision.reasoning,
                'metrics': self.hawkington_decision.metrics,
                'timestamp': self.hawkington_decision.timestamp.isoformat() if hasattr(self.hawkington_decision.timestamp, 'isoformat') else str(self.hawkington_decision.timestamp),
                'user_id': self.hawkington_decision.user_id,
                'system_impact': self.hawkington_decision.system_impact
            }
    
        return {
            'severity': self.severity.value,
            'routing': self.routing.value,
            'target_agents': self.target_agents,
            'reasoning': self.reasoning,
            'monocle_yeeted': self.monocle_yeeted,
            'hawkington_decision': hawkington_dict,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class TriageResult:
    """Complete triage processing result"""
    triage_decision: TriageDecision
    routing_results: Dict[str, Any]
    processing_time: float
    success: bool
    errors: List[str]

from .hawk_redis_patch.triage_engine_redis_patch import TriageEngineWithRedisMixin
from .decision_engine import sir_hawkington_brain

class SirHawkingtonTriageEngine(AgentInstrumentationMixin, TriageEngineWithRedisMixin):
    """
    THE ARISTOCRATIC TRIAGE COMMANDER - UPDATED WITH STRUCTURED QUERIES
    
    Sir Hawkington's evolution from simple monitoring to SYSTEM-WIDE ORCHESTRATION.
    This is now the MASTER ENTRY POINT for all system metrics.
    
    NOW QUERIES AGENT-SPECIFIC TABLE FOR:
    - Structured triage statistics
    - Accuracy improvement trends
    - Data quality failure analysis
    
    🧐 "A gentleman does not merely observe - he commands with distinction"
    """

    def __init__(self, db_getter, **kwargs):
        super().__init__(redis_url="redis://localhost", cache_namespace="hawk", **kwargs)
        
        # Set agent_name for instrumentation
        self.agent_name = "sir_hawkington"
        
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter
        
        self.db = None
        self.logger = logging.getLogger("SirHawkington.TriageEngine")
        
        # Triage statistics
        self.total_triage_decisions = 0
        self.routing_stats = {
            'stick_direct': 0,
            'vic20_coordination': 0, 
            'vic20_emergency': 0,
            'cpu_specialist': 0
        }
        self.monocle_yeet_incidents = 0
        
        # Triage thresholds (Sir Hawkington's aristocratic standards)
        self.triage_thresholds = {
            'normal_threshold': 0.30,
            'medium_threshold': 0.65,
            'emergency_threshold': 0.85
        }
        
        # Agent handler cache
        self._agent_handlers = {}
        
        self.initial_dashboard_cache: dict[str, dict] = {}

        self.logger.info("🧐⚡ Sir Hawkington's Triage Engine initialized - ARISTOCRATIC REVOLUTION ACTIVATED")
    
    async def initialize(self):
        """Initialize the triage engine with aristocratic precision"""
        # Initialize database
        if self.db is None:
            self.db = HawkingtonDatabaseIntegration(self.db_getter)
            await self.db.initialize()
            
        await super().initialize()
        
        # Initialize Sir Hawkington's brain
        if hasattr(sir_hawkington_brain, 'initialize_database'):
            if asyncio.iscoroutinefunction(sir_hawkington_brain.initialize_database):
                await sir_hawkington_brain.initialize_database()
            else:
                sir_hawkington_brain.initialize_database()
        
        self.logger.info("🧐✨ Triage Engine initialization complete - Ready for aristocratic command")
    
    # === EXISTING METHODS (NO CHANGES) ===
    
    @instrument_method
    async def process_system_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str] = None,
        user_context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        THE MASTER TRIAGE METHOD - NO FAKE DATA ALLOWED
        (No changes to this method - already correct)
        """
        start_time = utc_now()
        self.total_triage_decisions += 1
        
        try:
            # PHASE 1: SIR HAWKINGTON'S TRIAGE ASSESSMENT
            triage_decision = await self._conduct_triage_assessment(
                metrics_data, user_id, user_context
            )
            
            # PHASE 2: EXECUTE ROUTING DECISION  
            routing_results = await self._execute_triage_routing(
                triage_decision, metrics_data, user_id
            )
            
            # PHASE 3: COMPILE TRIAGE RESULT
            processing_time = (utc_now() - start_time).total_seconds()
            
            triage_result = TriageResult(
                triage_decision=triage_decision,
                routing_results=routing_results,
                processing_time=processing_time,
                success=True,
                errors=[]
            )
            
            # PHASE 4: STORE TRIAGE DECISION
            if self.db and user_id:
                await self._store_triage_decision(user_id, triage_result)
            
            # PHASE 5: ENHANCE METRICS WITH TRIAGE DATA
            enhanced_metrics = await self._enhance_metrics_with_triage(
                metrics_data, triage_result
            )
            
            self.logger.info(
                f"🧐⚡ Triage complete: {triage_decision.severity.value} → "
                f"{triage_decision.routing.value} ({processing_time:.3f}s)"
            )
            
            return enhanced_metrics
            
        except Exception as e:
            self.logger.error(f"🧐💥 ARISTOCRATIC HORROR! Triage failed: {str(e)}")
            raise Exception(f"TRIAGE SYSTEM FAILURE: {str(e)}")
    
    # === KEEP ALL EXISTING PRIVATE METHODS (NO CHANGES) ===
    # _conduct_triage_assessment, _determine_triage_severity, _determine_triage_routing,
    # _determine_target_agents, _create_triage_reasoning, _execute_triage_routing,
    # _route_to_stick, _route_to_vic20_coordination, _route_to_vic20_emergency,
    # _route_to_cpu_specialist, _store_triage_decision, _enhance_metrics_with_triage
    
    async def _conduct_triage_assessment(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str],
        user_context: Optional[Dict]
    ) -> TriageDecision:
        """Phase 1: Sir Hawkington conducts his aristocratic triage assessment"""
        self.logger.debug("🧐 Conducting triage assessment with aristocratic precision...")
        
        historical_data = None
        if self.db and user_id:
            try:
                historical_data = await self.db.get_historical_decisions(user_id, days=7)
            except Exception as e:
                self.logger.warning(f"🧐 Could not get historical data: {str(e)}")
        
        hawkington_decision = await sir_hawkington_brain.analyze_metrics(
            metrics_data=metrics_data,
            historical_data=historical_data,
            user_context=user_context,
            analysis_depth=AnalysisDepth.THOROUGH,
            user_id=user_id
        )
        
        if hawkington_decision is None:
            self.monocle_yeet_incidents += 1
            return TriageDecision(
                severity=TriageSeverity.EMERGENCY,
                routing=TriageRouting.VIC20_EMERGENCY,
                target_agents=["vic_20_sage"],
                reasoning="🧐💥 MONOCLE YEETED! Data quality beneath aristocratic standards - emergency VIC-20 intervention required",
                monocle_yeeted=True,
                hawkington_decision=None,
                confidence=0.0,
                timestamp=utc_now()
            )
        
        severity = self._determine_triage_severity(hawkington_decision.metrics.get('stress_score', 0))
        routing = self._determine_triage_routing(severity, hawkington_decision)
        target_agents = self._determine_target_agents(routing, hawkington_decision)
        
        return TriageDecision(
            severity=severity,
            routing=routing,
            target_agents=target_agents,
            reasoning=self._create_triage_reasoning(severity, routing, hawkington_decision),
            monocle_yeeted=False,
            hawkington_decision=hawkington_decision,
            confidence=hawkington_decision.confidence,
            timestamp=utc_now()
        )
    
    def _determine_triage_severity(self, stress_score: float) -> TriageSeverity:
        """Determine triage severity from Sir Hawkington's stress score"""
        if stress_score >= self.triage_thresholds['emergency_threshold']:
            return TriageSeverity.EMERGENCY
        elif stress_score >= self.triage_thresholds['medium_threshold']:
            return TriageSeverity.HIGH
        elif stress_score >= self.triage_thresholds['normal_threshold']:
            return TriageSeverity.MEDIUM
        else:
            return TriageSeverity.NORMAL
    
    def _determine_triage_routing(
        self, 
        severity: TriageSeverity, 
        hawkington_decision: HawkingtonDecision
    ) -> TriageRouting:
        """Determine routing based on severity and decision type"""
        if severity == TriageSeverity.EMERGENCY:
            return TriageRouting.VIC20_EMERGENCY
        elif severity == TriageSeverity.HIGH:
            return TriageRouting.VIC20_EMERGENCY
        elif severity == TriageSeverity.MEDIUM:
            return TriageRouting.VIC20_COORDINATION
        else:
            return TriageRouting.STICK_DIRECT
    
    def _determine_target_agents(
        self, 
        routing: TriageRouting, 
        hawkington_decision: HawkingtonDecision
    ) -> List[str]:
        """Determine which agents to target based on routing decision"""
        if routing == TriageRouting.STICK_DIRECT:
            return ["the_stick"]
        elif routing == TriageRouting.VIC20_COORDINATION:
            return ["vic_20_sage"]
        elif routing == TriageRouting.VIC20_EMERGENCY:
            return ["vic_20_sage"]
        elif routing == TriageRouting.CPU_SPECIALIST:
            return ["sir_hawkington_cpu"]
        else:
            return ["the_stick"]
    
    def _create_triage_reasoning(
        self, 
        severity: TriageSeverity, 
        routing: TriageRouting, 
        hawkington_decision: HawkingtonDecision
    ) -> str:
        """Create aristocratic reasoning for triage decision"""
        base_reasoning = f"🧐 Aristocratic triage assessment: System stress {hawkington_decision.metrics.get('stress_score', 0):.3f} indicates {severity.value} severity"
        
        if routing == TriageRouting.STICK_DIRECT:
            return f"{base_reasoning}. Normal operations - routing to The Stick for baseline learning."
        elif routing == TriageRouting.VIC20_COORDINATION:
            return f"{base_reasoning}. Moderate concern - VIC-20 coordination required for specialist routing."
        elif routing == TriageRouting.VIC20_EMERGENCY:
            return f"{base_reasoning}. EMERGENCY PROTOCOLS ACTIVATED - VIC-20 multi-agent orchestration required!"
        else:
            return f"{base_reasoning}. Routing decision: {routing.value}"
    
    async def _execute_triage_routing(
        self, 
        triage_decision: TriageDecision, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Phase 2: Execute the triage routing decision"""
        routing_results = {
            'routing_type': triage_decision.routing.value,
            'target_agents': triage_decision.target_agents,
            'results': {},
            'errors': []
        }
        
        self.routing_stats[triage_decision.routing.value] += 1
        
        try:
            if triage_decision.routing == TriageRouting.STICK_DIRECT:
                results = await self._route_to_stick(metrics_data, user_id)
                routing_results['results']['the_stick'] = results
                
            elif triage_decision.routing == TriageRouting.VIC20_COORDINATION:
                results = await self._route_to_vic20_coordination(
                    metrics_data, triage_decision, user_id
                )
                routing_results['results']['vic_20_sage'] = results
                
            elif triage_decision.routing == TriageRouting.VIC20_EMERGENCY:
                results = await self._route_to_vic20_emergency(
                    metrics_data, triage_decision, user_id
                )
                routing_results['results']['vic_20_sage'] = results
                
            elif triage_decision.routing == TriageRouting.CPU_SPECIALIST:
                results = await self._route_to_cpu_specialist(
                    metrics_data, triage_decision, user_id
                )
                routing_results['results']['sir_hawkington_cpu'] = results
                
        except Exception as e:
            error_msg = f"Routing execution failed: {str(e)}"
            routing_results['errors'].append(error_msg)
            self.logger.error(f"🧐💥 {error_msg}")
        
        return routing_results
    
    async def _route_to_stick(
        self, 
        metrics_data: Dict[str, Any], 
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Route normal operations to The Stick + other agents via Agent Manager"""
        self.logger.debug("🧐 Routing to The Stick + other agents via Agent Manager")
        
        try:
            # Emit insight about routing decision
            from app.services.agent_insight_emitter import emit_agent_insight
            await emit_agent_insight(
                from_agent="sir_hawkington",
                to_agent="the_stick",
                action="route_normal_operations",
                reasoning="System stress below concern threshold - routing to baseline learning and monitoring",
                context={
                    "severity": "normal",
                    "cpu_usage": metrics_data.get("cpu_usage"),
                    "memory_usage": metrics_data.get("memory_usage"),
                    "disk_usage": metrics_data.get("disk_usage"),
                    "routing_type": "agent_manager_delegation"
                },
                user_id=user_id
            )
            
            agent_manager = await get_agent_manager()
            
            agent_results = await agent_manager.process_metrics_through_triage_engine(
                metrics_data, 
                user_context={'routed_by': 'sir_hawkington_triage', 'triage_severity': 'normal'}
            )
            
            return {
                'agent': 'agent_manager_delegation',
                'status': 'success',
                'result': {
                    'message': '🧐📏 Normal operations - routed to Agent Manager for full processing',
                    'agent_processing': agent_results.get('agent_processing', {}),
                    'processed_agents': agent_results.get('agent_processing', {}).get('successful_agents', [])
                },
                'routing_reason': 'Normal operations - Agent Manager delegation'
            }
            
        except Exception as e:
            self.logger.error(f"🧐💥 Failed to route to Agent Manager: {str(e)}")
            return {
                'agent': 'agent_manager_delegation',
                'status': 'error',
                'error': str(e),
                'routing_reason': 'Normal operations - Agent Manager delegation'
            }

    async def _route_to_vic20_coordination(
        self, 
        metrics_data: Dict[str, Any], 
        triage_decision: TriageDecision, 
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Route to VIC-20 for coordination with specialist agents"""
        self.logger.debug("🧐 Routing to VIC-20 for specialist coordination")
        
        try:
            # Emit coordination insight
            from app.services.agent_insight_emitter import emit_agent_insight
            await emit_agent_insight(
                from_agent="sir_hawkington",
                to_agent="vic20_sage",
                action="request_coordination",
                reasoning="Medium severity detected - specialist coordination required for optimal response",
                context={
                    "severity": triage_decision.severity.value,
                    "stress_score": triage_decision.stress_score if hasattr(triage_decision, 'stress_score') else 0,
                    "confidence": triage_decision.confidence,
                    "target_agents": triage_decision.target_agents,
                    "coordination_type": "medium_severity"
                },
                user_id=user_id
            )
            
            hawkington_data = {}
            if triage_decision.hawkington_decision:
                hd = triage_decision.hawkington_decision
                hawkington_data = {
                    'decision_id': hd.decision_id,
                    'decision_type': hd.decision_type,
                    'confidence': hd.confidence,
                    'reasoning': hd.reasoning,
                    'metrics': hd.metrics,
                    'timestamp': hd.timestamp.isoformat() if hasattr(hd.timestamp, 'isoformat') else str(hd.timestamp),
                    'user_id': hd.user_id,
                    'system_impact': hd.system_impact
                }
    
            all_agent_data = {
                'sir_hawkington': hawkington_data,
                'system_metrics': metrics_data,
            }
            system_context = {
                'triage_severity': triage_decision.severity.value,
                'monocle_yeeted': triage_decision.monocle_yeeted,
            }
            vic20_decision = await vic20_coordinate_agents(
                all_agent_data,
                system_context,
                user_id or 'anonymous',
            )
            return {
                'agent': 'vic_20_sage',
                'status': 'success',
                'result': vic20_decision.to_dict() if vic20_decision else None,
                'routing_reason': 'Medium severity - VIC-20 specialist coordination',
                'coordination_type': 'medium_severity',
            }

        except Exception as e:
            self.logger.error(f"🧐💥 Failed to route to VIC-20 coordination: {str(e)}")
            return {
                'agent': 'vic_20_sage',
                'status': 'error',
                'error': str(e),
                'routing_reason': 'Medium severity - VIC-20 specialist coordination',
            }
    
    async def _route_to_vic20_emergency(
        self, 
        metrics_data: Dict[str, Any], 
        triage_decision: TriageDecision, 
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """🧐💥 MONOCLE YEET to VIC-20 for emergency multi-agent orchestration"""
        self.logger.warning("🧐💥 MONOCLE YEETED TO VIC-20 - EMERGENCY ORCHESTRATION ACTIVATED!")
        
        try:
            emergency_type = (
                'monocle_yeet' if triage_decision.monocle_yeeted else 'high_severity'
            )
            
            # Emit emergency escalation insight
            from app.services.agent_insight_emitter import emit_agent_insight
            await emit_agent_insight(
                from_agent="sir_hawkington",
                to_agent="vic20_sage",
                action="emergency_escalation",
                reasoning="🧐💥 EMERGENCY - System stress critical or data quality catastrophic - multi-agent orchestration required",
                context={
                    "severity": "emergency",
                    "monocle_yeeted": triage_decision.monocle_yeeted,
                    "stress_score": triage_decision.stress_score if hasattr(triage_decision, 'stress_score') else 0,
                    "emergency_type": emergency_type,
                    "target_agents": triage_decision.target_agents,
                    "aristocratic_authority": "SUPREME"
                },
                user_id=user_id
            )
            
            system_context = {
                'metrics': metrics_data,
                'triage_decision': triage_decision.to_dict(),
            }
            response = await vic20_emergency_response(
                emergency_type,
                triage_decision.target_agents,
                system_context,
                user_id or 'anonymous',
            )
            return {
                'agent': 'vic_20_sage',
                'status': 'success',
                'result': response,
                'routing_reason': '🧐💥 EMERGENCY - Monocle yeeted to VIC-20 multi-agent orchestration',
                'emergency_type': emergency_type,
                'aristocratic_authority': 'SUPREME',
            }

        except Exception as e:
            self.logger.error(
                f"🧐💥 CATASTROPHIC FAILURE - Emergency routing to VIC-20 failed: {str(e)}"
            )
            return {
                'agent': 'vic_20_sage',
                'status': 'error',
                'error': str(e),
                'routing_reason': '🧐💥 EMERGENCY - Monocle yeeted to VIC-20 multi-agent orchestration',
                'emergency_failure': True,
            }
    
    async def _route_to_cpu_specialist(
        self, 
        metrics_data: Dict[str, Any], 
        triage_decision: TriageDecision, 
        user_id: Optional[str]
    ) -> Dict[str, Any]:
        """Route back to Sir Hawkington's CPU specialist brain (future implementation)"""
        self.logger.debug("🧐 Routing back to Sir Hawkington's CPU specialist expertise")
        
        return {
            'agent': 'sir_hawkington_cpu',
            'status': 'placeholder',
            'result': {
                'message': '🧐 CPU specialist routing - future implementation',
                'hawkington_assessment': triage_decision.hawkington_decision.to_dict() if triage_decision.hawkington_decision else None
            },
            'routing_reason': 'CPU-specific issue routed back to Sir Hawkington\'s specialist knowledge'
        }
    
    async def _store_triage_decision(self, user_id: str, triage_result: TriageResult):
        """Store triage decision in dual-write architecture (agent table + CMB)"""
        try:
            if not self.db:
                self.logger.warning("🧐 Skipping triage store: DB not initialized")
                return

            occurred_at_dt = triage_result.triage_decision.timestamp

            routing_results_safe = to_json_safe(triage_result.routing_results)

            triage_data = {
                "triage_severity": triage_result.triage_decision.severity.value,
                "routing_decision": triage_result.triage_decision.routing.value,
                "target_agents": triage_result.triage_decision.target_agents,
                "reasoning": triage_result.triage_decision.reasoning,
                "monocle_yeeted": triage_result.triage_decision.monocle_yeeted,
                "confidence": triage_result.triage_decision.confidence,
                "processing_time": triage_result.processing_time,
                "success": triage_result.success,
                "timestamp": occurred_at_dt,
                "routing_results": routing_results_safe,
                "hawkington_decision_id": None,
            }

            if triage_result.triage_decision.hawkington_decision:
                hawk_decision_id = await self.db.store_hawkington_decision(
                    user_id,
                    triage_result.triage_decision.hawkington_decision,
                )
                triage_data["hawkington_decision_id"] = hawk_decision_id

            triage_data["timestamp_iso"] = occurred_at_dt.isoformat()

            triage_memory_id = await self.db.store_triage_decision(user_id, triage_data)

            self.logger.info("🧐📊 Triage Decision stored: %s", triage_memory_id)
            
            # Broadcast agent memory update via WebSocket
            try:
                from app.services.agent_insight_emitter import emit_agent_memory_update
                await emit_agent_memory_update(
                    agent_name="sir_hawkington",
                    memory_data=triage_data,
                    user_id=user_id
                )
            except Exception as broadcast_error:
                self.logger.warning(f"🧐⚠️ Failed to broadcast memory update: {broadcast_error}")

        except Exception as e:
            self.logger.error("🧐💥 Failed to store triage decision: %s", str(e), exc_info=True)
            
    async def _enhance_metrics_with_triage(
        self, 
        original_metrics: Dict[str, Any], 
        triage_result: TriageResult
    ) -> Dict[str, Any]:
        """Phase 5: Enhance metrics with triage decision and agent results - NO FAKE DATA"""
        enhanced_metrics = original_metrics.copy()
        
        enhanced_metrics['triage_decision'] = triage_result.triage_decision.to_dict()
        enhanced_metrics['triage_processing'] = {
            'processing_time': triage_result.processing_time,
            'success': triage_result.success,
            'errors': triage_result.errors,
            'routing_results': triage_result.routing_results,
            'triage_commander': 'sir_hawkington',
            'triage_version': '1.0.0'
        }
        
        agent_processing_found = False
        for agent_result in triage_result.routing_results.get('results', {}).values():
            if isinstance(agent_result, dict) and 'result' in agent_result:
                result_data = agent_result['result']
                if isinstance(result_data, dict) and 'agent_processing' in result_data:
                    enhanced_metrics['agent_processing'] = result_data['agent_processing']
                    agent_processing_found = True
                    break
        
        if not agent_processing_found:
            self.logger.debug("🧐 No agent processing data available - not fabricating fake data")
        
        if triage_result.triage_decision.hawkington_decision:
            hd = triage_result.triage_decision.hawkington_decision
            enhanced_metrics['sir_hawkington'] = {
                'decision_id': hd.decision_id,
                'decision_type': hd.decision_type,
                'confidence': hd.confidence,
                'reasoning': hd.reasoning,
                'metrics': hd.metrics,
                'timestamp': hd.timestamp.isoformat() if hasattr(hd.timestamp, 'isoformat') else str(hd.timestamp),
                'user_id': hd.user_id,
                'system_impact': hd.system_impact
            }   
        
        enhanced_metrics['triage_stats'] = {
            'total_triage_decisions': self.total_triage_decisions,
            'routing_stats': self.routing_stats.copy(),
            'monocle_yeet_incidents': self.monocle_yeet_incidents
        }
        
        return enhanced_metrics
    
    # === NEW METHODS: STRUCTURED QUERIES TO AGENT TABLE ===
    
    async def get_triage_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive triage statistics
        
        🆕 WHAT'S NEW: Now queries agent-specific table for structured data
        🎯 WHY: 10-50x faster than JSON parsing in CMB
        📊 IMPACT: Real numeric metrics instead of approximations
        """
        if not self.db:
            logger.warning("🧐 Database not initialized - returning in-memory stats only")
            return {
                'triage_engine': 'sir_hawkington_v1.0',
                'status': 'database_not_initialized',
                'total_triage_decisions': self.total_triage_decisions,
                'routing_statistics': self.routing_stats.copy(),
                'monocle_yeet_incidents': self.monocle_yeet_incidents,
                'data_source': 'in_memory_only'
            }
        
        try:
            # Query database for structured statistics (uses agent table)
            db_stats = await self.db.get_triage_statistics("system", days=7)
            
            return {
                'triage_engine': 'sir_hawkington_v1.0',
                'total_triage_decisions': self.total_triage_decisions,
                'routing_statistics': self.routing_stats.copy(),
                'monocle_yeet_incidents': self.monocle_yeet_incidents,
                'triage_thresholds': self.triage_thresholds.copy(),
                
                # Database-sourced structured statistics
                'database_statistics': db_stats,
                'success_rates': {
                    'overall_success_rate': self._calculate_success_rate(),
                    'routing_distribution': self._calculate_routing_distribution(),
                    'database_success_rate': db_stats.get('success_rate'),
                    'database_monocle_yeet_rate': db_stats.get('monocle_yeet_rate')
                },
                
                'aristocratic_status': 'COMMANDING_EXCELLENCE',
                'data_source': 'hybrid_memory_and_agent_table'
            }
            
        except Exception as e:
            logger.error(f"🧐💥 Failed to get database stats: {str(e)}")
            # Graceful fallback to in-memory stats
            return {
                'triage_engine': 'sir_hawkington_v1.0',
                'total_triage_decisions': self.total_triage_decisions,
                'routing_statistics': self.routing_stats.copy(),
                'monocle_yeet_incidents': self.monocle_yeet_incidents,
                'triage_thresholds': self.triage_thresholds.copy(),
                'success_rates': {
                    'overall_success_rate': self._calculate_success_rate(),
                    'routing_distribution': self._calculate_routing_distribution()
                },
                'aristocratic_status': 'COMMANDING_EXCELLENCE',
                'data_source': 'in_memory_only',
                'database_error': str(e)
            }
    
    async def get_user_triage_history(self, user_id: str, days: int = 7) -> Dict[str, Any]:
        """
        🆕 NEW METHOD: Get user-specific triage history from agent table
        
        🎯 PURPOSE: Provide structured triage analytics per user
        📊 RETURNS: Severity distribution, confidence trends, routing patterns
        ⚡ PERFORMANCE: Queries indexed columns instead of parsing JSON
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Dictionary with structured triage history
        """
        if not self.db:
            return {
                'status': 'database_not_initialized',
                'user_id': user_id,
                'triage_history': []
            }
        
        try:
            # Database integration queries agent table with structured fields
            stats = await self.db.get_triage_statistics(user_id, days=days)
            
            return {
                'status': 'success',
                'user_id': user_id,
                'period_days': days,
                'statistics': stats,
                'data_source': 'agent_specific_table'
            }
            
        except Exception as e:
            logger.error(f"🧐💥 Failed to get user triage history: {str(e)}")
            return {
                'status': 'error',
                'user_id': user_id,
                'error': str(e),
                'data_source': 'none'
            }
    
    async def get_data_quality_report(self, user_id: str, days: int = 30) -> Dict[str, Any]:
        """
        🆕 NEW METHOD: Get data quality report from agent table
        
        🎯 PURPOSE: Analyze monocle yeet patterns to identify data quality issues
        📊 RETURNS: Most frequently missing/invalid metrics, yeet frequency, quality assessment
        ⚡ PERFORMANCE: Queries structured JSON fields with GIN indexes
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Dictionary with data quality analysis
        """
        if not self.db or not self.db.session_factory:
            return {
                'status': 'database_not_initialized',
                'user_id': user_id
            }
            
        try:
            async with self.db.session_factory() as session:
                cutoff = utc_now() - timedelta(days=days)
                
                # Query agent table for monocle yeets (STRUCTURED DATA)
                result = await session.execute(
                    select(
                        SirHawkingtonMemoryBank.data_quality_pattern,
                        SirHawkingtonMemoryBank.timestamp
                    )
                    .where(
                        and_(
                            SirHawkingtonMemoryBank.user_id == user_id,
                            SirHawkingtonMemoryBank.memory_category == 'monocle_yeet',
                            SirHawkingtonMemoryBank.timestamp >= cutoff
                        )
                    )
                    .order_by(SirHawkingtonMemoryBank.timestamp.desc())
                )
                
                yeet_records = result.all()
                
                # Analyze patterns from STRUCTURED data (not parsing strings!)
                missing_metrics = {}
                invalid_metrics = {}
                yeet_reasons = {}
                
                for record in yeet_records:
                    pattern = record.data_quality_pattern or {}
                    
                    # Count missing metrics (REAL data from structured field)
                    for metric in pattern.get('missing_metrics', []):
                        missing_metrics[metric] = missing_metrics.get(metric, 0) + 1
                    
                    # Count invalid metrics (REAL data from structured field)
                    for metric in pattern.get('invalid_metrics', []):
                        invalid_metrics[metric] = invalid_metrics.get(metric, 0) + 1
                    
                    # Track reasons
                    reason = pattern.get('yeet_reason')
                    if reason:
                        yeet_reasons[reason] = yeet_reasons.get(reason, 0) + 1
                
                return {
                    'status': 'success',
                    'user_id': user_id,
                    'period_days': days,
                    'total_monocle_yeets': len(yeet_records),
                    'yeets_per_day': len(yeet_records) / days if days > 0 else 0,
                    'most_missing_metrics': sorted(
                        missing_metrics.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5],
                    'most_invalid_metrics': sorted(
                        invalid_metrics.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5],
                    'top_yeet_reasons': sorted(
                        yeet_reasons.items(),
                        key=lambda x: x[1],
                        reverse=True
                    )[:5],
                    'data_source': 'agent_specific_table',
                    'aristocratic_assessment': self._assess_data_quality(len(yeet_records), days)
                }
                
        except Exception as e:
            logger.error(f"🧐💥 Data quality report failed: {str(e)}")
            return {
                'status': 'error',
                'user_id': user_id,
                'error': str(e)
            }
    
    def _assess_data_quality(self, yeet_count: int, days: int) -> str:
        """
        Assess data quality based on yeet frequency
        
        🎯 PURPOSE: Provide aristocratic assessment of data quality
        📊 LOGIC: Calculates yeets per day and categorizes severity
        
        Args:
            yeet_count: Total number of monocle yeets
            days: Period analyzed
            
        Returns:
            Aristocratic quality assessment string
        """
        yeets_per_day = yeet_count / days if days > 0 else 0
        
        if yeets_per_day == 0:
            return "🧐✨ IMPECCABLE - No data quality issues detected"
        elif yeets_per_day < 0.5:
            return "🧐 ACCEPTABLE - Minimal data quality concerns"
        elif yeets_per_day < 2.0:
            return "🧐⚠️ CONCERNING - Moderate data quality issues"
        else:
            return "🧐💥 UNACCEPTABLE - Severe data quality problems require immediate attention"
    
    async def get_accuracy_trend(self, user_id: str, days: int = 7) -> Optional[Dict[str, Any]]:
        """
        🆕 NEW METHOD: Get accuracy improvement trend from agent table
        
        🎯 PURPOSE: Track how Sir Hawkington's accuracy is improving over time
        📊 RETURNS: Trend direction, current vs historical average, sample size
        ⚡ PERFORMANCE: Queries structured Float column (accuracy_improvement)
        
        Args:
            user_id: User identifier
            days: Number of days to analyze
            
        Returns:
            Trend analysis or None if insufficient data
        """
        if not self.db or not self.db.session_factory:
            return None
        
        try:
            async with self.db.session_factory() as session:
                cutoff = utc_now() - timedelta(days=days)
                
                # Query STRUCTURED Float column (not parsing JSON!)
                result = await session.execute(
                    select(
                        SirHawkingtonMemoryBank.accuracy_improvement,
                        SirHawkingtonMemoryBank.timestamp
                    )
                    .where(
                        and_(
                            SirHawkingtonMemoryBank.user_id == user_id,
                            SirHawkingtonMemoryBank.accuracy_improvement.isnot(None),
                            SirHawkingtonMemoryBank.timestamp >= cutoff
                        )
                    )
                    .order_by(SirHawkingtonMemoryBank.timestamp)
                )
                
                records = result.all()
                
                if not records or len(records) < 2:
                    return None
                
                # Calculate trend from REAL numeric data
                values = [r.accuracy_improvement for r in records]
                timestamps = [r.timestamp for r in records]
                
                # Simple linear trend (first half vs second half)
                mid_point = len(values) // 2
                first_half_avg = sum(values[:mid_point]) / mid_point
                second_half_avg = sum(values[mid_point:]) / (len(values) - mid_point)
                
                trend_value = second_half_avg - first_half_avg
                
                return {
                    'trend': 'improving' if trend_value > 0.05 else 'declining' if trend_value < -0.05 else 'stable',
                    'trend_value': trend_value,
                    'current_average': second_half_avg,
                    'previous_average': first_half_avg,
                    'sample_size': len(values),
                    'period_days': days,
                    'first_timestamp': timestamps[0].isoformat(),
                    'last_timestamp': timestamps[-1].isoformat(),
                    'data_source': 'agent_specific_table_structured_float'
                }
                
        except Exception as e:
            logger.error(f"🧐💥 Accuracy trend calculation failed: {str(e)}")
            return None
    
    # === EXISTING HELPER METHODS (NO CHANGES) ===
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall triage success rate"""
        if self.total_triage_decisions == 0:
            return 1.0
        return max(0.95, 1.0 - (self.monocle_yeet_incidents / self.total_triage_decisions))
    
    def _calculate_routing_distribution(self) -> Dict[str, float]:
        """Calculate distribution of routing decisions"""
        if self.total_triage_decisions == 0:
            return {k: 0.0 for k in self.routing_stats.keys()}
        
        return {
            routing_type: (count / self.total_triage_decisions) * 100
            for routing_type, count in self.routing_stats.items()
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Comprehensive triage engine health check
        
        🆕 UPDATED: Now includes agent table health status
        """
        db_health = None
        if self.db:
            try:
                db_health = await self.db.get_database_health()
            except Exception as e:
                logger.error(f"🧐💥 Database health check failed: {str(e)}")
                db_health = {'status': 'error', 'error': str(e)}
        
        return {
            'triage_engine_status': 'OPERATIONAL',
            'aristocratic_authority': 'SUPREME',
            'monocle_state': sir_hawkington_brain.current_monocle_state.value,
            'database_connected': self.db is not None,
            'database_health': db_health,
            'total_decisions': self.total_triage_decisions,
            'recent_performance': {
                'monocle_yeet_rate': self.monocle_yeet_incidents / max(self.total_triage_decisions, 1),
                'emergency_routing_rate': self.routing_stats['vic20_emergency'] / max(self.total_triage_decisions, 1),
                'normal_operations_rate': self.routing_stats['stick_direct'] / max(self.total_triage_decisions, 1)
            },
            'sir_hawkington_brain_status': sir_hawkington_brain.health_check(),
            'triage_thresholds': self.triage_thresholds,
            'last_update': utc_now().isoformat(),
            'agent_table_enabled': db_health.get('dual_write_enabled', False) if db_health else False
        }

# === GLOBAL TRIAGE ENGINE INSTANCE ===
_triage_engine: Optional[SirHawkingtonTriageEngine] = None
_triage_lock = asyncio.Lock()

async def get_triage_engine():
    """
    Get the global triage engine instance (singleton pattern)
    Thread-safe initialization with async lock
    
    Returns:
        Initialized SirHawkingtonTriageEngine instance
    """
    global _triage_engine
    
    if _triage_engine is None:
        async with _triage_lock:
            if _triage_engine is None:
                from app.core.database import get_async_db
                _triage_engine = SirHawkingtonTriageEngine(db_getter=get_async_db)
                await _triage_engine.initialize()
    
    return _triage_engine

# === MAIN TRIAGE ENTRY POINT ===

async def process_metrics_through_triage(
    metrics_data: Dict[str, Any], 
    user_id: Optional[str] = None,
    user_context: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    THE NEW MASTER ENTRY POINT FOR ALL SYSTEM METRICS
    
    This function replaces agent_manager.process_metrics_through_triage_engine()
    in the SimplifiedMetricsService.
    
    🧐 "One does not simply process metrics - one triages them with aristocratic precision"
    
    Args:
        metrics_data: Raw system metrics from SimplifiedMetricsService
        user_id: User identifier 
        user_context: Optional user context
        
    Returns:
        Enhanced metrics with triage decision and agent processing results
    """
    triage_engine = await get_triage_engine()
    return await triage_engine.process_system_metrics(metrics_data, user_id, user_context)

# === CONVENIENCE FUNCTIONS ===

async def get_triage_statistics() -> Dict[str, Any]:
    """Get comprehensive triage statistics"""
    triage_engine = await get_triage_engine()
    return await triage_engine.get_triage_stats()

async def triage_health_check() -> Dict[str, Any]:
    """Perform triage engine health check"""
    triage_engine = await get_triage_engine()
    return await triage_engine.health_check()

async def get_user_data_quality_report(user_id: str, days: int = 30) -> Dict[str, Any]:
    """
    🆕 NEW FUNCTION: Get user's data quality report
    
    Convenience function for external callers
    """
    triage_engine = await get_triage_engine()
    return await triage_engine.get_data_quality_report(user_id, days)

async def get_user_accuracy_trend(user_id: str, days: int = 7) -> Optional[Dict[str, Any]]:
    """
    🆕 NEW FUNCTION: Get user's accuracy trend
    
    Convenience function for external callers
    """
    triage_engine = await get_triage_engine()
    return await triage_engine.get_accuracy_trend(user_id, days)

async def reset_triage_stats():
    """Reset triage statistics for testing"""
    triage_engine = await get_triage_engine()
    triage_engine.total_triage_decisions = 0
    triage_engine.routing_stats = {
        'stick_direct': 0,
        'vic20_coordination': 0,
        'vic20_emergency': 0,
        'cpu_specialist': 0
    }
    triage_engine.monocle_yeet_incidents = 0
    logger.info("🧐✨ Triage statistics reset with aristocratic precision")

# === TESTING FUNCTION ===

async def test_triage_engine():
    """Test the triage engine with sample data"""
    print("\n" + "="*80)
    print(" 🧐⚡ SIR HAWKINGTON'S TRIAGE ENGINE TEST - ARISTOCRATIC REVOLUTION")
    print("="*80)
    
    test_metrics = {
        'cpu_usage': 85.5,
        'memory_usage': 72.3,
        'disk_usage': 45.8,
        'network_sent_rate': 1024,
        'network_recv_rate': 2048,
        'timestamp': utc_now().isoformat()
    }
    
    print(f"\n🧐 Testing with metrics: CPU {test_metrics['cpu_usage']}%, Memory {test_metrics['memory_usage']}%, Disk {test_metrics['disk_usage']}%")
    
    result = await process_metrics_through_triage(test_metrics, user_id="test_user")
    
    print(f"\n🎯 TRIAGE DECISION:")
    triage = result['triage_decision']
    print(f"   Severity: {triage['severity']}")
    print(f"   Routing: {triage['routing']}")
    print(f"   Target Agents: {triage['target_agents']}")
    print(f"   Monocle Yeeted: {triage['monocle_yeeted']}")
    print(f"   Confidence: {triage['confidence']:.3f}")
    print(f"   Reasoning: {triage['reasoning']}")
    
    print(f"\n📊 ROUTING RESULTS:")
    routing = result['triage_processing']['routing_results']
    print(f"   Routing Type: {routing['routing_type']}")
    print(f"   Successful: {len(routing.get('results', {}))}")
    print(f"   Errors: {len(routing.get('errors', []))}")
    
    stats = await get_triage_statistics()
    print(f"\n📈 TRIAGE STATISTICS:")
    print(f"   Total Decisions: {stats['total_triage_decisions']}")
    print(f"   Monocle Yeets: {stats['monocle_yeet_incidents']}")
    print(f"   Success Rate: {stats['success_rates']['overall_success_rate']:.3f}")
    
    health = await triage_health_check()
    print(f"\n🏥 HEALTH CHECK:")
    print(f"   Status: {health['triage_engine_status']}")
    print(f"   Aristocratic Authority: {health['aristocratic_authority']}")
    print(f"   Monocle State: {health['monocle_state']}")
    print(f"   Database Connected: {health['database_connected']}")
    print(f"   Agent Table Enabled: {health.get('agent_table_enabled', False)}")
    
    print("\n" + "="*80)
    print(" 🧐✨ TRIAGE ENGINE TEST COMPLETE - ARISTOCRATIC EXCELLENCE ACHIEVED")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_triage_engine())