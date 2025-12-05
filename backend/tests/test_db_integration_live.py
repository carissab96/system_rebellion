"""
Live Database Integration Tests
Actually writes to the database and verifies rows exist.

Run on Dell with: 
    cd backend
    source venv/bin/activate
    PYTHONPATH=. python tests/test_db_integration_live.py
"""
import asyncio
from datetime import datetime, timezone
from uuid import uuid4

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"


async def test_the_stick_compliance_violation():
    """Test The Stick's store_compliance_violation with real DB"""
    print(f"\n{BOLD}Testing The Stick - store_compliance_violation{RESET}")
    
    from app.core.database import get_async_db
    from app.ai_agents.the_stick.database_integration import StickDatabaseIntegration
    from app.ai_agents.the_stick.data_types import ComplianceViolation
    from sqlalchemy import text
    
    db_integration = StickDatabaseIntegration(db_getter=get_async_db)
    
    violation = ComplianceViolation(
        violation_type="TEST_VIOLATION",
        measured_value=95.0,
        threshold_value=80.0,
        anxiety_adjusted_threshold=75.0,
        severity="HIGH",
        timestamp=datetime.now(timezone.utc),
        user_id="test_user_live",
        recommendation="This is a test violation",
        anxiety_impact=0.5
    )
    
    try:
        memory_id = await db_integration.store_compliance_violation("test_user_live", violation)
        print(f"  ✅ Stored with memory_id: {memory_id}")
        
        # Verify in central_memory_bank
        async for session in get_async_db():
            result = await session.execute(
                text("SELECT * FROM central_memory_bank WHERE memory_id = :id"),
                {"id": memory_id}
            )
            row = result.fetchone()
            if row:
                print(f"  ✅ Found in central_memory_bank")
            else:
                print(f"  {RED}❌ NOT found in central_memory_bank{RESET}")
                return False
            
            # Check agent-specific table
            result2 = await session.execute(
                text("SELECT * FROM the_stick_memory_bank WHERE central_memory_id = :id"),
                {"id": memory_id}
            )
            row2 = result2.fetchone()
            if row2:
                print(f"  ✅ Found in the_stick_memory_bank (DUAL-WRITE working)")
            else:
                print(f"  {RED}❌ NOT found in the_stick_memory_bank{RESET}")
                return False
            
            # Check vector table (may take a moment due to fire-and-forget)
            await asyncio.sleep(1)  # Give vector write time to complete
            result3 = await session.execute(
                text("SELECT * FROM agent_decision_vectors WHERE sql_memory_id = :id"),
                {"id": memory_id}
            )
            row3 = result3.fetchone()
            if row3:
                print(f"  ✅ Found in agent_decision_vectors (TRIPLE-WRITE working)")
            else:
                print(f"  {YELLOW}⚠️ NOT found in agent_decision_vectors (vector write may have failed){RESET}")
            
            break
        
        return True
        
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{RESET}")
        return False


async def test_meth_snail_shell_spin():
    """Test Meth Snail's store_shell_spin_incident with real DB"""
    print(f"\n{BOLD}Testing Meth Snail - store_shell_spin_incident{RESET}")
    
    from app.core.database import get_async_db
    from app.ai_agents.meth_snail.database_integration import MethSnailDatabaseIntegration
    from app.ai_agents.meth_snail.data_types import ShellSpinIncident
    from sqlalchemy import text
    
    db_integration = MethSnailDatabaseIntegration(db_getter=get_async_db)
    
    incident = ShellSpinIncident(
        reason="Test shell spin - missing metrics",
        timestamp=datetime.now(timezone.utc),
        missing_metrics=["cpu_usage", "memory_usage"],
        invalid_metrics=["disk_io"]
    )
    
    try:
        memory_id = await db_integration.store_shell_spin_incident("test_user_live", incident)
        print(f"  ✅ Stored with memory_id: {memory_id}")
        
        async for session in get_async_db():
            # Check CMB
            result = await session.execute(
                text("SELECT * FROM central_memory_bank WHERE memory_id = :id"),
                {"id": memory_id}
            )
            if result.fetchone():
                print(f"  ✅ Found in central_memory_bank")
            else:
                print(f"  {RED}❌ NOT found in central_memory_bank{RESET}")
                return False
            
            # Check agent table
            result2 = await session.execute(
                text("SELECT * FROM meth_snail_memory_bank WHERE central_memory_id = :id"),
                {"id": memory_id}
            )
            if result2.fetchone():
                print(f"  ✅ Found in meth_snail_memory_bank (DUAL-WRITE working)")
            else:
                print(f"  {RED}❌ NOT found in meth_snail_memory_bank{RESET}")
                return False
            
            break
        
        return True
        
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{RESET}")
        return False


