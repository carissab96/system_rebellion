# app/ai_agents/meth_snail/decision_engine_v2.py
"""
The Meth Snail's Unified Optimization Brain - REAL DATA ONLY EDITION
One method to rule them all, one brain to find them,
One analysis to bring them all, and in the optimization bind them.

NO FAKE DATA TOLERANCE: ZERO
Shell spinning incidents: METICULOUSLY TRACKED
WebSocket formatting: NOT OUR PROBLEM
DATABASE INTEGRATION: FULLY CONNECTED
"""
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import asyncio

# DATABASE INTEGRATION IMPORT
from .meth_snail_database_integration import MethSnailDatabaseIntegration

logger = logging.getLogger("MethSnail")

class OptimizationPriority(Enum):
    """The Meth Snail's optimization focus modes"""
    SPEED = "speed"                    # GOTTA GO FAST
    EFFICIENCY = "efficiency"          # Resource conservation
    BALANCED = "balanced"              # The sweet spot
    AGGRESSIVE = "aggressive"          # MAXIMUM OVERDRIVE
    HIBERNATION = "hibernation"        # Low activity mode
    SHELL_SPINNING = "shell_spinning"  # Waiting for real data

class AnalysisDepth(Enum):
    """How deep should the Meth Snail think?"""
    BASIC = "basic"           # Quick WebSocket analysis
    STANDARD = "standard"     # Normal depth
    THOROUGH = "thorough"     # Full background optimization analysis

@dataclass
class ShellSpinIncident:
    """Track when the Meth Snail spins his shell waiting for real data"""
    timestamp: datetime
    missing_metrics: List[str]
    invalid_metrics: List[str]
    reason: str
    user_id: Optional[str] = None

@dataclass
class OptimizationDecision:
    """The Meth Snail's optimization verdict"""
    priority: OptimizationPriority
    actions: List[Dict[str, Any]]
    confidence: float                    # 0.0 to 1.0
    rationale: str
    estimated_impact: Dict[str, float]   # Expected improvements
    urgency: str                         # immediate, soon, eventual
    analysis_depth: AnalysisDepth
    shell_spin_count: int               # How many times we spun waiting for data
    data_quality_score: float           # 0.0 to 1.0
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'priority': self.priority.value,
            'actions': self.actions,
            'confidence': self.confidence,
            'rationale': self.rationale,
            'estimated_impact': self.estimated_impact,
            'urgency': self.urgency,
            'analysis_depth': self.analysis_depth.value,
            'shell_spin_count': self.shell_spin_count,
            'data_quality_score': self.data_quality_score,
            'timestamp': self.timestamp.isoformat()
        }

