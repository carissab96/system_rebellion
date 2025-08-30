# app/ai_agents/hamsters/test_database_integration.py
"""
Test The Hamsters' Central Memory Bank Integration
Real data, real beer, real duct tape!
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.ai_agents.hamsters.database_integration import HamstersDatabaseIntegration
from app.ai_agents.hamsters.datatypes import (
    InfrastructureIntervention, HamsterCommunication, DuctTapeUsage,
    InfrastructureEventType, HamsterInterventionStatus
)
from app.ai_agents.hamsters.constants import HamstersEventTypes, HAMSTER_STEVE, HAMSTER_BOB, HAMSTER_CARL

def utc_now():
    return datetime.now(timezone.utc)

async def test_hamsters_central_memory_basic():
    """Test basic hamster memory storage and retrieval"""
    db = HamstersDatabaseIntegration()
    await db.initialize()
    
    user_id = str(uuid4())
    
    # Create an infrastructure intervention
    intervention = InfrastructureIntervention(
        intervention_id=str(uuid4()),
        type=InfrastructureEventType.DISK_CLEANUP,
        status=HamsterInterventionStatus.COMPLETED,
        started_at=utc_now(),
        completed_at=utc_now() + timedelta(minutes=30),
        steve_action="Identified 30GB of safe deletions",
        bob_action="Deleted everything that looked deletable",
        carl_action="Applied quantum duct tape to bad sectors",
        beer_consumed=6,
        duct_tape_used=[
            DuctTapeUsage(
                timestamp=utc_now(),
                grade="quantum",
                amount_strips=3,
                purpose="sector_reinforcement",
                applied_by="carl",
                effectiveness=0.95
            )
        ],
        tools_used=["percussive_maintenance_hammer", "the_good_screwdriver"],
        space_freed_gb=45.5,
        fragmentation_reduced_percent=0.0,
        temperature_reduced_celsius=0.0,
        mystery_solved=False,
        squeaks_emitted=47,
        human_readable_summary="Hamsters freed 45.5GB through aggressive cleanup",
        required_vic20_intervention=False,
        caused_stick_anxiety_spike=True
    )
    
    # Store the intervention
    memory_id = await db.store_infrastructure_intervention(user_id, intervention)
    assert memory_id is not None
    print(f"✅ Stored intervention with memory_id: {memory_id}")
    
    # Test hamster communication
    communication = HamsterCommunication(
        timestamp=utc_now(),
        source_hamster=HAMSTER_BOB,
        telepathic_message="We should compress EVERYTHING!",
        audible_squeaks="*SQUEAK SQUEAK* BEER! *excited chirping*",
        human_translation="Bob suggests aggressive compression strategy",
        target_agent="the_stick",
        understood=True
    )
    
    comm_id = await db.store_hamster_communication(user_id, communication)
    assert comm_id is not None
    print(f"✅ Stored Bob's communication: {comm_id}")
    
    # Test duct tape tracking
    tape_usage = DuctTapeUsage(
        timestamp=utc_now(),
        grade="carls_special",
        amount_strips=1,
        purpose="impossible_fix",
        applied_by=HAMSTER_CARL,
        effectiveness=1.0  # Carl's special always works
    )
    
    tape_id = await db.track_duct_tape_usage(user_id, tape_usage)
    assert tape_id is not None
    print(f"✅ Tracked Carl's special duct tape usage: {tape_id}")
    
    # Test beer consumption
    for hamster, beers in [(HAMSTER_STEVE, 2), (HAMSTER_BOB, 4), (HAMSTER_CARL, 3)]:
        beer_id = await db.log_beer_consumption(user_id, hamster, beers, "disk_cleanup_celebration")
        assert beer_id is not None
        print(f"✅ Logged {hamster}'s beer consumption: {beers} beers")
    
    # Test supply closet raid
    raid_id = await db.log_supply_closet_raid(
        user_id,
        items_taken=["mystery_usb_drive", "emergency_pizza_money", "bobs_favorite_wrench"],
        purpose="emergency_cleanup_supplies",
        raided_by=HAMSTER_BOB
    )
    assert raid_id is not None
    print(f"✅ Logged Bob's supply closet raid: {raid_id}")
    
    # Test collective decision storage
    decision_data = {
        'decision_id': str(uuid4()),
        'intervention_type': 'defrag_special',
        'priority': 'hold_my_beer',
        'steve_assessment': "Fragmentation at 45%, defrag recommended",
        'bob_suggestion': "Let's shake the drive to settle the bits!",
        'carl_calculation': "Need 5 strips of quantum tape for stability",
        'telepathic_consensus': True,
        'confidence': 0.85,
        'tools_required': ['defrag_hammer', 'bit_settler'],
        'beer_consumption_estimate': 4,
        'duct_tape_grade': 'quantum',
        'actual_squeaks': '*SQUEAK SQUEAK* DEFRAG! *chirp*',
        'human_translation': 'Hamsters recommend defragmentation',
        'estimated_duration': 'Two beers',
        'urgency': 'HIGH'
    }
    
    decision_id = await db.store_collective_decision(user_id, decision_data)
    assert decision_id is not None
    print(f"✅ Stored collective hamster decision: {decision_id}")
    
    # Test retrieval of recent interventions
    recent = await db.get_recent_interventions(hours=1, user_id=user_id)
    assert len(recent) >= 1
    assert recent[0]['type'] == HamstersEventTypes.DISK_CLEANUP
    assert recent[0]['space_freed_gb'] == 45.5
    print(f"✅ Retrieved {len(recent)} recent interventions")
    
    # Test performance metrics
    metrics = await db.get_hamster_performance_metrics(user_id=user_id, days=1)
    assert metrics['total_interventions'] >= 1
    assert metrics['total_space_freed_gb'] >= 45.5
    assert metrics['total_beer_consumed'] >= 9  # 2+4+3 from individual consumption
    print(f"✅ Performance metrics: {metrics}")
    
    # Test pattern learning
    # First, store some observations
    for i in range(5):
        obs_metrics = {
            'disk': {'usage_percent': 75 + i * 5, 'fragmentation_percent': 20 + i * 2},
            'memory': {'usage_percent': 60 + i * 3}
        }
        await db.store_user_behavior_observation(user_id, obs_metrics)
    
    # Try to learn patterns (won't work with only 5 observations, but tests the function)
    pattern = await db.analyze_and_learn_patterns(user_id, min_observations=5)
    print(f"✅ Pattern learning attempted: {pattern}")
    
    # Test database health
    health = await db.get_database_health()
    assert health['status'] == 'healthy'
    assert health['hamster_approved'] == True
    print(f"✅ Database health check: {health}")
    
    print("\n🐹🍺 All hamster database tests passed! Time for beer!")

async def test_hamster_pattern_matching():
    """Test hamster pattern matching capabilities"""
    db = HamstersDatabaseIntegration()
    await db.initialize()
    
    user_id = str(uuid4())
    
    # Simulate metrics that should trigger patterns
    metrics = {
        'disk': {
            'usage_percent': 85,
            'fragmentation_percent': 45,
            'log_size_gb': 25
        },
        'memory': {
            'usage_percent': 70
        }
    }
    
    # Check pattern matches (will be empty initially)
    matches = await db.check_pattern_match(user_id, metrics)
    assert 'pattern_matches' in matches
    assert isinstance(matches['has_matches'], bool)
    print(f"✅ Pattern matching tested: {matches}")

async def test_hamster_beer_and_duct_tape_tracking():
    """Test detailed beer and duct tape tracking"""
    db = HamstersDatabaseIntegration()
    await db.initialize()
    
    user_id = str(uuid4())
    
    # Test different beer consumption scenarios
    scenarios = [
        (HAMSTER_STEVE, 1, "pre_intervention_courage"),
        (HAMSTER_BOB, 5, "emergency_response"),
        (HAMSTER_CARL, 3, "precision_taping")
    ]
    
    for hamster, beers, occasion in scenarios:
        beer_id = await db.log_beer_consumption(user_id, hamster, beers, occasion)
        assert beer_id is not None
        print(f"✅ {hamster} consumed {beers} beers for {occasion}")
    
    # Test various duct tape grades
    tape_grades = [
        ("regular", 10, "basic_fixes", 0.7),
        ("premium", 5, "production_repair", 0.85),
        ("quantum", 2, "impossible_fix", 0.95),
        ("carls_special", 1, "mystery_solution", 1.0)
    ]
    
    for grade, strips, purpose, effectiveness in tape_grades:
        tape_usage = DuctTapeUsage(
            timestamp=utc_now(),
            grade=grade,
            amount_strips=strips,
            purpose=purpose,
            applied_by=HAMSTER_CARL,
            effectiveness=effectiveness
        )
        tape_id = await db.track_duct_tape_usage(user_id, tape_usage)
        assert tape_id is not None
        print(f"✅ Used {strips} strips of {grade} tape with {effectiveness:.0%} effectiveness")
    
    print("\n🐹 Resource tracking complete!")

async def test_hamster_3am_interventions():
    """Test 3AM emergency intervention tracking"""
    db = HamstersDatabaseIntegration()
    await db.initialize()
    
    user_id = str(uuid4())
    
    # Create a 3AM intervention
    three_am = datetime.now(timezone.utc).replace(hour=3, minute=0, second=0)
    
    intervention = InfrastructureIntervention(
        intervention_id=str(uuid4()),
        type=InfrastructureEventType.EMERGENCY_SPACE,
        status=HamsterInterventionStatus.COMPLETED,
        started_at=three_am,
        completed_at=three_am + timedelta(minutes=15),
        steve_action="*yawns* Finding emergency deletions",
        bob_action="THIS IS WHAT WE TRAINED FOR!",
        carl_action="Emergency quantum tape deployment",
        beer_consumed=9,  # Extra beer for 3AM
        duct_tape_used=[],
        tools_used=["emergency_kit", "coffee", "more_beer"],
        space_freed_gb=75.0,
        fragmentation_reduced_percent=0.0,
        temperature_reduced_celsius=0.0,
        mystery_solved=True,
        squeaks_emitted=150,  # Lots of emergency squeaking
        human_readable_summary="3AM emergency: Hamsters saved the day!",
        required_vic20_intervention=False,
        caused_stick_anxiety_spike=True
    )
    
    memory_id = await db.store_infrastructure_intervention(user_id, intervention)
    assert memory_id is not None
    print(f"✅ Stored 3AM emergency intervention: {memory_id}")
    
    # Verify it shows up in metrics
    metrics = await db.get_hamster_performance_metrics(user_id=user_id, days=1)
    print(f"✅ 3AM interventions tracked in metrics: {metrics}")

# Run all tests
async def main():
    print("🐹 Starting Hamsters Central Memory Bank Tests...\n")
    
    await test_hamsters_central_memory_basic()
    print("\n" + "="*50 + "\n")
    
    await test_hamster_pattern_matching()
    print("\n" + "="*50 + "\n")
    
    await test_hamster_beer_and_duct_tape_tracking()
    print("\n" + "="*50 + "\n")
    
    await test_hamster_3am_interventions()
    
    print("\n🐹🍺✅ All tests complete! The Hamsters are satisfied!")

if __name__ == "__main__":
    asyncio.run(main())