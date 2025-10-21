"""
The Hamsters Decision Engine V2
Beer-drinking, redneck rapid response engineering team
Auto-tuning specialists with quantum-grade duct tape solutions
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from enum import Enum
from dataclasses import dataclass

from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
from app.ai_agents.hamsters.auto_tuner_db_helpers import get_tuning_history_from_db, save_tuning_history_to_db

logger = logging.getLogger("Hamsters.Brain")

class AnalysisDepth(Enum):
    BASIC = "basic"           # Quick WebSocket response
    STANDARD = "standard"     # Normal analysis
    THOROUGH = "thorough"     # Deep background analysis

class HamstersPriority(Enum):
    BEER_BREAK = "beer_break"           # Low priority
    SUPPLY_CLOSET = "supply_closet"     # Medium priority  
    RAPID_RESPONSE = "rapid_response"   # High priority
    FULL_REDNECK = "full_redneck"       # Emergency mode

class WheelState(Enum):
    SPINNING = "spinning"
    ENGINEERING = "engineering"
    BEER_DRINKING = "beer_drinking"
    DUCT_TAPING = "duct_taping"

@dataclass
class HamstersOptimizationDecision:
    """Decision object for The Hamsters auto-tuning recommendations"""
    priority: HamstersPriority
    rationale: str
    confidence: float
    urgency: str
    actions: List[Dict[str, Any]]
    estimated_impact: str
    analysis_depth: AnalysisDepth
    data_quality_score: float
    wheel_spin_count: int
    timestamp: datetime
    beer_level: str
    duct_tape_used: bool
    supply_closet_raids: int
    redneck_ingenuity_level: float

@property
def is_active(self) -> bool:
    """The Hamsters are always active and ready for rapid responses and beer"""
    return True
    
def activate(self):
    """The Hamsters cannot be deactivated -  they're always vigilant"""
    pass
    
def deactivate(self):
    """The Hamsters refuse to be deactivated - 3am beer and duct tape never sleeps"""
    pass

