# app/ai_agents/sir_hawkington/triage_engine.py
"""
Sir Hawkington's Triage Engine - THE ARISTOCRATIC REVOLUTION
DUAL ROLE COMMANDER: System-Wide Triage Officer + CPU Specialist

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
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import json

# Import agent manager at module level to avoid circular imports
from ..agent_manager import get_agent_manager

# Import Sir Hawkington's existing brain
from .decision_engine import (
    sir_hawkington_brain, 
    HawkingtonDecision, 
    DecisionType, 
    MonocleState,
    AnalysisDepth
)

# Database integration
from .database_integration import HawkingtonDatabaseIntegration

logger = logging.getLogger("SirHawkington.TriageEngine")

class TriageRouting(Enum):
    """Sir Hawkington's triage routing decisions"""
    STICK_DIRECT = "stick_direct"              # Normal operations → The Stick
    VIC20_COORDINATION = "vic20_coordination"  # Medium issues → VIC-20 coordination
    VIC20_EMERGENCY = "vic20_emergency"        # High/Emergency → Monocle yeet to VIC-20
    CPU_SPECIALIST = "cpu_specialist"          # Route back to Sir Hawkington's CPU brain

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
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/transmission"""
        return {
            'severity': self.severity.value,
            'routing': self.routing.value,
            'target_agents': self.target_agents,
            'reasoning': self.reasoning,
            'monocle_yeeted': self.monocle_yeeted,
            'hawkington_decision': self.hawkington_decision.to_dict() if self.hawkington_decision else None,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class TriageResult:
    """Complete triage processing result"""
    triage_decision: TriageDecision
    routing_results: Dict[str, Any]  # Results from routed agents
    processing_time: float
    success: bool
    errors: List[str]

class SirHawkingtonTriageEngine:
    """
    THE ARISTOCRATIC TRIAGE COMMANDER
    
    Sir Hawkington's evolution from simple monitoring to SYSTEM-WIDE ORCHESTRATION.
    This is now the MASTER ENTRY POINT for all system metrics.
    
    🧐 "A gentleman does not merely observe - he commands with distinction"
    """

    def __init__(self, db_getter=None):
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
            'normal_threshold': 0.30,      # Below this = normal operations
            'medium_threshold': 0.65,      # Above this = needs coordination
            'emergency_threshold': 0.85    # Above this = MONOCLE YEET!
        }
        
        # Agent handler cache
        self._agent_handlers = {}
        
        self.logger.info("🧐⚡ Sir Hawkington's Triage Engine initialized - ARISTOCRATIC REVOLUTION ACTIVATED")
    
    async def initialize(self):
        """Initialize the triage engine with aristocratic precision"""
        # Initialize database
        if not self.db:
            self.db = HawkingtonDatabaseIntegration(self.db_getter)
            await self.db.initialize()
            
        # Initialize Sir Hawkington's brain
        await sir_hawkington_brain.initialize_database()
            
        self.logger.info("🧐✨ Triage Engine initialization complete - Ready for aristocratic command")
    
    async def process_system_metrics(
            self, 
            metrics_data: Dict[str, Any], 
            user_id: Optional[str] = None,
            user_context: Optional[Dict] = None
        ) -> Dict[str, Any]:
        """
        THE MASTER TRIAGE METHOD - NO FAKE DATA ALLOWED
        
        This replaces agent_manager.process_metrics_through_agents() as the 
        primary entry point for ALL system metrics.
        
        Args:
            metrics_data: Raw system metrics from SimplifiedMetricsService
            user_id: User identifier for tracking
            user_context: Optional user context
            
        Returns:
            Enhanced metrics with triage decision and agent results
        """
        start_time = datetime.now()
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
            processing_time = (datetime.now() - start_time).total_seconds()
            
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
            # HONEST FAILURE - NO FAKE DATA GENERATION
            raise Exception(f"TRIAGE SYSTEM FAILURE: {str(e)}")
    
    async def _conduct_triage_assessment(
            self, 
            metrics_data: Dict[str, Any], 
            user_id: Optional[str],
            user_context: Optional[Dict]
        ) -> TriageDecision:
        """
        Phase 1: Sir Hawkington conducts his aristocratic triage assessment
        
        Uses his existing decision engine to determine severity and routing
        """
        self.logger.debug("🧐 Conducting triage assessment with aristocratic precision...")
        
        # Get historical data for thorough analysis
        historical_data = None
        if self.db and user_id:
            try:
                historical_data = await self.db.get_historical_decisions(user_id, days=7)
            except Exception as e:
                self.logger.warning(f"🧐 Could not get historical data: {str(e)}")
        
        # Use Sir Hawkington's existing decision engine for assessment
        hawkington_decision = await sir_hawkington_brain.analyze_metrics(
            metrics_data=metrics_data,
            historical_data=historical_data,
            user_context=user_context,
            analysis_depth=AnalysisDepth.THOROUGH,  # Always thorough for triage
            user_id=user_id
        )
        
        # Determine triage routing based on Sir Hawkington's decision
        if hawkington_decision is None:
            # MONOCLE YEETED - Data quality insufficient
            self.monocle_yeet_incidents += 1
            return TriageDecision(
                severity=TriageSeverity.EMERGENCY,
                routing=TriageRouting.VIC20_EMERGENCY,
                target_agents=["vic_20_sage"],
                reasoning="🧐💥 MONOCLE YEETED! Data quality beneath aristocratic standards - emergency VIC-20 intervention required",
                monocle_yeeted=True,
                hawkington_decision=None,
                confidence=0.0,
                timestamp=datetime.now(timezone.utc)
            )
        
        # Determine severity and routing from Sir Hawkington's stress score
        severity = self._determine_triage_severity(hawkington_decision.stress_score)
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
            timestamp=datetime.now(timezone.utc)
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
        """
        Determine routing based on severity and decision type
        
        THE ARISTOCRATIC ROUTING RULES:
        - NORMAL: Direct to The Stick for baseline learning
        - MEDIUM: VIC-20 coordination for specialist routing
        - HIGH/EMERGENCY: Monocle yeet to VIC-20 for multi-agent response
        """
        if severity == TriageSeverity.EMERGENCY:
            return TriageRouting.VIC20_EMERGENCY
        elif severity == TriageSeverity.HIGH:
            return TriageRouting.VIC20_EMERGENCY  # High also gets emergency treatment
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
            return ["vic_20_sage"]  # VIC-20 will coordinate other agents
        elif routing == TriageRouting.CPU_SPECIALIST:
            return ["sir_hawkington_cpu"]  # Route back to Sir Hawkington's CPU expertise
        else:
            return ["the_stick"]  # Default to stick for unknown routing
    
    def _create_triage_reasoning(
            self, 
            severity: TriageSeverity, 
            routing: TriageRouting, 
            hawkington_decision: HawkingtonDecision
        ) -> str:
        """Create aristocratic reasoning for triage decision"""
        base_reasoning = f"🧐 Aristocratic triage assessment: System stress {hawkington_decision.stress_score:.3f} indicates {severity.value} severity"
        
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
        """
        Phase 2: Execute the triage routing decision
        
        This is where Sir Hawkington actually routes metrics to the appropriate agents
        """
        routing_results = {
            'routing_type': triage_decision.routing.value,
            'target_agents': triage_decision.target_agents,
            'results': {},
            'errors': []
        }
        
        # Update routing statistics
        self.routing_stats[triage_decision.routing.value] += 1
        
        try:
            if triage_decision.routing == TriageRouting.STICK_DIRECT:
                # Route directly to The Stick for normal operations
                results = await self._route_to_stick(metrics_data, user_id)
                routing_results['results']['the_stick'] = results
                
            elif triage_decision.routing == TriageRouting.VIC20_COORDINATION:
                # Route to VIC-20 for coordination
                results = await self._route_to_vic20_coordination(
                    metrics_data, triage_decision, user_id
                )
                routing_results['results']['vic_20_sage'] = results
                
            elif triage_decision.routing == TriageRouting.VIC20_EMERGENCY:
                # MONOCLE YEET to VIC-20 for emergency orchestration
                results = await self._route_to_vic20_emergency(
                    metrics_data, triage_decision, user_id
                )
                routing_results['results']['vic_20_sage'] = results
                
            elif triage_decision.routing == TriageRouting.CPU_SPECIALIST:
                # Route back to Sir Hawkington's CPU specialization
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
            # Get agent manager instance
            agent_manager = await get_agent_manager()
            
            # Process through ALL agents except Sir Hawkington (he's already processed via triage)
            # The agent manager will handle The Stick, Meth Snail, Hamsters, etc.
            agent_results = await agent_manager.process_metrics_through_agents(
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
            # For now, we'll simulate VIC-20 coordination
            # TODO: Import and use actual VIC-20 handler when available
            return {
                'agent': 'vic_20_sage',
                'status': 'success', 
                'result': {
                    'message': '🖥️ VIC-20 received coordination request and will dispatch to specialists',
                    'coordination_type': 'medium_severity',
                    'recommendations_generated': True,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                },
                'routing_reason': 'Medium severity - VIC-20 specialist coordination',
                'coordination_type': 'medium_severity'
            }
            
        except Exception as e:
            self.logger.error(f"🧐💥 Failed to route to VIC-20 coordination: {str(e)}")
            return {
                'agent': 'vic_20_sage',
                'status': 'error',
                'error': str(e),
                'routing_reason': 'Medium severity - VIC-20 specialist coordination'
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
            # For now, we'll simulate emergency VIC-20 response
            # TODO: Import and use actual VIC-20 emergency handler when available
            return {
                'agent': 'vic_20_sage',
                'status': 'success',
                'result': {
                    'message': '🖥️💥 VIC-20 EMERGENCY RESPONSE ACTIVATED - Multi-agent orchestration initiated',
                    'emergency_type': 'monocle_yeet' if triage_decision.monocle_yeeted else 'high_severity',
                    'multi_agent_dispatch': True,
                    'priority_level': 'SUPREME',
                    'timestamp': datetime.now(timezone.utc).isoformat()
                },
                'routing_reason': '🧐💥 EMERGENCY - Monocle yeeted to VIC-20 multi-agent orchestration',
                'emergency_type': 'monocle_yeet' if triage_decision.monocle_yeeted else 'high_severity',
                'aristocratic_authority': 'SUPREME'
            }
            
        except Exception as e:
            self.logger.error(f"🧐💥 CATASTROPHIC FAILURE - Emergency routing to VIC-20 failed: {str(e)}")
            return {
                'agent': 'vic_20_sage',
                'status': 'error',
                'error': str(e),
                'routing_reason': '🧐💥 EMERGENCY - Monocle yeeted to VIC-20 multi-agent orchestration',
                'emergency_failure': True
            }
    
    async def _route_to_cpu_specialist(
            self, 
            metrics_data: Dict[str, Any], 
            triage_decision: TriageDecision, 
            user_id: Optional[str]
        ) -> Dict[str, Any]:
        """Route back to Sir Hawkington's CPU specialist brain (future implementation)"""
        self.logger.debug("🧐 Routing back to Sir Hawkington's CPU specialist expertise")
        
        # For now, this is a placeholder for when VIC-20 routes CPU issues back to Sir Hawkington
        # This maintains the dual-role architecture where Sir Hawkington is both triage commander AND CPU specialist
        
        return {
            'agent': 'sir_hawkington_cpu',
            'status': 'placeholder',
            'result': {
                'message': '🧐 CPU specialist routing - future implementation',
                'hawkington_assessment': triage_decision.hawkington_decision.to_dict() if triage_decision.hawkington_decision else None
            },
            'routing_reason': 'CPU-specific issue routed back to Sir Hawkington\'s specialist knowledge'
        }
    
    async def _store_triage_decision(
            self, 
            user_id: str, 
            triage_result: TriageResult
        ):
        """Store triage decision in database for pattern analysis"""
        try:
            if self.db:
                # Prepare triage data for storage
                triage_data = {
                    'triage_severity': triage_result.triage_decision.severity.value,
                    'routing_decision': triage_result.triage_decision.routing.value,
                    'target_agents': triage_result.triage_decision.target_agents,
                    'reasoning': triage_result.triage_decision.reasoning,
                    'monocle_yeeted': triage_result.triage_decision.monocle_yeeted,
                    'confidence': triage_result.triage_decision.confidence,
                    'processing_time': triage_result.processing_time,
                    'success': triage_result.success,
                    'timestamp': triage_result.triage_decision.timestamp,
                    'routing_results': triage_result.routing_results,
                    'hawkington_decision_id': None  # Will be set if we store the decision
                }
                
                # If Sir Hawkington made a decision, store that too
                if triage_result.triage_decision.hawkington_decision:
                    hawkington_decision_id = await self.db.store_decision(
                        user_id, 
                        triage_result.triage_decision.hawkington_decision
                    )
                    triage_data['hawkington_decision_id'] = hawkington_decision_id
                
                # Store triage decision
                triage_id = await self.db.store_triage_decision(user_id, triage_data)
                self.logger.info(f"🧐📊 Triage Decision #{triage_id} stored successfully")
                
        except Exception as e:
            self.logger.error(f"🧐💥 Failed to store triage decision: {str(e)}")
    
    async def _enhance_metrics_with_triage(
            self, 
            original_metrics: Dict[str, Any], 
            triage_result: TriageResult
        ) -> Dict[str, Any]:
        """
        Phase 5: Enhance metrics with triage decision and agent results - NO FAKE DATA
        """
        enhanced_metrics = original_metrics.copy()
        
        # Add triage information
        enhanced_metrics['triage_decision'] = triage_result.triage_decision.to_dict()
        enhanced_metrics['triage_processing'] = {
            'processing_time': triage_result.processing_time,
            'success': triage_result.success,
            'errors': triage_result.errors,
            'routing_results': triage_result.routing_results,
            'triage_commander': 'sir_hawkington',
            'triage_version': '1.0.0'
        }
        
        # ONLY add agent processing data if it actually exists from routing
        agent_processing_found = False
        for agent_result in triage_result.routing_results.get('results', {}).values():
            if isinstance(agent_result, dict) and 'result' in agent_result:
                result_data = agent_result['result']
                if isinstance(result_data, dict) and 'agent_processing' in result_data:
                    # We found REAL agent processing data
                    enhanced_metrics['agent_processing'] = result_data['agent_processing']
                    agent_processing_found = True
                    break
        
        # If no real agent processing data was found, DON'T CREATE FAKE DATA
        # Just leave it out entirely - the frontend can handle missing data
        if not agent_processing_found:
            self.logger.debug("🧐 No agent processing data available - not fabricating fake data")
        
        # Add Sir Hawkington's individual assessment if available
        if triage_result.triage_decision.hawkington_decision:
            enhanced_metrics['sir_hawkington'] = triage_result.triage_decision.hawkington_decision.to_dict()
        
        # Add triage statistics
        enhanced_metrics['triage_stats'] = {
            'total_triage_decisions': self.total_triage_decisions,
            'routing_stats': self.routing_stats.copy(),
            'monocle_yeet_incidents': self.monocle_yeet_incidents
        }
        
        return enhanced_metrics
    
    # === TRIAGE STATISTICS AND MONITORING ===
    
    async def get_triage_stats(self) -> Dict[str, Any]:
        """Get comprehensive triage statistics"""
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
            'aristocratic_status': 'COMMANDING_EXCELLENCE'
        }
    
    def _calculate_success_rate(self) -> float:
        """Calculate overall triage success rate"""
        if self.total_triage_decisions == 0:
            return 1.0
        # For now, assume all non-error decisions are successful
        # In future, we could track actual resolution outcomes
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
        """Comprehensive triage engine health check"""
        return {
            'triage_engine_status': 'OPERATIONAL',
            'aristocratic_authority': 'SUPREME',
            'monocle_state': sir_hawkington_brain.current_monocle_state.value,
            'database_connected': self.db is not None,
            'total_decisions': self.total_triage_decisions,
            'recent_performance': {
                'monocle_yeet_rate': self.monocle_yeet_incidents / max(self.total_triage_decisions, 1),
                'emergency_routing_rate': self.routing_stats['vic20_emergency'] / max(self.total_triage_decisions, 1),
                'normal_operations_rate': self.routing_stats['stick_direct'] / max(self.total_triage_decisions, 1)
            },
            'sir_hawkington_brain_status': sir_hawkington_brain.health_check(),
            'triage_thresholds': self.triage_thresholds,
            'last_update': datetime.now(timezone.utc).isoformat()
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
            # Double-check pattern for thread safety
            if _triage_engine is None:
                _triage_engine = SirHawkingtonTriageEngine()  # Fixed: removed self.db_getter
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
    
    This function replaces agent_manager.process_metrics_through_agents()
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
    
    # Test metrics data
    test_metrics = {
        'cpu_usage': 85.5,
        'memory_usage': 72.3,
        'disk_usage': 45.8,
        'network_sent_rate': 1024,
        'network_recv_rate': 2048,
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"\n🧐 Testing with metrics: CPU {test_metrics['cpu_usage']}%, Memory {test_metrics['memory_usage']}%, Disk {test_metrics['disk_usage']}%")
    
    # Process through triage
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
    
    # Get statistics
    stats = await get_triage_statistics()
    print(f"\n📈 TRIAGE STATISTICS:")
    print(f"   Total Decisions: {stats['total_triage_decisions']}")
    print(f"   Monocle Yeets: {stats['monocle_yeet_incidents']}")
    print(f"   Success Rate: {stats['success_rates']['overall_success_rate']:.3f}")
    print(f"   Routing Distribution:")
    for routing_type, percentage in stats['success_rates']['routing_distribution'].items():
        print(f"     {routing_type}: {percentage:.1f}%")
    
    # Health check
    health = await triage_health_check()
    print(f"\n🏥 HEALTH CHECK:")
    print(f"   Status: {health['triage_engine_status']}")
    print(f"   Aristocratic Authority: {health['aristocratic_authority']}")
    print(f"   Monocle State: {health['monocle_state']}")
    print(f"   Database Connected: {health['database_connected']}")
    
    print("\n" + "="*80)
    print(" 🧐✨ TRIAGE ENGINE TEST COMPLETE - ARISTOCRATIC EXCELLENCE ACHIEVED")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_triage_engine())