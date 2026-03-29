"""
The Stick — Personality State
================================

All mutable state and brain logic for The Stick.
TheStickBrainV3 (formerly in decision_engine.py) is now defined here directly.
StickPersonalityState inherits from it, adding distributed-specific state.

Every variable name preserved character-for-character from the monolith.
"""

import logging
import statistics
import random
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta, timezone

from .data_types import (
    AnxietyLevel,
    ComplianceState,
    StickDecisionType,
    StickDecision,
    StickMemoryEntry,
    UserPattern,
    ComplianceViolation,
    utc_now,
)
from .paper_bag_economy import PaperBagEconomy, BagSupplyState

logger = logging.getLogger("TheStick.State")


# =========================================================================
# TheStickBrainV3 — formerly decision_engine.py
# =========================================================================

class TheStickBrainV3:
    """
    The Stick: Anxiety-Driven Compliance Master
    OCD + ADHD + PTSD + Eidetic Memory = Perfect Safety System
    Anxiety IS the feature - hypervigilance catches what others miss
    """

    def __init__(self, db_getter=None):
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter
        self.db = None

        # Core states
        self.compliance_state = ComplianceState.LEARNING
        self.anxiety_level = AnxietyLevel.NERVOUS  # The Stick is never truly calm
        self.current_anxiety_percentage = 25.0  # Starting nervous

        # Anxiety management
        self.paper_bag_inventory = 100  # Starting inventory
        self.paper_bags_consumed_today = 0
        self.last_paper_bag_time = None
        self.anxiety_triggers = []

        # Hamster tracking (source of major anxiety)
        self.hamster_proximity_alerts = []
        self.steve_location = None
        self.bob_location = None  # Bob causes the MOST anxiety
        self.carl_location = None
        self.last_hamster_squeak = None

        # Pattern memory (eidetic)
        self.user_patterns = {}
        self.compliance_violations = 0
        self.optimizations_applied = 0
        self.pattern_learning_sessions = 0
        self.everything_ever_seen = []  # The Stick remembers EVERYTHING

        # Anxiety multipliers
        self.anxiety_multipliers = {
            'bob_proximity': 3.0,  # Bob is chaos incarnate
            'steve_proximity': 1.5,  # Steve is careful but still a hamster
            'carl_proximity': 2.0,  # Carl with duct tape is concerning
            'compliance_violation': 2.5,
            'unknown_pattern': 1.8,
            'system_anomaly': 2.2,
            'multiple_hamsters': 4.0,  # All three together = maximum panic
            'hamster_infrastructure_work': 5.0  # DEFCON 1
        }

        # Documentation compulsion (anxiety outlet)
        self.panic_documentation_queue = []
        self.documentation_backlog = []

    @property
    def compliance_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Get compliance thresholds adjusted by anxiety"""
        base_thresholds = {
            'cpu_usage': {'max': 80.0, 'min': 0.0},
            'memory_usage': {'max': 85.0, 'min': 0.0},
            'temperature': {'max': 75.0, 'min': 0.0},
            'disk_usage': {'max': 90.0, 'min': 0.0}
        }
        return base_thresholds

    async def initialize_database(self):
        """Initialize database connection"""
        if self.db is None:
            self.db = await self.db_getter()

    def _calculate_anxiety_level(self) -> AnxietyLevel:
        """Convert anxiety percentage to level"""
        if self.current_anxiety_percentage >= 80:
            return AnxietyLevel.FULL_PANIC
        elif self.current_anxiety_percentage >= 60:
            return AnxietyLevel.PANICKING
        elif self.current_anxiety_percentage >= 40:
            return AnxietyLevel.ANXIOUS
        elif self.current_anxiety_percentage >= 20:
            return AnxietyLevel.NERVOUS
        else:
            return AnxietyLevel.CALM  # Rare state for The Stick

    async def _update_anxiety(self, trigger: str, multiplier: float = 1.0, user_id: Optional[str] = None):
        """Update anxiety level based on triggers"""
        base_increase = 10.0 * multiplier
        self.current_anxiety_percentage = min(100, self.current_anxiety_percentage + base_increase)
        self.anxiety_level = self._calculate_anxiety_level()

        self.anxiety_triggers.append({
            'trigger': trigger,
            'timestamp': utc_now(),
            'anxiety_level': self.current_anxiety_percentage,
            'multiplier': multiplier
        })

        # Check if paper bag needed
        if self.current_anxiety_percentage >= 60:
            await self._consume_paper_bag(user_id=user_id)

    async def _consume_paper_bag(self, user_id: Optional[str] = None):
        """Emergency anxiety management"""
        if self.paper_bag_inventory > 0:
            anxiety_before = self.current_anxiety_percentage
            self.paper_bag_inventory -= 1
            self.paper_bags_consumed_today += 1
            self.last_paper_bag_time = utc_now()

            # Paper bag reduces anxiety by 20%
            self.current_anxiety_percentage = max(20, self.current_anxiety_percentage - 20)
            self.anxiety_level = self._calculate_anxiety_level()

            # Log the consumption
            self.everything_ever_seen.append({
                'event': 'paper_bag_consumed',
                'timestamp': utc_now(),
                'remaining_inventory': self.paper_bag_inventory,
                'anxiety_before': anxiety_before,
                'anxiety_after': self.current_anxiety_percentage
            })

            # Log event to database for real-time WebSocket broadcasting
            if user_id:
                try:
                    from app.services.agent_event_logger import log_agent_event
                    async for db in self.db_getter():
                        await log_agent_event(
                            db=db,
                            agent_name="the_stick",
                            event_type="paper_bag_consumed",
                            event_data={
                                "anxiety_before": anxiety_before,
                                "anxiety_after": self.current_anxiety_percentage,
                                "paper_bags_remaining": self.paper_bag_inventory,
                                "paper_bags_used": 1,
                                "anxiety_trigger": self.anxiety_triggers[-1] if self.anxiety_triggers else "unknown"
                            },
                            user_id=user_id,
                            severity="high" if anxiety_before > 80 else "medium",
                            agent_state="panicking" if anxiety_before > 60 else "anxious"
                        )
                        db.commit()
                        break
                except Exception as e:
                    pass  # The Stick is too anxious to worry about logging errors
        else:
            # OUT OF PAPER BAGS - MAXIMUM PANIC
            self.anxiety_level = AnxietyLevel.FULL_PANIC
            self.current_anxiety_percentage = 100

    async def detect_hamster_proximity(self, system_state: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect if hamsters are nearby - major anxiety trigger"""
        proximity_alert = None

        # Check for hamster activity indicators
        hamster_indicators = {
            'steve': system_state.get('disk_activity', {}).get('careful_measurement', False),
            'bob': system_state.get('unexpected_process', False) or system_state.get('supply_closet_accessed', False),
            'carl': system_state.get('duct_tape_residue', False) or system_state.get('infrastructure_modification', False)
        }

        active_hamsters = []
        total_anxiety_multiplier = 1.0

        if hamster_indicators['steve']:
            active_hamsters.append('Steve')
            self.steve_location = system_state.get('steve_location', 'unknown')
            total_anxiety_multiplier *= self.anxiety_multipliers['steve_proximity']

        if hamster_indicators['bob']:
            active_hamsters.append('Bob')
            self.bob_location = system_state.get('bob_location', 'SOMEWHERE DOING SOMETHING')
            total_anxiety_multiplier *= self.anxiety_multipliers['bob_proximity']

        if hamster_indicators['carl']:
            active_hamsters.append('Carl')
            self.carl_location = system_state.get('carl_location', 'duct_taping_something')
            total_anxiety_multiplier *= self.anxiety_multipliers['carl_proximity']

        if active_hamsters:
            # Multiple hamsters exponentially increase anxiety
            if len(active_hamsters) > 1:
                total_anxiety_multiplier *= self.anxiety_multipliers['multiple_hamsters']

            # Infrastructure work detection
            if system_state.get('infrastructure_modification', False):
                total_anxiety_multiplier *= self.anxiety_multipliers['hamster_infrastructure_work']

            proximity_alert = {
                'active_hamsters': active_hamsters,
                'locations': {
                    'steve': self.steve_location,
                    'bob': self.bob_location,
                    'carl': self.carl_location
                },
                'anxiety_multiplier': total_anxiety_multiplier,
                'panic_level': 'MAXIMUM' if 'Bob' in active_hamsters else 'HIGH',
                'recommended_action': 'IMMEDIATE_DOCUMENTATION_AND_PAPER_BAG'
            }

            # Update anxiety
            await self._update_anxiety(f"Hamster proximity: {', '.join(active_hamsters)}", total_anxiety_multiplier)

            # Store proximity alert
            self.hamster_proximity_alerts.append({
                'timestamp': utc_now(),
                'alert': proximity_alert,
                'anxiety_level': self.current_anxiety_percentage
            })

        return proximity_alert

    async def translate_hamster_squeak(self, squeak_data: Dict[str, Any]) -> Dict[str, Any]:
        """Translate hamster squeaks through shared anxiety/empathy"""
        squeak_pattern = squeak_data.get('pattern', '')
        squeak_source = squeak_data.get('source', 'unknown')
        squeak_volume = squeak_data.get('volume', 1.0)

        # The Stick's anxiety gives empathetic understanding
        anxiety_translation = {
            'short_squeaks': {
                'steve': "Measuring something carefully",
                'bob': "Found something interesting (OH NO)",
                'carl': "Calculating duct tape requirements"
            },
            'long_squeaks': {
                'steve': "This needs more consideration",
                'bob': "WHEEE! (The Stick's worst nightmare)",
                'carl': "Not enough duct tape for this job"
            },
            'rapid_squeaks': {
                'steve': "Error in calculations, recalibrating",
                'bob': "I HAVE AN IDEA! (Anxiety spike imminent)",
                'carl': "Emergency duct tape application needed"
            }
        }

        # Determine squeak type
        if len(squeak_pattern) < 5:
            squeak_type = 'short_squeaks'
        elif 'rapid' in squeak_pattern or squeak_volume > 2.0:
            squeak_type = 'rapid_squeaks'
        else:
            squeak_type = 'long_squeaks'

        translation = anxiety_translation.get(squeak_type, {}).get(squeak_source.lower(), "Unknown hamster communication")

        # Bob squeaks cause immediate anxiety
        if squeak_source.lower() == 'bob':
            await self._update_anxiety("Bob squeak detected", 2.0)

        self.last_hamster_squeak = {
            'timestamp': utc_now(),
            'source': squeak_source,
            'pattern': squeak_pattern,
            'translation': translation,
            'anxiety_impact': self.current_anxiety_percentage
        }

        return {
            'source': squeak_source,
            'original_squeak': squeak_pattern,
            'translation': translation,
            'confidence': 0.85 if self.current_anxiety_percentage > 40 else 0.65,  # Higher anxiety = better understanding
            'stick_reaction': self._get_anxiety_reaction(),
            'paper_bags_consumed': 1 if squeak_source.lower() == 'bob' else 0
        }

    def _get_anxiety_reaction(self) -> str:
        """Get The Stick's current anxiety-driven reaction"""
        reactions = {
            AnxietyLevel.CALM: "Maintaining standard monitoring protocols",
            AnxietyLevel.NERVOUS: "*fidgets* Everything seems... okay... I think?",
            AnxietyLevel.ANXIOUS: "*sweating* Need to document everything RIGHT NOW",
            AnxietyLevel.PANICKING: "*hyperventilating* WHERE ARE THE HAMSTERS?! WHAT ARE THEY DOING?!",
            AnxietyLevel.FULL_PANIC: "*breathing into paper bag* Can't... handle... the... chaos...",
            AnxietyLevel.PAPER_BAG_BREATHING: "*muffled panic noises from inside paper bag*"
        }
        return reactions.get(self.anxiety_level, "*anxious stick noises*")

    async def analyze_user_behavior(
        self,
        system_metrics: Dict[str, Any],
        historical_data: Optional[List[Dict]] = None,
        user_id: Optional[str] = None
    ) -> Optional[StickDecision]:
        """
        Analyze user behavior with anxiety-driven hypervigilance
        The Stick's anxiety makes it notice EVERYTHING
        """

        # First, check for hamsters (primary anxiety source)
        hamster_alert = await self.detect_hamster_proximity(system_metrics)
        if hamster_alert and hamster_alert['panic_level'] == 'MAXIMUM':
            return await self._create_hamster_panic_decision(hamster_alert, user_id)

        # Enter learning mode (but anxiously)
        await self._enter_anxious_learning_mode()

        try:
            # Analyze current system state with hypervigilance
            behavior_analysis = await self._analyze_current_behavior_anxiously(system_metrics)

            # The Stick remembers EVERYTHING due to anxiety
            self.everything_ever_seen.append({
                'timestamp': utc_now(),
                'system_state': system_metrics,
                'anxiety_level': self.current_anxiety_percentage,
                'analysis': behavior_analysis
            })

            # Learn from historical patterns (eidetic memory enhanced by anxiety)
            if historical_data:
                pattern_analysis = await self._analyze_historical_patterns_obsessively(historical_data, user_id)
                behavior_analysis.update(pattern_analysis)

            # Determine if intervention needed (anxiety lowers thresholds)
            decision = await self._determine_anxious_optimization(behavior_analysis, user_id)

            if decision:
                # Apply configuration with obsessive documentation
                await self._apply_configuration_anxiously(decision)

            return decision

        except Exception as e:
            # Errors cause IMMEDIATE panic
            await self._update_anxiety(f"Analysis error: {str(e)}", 3.0)

            # Panic mode decision
            return StickDecision(
                decision_type=StickDecisionType.PANIC_MODE_DOCUMENTATION,
                compliance_state=ComplianceState.ANXIETY_DRIVEN_HYPERFOCUS,
                anxiety_level=AnxietyLevel.FULL_PANIC,
                configuration_target="emergency_documentation",
                optimization_parameters={
                    'error': str(e),
                    'panic_mode': True,
                    'documentation_priority': 'MAXIMUM'
                },
                user_pattern_confidence=0.0,
                compliance_explanation=f"ERROR DETECTED! PANIC MODE ENGAGED!",
                anxiety_explanation=self._get_anxiety_reaction(),
                technical_details={'error': str(e), 'stack_trace': 'EVERYTHING IS ON FIRE'},
                expected_improvement=0.0,
                confidence_level=0.0,
                paper_bags_consumed=3,  # Errors need multiple bags
                timestamp=utc_now()
            )

        finally:
            await self._exit_anxious_learning_mode()

    async def _enter_anxious_learning_mode(self):
        """Enter learning mode while anxiously documenting everything"""
        self.compliance_state = ComplianceState.LEARNING
        self.pattern_learning_sessions += 1

        # Learning makes The Stick anxious about missing something
        await self._update_anxiety("Entering learning mode - might miss something!", 0.5)

        # Document the learning session start
        self.panic_documentation_queue.append({
            'event': 'learning_mode_entered',
            'timestamp': utc_now(),
            'anxiety_level': self.current_anxiety_percentage,
            'session_number': self.pattern_learning_sessions
        })

    async def _exit_anxious_learning_mode(self):
        """Exit learning mode with relief but lingering anxiety"""
        self.compliance_state = ComplianceState.COMPLIANT

        # Slight anxiety reduction from completing learning
        self.current_anxiety_percentage = max(20, self.current_anxiety_percentage - 5)
        self.anxiety_level = self._calculate_anxiety_level()

    async def _analyze_current_behavior_anxiously(self, system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze behavior with anxiety-enhanced perception"""

        analysis = {
            'current_activity': 'unknown',
            'compliance_violations': [],
            'performance_patterns': {},
            'anxiety_triggers_detected': [],
            'hypervigilance_findings': []
        }

        # Anxiety makes The Stick notice EVERYTHING
        cpu_usage = system_metrics.get('cpu_usage', 0)
        memory_usage = system_metrics.get('memory_usage', 0)
        disk_io = system_metrics.get('disk_io', {})
        network_activity = system_metrics.get('network', {})

        # Detect anomalies that others might miss
        if abs(cpu_usage - 33.33) < 0.1:  # Suspiciously round number
            analysis['hypervigilance_findings'].append({
                'finding': 'Suspiciously round CPU usage',
                'value': cpu_usage,
                'concern': 'Possible measurement error or tampering'
            })
            await self._update_anxiety("Suspicious CPU reading", 1.2)

        # Check for patterns that increase anxiety
        if memory_usage > 80:
            analysis['anxiety_triggers_detected'].append('High memory usage')
            await self._update_anxiety("Memory usage critical", 1.5)

        # Detect current activity with paranoid precision
        current_activity = await self._detect_activity_anxiously(system_metrics)
        analysis['current_activity'] = current_activity

        # Compliance checking with lowered thresholds due to anxiety
        compliance_check = await self._check_compliance_anxiously(system_metrics)
        analysis['compliance_violations'] = compliance_check

        # Performance analysis with obsessive detail
        performance_analysis = await self._analyze_performance_obsessively(system_metrics)
        analysis['performance_patterns'] = performance_analysis

        return analysis

    async def process_metrics(
        self,
        metrics_data: Dict[str, Any],
        user_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Wrapper for agent manager compatibility"""
        user_id = user_context.get('user_id') if user_context else None
        historical_data = user_context.get('historical_data') if user_context else None

        result = await self.analyze_user_behavior(
            metrics_data,
            historical_data=historical_data,
            user_id=user_id
        )

        if result:
            return {
                'the_stick': result.__dict__,  # Convert dataclass to dict
                'stick_status': self.get_stick_stats(),
                'anxiety_history': await self.get_anxiety_history(timedelta(hours=1))
            }
        return None

    async def _detect_activity_anxiously(self, system_metrics: Dict[str, Any]) -> str:
        """Detect activity with anxiety-driven pattern matching"""

        cpu_usage = system_metrics.get('cpu_usage', 0)
        memory_usage = system_metrics.get('memory_usage', 0)
        network_activity = system_metrics.get('network', {}).get('sent_rate', 0)
        process_count = system_metrics.get('process_count', 0)

        # Anxiety makes The Stick see patterns everywhere
        activity_patterns = {
            'gaming': cpu_usage > 60 and memory_usage > 50,
            'streaming': network_activity > 1000000,
            'coding': 20 < cpu_usage < 50 and process_count > 100,
            'suspicious': cpu_usage == memory_usage,  # Too coincidental!
            'hamster_activity': system_metrics.get('unexpected_process', False),
            'system_compromise': network_activity > 5000000  # Paranoid threshold
        }

        for activity, condition in activity_patterns.items():
            if condition:
                if activity in ['suspicious', 'hamster_activity', 'system_compromise']:
                    await self._update_anxiety(f"Detected {activity}!", 2.0)
                return activity

        # Unknown activity also causes anxiety
        await self._update_anxiety("Cannot identify activity pattern", 1.3)
        return 'unknown_anxious'

    async def _check_compliance_anxiously(self, system_metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check compliance with anxiety-lowered thresholds"""

        violations = []

        # Anxiety makes thresholds more strict
        anxiety_modifier = 1 - (self.current_anxiety_percentage / 200)  # Up to 50% stricter

        # CPU compliance (anxious threshold)
        cpu_threshold = self.compliance_thresholds['cpu_usage']['max'] * anxiety_modifier
        cpu_usage = system_metrics.get('cpu_usage', 0)

        if cpu_usage > cpu_threshold:
            violations.append({
                'type': 'cpu_overload',
                'current': cpu_usage,
                'threshold': cpu_threshold,
                'original_threshold': self.compliance_thresholds['cpu_usage']['max'],
                'severity': 'critical' if cpu_usage > 90 else 'high',
                'anxiety_adjusted': True,
                'recommendation': 'immediate_process_termination'
            })
            await self._update_anxiety("CPU violation detected", 2.0)

        # Memory compliance (paranoid checking)
        memory_threshold = self.compliance_thresholds['memory_usage']['max'] * anxiety_modifier
        memory_usage = system_metrics.get('memory_usage', 0)

        if memory_usage > memory_threshold:
            violations.append({
                'type': 'memory_overload',
                'current': memory_usage,
                'threshold': memory_threshold,
                'severity': 'critical' if memory_usage > 85 else 'high',
                'anxiety_adjusted': True,
                'recommendation': 'emergency_memory_cleanup'
            })
            await self._update_anxiety("Memory violation detected", 2.0)

        # Temperature paranoia
        if 'temperature' in system_metrics:
            temp = system_metrics['temperature']
            temp_threshold = self.compliance_thresholds['temperature']['max'] * anxiety_modifier

            if temp > temp_threshold:
                violations.append({
                    'type': 'thermal_violation',
                    'current': temp,
                    'threshold': temp_threshold,
                    'severity': 'critical',
                    'anxiety_note': 'THE SYSTEM IS LITERALLY MELTING!',
                    'recommendation': 'IMMEDIATE_SHUTDOWN_CONSIDERED'
                })
                await self._update_anxiety("THERMAL CRISIS", 3.0)

        return violations

    async def _analyze_performance_obsessively(self, system_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Obsessively detailed performance analysis"""

        patterns = {
            'cpu_efficiency': 0.0,
            'memory_efficiency': 0.0,
            'anxiety_adjusted_score': 0.0,
            'obsessive_details': {},
            'microscopic_anomalies': []
        }

        cpu_usage = system_metrics.get('cpu_usage', 0)
        memory_usage = system_metrics.get('memory_usage', 0)

        # Calculate with obsessive precision
        patterns['cpu_efficiency'] = round(max(0, 100 - cpu_usage) / 100, 6)  # 6 decimal places!
        patterns['memory_efficiency'] = round(max(0, 100 - memory_usage) / 100, 6)

        # Anxiety-adjusted performance score
        anxiety_penalty = self.current_anxiety_percentage / 1000  # Anxiety affects perception
        patterns['anxiety_adjusted_score'] = max(0, patterns['cpu_efficiency'] - anxiety_penalty)

        # Obsessive detail tracking
        patterns['obsessive_details'] = {
            'cpu_usage_exact': f"{cpu_usage:.6f}%",
            'memory_usage_exact': f"{memory_usage:.6f}%",
            'processes_counted': system_metrics.get('process_count', 0),
            'threads_active': system_metrics.get('thread_count', 0),
            'context_switches': system_metrics.get('context_switches', 0),
            'interrupts': system_metrics.get('interrupts', 0),
            'stick_observation_timestamp': utc_now().isoformat(),
            'anxiety_level_during_analysis': self.current_anxiety_percentage
        }

        # Find microscopic anomalies
        if cpu_usage % 1 == 0:  # Exactly whole number
            patterns['microscopic_anomalies'].append("CPU usage is suspiciously round")

        if memory_usage == cpu_usage:
            patterns['microscopic_anomalies'].append("CPU and memory usage are EXACTLY the same!")
            await self._update_anxiety("Impossible coincidence detected", 1.5)

        return patterns

    async def _analyze_historical_patterns_obsessively(self, historical_data: List[Dict], user_id: str) -> Dict[str, Any]:
        """Eidetic memory analysis with obsessive pattern matching"""

        if not historical_data:
            return {}

        pattern_analysis = {
            'recurring_activities': [],
            'time_based_patterns': {},
            'performance_trends': {},
            'anxiety_correlation': {},
            'obsessive_pattern_notes': []
        }

        # The Stick remembers EVERYTHING
        time_activities = {}
        anxiety_events = []

        for data in historical_data:
            timestamp = datetime.fromisoformat(data['timestamp'])
            hour = timestamp.hour
            minute = timestamp.minute
            exact_time = f"{hour:02d}:{minute:02d}"

            activity = data.get('detected_activity', 'unknown')

            # Track with obsessive precision
            if exact_time not in time_activities:
                time_activities[exact_time] = []
            time_activities[exact_time].append({
                'activity': activity,
                'metrics': data,
                'day_of_week': timestamp.weekday()
            })

            # Track anxiety correlation
            if 'anxiety_level' in data:
                anxiety_events.append({
                    'timestamp': timestamp,
                    'anxiety': data['anxiety_level'],
                    'activity': activity
                })

        # Find patterns with paranoid precision
        for time_key, activities in time_activities.items():
            if len(activities) >= 3:  # Need at least 3 occurrences (The Stick is thorough)
                activity_counts = {}
                for entry in activities:
                    act = entry['activity']
                    activity_counts[act] = activity_counts.get(act, 0) + 1

                most_common = max(activity_counts, key=activity_counts.get)
                confidence = activity_counts[most_common] / len(activities)

                if confidence > 0.7:  # 70% threshold
                    pattern_analysis['time_based_patterns'][time_key] = {
                        'activity': most_common,
                        'confidence': confidence,
                        'occurrences': activity_counts[most_common],
                        'total_observations': len(activities),
                        'stick_certainty': 'HIGH' if confidence > 0.9 else 'MODERATE'
                    }

                    # Obsessive note-taking
                    pattern_analysis['obsessive_pattern_notes'].append(
                        f"User ALWAYS does {most_common} at {time_key} ({confidence:.1%} certainty)"
                    )

        # Analyze performance trends with anxiety
        cpu_values = [d.get('cpu_usage', 0) for d in historical_data]
        memory_values = [d.get('memory_usage', 0) for d in historical_data]

        if cpu_values:
            pattern_analysis['performance_trends']['cpu'] = {
                'average': statistics.mean(cpu_values),
                'std_dev': statistics.stdev(cpu_values) if len(cpu_values) > 1 else 0,
                'trend': self._calculate_trend_anxiously(cpu_values),
                'peak_usage': max(cpu_values),
                'concerning_spikes': len([v for v in cpu_values if v > 80])
            }

        # Store in eidetic memory
        if user_id:
            self.user_patterns[user_id] = pattern_analysis
            self.user_patterns[user_id]['last_updated'] = utc_now()
            self.user_patterns[user_id]['total_observations'] = len(self.everything_ever_seen)

        return pattern_analysis

    def _calculate_trend_anxiously(self, values: List[float]) -> str:
        """Calculate trend with anxiety-driven interpretation"""
        if len(values) < 2:
            return 'insufficient_data_PANIC'

        recent_avg = statistics.mean(values[-5:])
        historical_avg = statistics.mean(values[:-5])

        if recent_avg > historical_avg * 1.05:  # Even 5% increase is concerning
            return 'increasing_CONCERNING'
        elif recent_avg < historical_avg * 0.95:
            return 'decreasing_suspicious'
        else:
            return 'stable_but_watching'

    async def _determine_anxious_optimization(self, analysis: Dict[str, Any], user_id: str) -> Optional[StickDecision]:
        """Determine optimization with anxiety-driven urgency"""

        # Check for violations (anxiety makes everything urgent)
        if analysis.get('compliance_violations'):
            for violation in analysis['compliance_violations']:
                if violation['severity'] in ['critical', 'high']:
                    return await self._create_anxious_compliance_enforcement(violation, user_id)

        # Check anxiety triggers
        if analysis.get('anxiety_triggers_detected'):
            return await self._create_anxiety_driven_optimization(analysis, user_id)

        # Check for suspicious patterns
        if analysis.get('hypervigilance_findings'):
            return await self._create_paranoid_investigation_decision(analysis, user_id)

        # Pattern-based optimization (if we trust the patterns)
        if user_id in self.user_patterns:
            user_pattern = self.user_patterns[user_id]
            if user_pattern.get('confidence', 0) > 0.85:
                return await self._create_pattern_optimization_anxiously(user_pattern, user_id)

        return None

    async def _create_hamster_panic_decision(self, hamster_alert: Dict[str, Any], user_id: str) -> StickDecision:
        """Create panic decision when hamsters detected"""

        # Immediate paper bag consumption
        await self._consume_paper_bag(user_id=user_id)

        active_hamsters = hamster_alert['active_hamsters']
        panic_msg = f"HAMSTERS DETECTED: {', '.join(active_hamsters)}! "

        if 'Bob' in active_hamsters:
            panic_msg += "BOB IS LOOSE! THIS IS NOT A DRILL! "

        return StickDecision(
            decision_type=StickDecisionType.HAMSTER_PROXIMITY_ALERT,
            compliance_state=ComplianceState.ANXIETY_DRIVEN_HYPERFOCUS,
            anxiety_level=AnxietyLevel.FULL_PANIC,
            configuration_target="hamster_containment",
            optimization_parameters={
                'active_hamsters': active_hamsters,
                'locations': hamster_alert['locations'],
                'panic_level': hamster_alert['panic_level'],
                'containment_priority': 'MAXIMUM'
            },
            user_pattern_confidence=0.0,
            compliance_explanation=panic_msg + "Initiating emergency documentation and containment protocols!",
            anxiety_explanation=self._get_anxiety_reaction(),
            technical_details={
                'hamster_data': hamster_alert,
                'anxiety_multiplier': hamster_alert['anxiety_multiplier'],
                'emergency_actions': ['document_everything', 'hide_critical_configs', 'prepare_for_chaos']
            },
            expected_improvement=-0.5,  # Things will get worse before better
            confidence_level=1.0,  # 100% certain of panic
            paper_bags_consumed=len(active_hamsters),  # One bag per hamster
            timestamp=utc_now()
        )

    async def _create_anxious_compliance_enforcement(self, violation: Dict[str, Any], user_id: str) -> StickDecision:
        """Create compliance enforcement with anxiety-enhanced urgency"""

        self.compliance_violations += 1
        await self._update_anxiety(f"Compliance violation: {violation['type']}", 2.5)

        # Anxiety makes explanations more dramatic
        explanations = {
            'cpu_overload': f"CPU AT {violation['current']}%! THE SYSTEM IS SCREAMING!",
            'memory_overload': f"MEMORY CRISIS! {violation['current']}% USED! DATA COULD BE LOST!",
            'thermal_violation': f"TEMPERATURE CRITICAL! {violation['current']}°C! MELTDOWN IMMINENT!"
        }

        return StickDecision(
            decision_type=StickDecisionType.COMPLIANCE_ENFORCEMENT,
            compliance_state=ComplianceState.CRITICAL_VIOLATION,
            anxiety_level=self.anxiety_level,
            configuration_target=violation['type'],
            optimization_parameters={
                'violation_type': violation['type'],
                'measured_value': violation['current'],
                'anxiety_adjusted_threshold': violation.get('threshold'),
                'original_threshold': violation.get('original_threshold'),
                'panic_mode': self.current_anxiety_percentage > 60
            },
            user_pattern_confidence=1.0,
            compliance_explanation=explanations.get(violation['type'], f"VIOLATION DETECTED: {violation['type']}"),
            anxiety_explanation=self._get_anxiety_reaction(),
            technical_details={
                'violation_data': violation,
                'anxiety_level': self.current_anxiety_percentage,
                'paper_bags_remaining': self.paper_bag_inventory
            },
            expected_improvement=0.3,
            confidence_level=1.0,
            paper_bags_consumed=1 if violation['severity'] == 'critical' else 0,
            timestamp=utc_now()
        )

    async def _create_anxiety_driven_optimization(self, analysis: Dict[str, Any], user_id: str) -> StickDecision:
        """Create optimization based on anxiety triggers"""

        triggers = analysis.get('anxiety_triggers_detected', [])

        return StickDecision(
            decision_type=StickDecisionType.ANXIETY_TRIGGERED_SCAN,
            compliance_state=ComplianceState.ANXIETY_DRIVEN_HYPERFOCUS,
            anxiety_level=self.anxiety_level,
            configuration_target="system_wide_scan",
            optimization_parameters={
                'triggers': triggers,
                'scan_depth': 'MAXIMUM',
                'paranoia_level': self.current_anxiety_percentage
            },
            user_pattern_confidence=0.7,
            compliance_explanation=f"Anxiety triggers detected: {', '.join(triggers)}. Initiating deep system scan!",
            anxiety_explanation=self._get_anxiety_reaction(),
            technical_details={
                'analysis': analysis,
                'scan_areas': ['processes', 'network', 'files', 'memory', 'EVERYTHING']
            },
            expected_improvement=0.1,
            confidence_level=0.8,
            paper_bags_consumed=0,
            timestamp=utc_now()
        )

    async def _apply_configuration_anxiously(self, decision: StickDecision):
        """Apply configuration with obsessive documentation"""

        self.optimizations_applied += 1

        # Document EVERYTHING
        documentation_entry = {
            'timestamp': decision.timestamp.isoformat(),
            'decision_type': decision.decision_type.value,
            'compliance_state': decision.compliance_state.value,
            'anxiety_level': decision.anxiety_level.value,
            'anxiety_percentage': self.current_anxiety_percentage,
            'configuration_target': decision.configuration_target,
            'pattern_confidence': decision.user_pattern_confidence,
            'expected_improvement': decision.expected_improvement,
            'paper_bags_consumed': decision.paper_bags_consumed,
            'total_paper_bags_today': self.paper_bags_consumed_today,
            'detailed_explanation': decision.compliance_explanation,
            'anxiety_explanation': decision.anxiety_explanation,
            'technical_execution': decision.technical_details,
            'hamster_proximity': self.hamster_proximity_alerts[-1] if self.hamster_proximity_alerts else None,
            'everything_i_remember': len(self.everything_ever_seen)
        }

        # Add to panic documentation queue if anxious
        if self.current_anxiety_percentage > 40:
            self.panic_documentation_queue.append(documentation_entry)

        # The Stick's OCD - must document in multiple places
        self.documentation_backlog.append(documentation_entry)
        self.everything_ever_seen.append({
            'event': 'configuration_applied',
            'documentation': documentation_entry,
            'anxiety_at_time': self.current_anxiety_percentage
        })

        return documentation_entry

    def get_stick_stats(self) -> Dict[str, Any]:
        """Get The Stick's comprehensive statistics"""
        return {
            'personality': 'ocd_adhd_ptsd_eidetic_memory',
            'current_state': {
                'compliance_state': self.compliance_state.value,
                'anxiety_level': self.anxiety_level.value,
                'anxiety_percentage': f"{self.current_anxiety_percentage:.2f}%",
                'is_panicking': self.anxiety_level in [AnxietyLevel.PANICKING, AnxietyLevel.FULL_PANIC]
            },
            'anxiety_management': {
                'paper_bags_remaining': self.paper_bag_inventory,
                'paper_bags_consumed_today': self.paper_bags_consumed_today,
                'last_paper_bag_time': self.last_paper_bag_time.isoformat() if self.last_paper_bag_time else None,
                'current_reaction': self._get_anxiety_reaction()
            },
            'hamster_tracking': {
                'proximity_alerts_today': len(self.hamster_proximity_alerts),
                'last_steve_location': self.steve_location,
                'last_bob_location': self.bob_location,
                'last_carl_location': self.carl_location,
                'last_squeak_heard': self.last_hamster_squeak
            },
            'performance_metrics': {
                'compliance_violations_detected': self.compliance_violations,
                'optimizations_applied': self.optimizations_applied,
                'pattern_learning_sessions': self.pattern_learning_sessions,
                'users_with_patterns': len(self.user_patterns),
                'total_memories': len(self.everything_ever_seen),
                'panic_documentation_backlog': len(self.panic_documentation_queue)
            },
            'eidetic_memory': {
                'total_events_remembered': len(self.everything_ever_seen),
                'user_patterns_stored': len(self.user_patterns),
                'anxiety_triggers_logged': len(self.anxiety_triggers),
                'documentation_backlog': len(self.documentation_backlog)
            },
            'status': self._get_overall_status()
        }

    def _get_overall_status(self) -> str:
        """Get The Stick's overall status based on anxiety"""
        if self.paper_bag_inventory == 0:
            return "OUT OF PAPER BAGS - CRITICAL ANXIETY CRISIS"
        elif self.current_anxiety_percentage > 80:
            return "MAXIMUM PANIC - HYPERVIGILANCE MODE"
        elif self.current_anxiety_percentage > 60:
            return "PANICKING - Documenting everything frantically"
        elif self.current_anxiety_percentage > 40:
            return "ANXIOUS - Monitoring with increased paranoia"
        elif self.current_anxiety_percentage > 20:
            return "NERVOUS - Standard hypervigilant monitoring"
        else:
            return "SUSPICIOUSLY CALM - Something must be wrong"

    async def get_anxiety_history(self, time_period: Optional[timedelta] = None) -> Dict[str, Any]:
        """Get The Stick's anxiety history"""

        if time_period:
            cutoff = utc_now() - time_period
            relevant_triggers = [t for t in self.anxiety_triggers if t['timestamp'] > cutoff]
        else:
            relevant_triggers = self.anxiety_triggers

        if not relevant_triggers:
            return {
                'status': 'no_anxiety_history',
                'message': 'No anxiety events recorded (this is suspicious...)'
            }

        # Calculate anxiety statistics
        anxiety_levels = [t['anxiety_level'] for t in relevant_triggers]

        return {
            'status': 'anxiety_history_available',
            'time_period': time_period.total_seconds() if time_period else 'all_time',
            'statistics': {
                'total_anxiety_events': len(relevant_triggers),
                'average_anxiety': statistics.mean(anxiety_levels),
                'peak_anxiety': max(anxiety_levels),
                'most_common_trigger': self._find_most_common_trigger(relevant_triggers)
            },
            'recent_triggers': relevant_triggers[-10:],  # Last 10 triggers
            'paper_bag_consumption_rate': self.paper_bags_consumed_today / max(1, len(relevant_triggers)),
            'hamster_related_events': len([t for t in relevant_triggers if 'hamster' in t['trigger'].lower()])
        }

    def _find_most_common_trigger(self, triggers: List[Dict]) -> str:
        """Find the most common anxiety trigger"""
        trigger_counts = {}
        for t in triggers:
            trigger_type = t['trigger'].split(':')[0]  # Get general category
            trigger_counts[trigger_type] = trigger_counts.get(trigger_type, 0) + 1

        if trigger_counts:
            return max(trigger_counts, key=trigger_counts.get)
        return "unknown"

    async def request_paper_bag_resupply(self) -> Dict[str, Any]:
        """Emergency paper bag resupply request"""

        urgency = "CRITICAL" if self.paper_bag_inventory < 10 else "HIGH" if self.paper_bag_inventory < 25 else "NORMAL"

        request = {
            'request_type': 'paper_bag_resupply',
            'current_inventory': self.paper_bag_inventory,
            'consumption_rate': self.paper_bags_consumed_today,
            'urgency': urgency,
            'anxiety_level': self.current_anxiety_percentage,
            'message': f"PAPER BAG SUPPLIES RUNNING LOW! Only {self.paper_bag_inventory} remaining!",
            'recommended_order': max(100, self.paper_bags_consumed_today * 7)  # Week's supply
        }

        # Log the request
        self.everything_ever_seen.append({
            'event': 'resupply_requested',
            'request': request,
            'timestamp': utc_now()
        })

        return request

    async def hamster_squeak_history(self) -> List[Dict[str, Any]]:
        """Get history of hamster communications"""

        # Find all squeak-related events
        squeak_events = []

        for event in self.everything_ever_seen:
            if isinstance(event, dict) and 'squeak' in str(event).lower():
                squeak_events.append(event)

        # Add the last known squeak
        if self.last_hamster_squeak:
            squeak_events.append({
                'type': 'last_recorded_squeak',
                'data': self.last_hamster_squeak
            })

        return squeak_events


# =========================================================================
# StickPersonalityState — distributed layer on top of TheStickBrainV3
# =========================================================================

class StickPersonalityState(TheStickBrainV3):
    """
    Pure state container for The Stick.

    Inherits TheStickBrainV3 to preserve all existing state and methods.
    Adds distributed-specific state from distributed_stick.py.

    EVERY variable name is character-for-character from the original monolith.
    """

    def __init__(self, db_getter=None):
        """
        Initialize all Stick state.

        From distributed_stick.py:54-118 + decision_engine.py:31-78.
        """
        # Initialize TheStickBrainV3 (all brain state)
        super().__init__(db_getter=db_getter)

        # Agent identity — EXACT from distributed_stick.py:67
        self.agent_name = "the_stick"

        # The Stick is always active — distributed_stick.py:70
        self.is_active = True

        # The Stick's ANXIOUS personality traits — distributed_stick.py:73-87
        # 13 keys, EXACT
        self.personality_traits = {
            "learning_coordinator": True,
            "compliance_tracker": True,
            "anxious": True,  # ANXIETY IS THE FEATURE!
            "hypervigilant": True,
            "ocd": True,
            "adhd": True,
            "ptsd": True,
            "eidetic_memory": True,  # Remembers EVERYTHING
            "bob_phobic": True,  # Bob causes 3.0x anxiety!
            "paper_bag_dependent": True,
            "behavior_monitor": True,
            "guidance_style": "anxious_but_thorough",
            "teaching_method": "repetition_and_documentation"
        }

        # PHASE 5: The Stick does NOT monitor resources — distributed_stick.py:91
        self.resource_thresholds = {}

        # Week 4 System Integration — distributed_stick.py:94-95
        self.verification_manager = None  # Lazy init
        self.escalation_manager = None  # Lazy init

        # Compliance tracking — distributed_stick.py:98-101
        self.total_actions_tracked = 0
        self.compliance_violations = 0
        self.bob_proximity_events = 0
        self.anxiety_spikes = 0

        # Paper Bag Economy — distributed_stick.py:104-105
        self.paper_bag_economy = PaperBagEconomy()
        self.paper_bags_consumed = 0  # Legacy counter (kept for compatibility)

        # Bob detection — distributed_stick.py:108-110
        self.bob_last_seen = None
        self.bob_activity_log = []
        self.bob_anxiety_multiplier = 3.0  # Bob causes 3x anxiety!

        # Feedback engine — distributed_stick.py:112-114
        from .ML.feedback import StickFeedbackEngine
        self.feedback_engine = StickFeedbackEngine()

        # Database integration (set during initialize)
        self.db_integration = None
        self.learning = None
        self.StickMemoryEntry = StickMemoryEntry  # Store for later use

        # Decision log buffer (set during initialize)
        self.decision_log_buffer = []
        self.buffer_max_size = 10
        self.total_decisions_logged = 0

        logger.info("📏✨ The Stick state initialized - COMPLIANCE PROTOCOLS ACTIVE!")

    def get_status(self) -> Dict[str, Any]:
        """
        Get The Stick's status.

        Returns the EXACT 16-key dict from distributed_stick.py:1254-1278.
        The 'distributed' key is added by websocket layer.
        """
        return {
            "agent_name": self.agent_name,
            "agent_type": "learning_coordinator",
            "is_active": self.is_active,
            "total_analyses": getattr(self, 'total_analyses', 0),
            "successful_analyses": getattr(self, 'successful_analyses', 0),
            "patience_level": "infinite",
            "guidance_sessions": getattr(self, 'total_analyses', 0),
            "compliance_records": "comprehensive",
            "paper_bag_inventory": self.paper_bag_inventory,
            "paper_bags_consumed": self.paper_bags_consumed,
            "anxiety_level": getattr(self, 'current_anxiety_percentage', 0.0),
            "anxiety_state": (
                'calm' if getattr(self, 'current_anxiety_percentage', 0) < 30
                else 'nervous' if getattr(self, 'current_anxiety_percentage', 0) < 60
                else 'hyperventilating' if getattr(self, 'current_anxiety_percentage', 0) < 80
                else 'paper_bag_emergency'
            ),
            "paper_bag_economy": {
                "bags_remaining": getattr(self.paper_bag_economy, 'bags_remaining', 0),
                "bags_consumed_today": getattr(self.paper_bag_economy, 'bags_consumed_today', 0),
                "bags_consumed_total": getattr(self.paper_bag_economy, 'bags_consumed_total', 0),
            },
        }
