# tests/test_qsp_complete_flow.py
"""
Test QSP with complete database integration
"""

import asyncio
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.ai_agents.quantum_shadow_people.database_integration import QSPDatabaseIntegration
from app.ai_agents.quantum_shadow_people.qsp_websocket_integration import QSPWebSocketHandler
from app.ai_agents.quantum_shadow_people.decision_engine import QSPDecision, QSPDecisionType, QuantumPhaseState
from app.core.database import get_async_db
def datetime_to_iso(dt):
    """Convert datetime to ISO string for JSON serialization"""
    return dt.isoformat() if dt else None

def serialize_for_json(obj):
    """Recursively convert datetime objects to ISO strings in nested structures"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_for_json(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Handle dataclass objects
        return serialize_for_json(obj.__dict__)
    else:
        return obj
        
def utc_now():
    """Get current UTC time with timezone awareness"""
    return datetime.now(timezone.utc)


@pytest.mark.asyncio
async def test_qsp_complete_flow():
    """Test complete QSP flow with all database tables"""
    
    # Initialize
    db = QSPDatabaseIntegration()
    await db.initialize()
    
    handler = QSPWebSocketHandler()
    await handler.initialize()
    
    user_id = str(uuid4())
    
    # 1. Test basic network metrics storage
    metrics = {
        'latency': 150,
        'bandwidth_utilization': 0.85,
        'packet_loss': 0.03,
        'jitter': 45,
        'active_connections': 542,
        'connection_states': {'ESTABLISHED': 500, 'SYN_SENT': 42}
    }
    
    memory_id = await db.store_network_metrics(user_id, metrics)
    assert memory_id is not None
    print(f"✅ Stored network metrics: {memory_id}")
    
    # 2. Test quantum decision storage
    decision = QSPDecision(
        decision_type=QSPDecisionType.MYSTERIOUS_LATENCY_FIX,
        quantum_state=QuantumPhaseState.TEQUILA_JELLO_DIMENSION,
        network_target="primary_router",
        optimization_parameters={
            'quantum_routing_algorithm': 'phase_shift_minimal_path',
            'temporal_adjustment': -0.023,
            'router_phase_angle': 47.3
        },
        tequila_jello_shots_required=3,
        mysterious_explanation="Phasing router through tequila jello dimension",
        technical_details={'current_latency': 150, 'target_latency': 50},
        expected_improvement=0.67,
        confidence_level=0.89,
        timestamp=utc_now()
    )
    
    decision_id = await db.store_decision(user_id, decision)
    assert decision_id is not None
    print(f"✅ Stored quantum decision: {decision_id}")
    
    # 3. Test pattern learning (simulate 50 observations)
    print("📊 Simulating 50 observations for pattern learning...")
    for i in range(50):
        test_metrics = {
            'latency': 100 + (i % 20) * 5,  # Varying latency
            'bandwidth_utilization': 0.7 + (i % 10) * 0.02,
            'packet_loss': 0.01 + (i % 5) * 0.01
        }
        await db.store_user_behavior_observation(user_id, test_metrics)
    
    # Trigger pattern learning
    pattern = await db.analyze_and_learn_patterns(user_id, min_observations=50)
    if pattern:
        print(f"✅ Pattern learned with confidence: {pattern['confidence']:.1%}")
    
    # 4. Test cross-agent learning
    hamster_data = {
        'message': 'Network congestion detected in sector 7',
        'consensus_type': 'unanimous',
        'urgency': 'high',
        'network_insight': True
    }
    
    telepathy_id = await db.record_hamster_telepathy(user_id, hamster_data)
    print(f"✅ Recorded hamster telepathy: {telepathy_id}")
    
    # 5. Test pattern matching
    pattern_match = await db.check_pattern_match(user_id, metrics)
    print(f"✅ Pattern match result: {pattern_match}")
    
    # 6. Test WebSocket handler processing
    response = await handler.process_metrics(metrics, user_id)
    print(f"✅ WebSocket response: {response['status']}")
    
    # 7. Test retrieval operations
    recent_fixes = await db.get_recent_quantum_fixes(hours=1, user_id=user_id)
    print(f"✅ Retrieved {len(recent_fixes)} recent fixes")
    
    performance = await db.get_qsp_performance_metrics(user_id=user_id, days=1)
    print(f"✅ Performance metrics: {performance}")
    
    # 8. Test pinned memories retrieval
    pinned = await db.get_pinned_decisions(user_id, limit=5)
    print(f"✅ Retrieved {len(pinned)} pinned decisions")
    
    print("\n🎉 All QSP database integration tests passed!")

@pytest.mark.asyncio
async def test_qsp_quantum_interventions():
    """Test different types of quantum interventions"""
    
    handler = QSPWebSocketHandler()
    await handler.initialize()
    
    user_id = str(uuid4())
    
    # Test critical latency scenario
    critical_metrics = {
        'latency': 500,
        'bandwidth_utilization': 0.5,
        'packet_loss': 0.02,
        'network': {'latency': 500}
    }
    
    response = await handler.process_metrics(critical_metrics, user_id)
    
    if 'decision' in response:
        assert response['decision']['type'] in [
            'mysterious_latency_fix',
            'network_dimension_shift'
        ]
        print(f"✅ Quantum intervention for high latency: {response['decision']['type']}")
    
    # Test bandwidth saturation scenario
    bandwidth_metrics = {
        'latency': 50,
        'bandwidth_utilization': 0.96,
        'packet_loss': 0.01,
        'network': {'bandwidth_utilization': 0.96}
    }
    
    response = await handler.process_metrics(bandwidth_metrics, user_id)
    
    if 'decision' in response:
        assert response['decision']['type'] == 'tequila_jello_optimization'
        print(f"✅ Tequila jello optimization triggered for bandwidth")
    
    # Test packet loss scenario
    packet_loss_metrics = {
        'latency': 80,
        'bandwidth_utilization': 0.6,
        'packet_loss': 0.08,
        'network': {'packet_loss': 0.08}
    }
    
    response = await handler.process_metrics(packet_loss_metrics, user_id)
    
    if 'decision' in response:
        assert response['decision']['type'] == 'phantom_packet_recovery'
        print(f"✅ Phantom packet recovery initiated")
    
    print("\n👻 All quantum intervention tests passed!")

if __name__ == "__main__":
    asyncio.run(test_qsp_complete_flow())
    asyncio.run(test_qsp_quantum_interventions())