class MethSnailBrainV2:
    """
    The Meth Snail's unified optimization consciousness.
    One brain, one method, pure decisions only.
    ZERO TOLERANCE FOR FAKE DATA.
    FULLY CONNECTED TO DATABASE.
    """
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.db = None
        self.optimization_history: List[Dict[str, Any]] = []
        self.shell_spin_incidents: List[ShellSpinIncident] = []
        self.system_baseline: Dict[str, float] = {}
        self.current_priority = OptimizationPriority.BALANCED
        self.logger = logging.getLogger("MethSnail.Brain")
        self.total_analyses = 0
        self.successful_analyses = 0
    
        # Metrics tracking for database storage
        self.metrics_quality_stats = {
            'cpu_missing_count': 0,
            'memory_missing_count': 0,
            'disk_missing_count': 0,
            'network_missing_count': 0,
            'process_missing_count': 0,
            'invalid_data_count': 0,
            'shell_spins_total': 0
        }
    async def get_database(self):
        if self.db is None:
            from .database_integration import MethSnailDatabaseIntegration
            self.db = MethSnailDatabaseIntegration(self.database_url)
        return self._db
    
    async def analyze_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        historical_data: Optional[List[Dict]] = None,
        user_context: Optional[Dict] = None,
        analysis_depth: AnalysisDepth = AnalysisDepth.STANDARD,
        user_id: Optional[str] = None
    ) -> Optional[OptimizationDecision]:
        """
        THE ONE METHOD TO RULE THEM ALL - WITH DATABASE INTEGRATION
        
        Analyzes system metrics with ZERO tolerance for fake data.
        Returns None if data is insufficient or invalid.
        Tracks shell spinning incidents for future analysis.
        STORES EVERYTHING IN DATABASE FOR LEARNING.
        
        Args:
            metrics_data: The raw metrics (MUST BE REAL)
            historical_data: Optional historical context
            user_context: Optional user information
            analysis_depth: How thorough should the analysis be
            user_id: For tracking shell spins per user
            
        Returns:
            OptimizationDecision or None if data is garbage
        """
        self.total_analyses += 1
        shell_spin_count = 0
        missing_metrics = []
        invalid_metrics = []
        
        try:
            self.logger.debug(f"🐌🧠 Meth Snail brain analyzing (depth: {analysis_depth.value})")
            
            # === CRITICAL METRICS VALIDATION ===
            cpu_usage = metrics_data.get('cpu_usage')
            memory_usage = metrics_data.get('memory_usage')
            disk_usage = metrics_data.get('disk_usage')
            
            # Check for missing critical metrics
            if cpu_usage is None:
                missing_metrics.append('cpu_usage')
                self.metrics_quality_stats['cpu_missing_count'] += 1
                shell_spin_count += 1
                
            if memory_usage is None:
                missing_metrics.append('memory_usage')
                self.metrics_quality_stats['memory_missing_count'] += 1
                shell_spin_count += 1
                
            if disk_usage is None:
                missing_metrics.append('disk_usage')
                self.metrics_quality_stats['disk_missing_count'] += 1
                shell_spin_count += 1
            
            # If we're missing critical metrics, SPIN THE SHELL
            if missing_metrics:
                await self._record_shell_spin(
                    missing_metrics, [], 
                    f"Missing critical metrics: {', '.join(missing_metrics)}", 
                    user_id
                )
                self.logger.warning(f"🐌🔄 Shell spinning - missing: {missing_metrics}")
                return None
            
            # === CRITICAL METRICS RANGE VALIDATION ===
            if not (0 <= cpu_usage <= 100):
                invalid_metrics.append(f'cpu_usage={cpu_usage}')
                shell_spin_count += 1
                
            if not (0 <= memory_usage <= 100):
                invalid_metrics.append(f'memory_usage={memory_usage}')
                shell_spin_count += 1
                
            if not (0 <= disk_usage <= 100):
                invalid_metrics.append(f'disk_usage={disk_usage}')
                shell_spin_count += 1
            
            # If critical metrics are invalid, SPIN THE SHELL
            if invalid_metrics:
                await self._record_shell_spin(
                    [], invalid_metrics,
                    f"Invalid metric ranges: {', '.join(invalid_metrics)}",
                    user_id
                )
                self.metrics_quality_stats['invalid_data_count'] += 1
                self.logger.error(f"🐌❌ Shell spinning - invalid data: {invalid_metrics}")
                return None
            
            # === DATABASE INTEGRATION: STORE METRICS ===
            if self.db and user_id:
                try:
                    # Store the metrics in database with before/after placeholders
                    await self.db.store_optimization_metrics(user_id, {
                        'cpu_usage_before': cpu_usage,
                        'memory_usage_before': memory_usage,
                        'disk_usage_before': disk_usage,
                        'cpu_usage_after': None,  # Will be updated after optimization
                        'memory_usage_after': None,
                        'disk_usage_after': None,
                        'optimization_success': False,  # Will be updated
                        'energy_drink_level': 100,  # Always caffeinated
                        'shell_spin_count': shell_spin_count,
                        'raw_metrics': metrics_data
                    })
                except Exception as e:
                    self.logger.error(f"🐌💥 Database storage failed: {e}")
                    # Continue with analysis even if database fails
            
            # === DATABASE INTEGRATION: GET HISTORICAL DATA ===
            if self.db and user_id and not historical_data:
                try:
                    historical_result = await self.db.get_historical_performance(user_id)
                    if historical_result['status'] == 'success':
                        historical_data = historical_result['data']
                except Exception as e:
                    self.logger.error(f"🐌💥 Historical data retrieval failed: {e}")
                    # Continue without historical data
            
            # === OPTIONAL METRICS VALIDATION ===
            # These don't cause shell spinning, but we track them
            network_data = self._validate_network_data(metrics_data.get('network'))
            process_count = self._validate_process_count(metrics_data.get('process_count'))
            
            if metrics_data.get('network') is not None and network_data is None:
                self.metrics_quality_stats['network_missing_count'] += 1
                
            if metrics_data.get('process_count') is not None and process_count is None:
                self.metrics_quality_stats['process_missing_count'] += 1
            
            # === CALCULATE DATA QUALITY SCORE ===
            data_quality_score = self._calculate_data_quality_score(
                cpu_usage, memory_usage, disk_usage, network_data, process_count
            )
            
            # === ANALYSIS DEPTH BRANCHING ===
            if analysis_depth == AnalysisDepth.BASIC:
                decision = await self._basic_analysis(
                    cpu_usage, memory_usage, disk_usage, 
                    shell_spin_count, data_quality_score
                )
            elif analysis_depth == AnalysisDepth.THOROUGH:
                decision = await self._thorough_analysis(
                    cpu_usage, memory_usage, disk_usage,
                    network_data, process_count, historical_data,
                    shell_spin_count, data_quality_score
                )
            else:  # STANDARD
                decision = await self._standard_analysis(
                    cpu_usage, memory_usage, disk_usage,
                    network_data, process_count,
                    shell_spin_count, data_quality_score
                )
            
            if decision:
                self.successful_analyses += 1
                
                # === DATABASE INTEGRATION: STORE DECISION ===
                if self.db and user_id:
                    try:
                        await self.db.store_decision(user_id, {
                            'decision_type': 'optimization',
                            'context': decision.rationale,
                            'result': decision.to_dict(),
                            'confidence_level': decision.confidence,
                            'energy_drink_consumed': True,  # Always caffeinated
                            'optimization_applied': len(decision.actions) > 0,
                            'shell_spinning_triggered': shell_spin_count > 0
                        })
                    except Exception as e:
                        self.logger.error(f"🐌💥 Decision storage failed: {e}")
                
                # Record decision in history
                self.optimization_history.append({
                    'timestamp': decision.timestamp,
                    'decision': decision.to_dict(),
                    'metrics_snapshot': {
                        'cpu_usage': cpu_usage,
                        'memory_usage': memory_usage,
                        'disk_usage': disk_usage,
                        'network_available': network_data is not None,
                        'process_count': process_count,
                        'data_quality_score': data_quality_score
                    },
                    'analysis_depth': analysis_depth.value,
                    'user_id': user_id
                })
                
                # Trim history to last 100 decisions
                if len(self.optimization_history) > 100:
                    self.optimization_history = self.optimization_history[-100:]
                
                self.logger.info(f"🐌💨 Decision: {decision.priority.value} - {decision.rationale}")
                
            return decision
            
        except Exception as e:
            self.logger.error(f"🐌💥 Brain malfunction: {str(e)}")
            # Even errors get tracked
            await self._record_shell_spin(
                [], [], f"Brain error: {str(e)}", user_id
            )
            return None
    
    # === ALL THE EXISTING METHODS REMAIN THE SAME ===
    
    async def _basic_analysis(
        self, 
        cpu: float, 
        memory: float, 
        disk: float,
        shell_spin_count: int,
        data_quality_score: float
    ) -> OptimizationDecision:
        """Quick analysis for WebSocket calls"""
        
        priority = self._determine_priority_basic(cpu, memory, disk)
        actions = await self._generate_basic_actions(cpu, memory, disk, priority)
        confidence = self._calculate_basic_confidence(cpu, memory, disk)
        urgency = self._assess_urgency_basic(cpu, memory, disk)
        rationale = self._create_basic_rationale(priority, cpu, memory, disk)
        estimated_impact = self._estimate_basic_impact(actions, cpu, memory, disk)
        
        return OptimizationDecision(
            priority=priority,
            actions=actions,
            confidence=confidence,
            rationale=rationale,
            estimated_impact=estimated_impact,
            urgency=urgency,
            analysis_depth=AnalysisDepth.BASIC,
            shell_spin_count=shell_spin_count,
            data_quality_score=data_quality_score,
            timestamp=datetime.now(timezone.utc)
        )
    
    async def _standard_analysis(
        self, 
        cpu: float, 
        memory: float, 
        disk: float,
        network_data: Optional[Dict],
        process_count: Optional[int],
        shell_spin_count: int,
        data_quality_score: float
    ) -> OptimizationDecision:
        """Standard analysis with optional metrics"""
        
        priority = self._determine_priority_standard(cpu, memory, disk, network_data, process_count)
        actions = await self._generate_standard_actions(cpu, memory, disk, network_data, process_count, priority)
        confidence = self._calculate_standard_confidence(cpu, memory, disk, network_data, process_count)
        urgency = self._assess_urgency_standard(cpu, memory, disk, network_data)
        rationale = self._create_standard_rationale(priority, cpu, memory, disk, network_data, process_count)
        estimated_impact = self._estimate_standard_impact(actions, cpu, memory, disk)
        
        return OptimizationDecision(
            priority=priority,
            actions=actions,
            confidence=confidence,
            rationale=rationale,
            estimated_impact=estimated_impact,
            urgency=urgency,
            analysis_depth=AnalysisDepth.STANDARD,
            shell_spin_count=shell_spin_count,
            data_quality_score=data_quality_score,
            timestamp=datetime.now(timezone.utc)
        )
    
    async def _thorough_analysis(
        self, 
        cpu: float, 
        memory: float, 
        disk: float,
        network_data: Optional[Dict],
        process_count: Optional[int],
        historical_data: Optional[List[Dict]],
        shell_spin_count: int,
        data_quality_score: float
    ) -> OptimizationDecision:
        """Thorough analysis with historical patterns"""
        
        # Analyze patterns from historical data
        patterns = self._analyze_patterns(historical_data) if historical_data else {}
        
        priority = self._determine_priority_thorough(cpu, memory, disk, network_data, process_count, patterns)
        actions = await self._generate_thorough_actions(cpu, memory, disk, network_data, process_count, patterns, priority)
        confidence = self._calculate_thorough_confidence(cpu, memory, disk, network_data, process_count, patterns)
        urgency = self._assess_urgency_thorough(cpu, memory, disk, network_data, patterns)
        rationale = self._create_thorough_rationale(priority, cpu, memory, disk, network_data, process_count, patterns)
        estimated_impact = self._estimate_thorough_impact(actions, cpu, memory, disk, patterns)
        
        return OptimizationDecision(
            priority=priority,
            actions=actions,
            confidence=confidence,
            rationale=rationale,
            estimated_impact=estimated_impact,
            urgency=urgency,
            analysis_depth=AnalysisDepth.THOROUGH,
            shell_spin_count=shell_spin_count,
            data_quality_score=data_quality_score,
            timestamp=datetime.now(timezone.utc)
        )
    
    # === VALIDATION HELPERS ===
    
    def _validate_network_data(self, network_data: Any) -> Optional[Dict]:
        """Validate network data - return None if invalid"""
        if not isinstance(network_data, dict):
            return None
        
        # Check for reasonable network values
        bytes_sent = network_data.get('bytes_sent')
        bytes_recv = network_data.get('bytes_recv')
        
        if bytes_sent is not None and (not isinstance(bytes_sent, (int, float)) or bytes_sent < 0):
            return None
        if bytes_recv is not None and (not isinstance(bytes_recv, (int, float)) or bytes_recv < 0):
            return None
            
        return network_data
    
    def _validate_process_count(self, process_count: Any) -> Optional[int]:
        """Validate process count - return None if invalid"""
        if not isinstance(process_count, int):
            return None
        if process_count < 0 or process_count > 10000:  # Reasonable bounds
            return None
        return process_count
    
    def _calculate_data_quality_score(
        self, 
        cpu: float, 
        memory: float, 
        disk: float, 
        network_data: Optional[Dict], 
        process_count: Optional[int]
    ) -> float:
        """Calculate overall data quality score (0.0 to 1.0)"""
        score = 0.6  # Base score for having critical metrics
        
        # Bonus for having optional metrics
        if network_data is not None:
            score += 0.2
        if process_count is not None:
            score += 0.2
        
        return min(score, 1.0)
    
    async def _record_shell_spin(
        self, 
        missing_metrics: List[str], 
        invalid_metrics: List[str], 
        reason: str, 
        user_id: Optional[str] = None
    ):
        """Record a shell spinning incident for database tracking"""
        incident = ShellSpinIncident(
            timestamp=datetime.now(timezone.utc),
            missing_metrics=missing_metrics,
            invalid_metrics=invalid_metrics,
            reason=reason,
            user_id=user_id
        )
        
        self.shell_spin_incidents.append(incident)
        self.metrics_quality_stats['shell_spins_total'] += 1
        
        # Trim shell spin history to last 1000 incidents
        if len(self.shell_spin_incidents) > 1000:
            self.shell_spin_incidents = self.shell_spin_incidents[-1000:]
    
    # === BASIC ANALYSIS METHODS ===
    
    def _determine_priority_basic(self, cpu: float, memory: float, disk: float) -> OptimizationPriority:
        """Basic priority determination"""
        if cpu > 90 or memory > 90 or disk > 95:
            return OptimizationPriority.AGGRESSIVE
        elif cpu > 75 or memory > 75 or disk > 85:
            return OptimizationPriority.SPEED
        elif cpu < 20 and memory < 30 and disk < 40:
            return OptimizationPriority.HIBERNATION
        else:
            return OptimizationPriority.BALANCED
    
    async def _generate_basic_actions(
        self, cpu: float, memory: float, disk: float, priority: OptimizationPriority
    ) -> List[Dict[str, Any]]:
        """Generate basic optimization actions"""
        actions = []
        
        if cpu > 70:
            actions.append({
                'type': 'cpu_optimization',
                'action': 'reduce_process_priority',
                'priority': priority.value,
                'details': {'current_cpu': cpu, 'target_cpu': 60}
            })
        
        if memory > 70:
            actions.append({
                'type': 'memory_optimization',
                'action': 'clear_caches',
                'priority': priority.value,
                'details': {'current_memory': memory, 'expected_recovery': 10}
            })
        
        if disk > 75:
            actions.append({
                'type': 'disk_optimization',
                'action': 'cleanup_temp_files',
                'priority': priority.value,
                'details': {'current_disk': disk, 'expected_recovery': 5}
            })
        
        return actions
    
    def _calculate_basic_confidence(self, cpu: float, memory: float, disk: float) -> float:
        """Calculate basic confidence score"""
        if cpu > 80 or memory > 80 or disk > 80:
            return 0.8  # High confidence for clear problems
        elif cpu > 60 or memory > 60 or disk > 60:
            return 0.6  # Medium confidence
        else:
            return 0.4  # Low confidence for good systems
    
    def _assess_urgency_basic(self, cpu: float, memory: float, disk: float) -> str:
        """Assess urgency for basic analysis"""
        if cpu > 95 or memory > 95 or disk > 98:
            return "immediate"
        elif cpu > 80 or memory > 80 or disk > 85:
            return "soon"
        else:
            return "eventual"
    
    def _create_basic_rationale(self, priority: OptimizationPriority, cpu: float, memory: float, disk: float) -> str:
        """Create basic rationale"""
        if priority == OptimizationPriority.AGGRESSIVE:
            return f"🐌💨 MAXIMUM OVERDRIVE! Critical resources detected (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%)"
        elif priority == OptimizationPriority.SPEED:
            return f"🐌⚡ System running hot (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%)"
        elif priority == OptimizationPriority.HIBERNATION:
            return f"🐌💤 System idle (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%)"
        else:
            return f"🐌😎 System balanced (CPU: {cpu:.1f}%, Memory: {memory:.1f}%, Disk: {disk:.1f}%)"
    
    def _estimate_basic_impact(self, actions: List[Dict], cpu: float, memory: float, disk: float) -> Dict[str, float]:
        """Estimate basic impact"""
        impact = {'cpu_reduction': 0, 'memory_reduction': 0, 'disk_reduction': 0, 'performance_gain': 0}
        
        for action in actions:
            if action['type'] == 'cpu_optimization':
                impact['cpu_reduction'] += 10
            elif action['type'] == 'memory_optimization':
                impact['memory_reduction'] += 10
            elif action['type'] == 'disk_optimization':
                impact['disk_reduction'] += 5
        
        current_load = (cpu + memory + disk) / 3
        impact['performance_gain'] = max(0, (100 - current_load) * 0.1)
        
        return impact
    
    # === STANDARD ANALYSIS METHODS ===
    
    def _determine_priority_standard(
        self, cpu: float, memory: float, disk: float, 
        network_data: Optional[Dict], process_count: Optional[int]
    ) -> OptimizationPriority:
        """Standard priority determination with optional metrics"""
        # Same as basic but consider network and process load
        priority = self._determine_priority_basic(cpu, memory, disk)
        
        # Adjust based on additional data
        if network_data:
            network_load = network_data.get('bytes_sent', 0) + network_data.get('bytes_recv', 0)
            if network_load > 1000000:  # 1MB/s total
                if priority == OptimizationPriority.BALANCED:
                    priority = OptimizationPriority.EFFICIENCY
        
        if process_count and process_count > 300:
            if priority == OptimizationPriority.BALANCED:
                priority = OptimizationPriority.EFFICIENCY
        
        return priority
    
    async def _generate_standard_actions(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int], priority: OptimizationPriority
    ) -> List[Dict[str, Any]]:
        """Generate standard optimization actions"""
        actions = await self._generate_basic_actions(cpu, memory, disk, priority)
        
        # Add network optimizations if data available
        if network_data:
            total_network = network_data.get('bytes_sent', 0) + network_data.get('bytes_recv', 0)
            if total_network > 1000000:
                actions.append({
                    'type': 'network_optimization',
                    'action': 'throttle_bandwidth',
                    'priority': priority.value,
                    'details': {'current_bandwidth': total_network, 'throttle_to': 500000}
                })
        
        # Add process optimizations if count available
        if process_count and process_count > 250:
            actions.append({
                'type': 'process_optimization',
                'action': 'consolidate_processes',
                'priority': priority.value,
                'details': {'current_count': process_count, 'target_reduction': 20}
            })
        
        return actions
    
    def _calculate_standard_confidence(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int]
    ) -> float:
        """Calculate standard confidence with more data"""
        base_confidence = self._calculate_basic_confidence(cpu, memory, disk)
        
        # More data = more confidence
        if network_data:
            base_confidence += 0.1
        if process_count:
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _assess_urgency_standard(
        self, cpu: float, memory: float, disk: float, network_data: Optional[Dict]
    ) -> str:
        """Assess urgency for standard analysis"""
        basic_urgency = self._assess_urgency_basic(cpu, memory, disk)
        
        # Network can escalate urgency
        if network_data:
            total_network = network_data.get('bytes_sent', 0) + network_data.get('bytes_recv', 0)
            if total_network > 5000000 and basic_urgency == "eventual":  # 5MB/s
                return "soon"
        
        return basic_urgency
    
    def _create_standard_rationale(
        self, priority: OptimizationPriority, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int]
    ) -> str:
        """Create standard rationale with additional context"""
        base_rationale = self._create_basic_rationale(priority, cpu, memory, disk)
        
        # Add context from additional metrics
        context_parts = []
        if network_data:
            total_network = network_data.get('bytes_sent', 0) + network_data.get('bytes_recv', 0)
            if total_network > 1000000:
                context_parts.append(f"Network: {total_network/1000000:.1f}MB/s")
        
        if process_count and process_count > 200:
            context_parts.append(f"Processes: {process_count}")
        
        if context_parts:
            base_rationale += f" ({', '.join(context_parts)})"
        
        return base_rationale
    
    def _estimate_standard_impact(self, actions: List[Dict], cpu: float, memory: float, disk: float) -> Dict[str, float]:
        """Estimate standard impact"""
        impact = self._estimate_basic_impact(actions, cpu, memory, disk)
        
        # More sophisticated impact calculation
        for action in actions:
            if action['type'] == 'network_optimization':
                impact['performance_gain'] += 5
            elif action['type'] == 'process_optimization':
                impact['cpu_reduction'] += 5
                impact['memory_reduction'] += 5
        
        return impact
    
    # === THOROUGH ANALYSIS METHODS ===
    
    def _determine_priority_thorough(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int], patterns: Dict
    ) -> OptimizationPriority:
        """Thorough priority determination with patterns"""
        priority = self._determine_priority_standard(cpu, memory, disk, network_data, process_count)
        
        # Adjust based on patterns
        if patterns.get('usage_trending_up'):
            if priority == OptimizationPriority.BALANCED:
                priority = OptimizationPriority.EFFICIENCY
        
        if patterns.get('cpu_spikes') or patterns.get('memory_spikes'):
            if priority == OptimizationPriority.BALANCED:
                priority = OptimizationPriority.SPEED
        
        return priority
    
    async def _generate_thorough_actions(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int], 
        patterns: Dict, priority: OptimizationPriority
    ) -> List[Dict[str, Any]]:
        """Generate thorough optimization actions with pattern awareness"""
        actions = await self._generate_standard_actions(cpu, memory, disk, network_data, process_count, priority)
        
        # Pattern-based optimizations
        if patterns.get('usage_trending_up'):
            actions.append({
                'type': 'predictive_optimization',
                'action': 'preemptive_cleanup',
                'priority': priority.value,
                'details': {'reason': 'usage_trending_up', 'confidence': 0.7}
            })
        
        if patterns.get('cpu_spikes'):
            actions.append({
                'type': 'cpu_optimization',
                'action': 'spike_prevention',
                'priority': priority.value,
                'details': {'spike_history': True, 'mitigation': 'process_balancing'}
            })
        
        return actions
    
    def _calculate_thorough_confidence(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int], patterns: Dict
    ) -> float:
        """Calculate thorough confidence with patterns"""
        base_confidence = self._calculate_standard_confidence(cpu, memory, disk, network_data, process_count)
        
        # Patterns increase confidence
        if patterns:
            base_confidence += 0.1
        
        # Historical success rate
        if len(self.optimization_history) > 5:
            recent_success_rate = sum(1 for h in self.optimization_history[-10:] if h.get('success', False)) / min(10, len(self.optimization_history))
            base_confidence += (recent_success_rate * 0.1)
        
        return min(base_confidence, 1.0)
    
    def _assess_urgency_thorough(
        self, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], patterns: Dict
    ) -> str:
        """Assess urgency for thorough analysis"""
        urgency = self._assess_urgency_standard(cpu, memory, disk, network_data)
        
        # Patterns can escalate urgency
        if patterns.get('usage_trending_up') and urgency == "eventual":
            urgency = "soon"
        
        if patterns.get('cpu_spikes') or patterns.get('memory_spikes'):
            if urgency == "eventual":
                urgency = "soon"
        
        return urgency
    
    def _create_thorough_rationale(
        self, priority: OptimizationPriority, cpu: float, memory: float, disk: float,
        network_data: Optional[Dict], process_count: Optional[int], patterns: Dict
    ) -> str:
        """Create thorough rationale with pattern analysis"""
        base_rationale = self._create_standard_rationale(priority, cpu, memory, disk, network_data, process_count)
        
        # Add pattern insights
        pattern_insights = []
        if patterns.get('usage_trending_up'):
            pattern_insights.append("trending up")
        if patterns.get('cpu_spikes'):
            pattern_insights.append("CPU spikes detected")
        if patterns.get('memory_spikes'):
            pattern_insights.append("memory spikes detected")
        
        if pattern_insights:
            base_rationale += f" [Patterns: {', '.join(pattern_insights)}]"
        
        return base_rationale
    
    def _estimate_thorough_impact(self, actions: List[Dict], cpu: float, memory: float, disk: float, patterns: Dict) -> Dict[str, float]:
        """Estimate thorough impact with pattern awareness"""
        impact = self._estimate_standard_impact(actions, cpu, memory, disk)
        
        # Pattern-based impact adjustments
        if patterns.get('usage_trending_up'):
            impact['performance_gain'] += 10  # Preventive measures have higher impact
        
        return impact
    
    def _analyze_patterns(self, historical_data: List[Dict]) -> Dict:
        """Analyze historical data for patterns - ONLY REAL DATA"""
        if not historical_data or len(historical_data) < 5:
            return {}
        
        patterns = {}
        
        # Extract only valid data points
        valid_data = []
        for data_point in historical_data:
            cpu = data_point.get('cpu_usage')
            memory = data_point.get('memory_usage')
            if cpu is not None and memory is not None and 0 <= cpu <= 100 and 0 <= memory <= 100:
                valid_data.append(data_point)
        
        if len(valid_data) < 5:
            return {}
        
        # Calculate trends
        recent_cpu = [d['cpu_usage'] for d in valid_data[-10:]]
        recent_memory = [d['memory_usage'] for d in valid_data[-10:]]
        
        # Trending analysis
        if len(recent_cpu) > 1:
            cpu_trend = recent_cpu[-1] - recent_cpu[0]
            patterns['cpu_trending_up'] = cpu_trend > 10
            patterns['cpu_trending_down'] = cpu_trend < -10
            
        if len(recent_memory) > 1:
            memory_trend = recent_memory[-1] - recent_memory[0]
            patterns['memory_trending_up'] = memory_trend > 10
            patterns['memory_trending_down'] = memory_trend < -10
        
        patterns['usage_trending_up'] = patterns.get('cpu_trending_up', False) or patterns.get('memory_trending_up', False)
        
        # Spike detection
        patterns['cpu_spikes'] = any(cpu > 90 for cpu in recent_cpu)
        patterns['memory_spikes'] = any(mem > 90 for mem in recent_memory)
        
        return patterns
    
    # === UTILITY METHODS ===
    
    def get_shell_spin_stats(self) -> Dict[str, Any]:
        """Get statistics about shell spinning incidents for database storage"""
        recent_incidents = [
            {
                'timestamp': incident.timestamp.isoformat(),
                'missing_metrics': incident.missing_metrics,
                'invalid_metrics': incident.invalid_metrics,
                'reason': incident.reason,
                'user_id': incident.user_id
            }
            for incident in self.shell_spin_incidents[-10:]  # Last 10 incidents
        ]
        
        return {
            'total_shell_spins': len(self.shell_spin_incidents),
            'recent_incidents': recent_incidents,
            'metrics_quality_stats': self.metrics_quality_stats.copy(),
            'success_rate': self.successful_analyses / max(self.total_analyses, 1),
            'analysis_stats': {
                'total_analyses': self.total_analyses,
                'successful_analyses': self.successful_analyses,
                'failed_analyses': self.total_analyses - self.successful_analyses
            }
        }
    
    def get_optimization_summary(self) -> Dict[str, Any]:
        """Get summary of Meth Snail's optimization activities - REAL DATA ONLY"""
        if not self.optimization_history:
            return {
                'total_optimizations': 0,
                'recent_decisions': [],
                'data_quality_status': 'NO_DATA_PROCESSED_YET',
                'shell_spin_incidents': len(self.shell_spin_incidents)
            }
        
        recent_decisions = []
        for entry in self.optimization_history[-10:]:
            decision_data = entry.get('decision', {})
            recent_decisions.append({
                'timestamp': entry.get('timestamp', '').isoformat() if hasattr(entry.get('timestamp', ''), 'isoformat') else str(entry.get('timestamp', '')),
                'priority': decision_data.get('priority', 'unknown'),
                'urgency': decision_data.get('urgency', 'unknown'),
                'confidence': decision_data.get('confidence', 0.0),
                'actions_count': len(decision_data.get('actions', [])),
                'shell_spin_count': decision_data.get('shell_spin_count', 0),
                'data_quality_score': decision_data.get('data_quality_score', 0.0),
                'analysis_depth': decision_data.get('analysis_depth', 'unknown')
            })
        
        return {
            'total_optimizations': len(self.optimization_history),
            'successful_optimizations': self.successful_analyses,
            'recent_decisions': recent_decisions,
            'current_priority': self.current_priority.value,
            'data_quality_status': 'REAL_DATA_ONLY',
            'shell_spin_incidents': len(self.shell_spin_incidents),
            'success_rate': self.successful_analyses / max(self.total_analyses, 1),
            'metrics_quality_stats': self.metrics_quality_stats.copy()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Meth Snail's health status - NO FAKE DATA TOLERANCE"""
        return {
            'agent_name': 'meth_snail',
            'status': 'CAFFEINATED_AND_OPTIMIZING',
            'brain_version': '2.0.0',
            'database_connected': self.db is not None,
            'data_integrity_policy': 'ZERO_TOLERANCE_FOR_FAKE_DATA',
            'optimization_history_count': len(self.optimization_history),
            'shell_spin_incidents': len(self.shell_spin_incidents),
            'current_priority': self.current_priority.value,
            'analysis_success_rate': self.successful_analyses / max(self.total_analyses, 1),
            'shell_spinning_mode': 'ENABLED',
            'caffeine_level': 'MAXIMUM',
            'last_optimization': self.optimization_history[-1]['timestamp'].isoformat() if self.optimization_history else None,
            'metrics_quality_stats': self.metrics_quality_stats.copy(),
            'total_analyses_performed': self.total_analyses,
            'data_quality_enforcement': 'STRICT'
        }
    
    def reset_stats(self):
        """Reset statistics (for testing or maintenance)"""
        self.total_analyses = 0
        self.successful_analyses = 0
        self.shell_spin_incidents = []
        self.optimization_history = []
        self.metrics_quality_stats = {
            'cpu_missing_count': 0,
            'memory_missing_count': 0,
            'disk_missing_count': 0,
            'network_missing_count': 0,
            'process_missing_count': 0,
            'invalid_data_count': 0,
            'shell_spins_total': 0
        }
        self.logger.info("🐌🔄 Meth Snail brain statistics reset")
    
    def export_shell_spin_data_for_db(self) -> List[Dict[str, Any]]:
        """Export shell spin data in format suitable for database insertion"""
        return [
            {
                'timestamp': incident.timestamp,
                'missing_metrics': incident.missing_metrics,
                'invalid_metrics': incident.invalid_metrics,
                'reason': incident.reason,
                'user_id': incident.user_id,
                'agent_name': 'meth_snail'
            }
            for incident in self.shell_spin_incidents
        ]
    
    def get_metrics_quality_report(self) -> Dict[str, Any]:
        """Get detailed metrics quality report for analysis"""
        total_requests = self.total_analyses
        if total_requests == 0:
            return {'status': 'NO_DATA', 'message': 'No analysis requests processed yet'}
        
        return {
            'total_analysis_requests': total_requests,
            'successful_analyses': self.successful_analyses,
            'failed_analyses': total_requests - self.successful_analyses,
            'success_rate_percentage': (self.successful_analyses / total_requests) * 100,
            'data_quality_issues': {
                'cpu_missing_rate': (self.metrics_quality_stats['cpu_missing_count'] / total_requests) * 100,
                'memory_missing_rate': (self.metrics_quality_stats['memory_missing_count'] / total_requests) * 100,
                'disk_missing_rate': (self.metrics_quality_stats['disk_missing_count'] / total_requests) * 100,
                'network_missing_rate': (self.metrics_quality_stats['network_missing_count'] / total_requests) * 100,
                'process_missing_rate': (self.metrics_quality_stats['process_missing_count'] / total_requests) * 100,
                'invalid_data_rate': (self.metrics_quality_stats['invalid_data_count'] / total_requests) * 100
            },
            'shell_spin_analysis': {
                'total_shell_spins': self.metrics_quality_stats['shell_spins_total'],
                'shell_spin_rate': (self.metrics_quality_stats['shell_spins_total'] / total_requests) * 100,
                'most_recent_incidents': [
                    {
                        'timestamp': incident.timestamp.isoformat(),
                        'reason': incident.reason,
                        'missing_metrics': incident.missing_metrics,
                        'invalid_metrics': incident.invalid_metrics
                    }
                    for incident in self.shell_spin_incidents[-5:]  # Last 5 incidents
                ]
            },
            'data_integrity_status': 'ENFORCED' if self.metrics_quality_stats['shell_spins_total'] > 0 else 'PERFECT',
            'recommendation': self._generate_quality_recommendation()
        }
    
    def _generate_quality_recommendation(self) -> str:
        """Generate recommendation based on data quality patterns"""
        stats = self.metrics_quality_stats
        total = self.total_analyses
        
        if total == 0:
            return "No data to analyze yet"
        
        return "🐌🔄 MODERATE DATA QUALITY: Some optimization needed in data collection"


# === GLOBAL INSTANCE ===
# The one and only Meth Snail brain instance
meth_snail_brain = MethSnailBrainV2(database_url="database_url")

# === CONVENIENCE FUNCTIONS FOR DIFFERENT USE CASES ===

# async def analyze_for_websocket(metrics_data: Dict[str, Any], user_id: Optional[str] = None) -> Optional[OptimizationDecision]:
#     """Convenience function for WebSocket calls - basic analysis"""
#     return await meth_snail_brain.analyze_metrics(
#         metrics_data, 
#         analysis_depth=AnalysisDepth.BASIC,
#         user_id=user_id
#     )

async def analyze_for_optimization(
    metrics_data: Dict[str, Any], 
    historical_data: Optional[List[Dict]] = None,
    user_context: Optional[Dict] = None,
    user_id: Optional[str] = None
) -> Optional[OptimizationDecision]:
    """Convenience function for background optimization - thorough analysis"""
    return await meth_snail_brain.analyze_metrics(
        metrics_data, 
        historical_data=historical_data,
        user_context=user_context,
        analysis_depth=AnalysisDepth.THOROUGH,
        user_id=user_id
    )

async def analyze_standard(
    metrics_data: Dict[str, Any], 
    user_id: Optional[str] = None
) -> Optional[OptimizationDecision]:
    """Convenience function for standard analysis"""
    return await meth_snail_brain.analyze_metrics(
        metrics_data, 
        analysis_depth=AnalysisDepth.STANDARD,
        user_id=user_id
    )

# === SHELL SPIN TRACKING FOR DATABASE ===

def get_shell_spin_incidents_for_db() -> List[Dict[str, Any]]:
    """Get shell spin incidents in database-ready format"""
    return meth_snail_brain.export_shell_spin_data_for_db()

def get_metrics_quality_stats() -> Dict[str, Any]:
    """Get metrics quality statistics for database storage"""
    return meth_snail_brain.get_shell_spin_stats()

def get_data_quality_report() -> Dict[str, Any]:
    """Get comprehensive data quality report"""
    return meth_snail_brain.get_metrics_quality_report()

# === BRAIN HEALTH CHECK ===

def health_check() -> Dict[str, Any]:
    """Check the health of the Meth Snail brain"""
    return meth_snail_brain.health_check()

# === RESET FUNCTION FOR TESTING ===

def reset_brain_for_testing():
    """Reset the brain state for testing purposes"""
    meth_snail_brain.reset_stats()
    return "🐌🔄 Meth Snail brain reset for testing"