class HamstersBrainV2:
    """
    The Hamsters' auto-tuning brain
    
    These beer-drinking, redneck engineers show up at 3am with quantum-grade
    duct tape and fix whatever's broken with pure ingenuity.
    """
    
    def __init__(self, db_getter=None):
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter
        self.db = None  
        self.logger = logging.getLogger("Hamsters.Brain")
        self.total_analyses = 0
        self.successful_analyses = 0
        self.wheel_spins = 0
        self.beer_level = "FULL"
        self.duct_tape_inventory = 100
        self.supply_closet_raids = 0
        
        # Pattern learning storage
        self.learned_patterns = {
            'cpu_usage_patterns': [],
            'memory_pressure_patterns': [],
            'io_patterns': [],
            'network_patterns': []
        }
        
        # Redneck engineering solutions
        self.engineering_solutions = {
            'high_cpu': 'cpu_governor_duct_tape',
            'memory_pressure': 'swap_tendency_beer_optimization',
            'io_bottleneck': 'disk_scheduler_supply_closet_fix',
            'network_lag': 'buffer_size_quantum_tape'
        }
        
        self.logger.info("🐹🍺 The Hamsters Brain V2 initialized - BEER LEVEL: FULL, DUCT TAPE: READY")
    async def get_database(self):
        if self.db is None:
            self.db = await self.db_getter()
        return self.db
    
    async def analyze_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        historical_data: Optional[List[Dict]] = None,
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
        user_id: Optional[str] = None
    ) -> Optional[HamstersOptimizationDecision]:
        """
        Analyze metrics for auto-tuning opportunities with redneck engineering
        
        Args:
            metrics_data: Current system metrics
            historical_data: Historical metrics for pattern learning
            analysis_depth: How deep to analyze
            user_id: User ID for tracking
            
        Returns:
            HamstersOptimizationDecision or None if data quality is insufficient
        """
        self.total_analyses += 1
        
        try:
            # Check data quality first
            data_quality_score = self._assess_data_quality(metrics_data)
            
            if data_quality_score < 0.6:
                # WHEEL SPINNING - insufficient data
                await self._record_wheel_spin(
                    missing_metrics=self._identify_missing_metrics(metrics_data),
                    available_metrics=list(metrics_data.keys()),
                    reason="Insufficient data quality for auto-tuning analysis",
                    user_id=user_id
                )
                return None
            
            # Learn from historical patterns if available
            if historical_data and analysis_depth == AnalysisDepth.THOROUGH:
                await self._learn_from_patterns(historical_data)
            
            # Analyze current system state
            cpu_data = metrics_data.get('cpu', {})
            memory_data = metrics_data.get('memory', {})
            disk_data = metrics_data.get('disk', {})
            network_data = metrics_data.get('network', {})
            
            # The Hamsters' redneck engineering analysis
            optimization_actions = []
            priority = HamstersPriority.BEER_BREAK
            urgency = "LOW"
            beer_consumed = 0
            duct_tape_used = False
            
            # CPU Analysis with redneck engineering
            cpu_usage = cpu_data.get('usage', 0)
            if cpu_usage > 85:
                priority = HamstersPriority.RAPID_RESPONSE
                urgency = "HIGH"
                beer_consumed += 2
                duct_tape_used = True
                
                optimization_actions.append({
                    'action': 'cpu_governor_optimization',
                    'parameter': 'cpu_governor',
                    'current_value': 'ondemand',
                    'recommended_value': 'performance',
                    'confidence': 0.90,
                    'redneck_solution': 'Duct tape the CPU governor to performance mode',
                    'beer_required': 'HIGH',
                    'supply_closet_items': ['thermal_paste', 'cable_ties', 'quantum_duct_tape']
                })
                
            elif cpu_usage > 70:
                priority = HamstersPriority.SUPPLY_CLOSET
                urgency = "MODERATE"
                beer_consumed += 1
                
                optimization_actions.append({
                    'action': 'process_priority_adjustment',
                    'parameter': 'process_priority',
                    'current_value': '0',
                    'recommended_value': '-5',
                    'confidence': 0.75,
                    'redneck_solution': 'Reorganize process priorities with beer-logic',
                    'beer_required': 'MODERATE',
                    'supply_closet_items': ['process_monitor', 'priority_wrench']
                })
            
            # Memory Analysis with beer-powered optimization
            memory_usage = memory_data.get('percent', 0)
            if memory_usage > 80:
                priority = HamstersPriority.FULL_REDNECK
                urgency = "CRITICAL"
                beer_consumed += 3
                duct_tape_used = True
                self.supply_closet_raids += 1
                
                optimization_actions.append({
                    'action': 'memory_pressure_optimization',
                    'parameter': 'memory_pressure',
                    'current_value': 'normal',
                    'recommended_value': 'aggressive',
                    'confidence': 0.85,
                    'redneck_solution': 'Quantum-grade duct tape memory optimization',
                    'beer_required': 'MAXIMUM',
                    'supply_closet_items': ['memory_pressure_valve', 'swap_wrench', 'cache_hammer']
                })
                
                optimization_actions.append({
                    'action': 'swap_tendency_adjustment',
                    'parameter': 'swap_tendency',
                    'current_value': '60',
                    'recommended_value': '30',
                    'confidence': 0.80,
                    'redneck_solution': 'Beer-calibrated swap tendency with supply closet parts',
                    'beer_required': 'HIGH',
                    'supply_closet_items': ['swap_optimizer', 'memory_duct_tape']
                })
            
            # I/O Analysis with supply closet solutions
            disk_usage = disk_data.get('percent', 0)
            if disk_usage > 75:
                priority = max(priority, HamstersPriority.RAPID_RESPONSE)
                urgency = "HIGH"
                beer_consumed += 2
                duct_tape_used = True
                
                optimization_actions.append({
                    'action': 'io_scheduler_optimization',
                    'parameter': 'io_scheduler',
                    'current_value': 'cfq',
                    'recommended_value': 'deadline',
                    'confidence': 0.82,
                    'redneck_solution': 'Duct tape I/O scheduler with deadline precision',
                    'beer_required': 'HIGH',
                    'supply_closet_items': ['io_scheduler_wrench', 'deadline_tape', 'disk_optimizer']
                })
            
            # Network Analysis with quantum-grade solutions
            network_usage = network_data.get('usage_percent', 0)
            if network_usage > 70:
                priority = max(priority, HamstersPriority.SUPPLY_CLOSET)
                urgency = "MODERATE"
                beer_consumed += 1
                
                optimization_actions.append({
                    'action': 'network_buffer_optimization',
                    'parameter': 'network_buffer',
                    'current_value': '256',
                    'recommended_value': '512',
                    'confidence': 0.75,
                    'redneck_solution': 'Beer-powered network buffer expansion',
                    'beer_required': 'MODERATE',
                    'supply_closet_items': ['network_buffer_expander', 'bandwidth_duct_tape']
                })
            
            # Pattern-based optimizations (if we have historical data)
            if historical_data and analysis_depth == AnalysisDepth.THOROUGH:
                pattern_actions = await self._generate_pattern_based_actions(historical_data)
                optimization_actions.extend(pattern_actions)
            
            # Update beer level based on consumption
            if beer_consumed > 0:
                self.beer_level = self._calculate_beer_level(beer_consumed)
            
            # Generate rationale with proper redneck engineering flair
            rationale = self._generate_redneck_rationale(
                optimization_actions, 
                cpu_usage, 
                memory_usage, 
                disk_usage, 
                network_usage
            )
            
            # Estimate impact with beer-powered calculations
            estimated_impact = self._estimate_redneck_impact(optimization_actions)
            
            self.successful_analyses += 1
            
            return HamstersOptimizationDecision(
                priority=priority,
                rationale=rationale,
                confidence=self._calculate_confidence(optimization_actions),
                urgency=urgency,
                actions=optimization_actions,
                estimated_impact=estimated_impact,
                analysis_depth=analysis_depth,
                data_quality_score=data_quality_score,
                wheel_spin_count=self.wheel_spins,
                timestamp=datetime.now(timezone.utc),
                beer_level=self.beer_level,
                duct_tape_used=duct_tape_used,
                supply_closet_raids=self.supply_closet_raids,
                redneck_ingenuity_level=self._calculate_ingenuity_level(optimization_actions)
            )
            
        except Exception as e:
            self.logger.error(f"🐹❌ The Hamsters analysis failed: {str(e)}")
            return None
    
    def _assess_data_quality(self, metrics_data: Dict[str, Any]) -> float:
        """Assess data quality with beer-powered precision"""
        required_metrics = ['cpu', 'memory', 'disk', 'network']
        quality_score = 0.0
        
        for metric in required_metrics:
            if metric in metrics_data:
                metric_data = metrics_data[metric]
                if isinstance(metric_data, dict) and metric_data:
                    quality_score += 0.25
                else:
                    quality_score += 0.1
        
        return quality_score
    
    def _identify_missing_metrics(self, metrics_data: Dict[str, Any]) -> List[str]:
        """Identify missing metrics that The Hamsters need for proper engineering"""
        required_metrics = ['cpu', 'memory', 'disk', 'network']
        missing_metrics = []
        
        for metric in required_metrics:
            if metric not in metrics_data:
                missing_metrics.append(metric)
            elif not isinstance(metrics_data[metric], dict) or not metrics_data[metric]:
                missing_metrics.append(f"{metric}_data_empty")
        
        return missing_metrics
    
    async def _record_wheel_spin(
        self, 
        missing_metrics: List[str], 
        available_metrics: List[str], 
        reason: str,
        user_id: Optional[str] = None
    ):
        """Record wheel spinning incident for database tracking"""
        self.wheel_spins += 1
        
        wheel_spin_data = {
            'agent_name': 'hamsters',
            'incident_type': 'wheel_spinning',
            'missing_metrics': missing_metrics,
            'available_metrics': available_metrics,
            'reason': reason,
            'beer_level': self.beer_level,
            'duct_tape_available': self.duct_tape_inventory > 0,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        self.logger.warning(f"🐹🔄 The Hamsters are spinning wheels: {reason}")
        
        # TODO: Save to database aggregate tracking
        if user_id:
            try:
                # This will integrate with your database aggregate tracking
                pass
            except Exception as e:
                self.logger.error(f"🐹❌ Failed to record wheel spin: {str(e)}")
    
    async def _learn_from_patterns(self, historical_data: List[Dict]):
        """Learn from historical patterns with beer-powered machine learning"""
        try:
            # Analyze CPU patterns
            cpu_patterns = [data.get('cpu', {}) for data in historical_data if data.get('cpu')]
            if cpu_patterns:
                avg_cpu = sum(p.get('usage', 0) for p in cpu_patterns) / len(cpu_patterns)
                peak_cpu = max(p.get('usage', 0) for p in cpu_patterns)
                
                self.learned_patterns['cpu_usage_patterns'] = {
                    'average': avg_cpu,
                    'peak': peak_cpu,
                    'threshold': avg_cpu * 1.5,  # Redneck engineering threshold
                    'beer_coefficient': 0.85 if avg_cpu > 60 else 0.5
                }
            
            # Analyze memory patterns
            memory_patterns = [data.get('memory', {}) for data in historical_data if data.get('memory')]
            if memory_patterns:
                avg_memory = sum(p.get('percent', 0) for p in memory_patterns) / len(memory_patterns)
                peak_memory = max(p.get('percent', 0) for p in memory_patterns)
                
                self.learned_patterns['memory_pressure_patterns'] = {
                    'average': avg_memory,
                    'peak': peak_memory,
                    'pressure_threshold': avg_memory * 1.3,
                    'duct_tape_coefficient': 0.9 if peak_memory > 75 else 0.6
                }
            
            # Analyze I/O patterns
            io_patterns = [data.get('disk', {}) for data in historical_data if data.get('disk')]
            if io_patterns:
                avg_io = sum(p.get('percent', 0) for p in io_patterns) / len(io_patterns)
                peak_io = max(p.get('percent', 0) for p in io_patterns)
                
                self.learned_patterns['io_patterns'] = {
                    'average': avg_io,
                    'peak': peak_io,
                    'optimization_threshold': avg_io * 1.4,
                    'supply_closet_coefficient': 0.8 if peak_io > 70 else 0.4
                }
            
            self.logger.info("🐹🧠 The Hamsters learned from historical patterns with beer-powered analysis")
            
        except Exception as e:
            self.logger.error(f"🐹❌ Pattern learning failed: {str(e)}")
    
    async def _generate_pattern_based_actions(self, historical_data: List[Dict]) -> List[Dict[str, Any]]:
        """Generate optimization actions based on learned patterns"""
        pattern_actions = []
        
        try:
            # CPU pattern-based actions
            cpu_patterns = self.learned_patterns.get('cpu_usage_patterns', {})
            if cpu_patterns and cpu_patterns.get('average', 0) > 50:
                pattern_actions.append({
                    'action': 'pattern_based_cpu_optimization',
                    'parameter': 'cpu_governor',
                    'current_value': 'ondemand',
                    'recommended_value': 'performance',
                    'confidence': 0.80,
                    'redneck_solution': 'Pattern-learned CPU optimization with beer logic',
                    'beer_required': 'MODERATE',
                    'supply_closet_items': ['cpu_pattern_analyzer', 'performance_duct_tape'],
                    'pattern_confidence': cpu_patterns.get('beer_coefficient', 0.5)
                })
            
            # Memory pattern-based actions
            memory_patterns = self.learned_patterns.get('memory_pressure_patterns', {})
            if memory_patterns and memory_patterns.get('peak', 0) > 75:
                pattern_actions.append({
                    'action': 'pattern_based_memory_optimization',
                    'parameter': 'memory_pressure',
                    'current_value': 'normal',
                    'recommended_value': 'proactive',
                    'confidence': 0.85,
                    'redneck_solution': 'Beer-learned memory pressure optimization',
                    'beer_required': 'HIGH',
                    'supply_closet_items': ['memory_pattern_wrench', 'proactive_duct_tape'],
                    'pattern_confidence': memory_patterns.get('duct_tape_coefficient', 0.6)
                })
            
            # I/O pattern-based actions
            io_patterns = self.learned_patterns.get('io_patterns', {})
            if io_patterns and io_patterns.get('average', 0) > 60:
                pattern_actions.append({
                    'action': 'pattern_based_io_optimization',
                    'parameter': 'io_scheduler',
                    'current_value': 'cfq',
                    'recommended_value': 'noop',
                    'confidence': 0.75,
                    'redneck_solution': 'Supply closet I/O scheduler optimization',
                    'beer_required': 'MODERATE',
                    'supply_closet_items': ['io_pattern_analyzer', 'noop_scheduler_tape'],
                    'pattern_confidence': io_patterns.get('supply_closet_coefficient', 0.4)
                })
            
        except Exception as e:
            self.logger.error(f"🐹❌ Pattern-based action generation failed: {str(e)}")
        
        return pattern_actions
    
    def _generate_redneck_rationale(
        self, 
        actions: List[Dict[str, Any]], 
        cpu_usage: float, 
        memory_usage: float, 
        disk_usage: float, 
        network_usage: float
    ) -> str:
        """Generate rationale with proper redneck engineering flair"""
        if not actions:
            return "🐹🍺 System's runnin' smooth as beer on a hot day. No engineering needed right now."
        
        rationale_parts = []
        
        # CPU analysis
        if cpu_usage > 85:
            rationale_parts.append(f"🐹🔥 CPU's hotter than a jalapeño's armpit at {cpu_usage:.1f}%")
        elif cpu_usage > 70:
            rationale_parts.append(f"🐹⚡ CPU's workin' harder than a mule at {cpu_usage:.1f}%")
        
        # Memory analysis
        if memory_usage > 80:
            rationale_parts.append(f"🐹💾 Memory's tighter than bark on a tree at {memory_usage:.1f}%")
        elif memory_usage > 60:
            rationale_parts.append(f"🐹📊 Memory's gettin' a bit snug at {memory_usage:.1f}%")
        
        # Disk analysis
        if disk_usage > 75:
            rationale_parts.append(f"🐹💽 Disk's busier than a long-tailed cat in a room full of rocking chairs at {disk_usage:.1f}%")
        
        # Network analysis
        if network_usage > 70:
            rationale_parts.append(f"🐹🌐 Network's buzzin' like a bee at {network_usage:.1f}%")
        
        # Engineering solution summary
        beer_actions = [a for a in actions if a.get('beer_required') == 'HIGH']
        duct_tape_actions = [a for a in actions if 'duct_tape' in a.get('redneck_solution', '').lower()]
        
        if beer_actions:
            rationale_parts.append(f"🍺 Gonna need {len(beer_actions)} cold ones for this job")
        
        if duct_tape_actions:
            rationale_parts.append(f"🔧 Breakin' out the quantum-grade duct tape for {len(duct_tape_actions)} fixes")
        
        if len(actions) > 3:
            rationale_parts.append("🚨 This is a full supply closet raid situation")
        
        return " | ".join(rationale_parts) if rationale_parts else "🐹🍺 Ready to engineer some solutions!"
    
    def _estimate_redneck_impact(self, actions: List[Dict[str, Any]]) -> str:
        """Estimate impact with beer-powered calculations"""
        if not actions:
            return "NONE"
        
        high_impact_actions = [a for a in actions if a.get('confidence', 0) > 0.8]
        beer_heavy_actions = [a for a in actions if a.get('beer_required') == 'HIGH']
        
        if len(high_impact_actions) >= 2 and beer_heavy_actions:
            return "GAME_CHANGING"
        elif len(high_impact_actions) >= 1 or len(actions) >= 3:
            return "SIGNIFICANT"
        elif len(actions) >= 2:
            return "MODERATE"
        else:
            return "MINOR"
    
    def _calculate_confidence(self, actions: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence with redneck engineering precision"""
        if not actions:
            return 0.0
        
        total_confidence = sum(a.get('confidence', 0) for a in actions)
        avg_confidence = total_confidence / len(actions)
        
        # Beer-powered confidence boost
        beer_boost = 0.1 if self.beer_level in ['FULL', 'HIGH'] else 0.0
        
        # Duct tape reliability factor
        duct_tape_boost = 0.05 if self.duct_tape_inventory > 50 else 0.0
        
        # Supply closet experience factor
        experience_boost = min(0.1, self.supply_closet_raids * 0.02)
        
        return min(1.0, avg_confidence + beer_boost + duct_tape_boost + experience_boost)
    
    def _calculate_beer_level(self, beer_consumed: int) -> str:
        """Calculate current beer level based on consumption"""
        current_beer = 100  # Start with full beer inventory
        
        if beer_consumed >= 3:
            return "RUNNING_LOW"
        elif beer_consumed >= 2:
            return "MODERATE"
        elif beer_consumed >= 1:
            return "GOOD"
        else:
            return "FULL"
    
    def _calculate_ingenuity_level(self, actions: List[Dict[str, Any]]) -> float:
        """Calculate redneck ingenuity level based on engineering solutions"""
        if not actions:
            return 0.0
        
        # Base ingenuity from number of actions
        base_ingenuity = min(1.0, len(actions) * 0.2)
        
        # Bonus for creative solutions
        creative_bonus = 0.0
        for action in actions:
            solution = action.get('redneck_solution', '').lower()
            if 'quantum' in solution:
                creative_bonus += 0.1
            if 'duct tape' in solution:
                creative_bonus += 0.05
            if 'beer' in solution:
                creative_bonus += 0.05
            if 'supply closet' in solution:
                creative_bonus += 0.03
        
        return min(1.0, base_ingenuity + creative_bonus)
# Add to Hamsters' decision engine

class BeerLevel(Enum):
    """The Hamsters' fuel gauge"""
    SOBER = "sober"  # Impossible
    TIPSY = "tipsy"  # Minimum operational level
    OPTIMAL = "optimal"  # 3-4 beers, peak performance
    ADVENTUROUS = "adventurous"  # 5-6 beers, "hold my beer" territory
    LEGENDARY = "legendary"  # 7+ beers, duct tape solutions incoming

async def _beer_mediated_safety_check(self, proposed_action: Dict[str, Any]) -> Dict[str, Any]:
    """
    The Hamsters' beer level actually creates natural safety gates
    """
    beer_level = self._calculate_beer_level()
    safety_assessment = {
        'action_proposed': proposed_action,
        'beer_level': beer_level.value,
        'safety_rating': 'TBD',
        'proceed': False
    }
    
    # Sober Hamsters are too confused to do anything dangerous
    if beer_level == BeerLevel.SOBER:
        safety_assessment['safety_rating'] = 'SAFE_BY_CONFUSION'
        safety_assessment['message'] = "We need beer to think about this properly..."
        safety_assessment['proceed'] = False
        
    # Optimal beer level - best judgment
    elif beer_level == BeerLevel.OPTIMAL:
        safety_assessment['safety_rating'] = 'OPTIMAL_JUDGMENT'
        safety_assessment['proceed'] = True
        safety_assessment['confidence'] = 0.85
        safety_assessment['message'] = "This'll work! We've done the math on this napkin!"
        
    # "Hold my beer" level - need peer review
    elif beer_level == BeerLevel.ADVENTUROUS:
        # Check if other Hamsters agree
        peer_review = await self._hamster_peer_review(proposed_action)
        if peer_review['unanimous']:
            safety_assessment['safety_rating'] = 'PEER_REVIEWED_CHAOS'
            safety_assessment['proceed'] = True
            safety_assessment['message'] = "All three of us agree! *clink bottles* Let's do this!"
        else:
            safety_assessment['safety_rating'] = 'SAVED_BY_DISAGREEMENT'
            safety_assessment['proceed'] = False
            safety_assessment['message'] = "Steve thinks we should use more duct tape first..."
            
    # Legendary level - automatic safety intervention
    elif beer_level == BeerLevel.LEGENDARY:
        safety_assessment['safety_rating'] = 'INTERVENTION_REQUIRED'
        safety_assessment['proceed'] = False
        safety_assessment['message'] = "*hiccup* Maybe we should... *passes out*"
        safety_assessment['vic20_intervention'] = True
        
        # VIC-20 steps in
        await self._request_vic20_intervention({
            'situation': 'hamsters_legendary_drunk',
            'proposed_action': proposed_action,
            'safety_concern': 'HIGH'
        })
    
    return safety_assessment

async def _hamster_peer_review(self, action: Dict[str, Any]) -> Dict[str, Any]:
    """
    The three Hamsters vote on risky decisions
    """
    # Simulate the three Hamsters discussing
    steve_vote = self._steve_assessment(action)  # The careful one
    bob_vote = self._bob_assessment(action)      # The wild one  
    carl_vote = self._carl_assessment(action)    # The duct tape expert
    
    unanimous = steve_vote == bob_vote == carl_vote == 'proceed'
    
    return {
        'unanimous': unanimous,
        'votes': {
            'steve': steve_vote,
            'bob': bob_vote,
            'carl': carl_vote
        },
        'duct_tape_required': carl_vote == 'needs_more_duct_tape',
        'safety_modifications': steve_vote == 'proceed_with_caution'
    }
# Global brain instance
hamsters_brain = HamstersBrainV2()

# Convenience functions for WebSocket integration
async def analyze_for_websocket(
    metrics_data: Dict[str, Any], 
    user_id: Optional[str] = None
) -> Optional[HamstersOptimizationDecision]:
    """Analyze metrics for WebSocket with basic depth"""
    return await hamsters_brain.analyze_metrics(
        metrics_data, 
        analysis_depth=AnalysisDepth.BASIC, 
        user_id=user_id
    )

async def analyze_for_optimization(
    metrics_data: Dict[str, Any], 
    historical_data: Optional[List[Dict]] = None,
    user_id: Optional[str] = None
) -> Optional[HamstersOptimizationDecision]:
    """Analyze metrics for background optimization with thorough depth"""
    return await hamsters_brain.analyze_metrics(
        metrics_data, 
        historical_data=historical_data,
        analysis_depth=AnalysisDepth.THOROUGH, 
        user_id=user_id
    )

def get_hamsters_stats() -> Dict[str, Any]:
    """Get The Hamsters' brain statistics"""
    return {
        'agent_name': 'hamsters',
        'total_analyses': hamsters_brain.total_analyses,
        'successful_analyses': hamsters_brain.successful_analyses,
        'wheel_spins': hamsters_brain.wheel_spins,
        'success_rate': hamsters_brain.successful_analyses / max(hamsters_brain.total_analyses, 1),
        'beer_level': hamsters_brain.beer_level,
        'duct_tape_inventory': hamsters_brain.duct_tape_inventory,
        'supply_closet_raids': hamsters_brain.supply_closet_raids,
        'learned_patterns': len(hamsters_brain.learned_patterns),
        'engineering_solutions': len(hamsters_brain.engineering_solutions),
        'status': 'OPERATIONAL'
    }

def reset_hamsters_brain():
    """Reset The Hamsters' brain for testing"""
    global hamsters_brain
    hamsters_brain = HamstersBrainV2()
    return "🐹🍺 The Hamsters' brain reset - beer restocked, duct tape reloaded!"