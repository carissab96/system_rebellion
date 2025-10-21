# test_hawkington_dual_write.py

import asyncio
from datetime import datetime, timezone
from app.ai_agents.sir_hawkington.database_integration import HawkingtonDatabaseIntegration
from app.ai_agents.sir_hawkington.data_types import HawkingtonDecision
from app.core.database import get_async_db
from app.models.agent_memory_banks import SirHawkingtonMemoryBank, CentralMemoryBank
from app.models.user import User

async def test_dual_write():
    print("🧐 Testing Dual-Write Architecture...\n")
    
    # Initialize database
    db = HawkingtonDatabaseIntegration(get_async_db)
    await db.initialize()
    
    # Create test decision
    decision = HawkingtonDecision(
        decision_id="test-123",
        decision_type="concern",
        confidence=0.85,
        reasoning="Test decision for dual-write verification",
        metrics={
            'cpu_usage': 75.5,
            'memory_usage': 68.2,
            'disk_usage': 45.0,
            'stress_score': 0.67
        },
        timestamp=datetime.now(timezone.utc),
        user_id="test-user-001",
        system_impact="monitoring_recommended"
    )
    
    # Store with dual-write
    try:
        memory_id = await db.store_decision("test-user-001", decision)
        print(f"✅ Dual-write successful!")
        print(f"   Central Memory ID: {memory_id}")
        
        # Verify agent table
        async with db.session_factory() as session:
            from sqlalchemy import select, text
            
            # Check agent table
            agent_result = await session.execute(
                select(SirHawkingtonMemoryBank).where(
                    SirHawkingtonMemoryBank.central_memory_id == memory_id
                )
            )
            agent_record = agent_result.scalar_one_or_none()
            
            if agent_record:
                print(f"\n✅ Agent Table Record Found:")
                print(f"   Memory ID: {agent_record.memory_id}")
                print(f"   Category: {agent_record.memory_category}")
                print(f"   Accuracy Improvement: {agent_record.accuracy_improvement}")
                print(f"   Data Quality Pattern: {agent_record.data_quality_pattern}")
            else:
                print(f"\n❌ Agent table record NOT found")
            
            # Check central memory bank
            cmb_result = await session.execute(
                select(CentralMemoryBank).where(
                    CentralMemoryBank.memory_id == memory_id
                )
            )
            cmb_record = cmb_result.scalar_one_or_none()
            
            if cmb_record:
                print(f"\n✅ Central Memory Bank Record Found:")
                print(f"   Memory ID: {cmb_record.memory_id}")
                print(f"   Agent Name: {cmb_record.agent_name}")
                print(f"   Event Type: {cmb_record.event_type}")
                print(f"   Has Agent Memory Ref: {'agent_memory_id' in (cmb_record.metadata_ or {})}")
            else:
                print(f"\n❌ CMB record NOT found")
            
            # Verify foreign key link
            if agent_record and cmb_record:
                if agent_record.central_memory_id == cmb_record.memory_id:
                    print(f"\n✅ Foreign Key Link VERIFIED")
                    print(f"   Agent record points to CMB: {agent_record.central_memory_id}")
                    print(f"   CMB record ID: {cmb_record.memory_id}")
                else:
                    print(f"\n❌ Foreign Key Link BROKEN")
        
        print(f"\n🧐✨ Test completed with aristocratic precision!")
        
    except Exception as e:
        print(f"\n❌ Test FAILED: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_dual_write())