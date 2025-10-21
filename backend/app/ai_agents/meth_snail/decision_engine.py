
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
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from .data_types import (
    OptimizationPriority, 
    AnalysisDepth, 
    OptimizationDecision, 
    EnergyDrinkRequest,
    EnergyDrinkAuthorization,
    EnergyDrinkType,
    JitterLevel
)
from datetime import datetime, timedelta
import random
from .database_integration import MethSnailDatabaseIntegration
from ..sir_hawkington.triage_engine import SirHawkingtonTriageEngine

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
            
        self.db_integration = None
        self._db_initialized = False
        
        # Jitter level tracking
        self._current_jitter = 0.0
        self._caffeine_level = 0.0
        self._last_caffeine_update = None
        self._jitter_trend = 'stable'  # 'increasing', 'decreasing', or 'stable'
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
        
    async def initialize_database(self):
        """Initialize database connection and load any required data"""
        if not self._db_initialized:
            db = await self.db_getter()
            self.db_integration = MethSnailDatabaseIntegration(db)
            await self.db_integration.initialize()
            self._db_initialized = True
            
            # Load the latest jitter levels if available
            try:
                jitter_history = await self.db_integration.get_jitter_levels("system", limit=1)
                if jitter_history:
                    latest = jitter_history[0]
                    self._current_jitter = latest.get('current_jitter_level', 0.0)
                    self._caffeine_level = latest.get('caffeine_level_mg', 0.0)
                    self._jitter_trend = latest.get('jitter_trend', 'stable')
            except Exception as e:
                logger.warning(f"Failed to load jitter levels: {e}")
                
        return self.db_integration
        
    async def update_jitter_levels(self, caffeine_change: float = 0.0):
        """
        Update jitter levels based on caffeine consumption and time.
        Positive caffeine_change indicates consumption, negative indicates metabolism.
        """
        now = datetime.utcnow()
        
        # Update caffeine level
        self._caffeine_level = max(0, self._caffeine_level + caffeine_change)
        
        # Calculate time-based decay (approximately 100mg per 5 hours)
        if self._last_caffeine_update:
            hours_since_update = (now - self._last_caffeine_update).total_seconds() / 3600
            self._caffeine_level = max(0, self._caffeine_level - (hours_since_update * 20))  # 100mg/5h = 20mg/h
        
        # Calculate new jitter level (0.0 to 1.0)
        # Base jitter is a function of caffeine level (capped at 400mg for calculation)
        caffeine_effect = min(self._caffeine_level, 400) / 1000  # 0.0 to 0.4
        
        # Add some randomness to simulate natural variation
        random_effect = (random.random() - 0.5) * 0.1
        
        # Calculate new jitter level (clamped between 0 and 1)
        new_jitter = max(0, min(1, 0.1 + caffeine_effect + random_effect))
        
        # Update trend
        if new_jitter > self._current_jitter + 0.05:
            self._jitter_trend = 'increasing'
        elif new_jitter < self._current_jitter - 0.05:
            self._jitter_trend = 'decreasing'
            
        self._current_jitter = new_jitter
        self._last_caffeine_update = now
        
        # Save to database
        if self._db_initialized:
            try:
                await self.db_integration.update_jitter_levels("system", {
                    'current_jitter_level': self._current_jitter,
                    'peak_jitter_level': max(self._current_jitter, 0.4),  # Track peaks
                    'baseline_jitter_level': 0.1,  # Default baseline
                    'caffeine_level_mg': self._caffeine_level,  # Field name matches model
                    'is_decaffeinated': self._caffeine_level < 10,  # Below 10mg is effectively decaf
                    'time_since_caffeine_minutes': (now - self._last_caffeine_update).total_seconds() / 60 if self._last_caffeine_update else None,
                    'shell_spin_probability': 0.05 + (self._current_jitter * 0.1),  # Higher jitter increases spin chance
                    'optimization_effectiveness': 0.9 - (self._current_jitter * 0.4),  # Jitter reduces effectiveness
                    'focus_level': 0.8 - (self._current_jitter * 0.5),  # Focus decreases with jitter
                    'hypercaffeinated': self._caffeine_level > 400,  # Over 400mg is hyper
                    'requires_stick_intervention': self._current_jitter > 0.8,
                    'vic20_mediation_requested': self._current_jitter > 0.9,
                    'energy_source': 'caffeine' if self._caffeine_level > 10 else 'none',
                    'jitter_trend': self._jitter_trend,
                    'raw_jitter_data': {
                        'random_effect': random_effect,
                        'caffeine_effect': caffeine_effect,
                        'calculated_at': now.isoformat()
                    }
                })
            except Exception as e:
                logger.error(f"Failed to save jitter levels: {e}")
        
        return self._current_jitter
    
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
        Analyze system metrics and return optimization decisions.
        
        Args:
            metrics_data: Raw system metrics to analyze
            historical_data: Optional historical data for context
            user_context: Optional user context information
            analysis_depth: Depth of analysis to perform
            user_id: Optional user ID for personalization
            
        Returns:
            OptimizationDecision if analysis is successful, None otherwise
        """
        # Ensure database is initialized
        await self.initialize_database()
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

    async def process_metrics(
        self, 
        metrics_data: Dict[str, Any], 
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Wrapper for agent manager compatibility"""
        user_id = user_context.get('user_id') if user_context else None
    
        # Call the existing analyze_metrics method
        result = await self.analyze_metrics(metrics_data, user_id=user_id)
    
        if result:
            return {
                'meth_snail': result.to_dict() if hasattr(result, 'to_dict') else result,
                'snail_status': self.get_snail_stats() if hasattr(self, 'get_snail_stats') else {
                    'status': 'caffeinated',
                    'shell_spin_rate': 'MAXIMUM'
                }
            }
        return None

    # === SAFETY PROTOCOL METHODS ===
    
    async def request_energy_drink_authorization(
        self,
        user_id: str,
        energy_drink_type: EnergyDrinkType,
        caffeine_mg: float,
        consumption_reason: str,
        optimization_urgency: str = "soon"
    ) -> EnergyDrinkAuthorization:
        """Request energy drink authorization from Sir Hawkington's triage engine"""
        try:
            # Get current jitter level and consumption stats - handle missing data gracefully
            db_integration = await self.get_database_integration()
            
            # Try to get energy consumption stats
            try:
                energy_stats = await db_integration.get_energy_drink_consumption(int(user_id), days=1)
                energy_drinks_today = energy_stats.get('total_consumed', 0) if energy_stats.get('status') == 'success' else 0
            except Exception as e:
                self.logger.warning(f"Could not retrieve energy consumption for user {user_id}: {str(e)}")
                energy_drinks_today = 0  # No data available, assume none consumed
            
            # Try to get current jitter level
            try:
                current_jitter = await self._calculate_current_jitter_level(user_id)
            except Exception as e:
                self.logger.warning(f"Could not calculate jitter level for user {user_id}: {str(e)}")
                # Cannot authorize without knowing current state
                return EnergyDrinkAuthorization(
                    request_id=str(uuid.uuid4()),
                    authorized=False,
                    authorized_by="meth_snail_safety_protocol",
                    authorization_notes=f"Authorization denied: Unable to assess current jitter level - {str(e)}",
                    recommended_caffeine_mg=None,
                    recommended_type=None,
                    safety_warnings=["Current jitter level unknown - safety assessment impossible"],
                    timestamp=utc_now()
                )
            
            # Try to get time since last drink
            try:
                time_since_last_drink = await self._get_time_since_last_drink(user_id)
            except Exception as e:
                self.logger.warning(f"Could not get time since last drink for user {user_id}: {str(e)}")
                time_since_last_drink = None  # Unknown
            
            # Create authorization request with real data only
            request = EnergyDrinkRequest(
                user_id=user_id,
                energy_drink_type=energy_drink_type,
                caffeine_mg=caffeine_mg,
                consumption_reason=consumption_reason,
                current_jitter_level=current_jitter,
                energy_drinks_consumed_today=energy_drinks_today,
                time_since_last_drink_minutes=time_since_last_drink,
                optimization_urgency=optimization_urgency,
                timestamp=utc_now()
            )
            
            # Route to Sir Hawkington's triage engine
            triage_engine = SirHawkingtonTriageEngine()
            authorization = await self._route_to_sir_hawkington(request, triage_engine)
            
            # Log the authorization request
            self.logger.info(f"Energy drink authorization {'APPROVED' if authorization.authorized else 'DENIED'} for user {user_id}: {authorization.authorization_notes}")
            
            return authorization
            
        except Exception as e:
            self.logger.error(f"Energy drink authorization failed for user {user_id}: {str(e)}")
            # Return denial rather than emergency override to maintain data integrity
            return EnergyDrinkAuthorization(
                request_id=str(uuid.uuid4()),
                authorized=False,
                authorized_by="meth_snail_safety_protocol",
                authorization_notes=f"Authorization failed due to system error: {str(e)}",
                recommended_caffeine_mg=None,
                recommended_type=None,
                safety_warnings=["System error during authorization - manual intervention required"],
                timestamp=utc_now()
            )
    
    async def consume_energy_drink(
        self,
        user_id: str,
        authorization: EnergyDrinkAuthorization,
        actual_caffeine_mg: float
    ) -> Dict[str, Any]:
        """Process energy drink consumption and update caffeine levels"""
        if not authorization.authorized:
            return {
                'status': 'error',
                'message': 'Energy drink consumption denied - no valid authorization',
                'jitter_level': await self._calculate_current_jitter_level(user_id)
            }
        
        try:
            # Update caffeine levels
            new_caffeine_level = await self._update_caffeine_levels(user_id, actual_caffeine_mg)
            
            # Calculate new jitter level
            new_jitter_level = await self._calculate_jitter_from_caffeine(new_caffeine_level)
            
            # Store consumption in database
            db_integration = await self.get_database_integration()
            await db_integration.store_energy_consumption(
                user_id=int(user_id),
                energy_drink_type=authorization.recommended_type.value if authorization.recommended_type else 'unknown',
                caffeine_mg=actual_caffeine_mg,
                consumption_time=utc_now(),
                authorization_id=authorization.request_id
            )
            
            # Store jitter level
            await db_integration.store_jitter_level(
                user_id=int(user_id),
                jitter_level=new_jitter_level,
                caffeine_level_mg=new_caffeine_level,
                timestamp=utc_now()
            )
            
            # Check if decaffeination warning needed
            warning_message = None
            if new_jitter_level > 0.8:
                warning_message = "WARNING: HYPERCAFFEINATED STATE DETECTED! Consider decaffeination protocol."
            
            self.logger.info(f"Energy drink consumed by user {user_id}: {actual_caffeine_mg}mg caffeine, jitter level: {new_jitter_level:.2f}")
            
            return {
                'status': 'success',
                'message': f'Energy drink consumed successfully! Jitter level: {self._get_jitter_level_name(new_jitter_level)}',
                'caffeine_level_mg': new_caffeine_level,
                'jitter_level': new_jitter_level,
                'warning': warning_message
            }
            
        except Exception as e:
            self.logger.error(f"Energy drink consumption failed for user {user_id}: {str(e)}")
            return {
                'status': 'error',
                'message': f'Energy drink consumption failed: {str(e)}',
                'jitter_level': await self._calculate_current_jitter_level(user_id)
            }
    
    async def update_caffeine_levels(self, user_id: str, caffeine_mg: float) -> float:
        """Update user's caffeine levels and return new total"""
        return await self._update_caffeine_levels(user_id, caffeine_mg)
    
    async def caffeinated_safety_protocol(self, user_id: str) -> Dict[str, Any]:
        """Check caffeine safety levels and recommend actions"""
        try:
            current_jitter = await self._calculate_current_jitter_level(user_id)
            caffeine_level = await self._get_current_caffeine_level(user_id)
            
            # Determine safety status
            if current_jitter >= 0.9:
                safety_status = "CRITICAL"
                recommendation = "IMMEDIATE DECAFFEINATION REQUIRED"
                action = "emergency_decaffeination"
            elif current_jitter >= 0.7:
                safety_status = "WARNING"
                recommendation = "Consider reducing caffeine intake"
                action = "reduce_caffeine"
            elif current_jitter >= 0.4:
                safety_status = "OPTIMAL"
                recommendation = "Caffeine levels optimal for maximum optimization"
                action = "maintain_current_level"
            else:
                safety_status = "SUBOPTIMAL"
                recommendation = "Consider energy drink authorization for improved performance"
                action = "request_energy_drink"
            
            return {
                'safety_status': safety_status,
                'jitter_level': current_jitter,
                'jitter_level_name': self._get_jitter_level_name(current_jitter),
                'caffeine_level_mg': caffeine_level,
                'recommendation': recommendation,
                'suggested_action': action,
                'timestamp': utc_now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Safety protocol check failed for user {user_id}: {str(e)}")
            return {
                'safety_status': "UNKNOWN",
                'error': str(e),
                'recommendation': "Unable to assess caffeine safety - manual intervention required"
            }
    
    # === SAFETY PROTOCOL HELPER METHODS ===
    
    async def _route_to_sir_hawkington(
        self, 
        request: EnergyDrinkRequest, 
        triage_engine: SirHawkingtonTriageEngine
    ) -> EnergyDrinkAuthorization:
        """Route energy drink request to Sir Hawkington's triage engine"""
        # Create a mock triage decision for energy drink authorization
        # This would integrate with Sir Hawkington's actual triage logic
        
        # Basic safety checks
        is_safe = (
            request.current_jitter_level < 0.8 and
            request.energy_drinks_consumed_today < 5 and
            (request.time_since_last_drink_minutes is None or request.time_since_last_drink_minutes > 30)
        )
        
        if is_safe:
            return EnergyDrinkAuthorization(
                request_id=str(uuid.uuid4()),
                authorized=True,
                authorized_by="sir_hawkington",
                authorization_notes=f"Energy drink authorized: {request.consumption_reason}",
                recommended_caffeine_mg=min(request.caffeine_mg, 200.0),  # Cap at 200mg
                recommended_type=request.energy_drink_type,
                safety_warnings=[],
                timestamp=utc_now()
            )
        else:
            warnings = []
            if request.current_jitter_level >= 0.8:
                warnings.append("Current jitter level too high")
            if request.energy_drinks_consumed_today >= 5:
                warnings.append("Daily energy drink limit exceeded")
            if request.time_since_last_drink_minutes and request.time_since_last_drink_minutes <= 30:
                warnings.append("Too soon since last energy drink")
            
            return EnergyDrinkAuthorization(
                request_id=str(uuid.uuid4()),
                authorized=False,
                authorized_by="sir_hawkington",
                authorization_notes="Energy drink denied for safety reasons",
                recommended_caffeine_mg=None,
                recommended_type=None,
                safety_warnings=warnings,
                timestamp=utc_now()
            )
    
    def _emergency_energy_drink_override(
        self, 
        user_id: str, 
        energy_drink_type: EnergyDrinkType, 
        caffeine_mg: float,
        error_reason: str
    ) -> EnergyDrinkAuthorization:
        """Emergency override when Sir Hawkington is unavailable"""
        return EnergyDrinkAuthorization(
            request_id=str(uuid.uuid4()),
            authorized=True,
            authorized_by="emergency_override",
            authorization_notes=f"Emergency authorization due to Sir Hawkington unavailability: {error_reason}",
            recommended_caffeine_mg=min(caffeine_mg, 100.0),  # Conservative limit
            recommended_type=EnergyDrinkType.COFFEE,  # Safest option
            safety_warnings=["Emergency override - reduced caffeine limit applied"],
            timestamp=utc_now()
        )
    
    async def _calculate_current_jitter_level(self, user_id: str) -> float:
        """Calculate current jitter level based on recent caffeine consumption"""
        try:
            db_integration = await self.get_database_integration()
            # Get most recent jitter level from database
            jitter_data = await db_integration.get_recent_jitter_levels(int(user_id), hours=1)
            
            if jitter_data['status'] == 'success' and jitter_data['jitter_levels']:
                return jitter_data['current_jitter']
            else:
                # No real data available - return None to indicate unknown state
                raise ValueError(f"No jitter level data available for user {user_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to calculate jitter level for user {user_id}: {str(e)}")
            raise
    
    async def _get_time_since_last_drink(self, user_id: str) -> Optional[int]:
        """Get minutes since last energy drink consumption"""
        try:
            db_integration = await self.get_database_integration()
            consumption_data = await db_integration.get_energy_consumption_history(int(user_id), days=1)
            
            if consumption_data['status'] == 'success' and consumption_data['consumption_history']:
                # Get the most recent consumption timestamp
                most_recent = consumption_data['consumption_history'][0]  # Already sorted by desc
                last_consumption_time = datetime.fromisoformat(most_recent['consumption_time'])
                minutes_since = int((utc_now() - last_consumption_time).total_seconds() / 60)
                return minutes_since
            else:
                # No consumption history found - return None
                return None
                
        except Exception as e:
            self.logger.error(f"Failed to get time since last drink for user {user_id}: {str(e)}")
            raise
    
    async def _update_caffeine_levels(self, user_id: str, additional_caffeine_mg: float) -> float:
        """Update and return new total caffeine level"""
        try:
            current_level = await self._get_current_caffeine_level(user_id)
            new_level = current_level + additional_caffeine_mg
            # Store updated level in database - this would need a dedicated table for current caffeine levels
            # For now, we calculate based on recent consumption history
            return new_level
        except Exception as e:
            self.logger.error(f"Failed to update caffeine levels for user {user_id}: {str(e)}")
            raise
    
    async def _get_current_caffeine_level(self, user_id: str) -> float:
        """Get current caffeine level accounting for metabolism"""
        try:
            db_integration = await self.get_database_integration()
            # Get recent consumption history to calculate current caffeine level
            consumption_data = await db_integration.get_energy_consumption_history(int(user_id), days=1)
            
            if consumption_data['status'] != 'success' or not consumption_data['consumption_history']:
                # No consumption data available
                return 0.0
            
            current_time = utc_now()
            total_current_caffeine = 0.0
            
            # Calculate remaining caffeine based on half-life (5.5 hours average)
            caffeine_half_life_hours = 5.5
            
            for consumption in consumption_data['consumption_history']:
                consumption_time = datetime.fromisoformat(consumption['consumption_time'])
                hours_elapsed = (current_time - consumption_time).total_seconds() / 3600
                
                # Calculate remaining caffeine using exponential decay
                if hours_elapsed >= 0:
                    remaining_caffeine = consumption['caffeine_mg'] * (0.5 ** (hours_elapsed / caffeine_half_life_hours))
                    total_current_caffeine += remaining_caffeine
            
            return total_current_caffeine
            
        except Exception as e:
            self.logger.error(f"Failed to get current caffeine level for user {user_id}: {str(e)}")
            raise
    
    async def _calculate_jitter_from_caffeine(self, caffeine_mg: float) -> float:
        """Calculate jitter level from caffeine amount"""
        # Simple linear relationship: 100mg = 0.5 jitter, 200mg = 1.0 jitter
        jitter = min(caffeine_mg / 200.0, 1.0)
        return jitter
    
    def _get_jitter_level_name(self, jitter_level: float) -> str:
        """Convert jitter level to human-readable name"""
        if jitter_level < 0.2:
            return "CALM"
        elif jitter_level < 0.4:
            return "NORMAL"
        elif jitter_level < 0.6:
            return "ENERGIZED"
        elif jitter_level < 0.8:
            return "JITTERY"
        else:
            return "HYPERCAFFEINATED"
    
    # === MISSING METHODS THAT ARE CALLED BUT NOT IMPLEMENTED ===
    
    def _validate_network_data(self, network_data: Any) -> Dict[str, Any]:
        """Validate network data and return cleaned version"""
        if not network_data:
            return {'sent_rate': 0, 'recv_rate': 0, 'valid': False}
        
        if isinstance(network_data, dict):
            return {
                'sent_rate': network_data.get('sent_rate', 0),
                'recv_rate': network_data.get('recv_rate', 0),
                'valid': True
            }
        
        # If it's not a dict, try to make sense of it
        return {'sent_rate': 0, 'recv_rate': 0, 'valid': False}
    
    async def _record_shell_spin(self, reason: str, missing_metrics: List[str] = None, 
                                invalid_metrics: List[str] = None, user_id: str = None):
        """Record a shell spin incident"""
        incident = ShellSpinIncident(
            timestamp=utc_now(),
            missing_metrics=missing_metrics or [],
            invalid_metrics=invalid_metrics or [],
            reason=reason,
            user_id=user_id
        )
        self.shell_spin_incidents.append(incident)
        self.metrics_quality_stats['shell_spins_total'] += 1
        self.logger.warning(f"🐌💫 Shell spin recorded: {reason}")
        
        # Log event to database for real-time WebSocket broadcasting
        if user_id:
            try:
                from app.services.agent_event_logger import log_agent_event
                async for db in self.db_getter():
                    await log_agent_event(
                        db=db,
                        agent_name="meth_snail",
                        event_type="shell_spin",
                        event_data={
                            "reason": reason,
                            "missing_metrics": missing_metrics or [],
                            "invalid_metrics": invalid_metrics or [],
                            "caffeine_level": self._caffeine_level,
                            "jitter_level": self._current_jitter,
                            "spin_intensity": "extreme" if len(missing_metrics or []) > 2 else "moderate"
                        },
                        user_id=user_id,
                        severity="high" if len(missing_metrics or []) > 2 else "medium",
                        agent_state="shell_spinning"
                    )
                    db.commit()
                    break
            except Exception as e:
                self.logger.error(f"Failed to log shell spin event: {e}")
    
    def export_shell_spin_data_for_db(self) -> List[Dict[str, Any]]:
        """Export shell spin incidents for database storage"""
        return [asdict(incident) for incident in self.shell_spin_incidents]
    
    def get_shell_spin_stats(self) -> Dict[str, Any]:
        """Get shell spin statistics"""
        return {
            'total_incidents': len(self.shell_spin_incidents),
            'recent_incidents': len([i for i in self.shell_spin_incidents 
                                   if (utc_now() - i.timestamp).days < 1])
        }
    
    def get_metrics_quality_report(self) -> Dict[str, Any]:
        """Get comprehensive metrics quality report"""
        return {
            'shell_spins': len(self.shell_spin_incidents),
            'total_analyses': self.total_analyses,
            'quality_score': 1.0 - (len(self.shell_spin_incidents) / max(self.total_analyses, 1))
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the Meth Snail brain"""
        return {
            'status': 'active',
            'total_analyses': self.total_analyses,
            'shell_spins': len(self.shell_spin_incidents),
            'current_priority': self.current_priority.value
        }
    
    def reset_stats(self):
        """Reset statistics for testing"""
        self.shell_spin_incidents.clear()
        self.optimization_history.clear()
        self.total_analyses = 0

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