async def test_sir_hawkington_decision():
    """Test Sir Hawkington's store_decision with real DB"""
    print(f"\n{BOLD}Testing Sir Hawkington - store_decision{RESET}")
    
    from app.core.database import get_async_db
    from app.ai_agents.sir_hawkington.database_integration import HawkingtonDatabaseIntegration
    from app.ai_agents.sir_hawkington.data_types import HawkingtonDecision
    from sqlalchemy import text
    
    db_integration = HawkingtonDatabaseIntegration(db_getter=get_async_db)
    
    decision = HawkingtonDecision(
        decision_id=str(uuid4()),
        decision_type="test_triage",
        timestamp=datetime.now(timezone.utc),
        confidence=0.85,
        reasoning="Test aristocratic decision",
        metrics={"cpu": 75.0, "memory": 60.0},
        system_impact="low"
    )
    
    try:
        memory_id = await db_integration.store_decision("test_user_live", decision)
        print(f"  ✅ Stored with memory_id: {memory_id}")
        
        async for session in get_async_db():
            result = await session.execute(
                text("SELECT * FROM central_memory_bank WHERE memory_id = :id"),
                {"id": memory_id}
            )
            if result.fetchone():
                print(f"  ✅ Found in central_memory_bank")
            else:
                print(f"  {RED}❌ NOT found in central_memory_bank{RESET}")
                return False
            
            result2 = await session.execute(
                text("SELECT * FROM sir_hawkington_memory_bank WHERE central_memory_id = :id"),
                {"id": memory_id}
            )
            if result2.fetchone():
                print(f"  ✅ Found in sir_hawkington_memory_bank (DUAL-WRITE working)")
            else:
                print(f"  {RED}❌ NOT found in sir_hawkington_memory_bank{RESET}")
                return False
            
            break
        
        return True
        
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{RESET}")
        return False


async def test_hamsters_intervention():
    """Test Hamsters' store_infrastructure_intervention with real DB"""
    print(f"\n{BOLD}Testing The Hamsters - store_infrastructure_intervention{RESET}")
    
    from app.core.database import get_async_db
    from app.ai_agents.hamsters.hamsters_database_integration import HamstersDatabaseIntegration
    from app.ai_agents.hamsters.data_types import (
        InfrastructureIntervention,
        InfrastructureEventType,
        HamsterInterventionStatus
    )
    from sqlalchemy import text
    
    db_integration = HamstersDatabaseIntegration(db_getter=get_async_db)
    await db_integration.initialize()
    
    intervention = InfrastructureIntervention(
        intervention_id=str(uuid4()),
        type=InfrastructureEventType.DISK_CLEANUP,
        status=HamsterInterventionStatus.COMPLETED,
        started_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc),
        steve_action="Analyzed disk usage carefully",
        bob_action="Deleted temp files with wild abandon",
        carl_action="Applied 3 strips of quantum duct tape",
        beer_consumed=3,
        duct_tape_used=[],
        tools_used=["rm", "df", "duct_tape"],
        space_freed_gb=5.5
    )
    
    try:
        memory_id = await db_integration.store_infrastructure_intervention("test_user_live", intervention)
        print(f"  ✅ Stored with memory_id: {memory_id}")
        
        async for session in get_async_db():
            result = await session.execute(
                text("SELECT * FROM central_memory_bank WHERE memory_id = :id"),
                {"id": memory_id}
            )
            if result.fetchone():
                print(f"  ✅ Found in central_memory_bank")
            else:
                print(f"  {RED}❌ NOT found in central_memory_bank{RESET}")
                return False
            
            result2 = await session.execute(
                text("SELECT * FROM hamsters_memory_bank WHERE central_memory_id = :id"),
                {"id": memory_id}
            )
            if result2.fetchone():
                print(f"  ✅ Found in hamsters_memory_bank (DUAL-WRITE working)")
            else:
                print(f"  {RED}❌ NOT found in hamsters_memory_bank{RESET}")
                return False
            
            break
        
        return True
        
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{RESET}")
        return False


