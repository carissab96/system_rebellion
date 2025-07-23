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
    
    def __init__(self, db_getter=None):
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter
            
        self.db_integration = None  # Will be initialized on first use
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
        
    @property
    def is_active(self) -> bool:
        """The Meth Snail is always active and ready for optimization"""
        return True
        
    def activate(self):
        """The Meth Snail cannot be deactivated - he's always vigilant"""
        pass
        
    def deactivate(self):
        """The Meth Snail refuses to be deactivated - optimization never sleeps"""
        pass
        
    async def get_database_integration(self):
        """Get or create database integration instance"""
        if self.db_integration is None:
            db = await self.db_getter()
            self.db_integration = MethSnailDatabaseIntegration(db)
        return self.db_integration
    
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
            if user_id:
                try:
                    db_integration = await self.get_database_integration()
                    await db_integration.store_optimization_metrics(user_id, {
                        'cpu_usage_before': cpu_usage,
                        'memory_usage_before': memory_usage,
                        'disk_usage_before': disk_usage,
                        'cpu_usage_after': None,  # Will be updated after optimization
                        'memory_usage_after': None,
                        'disk_usage_after': None,
                        'optimization_success': False,  # Will be updated
                        'shell_spin_count': shell_spin_count,
                        'raw_metrics': metrics_data
                    })
                except Exception as e:
                    self.logger.error(f"🐌💥 Database storage failed: {e}")
                    # Continue with analysis even if database fails
            
            # === DATABASE INTEGRATION: GET HISTORICAL DATA ===
            if user_id and not historical_data:
                try:
                    db_integration = await self.get_database_integration()
                    historical_result = await db_integration.get_historical_performance(user_id)
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
                if user_id:
                    try:
                        db_integration = await self.get_database_integration()
                        await db_integration.store_decision(user_id, {
                            'decision_type': 'optimization',
                            'context': decision.rationale,
                            'result': decision.to_dict(),
                            'confidence_level': decision.confidence,
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
    # [All the analysis methods from _basic_analysis through _generate_quality_recommendation remain unchanged]

# === GLOBAL INSTANCE ===
# The one and only Meth Snail brain instance
meth_snail_brain = MethSnailBrainV2()

# === CONVENIENCE FUNCTIONS FOR DIFFERENT USE CASES ===

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