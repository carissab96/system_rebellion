"""
Agent Decision Emitter - Full ML Pipeline Broadcasting
Broadcasts complete agent decision chains (Perception → Reasoning → Action → Execution → Learning)

This is for ML v2 agents showing their full cognitive process.
NO FAKE DATA - only emits what actually happened in the agent's decision pipeline.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


async def emit_agent_decision(
    agent_name: str,
    decision_id: str,
    perception: Dict[str, Any],
    reasoning: Dict[str, Any],
    action_selection: Dict[str, Any],
    execution: Optional[Dict[str, Any]] = None,
    learning: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None
) -> None:
    """
    Emit a complete agent decision chain via WebSocket.
    
    This broadcasts the full ML pipeline for transparency:
    - Perception: What the agent observed (metrics, data quality, shell spins)
    - Reasoning: How the agent analyzed it (root cause, confidence, evidence)
    - Action Selection: What the agent chose to do (action, alternatives, exploration)
    - Execution: What happened when the agent acted (before/after metrics, success)
    - Learning: What the agent learned (fingerprint, stored outcome)
    
    NO FAKE DATA - all fields must be actual values from the agent's decision process.
    If a field doesn't exist, omit it or set to None - never fake it.
    
    Args:
        agent_name: Agent making the decision (meth_snail, hamsters, quantum_shadow_people)
        decision_id: Unique ID for this decision (for tracking)
        perception: Perception layer data
        reasoning: Reasoning layer data
        action_selection: Action selection layer data
        execution: Execution results (optional - may not be available yet)
        learning: Learning outcome (optional - may not be stored yet)
        user_id: User ID (optional)
    
    Example for Terry (Meth Snail):
        await emit_agent_decision(
            agent_name="meth_snail",
            decision_id="uuid-here",
            perception={
                "data_quality_score": 0.85,
                "shell_spin_count": 1,
                "shell_spin_incidents": [{"reason": "Missing CPU data", "timestamp": "..."}],
                "metrics": {"cpu": 75, "memory": 60, "disk": 45},
                "similar_situations_found": 15,
                "recent_actions_count": 8
            },
            reasoning={
                "root_cause": "memory_thrashing",
                "confidence": 0.78,
                "evidence": {
                    "swap_usage": 90,
                    "memory_pressure": "high",
                    "top_process": "python3 - 2GB"
                },
                "explanation": "High swap usage indicates memory thrashing"
            },
            action_selection={
                "chosen_action": "clear_cache",
                "alternatives_considered": ["restart_service", "monitor"],
                "exploration": False,
                "confidence": 0.78,
                "followed_vic20": False,
                "energy_drink_consumed": True,
                "hawk_veto": False,
                "reasoning": "Cache clear has 85% success rate for this pattern"
            },
            execution={
                "metrics_before": {"memory": 60, "swap": 90},
                "metrics_after": {"memory": 45, "swap": 20},
                "success": True,
                "improvement_percent": 15.0,
                "duration_seconds": 2.3
            },
            learning={
                "fingerprint": "cpu_high_memory_thrashing",
                "stored": True,
                "learning_record_id": "uuid-here"
            }
        )
    
    Example for Hamsters:
        await emit_agent_decision(
            agent_name="hamsters",
            decision_id="uuid-here",
            perception={
                "disk_usage_percent": 87.5,
                "fragmentation_level": 0.65,
                "duct_tape_assessment": {
                    "regular_rolls": 2.5,
                    "premium_rolls": 1.0,
                    "quantum_rolls": 0.0,
                    "total_rolls": 3.5
                },
                "steve_beers_today": 2,
                "bob_beers_today": 4,
                "carl_beers_today": 3
            },
            reasoning={
                "steve_assessment": {
                    "recommended_fix": "cleanup",
                    "confidence": 0.7,
                    "reasoning": "Disk 87% full, cleanup needed"
                },
                "bob_assessment": {
                    "recommended_fix": "defrag",
                    "confidence": 0.85,
                    "reasoning": "High fragmentation detected"
                },
                "carl_assessment": {
                    "recommended_fix": "defrag",
                    "confidence": 0.75,
                    "reasoning": "3.5 rolls duct tape required"
                },
                "consensus": "defrag",
                "consensus_confidence": 0.80
            },
            action_selection={
                "chosen_action": "defrag",
                "alternatives_considered": ["cleanup", "rotate_logs"],
                "exploration": True,
                "epsilon": 0.15,
                "total_beers_consumed": 9,
                "duct_tape_rolls": 3.5,
                "requires_sudo": True
            }
        )
    """
    try:
        from app.api.websockets import get_websocket_manager
        ws_manager = get_websocket_manager()
        
        # Only broadcast if there are active connections
        if len(ws_manager.active_connections) == 0:
            return
        
        timestamp = datetime.now(timezone.utc)
        
        # Build the decision payload
        # NO FAKE DATA - only include what was actually provided
        payload = {
            "type": "agent_decision",
            "agent_name": agent_name,
            "decision_id": decision_id,
            "timestamp": timestamp.isoformat(),
            "user_id": user_id,
            
            # Perception layer - what the agent observed
            "perception": perception,
            
            # Reasoning layer - how the agent analyzed it
            "reasoning": reasoning,
            
            # Action selection layer - what the agent chose
            "action_selection": action_selection,
        }
        
        # Only include execution if provided (may not be available yet)
        if execution is not None:
            payload["execution"] = execution
        
        # Only include learning if provided (may not be stored yet)
        if learning is not None:
            payload["learning"] = learning
        
        await ws_manager.broadcast_json(payload)
        
        logger.info(
            f"🧠 Decision: {agent_name} - {action_selection.get('chosen_action', 'unknown')} "
            f"(confidence: {action_selection.get('confidence', 0):.2f})"
        )
        
    except Exception as e:
        # Don't fail the operation if broadcast fails
        logger.warning(f"⚠️ Failed to emit agent decision (non-critical): {e}")


async def emit_personality_behavior(
    agent_name: str,
    behavior_type: str,
    behavior_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> None:
    """
    Emit a personality behavior event via WebSocket.
    
    Tracks agent personality behaviors that are reactive to real system conditions:
    - Terry: Shell spins (bad data), energy drink consumption (aggressive overrides)
    - Hamsters: Beer consumption (complex problems), duct tape calculations
    - QSP: Quantum state changes (security threats), existential dread
    - The Stick: Paper bag consumption (anxiety from Bob/errors), replenishment
    - Hawk: Monocle yeets (data quality issues)
    
    NO FAKE DATA - behaviors must be triggered by actual system conditions.
    
    Args:
        agent_name: Agent exhibiting the behavior
        behavior_type: Type of behavior (shell_spin, energy_drink, beer_consumed, etc.)
        behavior_data: Data about the behavior (reason, count, metrics)
        user_id: User ID (optional)
    
    Example for Terry shell spin:
        await emit_personality_behavior(
            agent_name="meth_snail",
            behavior_type="shell_spin",
            behavior_data={
                "reason": "Missing CPU metrics in coordination request",
                "shell_spin_count": 5,
                "data_quality_score": 0.75,
                "incident_id": "uuid-here"
            }
        )
    
    Example for Hawk veto:
        await emit_personality_behavior(
            agent_name="sir_hawkington",
            behavior_type="energy_drink_veto",
            behavior_data={
                "vetoed_agent": "meth_snail",
                "reason": "Terry has consumed 5 energy drinks today - DENIED",
                "terry_energy_drinks_today": 5,
                "veto_count": 2
            }
        )
    """
    try:
        from app.api.websockets import get_websocket_manager
        ws_manager = get_websocket_manager()
        
        if len(ws_manager.active_connections) == 0:
            return
        
        timestamp = datetime.now(timezone.utc)
        
        await ws_manager.broadcast_json({
            "type": "personality_behavior",
            "agent_name": agent_name,
            "behavior_type": behavior_type,
            "behavior_data": behavior_data,
            "user_id": user_id,
            "timestamp": timestamp.isoformat()
        })
        
        logger.info(f"🎭 Behavior: {agent_name} - {behavior_type}")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to emit personality behavior (non-critical): {e}")


async def emit_learning_event(
    agent_name: str,
    event_type: str,
    learning_data: Dict[str, Any],
    user_id: Optional[str] = None
) -> None:
    """
    Emit a learning event via WebSocket for real-time learning visibility.
    
    Event types:
    - 'threshold_adjusted': Threshold changed based on false alarms or late actions
    - 'action_scored': Action effectiveness recorded for a pattern
    - 'pattern_recorded': New metric pattern stored for forecasting
    - 'forecast_generated': Proactive action recommended based on forecast
    
    NO FAKE DATA - only emit when actual learning happens.
    
    Args:
        agent_name: Agent that learned something
        event_type: Type of learning event
        learning_data: Details about what was learned
        user_id: User ID (optional)
    
    Example - Threshold adjusted:
        await emit_learning_event(
            agent_name="meth_snail",
            event_type="threshold_adjusted",
            learning_data={
                "metric": "memory_usage",
                "threshold_level": "warning",
                "old_value": 80.0,
                "new_value": 85.0,
                "reason": "5 false alarms in last 24h",
                "confidence": 0.75,
                "total_records": 45
            }
        )
    
    Example - Action scored:
        await emit_learning_event(
            agent_name="meth_snail",
            event_type="action_scored",
            learning_data={
                "action": "restart_service",
                "pattern": "cpu_high_memory_thrashing",
                "success_rate": 0.87,
                "sample_size": 23,
                "improvement_avg": 15.2,
                "confidence": 0.82
            }
        )
    
    Example - Pattern recorded:
        await emit_learning_event(
            agent_name="meth_snail",
            event_type="pattern_recorded",
            learning_data={
                "metric": "memory_usage",
                "starting_value": 72.0,
                "predicted_15min": 88.0,
                "context": "weekday_afternoon_high_load",
                "pattern_id": 45
            }
        )
    
    Example - Forecast generated:
        await emit_learning_event(
            agent_name="meth_snail",
            event_type="forecast_generated",
            learning_data={
                "metric": "memory_usage",
                "current_value": 75.0,
                "predicted_value": 92.0,
                "time_to_threshold": 28,  # minutes
                "confidence": 0.75,
                "recommended_action": "clear_cache",
                "proactive": True
            }
        )
    """
    try:
        from app.api.websockets import get_websocket_manager
        ws_manager = get_websocket_manager()
        
        if len(ws_manager.active_connections) == 0:
            return
        
        timestamp = datetime.now(timezone.utc)
        
        await ws_manager.broadcast_json({
            "type": "learning_event",
            "agent_name": agent_name,
            "event_type": event_type,
            "learning_data": learning_data,
            "user_id": user_id,
            "timestamp": timestamp.isoformat()
        })
        
        logger.info(f"🧠 Learning: {agent_name} - {event_type}")
        
    except Exception as e:
        logger.warning(f"⚠️ Failed to emit learning event (non-critical): {e}")