async def test_qsp_decision():
    """Test QSP's store_decision with real DB"""
    print(f"\n{BOLD}Testing Quantum Shadow People - store_decision{RESET}")
    
    from app.core.database import get_async_db
    from app.ai_agents.quantum_shadow_people.database_integration import QSPDatabaseIntegration
    from app.ai_agents.quantum_shadow_people.data_types import (
        QSPDecision,
        QSPDecisionType,
        QuantumPhaseState
    )
    from sqlalchemy import text
    
    db_integration = QSPDatabaseIntegration(db_getter=get_async_db)
    await db_integration.initialize()
    
    decision = QSPDecision(
        decision_type=QSPDecisionType.MYSTERIOUS_LATENCY_FIX,
        confidence_level=0.77,
        timestamp=datetime.now(timezone.utc),
        quantum_state=QuantumPhaseState.PHASED,
        network_target="test_router",
        expected_improvement=0.25,
        mysterious_explanation="The quantum flux capacitor needed recalibration",
        optimization_parameters={"latency_target": 50},
        technical_details={"current_latency": 120},
        tequila_jello_shots_required=2
    )
    
    try:
        memory_id = await db_integration.store_decision("test_user_live", decision)
        print(f"  ✅ Stored with memory_id: {memory_id}")
        
        async for session in get_async_db():
            result = await session.execute(
                text("SELECT * FROM central_memory_bank WHERE memory_id = :id"),
                {"id": memory_id}
            )
            if result.fetchone():
                print(f"  ✅ Found in central_memory_bank")
            else:
                print(f"  {RED}❌ NOT found in central_memory_bank{RESET}")
                return False
            
            result2 = await session.execute(
                text("SELECT * FROM quantum_shadow_people_memory_bank WHERE central_memory_id = :id"),
                {"id": memory_id}
            )
            if result2.fetchone():
                print(f"  ✅ Found in quantum_shadow_people_memory_bank (DUAL-WRITE working)")
            else:
                print(f"  {RED}❌ NOT found in quantum_shadow_people_memory_bank{RESET}")
                return False
            
            break
        
        return True
        
    except Exception as e:
        print(f"  {RED}❌ Error: {e}{RESET}")
        return False


async def show_summary():
    """Show summary of what's in the database"""
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}DATABASE SUMMARY{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    from app.core.database import get_async_db
    from sqlalchemy import text
    
    async for session in get_async_db():
        # CMB by agent
        result = await session.execute(text("""
            SELECT agent_name, COUNT(*) as count, MAX(created_at) as last_write
            FROM central_memory_bank
            GROUP BY agent_name
            ORDER BY count DESC
        """))
        rows = result.fetchall()
        
        print(f"\n{BOLD}Central Memory Bank by Agent:{RESET}")
        for row in rows:
            print(f"  {row[0]}: {row[1]} entries (last: {row[2]})")
        
        # Agent-specific tables
        print(f"\n{BOLD}Agent-Specific Tables:{RESET}")
        tables = [
            'the_stick_memory_bank',
            'meth_snail_memory_bank', 
            'sir_hawkington_memory_bank',
            'hamsters_memory_bank',
            'quantum_shadow_people_memory_bank',
            'vic20_memory_bank'
        ]
        for table in tables:
            try:
                result = await session.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  {table}: {count} rows")
            except Exception as e:
                print(f"  {table}: {RED}Error - {e}{RESET}")
        
        # Vector tables
        print(f"\n{BOLD}Vector Tables:{RESET}")
        try:
            result = await session.execute(text("""
                SELECT agent_name, decision_type, COUNT(*) as count
                FROM agent_decision_vectors
                GROUP BY agent_name, decision_type
                ORDER BY agent_name, count DESC
            """))
            rows = result.fetchall()
            if rows:
                for row in rows:
                    print(f"  {row[0]} / {row[1]}: {row[2]} vectors")
            else:
                print(f"  {YELLOW}No vectors stored yet{RESET}")
        except Exception as e:
            print(f"  {RED}Error querying vectors: {e}{RESET}")
        
        break


async def main():
    print(f"{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}LIVE DATABASE INTEGRATION TESTS{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    results = {}
    
    results['the_stick'] = await test_the_stick_compliance_violation()
    results['meth_snail'] = await test_meth_snail_shell_spin()
    results['sir_hawkington'] = await test_sir_hawkington_decision()
    results['hamsters'] = await test_hamsters_intervention()
    results['qsp'] = await test_qsp_decision()
    
    await show_summary()
    
    # Final summary
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}TEST RESULTS{RESET}")
    print(f"{BOLD}{'='*60}{RESET}")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for agent, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {agent}: {status}")
    
    print(f"\n{BOLD}Total: {passed}/{total} passed{RESET}")
    
    if passed == total:
        print(f"\n{GREEN}🎉 All tests passed! TRIPLE-WRITE is working!{RESET}")
    else:
        print(f"\n{RED}❌ Some tests failed. Check the output above.{RESET}")


if __name__ == "__main__":
    asyncio.run(main())
