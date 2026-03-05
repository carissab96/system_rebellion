"""
Quantum Shadow People — Personality State
===========================================

Pure state container. Holds all QSP identity, quantum state,
paranoia tracking, and network analysis state.

Extracted from distributed_qsp.py (lines 58–112) and
decision_engine.py (lines 48–111).

No Redis. No message bus. No ML pipeline. Just state.
"""

import logging
import asyncio
import psutil
from typing import Dict, Any, Optional
from collections import defaultdict

from app.optimization.resource_monitor import ResourceType
from ..distributed.agent_autonomy import AgentChoiceEngine

from .data_types import QuantumPhaseState, QSPDecisionType, QSPDecision
from .qsp_data_types import ParanoiaLevel

logger = logging.getLogger("QSP.Personality")


class QSPPersonalityState:
    """
    Quantum Shadow People — all mutable state lives here.

    Holds:
    - personality_traits dict
    - Paranoia tracking (level, threats, false alarms, tequila shots)
    - Quantum state (phase, shifts, fixes applied)
    - Network intelligence (interfaces, patterns, thresholds)
    - Choice engine (Week 4 autonomy)
    - Database integration reference

    No inheritance from anything. Composition over inheritance.
    """

    def __init__(self, db_getter=None):
        # Database
        if db_getter is None:
            from app.core.database import get_async_db
            self.db_getter = get_async_db
        else:
            self.db_getter = db_getter

        self.db_integration = None  # Lazy init in initialize()

        # Agent identity
        self.agent_name = "quantum_shadow_people"

        # QSP personality traits
        self.personality_traits = {
            "quantum": True,
            "paranoid": True,
            "tequila_jello_shot_powered": True,
            "network_obsessed": True,
            "security_focused": True,
            "phase_shifting": True,
            "coherence_maintenance": "critical",
            "scan_frequency": "continuous",
            "trust_level": 0.4,  # LOW - TRUST NO ONE!
        }

        # Resource monitoring thresholds
        self.resource_thresholds = {
            ResourceType.NETWORK: 85.0,
        }

        # Choice engine (Week 4 autonomy — LOW trust)
        self.choice_engine = AgentChoiceEngine(
            self.agent_name, self.personality_traits
        )

        # --- Paranoia tracking (from distributed_qsp.py) ---
        self.paranoia_level = ParanoiaLevel.HEALTHY
        self.threats_detected = 0
        self.false_alarms = 0
        self.total_security_scans = 0
        self.quantum_phase_shifts = 0
        self.tequila_shots_today = 0

        # --- Quantum state (from decision_engine.py) ---
        self.quantum_state = QuantumPhaseState.PHASED
        self.quantum_fixes_applied = 0
        self.dimensional_shifts_performed = 0
        self.tequila_jello_shots = 0  # Lifetime total

        # --- Network intelligence (from decision_engine.py) ---
        self.network_interfaces: Dict[str, Any] = {}
        self.network_patterns: Dict[str, Any] = {}
        self.bandwidth_patterns: Dict[str, Any] = {}
        self.packet_loss_history: Dict[str, Any] = {}
        self.connection_patterns = defaultdict(
            lambda: {"count": 0, "last_seen": None}
        )
        self.router_configurations: Dict[str, Any] = {}
        self.interdimensional_threats = []

        self.latency_thresholds = {
            "gaming": 20,
            "streaming": 50,
            "general": 100,
            "critical": 5,
        }

        self.phase_abilities = {
            QuantumPhaseState.CORPOREAL: ["basic_monitoring"],
            QuantumPhaseState.PHASED: ["latency_optimization", "bandwidth_boost"],
            QuantumPhaseState.QUANTUM_ENTANGLED: [
                "phantom_packet_recovery",
                "router_entanglement",
            ],
            QuantumPhaseState.INTERDIMENSIONAL: [
                "threat_detection",
                "dimensional_routing",
            ],
            QuantumPhaseState.VOID_WALKER: ["data_interception", "void_routing"],
            QuantumPhaseState.TEQUILA_JELLO_DIMENSION: [
                "mysterious_fixes",
                "reality_bending",
            ],
        }

        # Update network interfaces from real system data
        self._update_network_interfaces()

        # Analysis counters (used by get_agent_status)
        self.total_analyses = 0
        self.successful_analyses = 0

        logger.info(
            "👻🔮 QSP personality state initialized — "
            "QUANTUM SURVEILLANCE ACTIVE!"
        )

    # === Network Interface Discovery ===

    def _update_network_interfaces(self):
        """Get actual network interface information from psutil."""
        try:
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            for interface, stat in stats.items():
                if stat.isup:
                    self.network_interfaces[interface] = {
                        "speed": stat.speed,
                        "mtu": stat.mtu,
                        "addresses": addrs.get(interface, []),
                    }
        except Exception as e:
            logger.error(f"Failed to update network interfaces: {e}")

    def get_actual_bandwidth_capacity(self) -> float:
        """Get total bandwidth capacity from actual network interfaces (bps)."""
        total_capacity = 0
        for _iface, info in self.network_interfaces.items():
            if info["speed"] > 0:
                total_capacity += info["speed"]

        if total_capacity == 0:
            try:
                connections = psutil.net_connections()
                if len(connections) > 100:
                    total_capacity = 1000
                elif len(connections) > 50:
                    total_capacity = 100
                else:
                    total_capacity = 10
            except Exception:
                total_capacity = 10

        return total_capacity * 1024 * 1024  # Mbps → bps

    # === Paranoia Management ===

    async def update_paranoia_level(self, trigger: str) -> None:
        """
        Update QSP's paranoia level based on events.

        Paranoia levels: healthy → elevated → maximum → JUSTIFIED
        """
        if trigger == "threat_detected":
            self.threats_detected += 1
            if self.threats_detected >= 5:
                self.paranoia_level = ParanoiaLevel.JUSTIFIED
                logger.warning(
                    f"👻🚨 PARANOIA JUSTIFIED! {self.threats_detected} threats!"
                )
            elif self.threats_detected >= 3:
                self.paranoia_level = ParanoiaLevel.MAXIMUM
                logger.warning(
                    f"👻⚠️ Paranoia MAXIMUM! Threats: {self.threats_detected}"
                )
            elif self.threats_detected >= 1:
                self.paranoia_level = ParanoiaLevel.ELEVATED
                logger.info(
                    f"👻🔺 Paranoia ELEVATED! Threats: {self.threats_detected}"
                )

        elif trigger == "false_alarm":
            self.false_alarms += 1
            if (
                self.paranoia_level == ParanoiaLevel.JUSTIFIED
                and self.false_alarms > 3
            ):
                self.paranoia_level = ParanoiaLevel.MAXIMUM
            elif (
                self.paranoia_level == ParanoiaLevel.MAXIMUM
                and self.false_alarms > 5
            ):
                self.paranoia_level = ParanoiaLevel.ELEVATED

        elif trigger == "tequila_shot":
            self.tequila_shots_today += 1
            if self.tequila_shots_today > 5:
                logger.warning(
                    f"👻🍸 {self.tequila_shots_today} tequila shots! "
                    f"*paranoia intensifies beyond reason*"
                )

        self.quantum_phase_shifts += 1

    # === Quantum Phase Management ===

    async def phase_into_quantum_dimension(self):
        """Phase into network analysis dimension."""
        self.quantum_state = QuantumPhaseState.QUANTUM_ENTANGLED
        await asyncio.sleep(0.001)

    async def phase_back_to_corporeal(self):
        """Return to normal dimension."""
        self.quantum_state = QuantumPhaseState.CORPOREAL
        await asyncio.sleep(0.001)

    async def shift_to_phase(
        self, target_phase: QuantumPhaseState, user_id: Optional[str] = None
    ):
        """Shift to specific quantum phase."""
        previous_phase = self.quantum_state
        self.quantum_state = target_phase
        self.dimensional_shifts_performed += 1
        logger.info(f"👻 Phase shifted to {target_phase.value}")

        # Log dimensional shift event
        if user_id:
            try:
                from app.services.agent_event_logger import log_agent_event

                db_gen = self.db_getter()
                async for db in db_gen:
                    await log_agent_event(
                        db=db,
                        agent_name="quantum_shadow_people",
                        event_type="dimensional_shift",
                        event_data={
                            "from_phase": previous_phase.value,
                            "to_phase": target_phase.value,
                            "total_shifts": self.dimensional_shifts_performed,
                            "is_interdimensional": target_phase
                            in [
                                QuantumPhaseState.INTERDIMENSIONAL,
                                QuantumPhaseState.VOID_WALKER,
                            ],
                            "mystery_level": "extreme"
                            if target_phase
                            == QuantumPhaseState.TEQUILA_JELLO_DIMENSION
                            else "moderate",
                        },
                        user_id=user_id,
                        severity="high"
                        if target_phase == QuantumPhaseState.VOID_WALKER
                        else "medium",
                        agent_state="phasing",
                    )
                    db.commit()
                    break
            except Exception as e:
                logger.error(f"Failed to log dimensional shift: {e}")

        # Different phases require different amounts of tequila jello shots
        phase_requirements = {
            QuantumPhaseState.INTERDIMENSIONAL: 3,
            QuantumPhaseState.VOID_WALKER: 5,
            QuantumPhaseState.TEQUILA_JELLO_DIMENSION: 7,
        }
        if target_phase in phase_requirements:
            await self.consume_tequila_jello_shots(
                phase_requirements[target_phase], user_id=user_id
            )

    async def consume_tequila_jello_shots(
        self, count: int, user_id: Optional[str] = None
    ) -> int:
        """Consume tequila jello shots for quantum courage."""
        self.tequila_jello_shots += count
        logger.info(
            f"👻🍹 Consumed {count} tequila jello shots. "
            f"Total: {self.tequila_jello_shots}"
        )

        if user_id and count > 0:
            try:
                from app.services.agent_event_logger import log_agent_event

                db_gen = self.db_getter()
                async for db in db_gen:
                    await log_agent_event(
                        db=db,
                        agent_name="quantum_shadow_people",
                        event_type="tequila_jello_shot_consumed",
                        event_data={
                            "shots_consumed": count,
                            "total_shots": self.tequila_jello_shots,
                            "quantum_state": self.quantum_state.value,
                            "courage_level": "legendary"
                            if self.tequila_jello_shots > 20
                            else "adequate",
                        },
                        user_id=user_id,
                        severity="low" if count <= 3 else "medium",
                        agent_state="consuming",
                    )
                    db.commit()
                    break
            except Exception as e:
                logger.error(
                    f"Failed to log tequila jello shot consumption: {e}"
                )

        return count

    # === Database ===

    async def initialize_database(self):
        """Initialize QSP database integration."""
        if self.db_getter:
            try:
                from .database_integration import QSPDatabaseIntegration

                self.db_integration = QSPDatabaseIntegration(
                    db_getter=self.db_getter
                )
                await self.db_integration.initialize()
                logger.info(
                    "👻💾 Database integration initialized — "
                    "Paranoid records enabled!"
                )
            except Exception as e:
                logger.error(
                    f"👻💥 Failed to initialize database: {e}", exc_info=True
                )
                self.db_integration = None
        else:
            self.db_integration = None
            logger.warning(
                "👻⚠️ No db_getter provided — PostgreSQL writes disabled"
            )

    # === Status ===

    def get_status(self) -> Dict[str, Any]:
        """Get QSP's full personality/state snapshot."""
        return {
            "agent_name": self.agent_name,
            "agent_type": "network_specialists",
            "is_active": True,
            "total_analyses": self.total_analyses,
            "successful_analyses": self.successful_analyses,
            "quantum_phase": self.quantum_state.value,
            "coherence_level": "high",
            "tequila_jello_shots": self.tequila_shots_today,
            "paranoia_level": self.paranoia_level.value,
            "threats_detected": self.threats_detected,
            "false_alarms": self.false_alarms,
            "quantum_phase_shifts": self.quantum_phase_shifts,
        }
