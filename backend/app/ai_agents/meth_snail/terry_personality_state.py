"""
Terry the Meth Snail — Personality State
=========================================

Everything that makes Terry WHO HE IS.

Owns: jitter levels, caffeine tracking, shell spin incidents,
personality traits, override tracking, energy drink stats.

No decisions. No messaging. No inheritance.
The ML pipeline reads and writes this.
The websocket reads this.
Nobody inherits from this.
"""

import logging
import random
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from dataclasses import asdict

from .data_types import (
    OptimizationPriority,
    ShellSpinIncident,
    EnergyDrinkAuthorization,
    EnergyDrinkType,
    JitterLevel
)
from .database_integration import MethSnailDatabaseIntegration

logger = logging.getLogger("MethSnail.Personality")


def utc_now() -> datetime:
    """Get current UTC time"""
    from datetime import timezone
    return datetime.now(timezone.utc)


class TerryPersonalityState:
    """
    Terry the Meth Snail's personality and identity state.

    Pure state container. No decisions. No messaging. No base classes.
    """

    def __init__(self, db_getter=None):
        # Database integration for jitter/caffeine persistence
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter

        self.db_integration = None
        self._db_initialized = False

        # Jitter and caffeine state
        self._current_jitter = 0.0
        self._caffeine_level = 0.0
        self._last_caffeine_update = None
        self._jitter_trend = 'stable'

        # Shell spin tracking
        self.shell_spin_incidents: List[ShellSpinIncident] = []
        self.metrics_quality_stats = {
            'cpu_missing_count': 0,
            'memory_missing_count': 0,
            'disk_missing_count': 0,
            'network_missing_count': 0,
            'process_missing_count': 0,
            'invalid_data_count': 0,
            'shell_spins_total': 0
        }

        # Analysis tracking
        self.optimization_history: List[Dict[str, Any]] = []
        self.current_priority = OptimizationPriority.BALANCED
        self.total_analyses = 0
        self.successful_analyses = 0

        # Override tracking (from distributed file)
        self.total_overrides = 0
        self.successful_overrides = 0
        self.failed_overrides = 0
        self.override_success_rate = 0.0

        # Energy drink tracking (from distributed file)
        self.energy_drinks_today = 0
        self.shell_spins_today = 0
        self._last_energy_drink_system = None

        # Personality traits (from distributed file)
        self.personality_traits = {
            "speed_obsessed": True,
            "hyperactive": True,
            "shell_spinning_enabled": True,
            "cache_clearing_frequency": "MAXIMUM",
            "energy_drink_powered": True,
            "no_fake_data_tolerance": 0,
            "optimization_priority": "speed",
            "jitter_level": "moderate",
            "trust_level": 0.2
        }

    # === DATABASE INITIALIZATION ===

    async def initialize_database(self):
        """Initialize database connection and load persisted state"""
        if not self._db_initialized:
            self.db_integration = MethSnailDatabaseIntegration(self.db_getter)
            await self.db_integration.initialize()
            self._db_initialized = True

            # Load persisted jitter levels
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

    async def get_database_integration(self):
        """Get or create database integration instance"""
        if self.db_integration is None:
            self.db_integration = MethSnailDatabaseIntegration(self.db_getter)
        return self.db_integration

    # === JITTER / CAFFEINE SYSTEM ===

    async def update_jitter_levels(self, caffeine_change: float = 0.0) -> float:
        """
        Update jitter levels based on caffeine consumption and time.
        Positive caffeine_change = consumption, negative = metabolism.
        """
        now = utc_now()

        self._caffeine_level = max(0, self._caffeine_level + caffeine_change)

        # Time-based decay (~100mg per 5 hours)
        if self._last_caffeine_update:
            hours_since_update = (now - self._last_caffeine_update).total_seconds() / 3600
            self._caffeine_level = max(0, self._caffeine_level - (hours_since_update * 20))

        # Calculate jitter (0.0 to 1.0)
        caffeine_effect = min(self._caffeine_level, 400) / 1000
        random_effect = (random.random() - 0.5) * 0.1
        new_jitter = max(0, min(1, 0.1 + caffeine_effect + random_effect))

        # Update trend
        if new_jitter > self._current_jitter + 0.05:
            self._jitter_trend = 'increasing'
        elif new_jitter < self._current_jitter - 0.05:
            self._jitter_trend = 'decreasing'

        self._current_jitter = new_jitter
        self._last_caffeine_update = now

        # Persist to database
        if self._db_initialized:
            try:
                await self.db_integration.update_jitter_levels("system", {
                    'current_jitter_level': self._current_jitter,
                    'peak_jitter_level': max(self._current_jitter, 0.4),
                    'baseline_jitter_level': 0.1,
                    'caffeine_level_mg': self._caffeine_level,
                    'is_decaffeinated': self._caffeine_level < 10,
                    'time_since_caffeine_minutes': (
                        (now - self._last_caffeine_update).total_seconds() / 60
                        if self._last_caffeine_update else None
                    ),
                    'shell_spin_probability': 0.05 + (self._current_jitter * 0.1),
                    'optimization_effectiveness': 0.9 - (self._current_jitter * 0.4),
                    'focus_level': 0.8 - (self._current_jitter * 0.5),
                    'hypercaffeinated': self._caffeine_level > 400,
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

    async def _calculate_current_jitter_level(self, user_id: str) -> float:
        """Calculate current jitter level from database"""
        try:
            db_integration = await self.get_database_integration()
            jitter_data = await db_integration.get_recent_jitter_levels(int(user_id), hours=1)

            if jitter_data['status'] == 'success' and jitter_data['jitter_levels']:
                return jitter_data['current_jitter']
            else:
                raise ValueError(f"No jitter level data available for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to calculate jitter level for user {user_id}: {e}")
            raise

    async def _get_current_caffeine_level(self, user_id: str) -> float:
        """Get current caffeine level accounting for metabolism (half-life decay)"""
        try:
            db_integration = await self.get_database_integration()
            consumption_data = await db_integration.get_energy_consumption_history(int(user_id), days=1)

            if consumption_data['status'] != 'success' or not consumption_data['consumption_history']:
                return 0.0

            current_time = utc_now()
            total_current_caffeine = 0.0
            caffeine_half_life_hours = 5.5

            for consumption in consumption_data['consumption_history']:
                consumption_time = datetime.fromisoformat(consumption['consumption_time'])
                hours_elapsed = (current_time - consumption_time).total_seconds() / 3600

                if hours_elapsed >= 0:
                    remaining = consumption['caffeine_mg'] * (0.5 ** (hours_elapsed / caffeine_half_life_hours))
                    total_current_caffeine += remaining

            return total_current_caffeine
        except Exception as e:
            logger.error(f"Failed to get current caffeine level for user {user_id}: {e}")
            raise

    async def _update_caffeine_levels(self, user_id: str, additional_caffeine_mg: float) -> float:
        """Update and return new total caffeine level"""
        try:
            current_level = await self._get_current_caffeine_level(user_id)
            return current_level + additional_caffeine_mg
        except Exception as e:
            logger.error(f"Failed to update caffeine levels for user {user_id}: {e}")
            raise

    async def _calculate_jitter_from_caffeine(self, caffeine_mg: float) -> float:
        """Calculate jitter level from caffeine amount"""
        return min(caffeine_mg / 200.0, 1.0)

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

    # === SHELL SPIN TRACKING ===

    async def record_shell_spin(
        self,
        reason: str,
        missing_metrics: List[str] = None,
        invalid_metrics: List[str] = None,
        user_id: str = None
    ):
        """Record a shell spin incident in personality state"""
        incident = ShellSpinIncident(
            timestamp=utc_now(),
            missing_metrics=missing_metrics or [],
            invalid_metrics=invalid_metrics or [],
            reason=reason,
            user_id=user_id
        )
        self.shell_spin_incidents.append(incident)
        self.metrics_quality_stats['shell_spins_total'] += 1
        logger.warning(f"🐌💫 Shell spin recorded: {reason}")

        # Persist to database
        if user_id and self._db_initialized:
            try:
                from app.services.agent_event_logger import log_agent_event
                db_gen = self.db_getter()
                async for db in db_gen:
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
                logger.error(f"Failed to log shell spin event: {e}")

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

    # === OVERRIDE TRACKING ===

    def record_override_result(self, success: bool):
        """Record whether an override of VIC-20's recommendation succeeded"""
        self.total_overrides += 1
        if success:
            self.successful_overrides += 1
        else:
            self.failed_overrides += 1
        self.override_success_rate = self.successful_overrides / max(1, self.total_overrides)

    # === ENERGY DRINK STATE ===

    async def consume_energy_drink(
        self,
        user_id: str,
        authorization: EnergyDrinkAuthorization,
        actual_caffeine_mg: float
    ) -> Dict[str, Any]:
        """Process energy drink consumption and update caffeine/jitter state"""
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

            warning_message = None
            if new_jitter_level > 0.8:
                warning_message = "WARNING: HYPERCAFFEINATED STATE DETECTED! Consider decaffeination protocol."

            logger.info(f"Energy drink consumed by user {user_id}: {actual_caffeine_mg}mg, jitter: {new_jitter_level:.2f}")

            return {
                'status': 'success',
                'message': f'Energy drink consumed! Jitter: {self._get_jitter_level_name(new_jitter_level)}',
                'caffeine_level_mg': new_caffeine_level,
                'jitter_level': new_jitter_level,
                'warning': warning_message
            }

        except Exception as e:
            logger.error(f"Energy drink consumption failed for user {user_id}: {e}")
            return {
                'status': 'error',
                'message': f'Consumption failed: {e}',
                'jitter_level': await self._calculate_current_jitter_level(user_id)
            }

    async def caffeinated_safety_protocol(self, user_id: str) -> Dict[str, Any]:
        """Check caffeine safety levels and recommend actions"""
        try:
            current_jitter = await self._calculate_current_jitter_level(user_id)
            caffeine_level = await self._get_current_caffeine_level(user_id)

            if current_jitter >= 0.9:
                safety_status, recommendation, action = "CRITICAL", "IMMEDIATE DECAFFEINATION REQUIRED", "emergency_decaffeination"
            elif current_jitter >= 0.7:
                safety_status, recommendation, action = "WARNING", "Consider reducing caffeine intake", "reduce_caffeine"
            elif current_jitter >= 0.4:
                safety_status, recommendation, action = "OPTIMAL", "Caffeine levels optimal for maximum optimization", "maintain_current_level"
            else:
                safety_status, recommendation, action = "SUBOPTIMAL", "Consider energy drink for improved performance", "request_energy_drink"

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
            logger.error(f"Safety protocol check failed for user {user_id}: {e}")
            return {
                'safety_status': "UNKNOWN",
                'error': str(e),
                'recommendation': "Unable to assess - manual intervention required"
            }

    async def _get_time_since_last_drink(self, user_id: str) -> Optional[int]:
        """Get minutes since last energy drink consumption"""
        try:
            db_integration = await self.get_database_integration()
            consumption_data = await db_integration.get_energy_consumption_history(int(user_id), days=1)

            if consumption_data['status'] == 'success' and consumption_data['consumption_history']:
                most_recent = consumption_data['consumption_history'][0]
                last_consumption_time = datetime.fromisoformat(most_recent['consumption_time'])
                minutes_since = int((utc_now() - last_consumption_time).total_seconds() / 60)
                return minutes_since
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get time since last drink for user {user_id}: {e}")
            raise
