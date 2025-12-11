"""
Test VIC-20's Historical Query Capability
==========================================

Verifies that VIC-20:
1. Queries the database for historical effectiveness data
2. Uses that data to adjust recommendation confidence
3. Suggests alternative actions when history shows better options

Run with: pytest tests/test_vic20_history_query.py -v
"""

import pytest
import asyncio
import json
from datetime import datetime, timezone, timedelta
from unittest.mock import AsyncMock, MagicMock, patch


class TestVIC20HistoryQuery:
    """Test VIC-20's ability to query and use historical data"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session"""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def sample_history_data(self):
        """Sample historical data that would come from the database"""
        return [
            {
                "action": "clear_cache",
                "confidence": 0.85,
                "outcome": "success",
                "success": True,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
            },
            {
                "action": "clear_cache",
                "confidence": 0.80,
                "outcome": "success",
                "success": True,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=5)).isoformat()
            },
            {
                "action": "clear_cache",
                "confidence": 0.75,
                "outcome": "partial",
                "success": False,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=8)).isoformat()
            },
            {
                "action": "throttle_processes",
                "confidence": 0.90,
                "outcome": "success",
                "success": True,
                "timestamp": (datetime.now(timezone.utc) - timedelta(hours=12)).isoformat()
            },
        ]
    
    @pytest.mark.asyncio
    async def test_generate_recommendation_uses_history(self, sample_history_data):
        """Test that _generate_recommendation queries and uses historical data"""
        from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
        
        # Create VIC-20 instance
        vic20 = VIC20SageDistributed()
        
        # Mock the history query to return our sample data
        vic20._get_historical_effectiveness = AsyncMock(return_value=sample_history_data)
        
        # Generate a recommendation for memory
        rec = await vic20._generate_recommendation(
            resource_type="memory",
            current_value=85.0,
            threshold=70.0,
            severity="high"
        )
        
        # Verify history was queried
        vic20._get_historical_effectiveness.assert_called_once_with("memory")
        
        # Verify recommendation includes historical basis
        assert rec.get('historical_basis') is not None, "Recommendation should include historical basis"
        assert rec['historical_basis']['matching_records'] > 0, "Should have matching records"
        
        # Verify reasoning mentions historical data
        assert "past actions" in rec['reasoning'], "Reasoning should mention past actions"
        
        print(f"\n✅ Recommendation generated with historical context:")
        print(f"   Action: {rec['action']}")
        print(f"   Confidence: {rec['confidence']:.0%}")
        print(f"   Historical records: {rec['historical_basis']['matching_records']}")
        print(f"   Success rate: {rec['historical_basis']['success_rate']:.0%}")
        print(f"   Reasoning: {rec['reasoning']}")
    
    @pytest.mark.asyncio
    async def test_no_history_uses_defaults(self):
        """Test that recommendations work with no historical data"""
        from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
        
        vic20 = VIC20SageDistributed()
        
        # Mock history query to return None (no data)
        vic20._get_historical_effectiveness = AsyncMock(return_value=None)
        
        rec = await vic20._generate_recommendation(
            resource_type="cpu",
            current_value=90.0,
            threshold=70.0,
            severity="critical"
        )
        
        # Should still get a recommendation
        assert rec['action'] == 'throttle_processes'
        assert rec['historical_basis'] is None
        assert "No historical data" in rec['reasoning']
        
        print(f"\n✅ Default recommendation (no history):")
        print(f"   Action: {rec['action']}")
        print(f"   Confidence: {rec['confidence']:.0%}")
        print(f"   Reasoning: {rec['reasoning']}")
    
    @pytest.mark.asyncio
    async def test_alternative_action_suggested(self):
        """Test that VIC-20 suggests alternative actions when history shows better options"""
        from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
        
        vic20 = VIC20SageDistributed()
        
        # Create history where a different action worked better
        history_with_better_alternative = [
            # Default action (clear_cache) has poor success
            {"action": "clear_cache", "success": False, "confidence": 0.7},
            {"action": "clear_cache", "success": False, "confidence": 0.7},
            {"action": "clear_cache", "success": True, "confidence": 0.7},
            # Alternative action (restart_service) has great success
            {"action": "restart_service", "success": True, "confidence": 0.9},
            {"action": "restart_service", "success": True, "confidence": 0.9},
            {"action": "restart_service", "success": True, "confidence": 0.9},
            {"action": "restart_service", "success": True, "confidence": 0.9},
        ]
        
        vic20._get_historical_effectiveness = AsyncMock(return_value=history_with_better_alternative)
        
        rec = await vic20._generate_recommendation(
            resource_type="memory",
            current_value=85.0,
            threshold=70.0,
            severity="high"
        )
        
        # Should suggest the alternative action
        assert rec.get('alternative_action') == 'restart_service', "Should suggest better alternative"
        assert rec.get('alternative_confidence', 0) > 0.7, "Alternative should have high confidence"
        
        print(f"\n✅ Alternative action suggested:")
        print(f"   Default action: {rec['action']}")
        print(f"   Alternative action: {rec.get('alternative_action')}")
        print(f"   Alternative confidence: {rec.get('alternative_confidence', 0):.0%}")


class TestVIC20DatabaseQuery:
    """Test the actual database query (requires database connection)"""
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(True, reason="Requires database connection - run manually on Dell")
    async def test_real_database_query(self):
        """
        Test actual database query for historical effectiveness.
        
        Run this test on Dell with: 
            pytest tests/test_vic20_history_query.py::TestVIC20DatabaseQuery::test_real_database_query -v -s
        """
        from app.ai_agents.vic_20_sage.distributed_vic20 import VIC20SageDistributed
        from app.core.database import get_async_db
        
        vic20 = VIC20SageDistributed(db_getter=get_async_db)
        
        # Query for CPU history
        history = await vic20._get_historical_effectiveness("cpu")
        
        if history:
            print(f"\n✅ Found {len(history)} historical records for CPU:")
            for h in history[:5]:  # Show first 5
                print(f"   - {h['action']}: success={h['success']}, confidence={h['confidence']}")
        else:
            print("\n⚠️ No historical records found for CPU (this is expected if no data yet)")
        
        # Query for memory history
        history = await vic20._get_historical_effectiveness("memory")
        
        if history:
            print(f"\n✅ Found {len(history)} historical records for memory:")
            for h in history[:5]:
                print(f"   - {h['action']}: success={h['success']}, confidence={h['confidence']}")
        else:
            print("\n⚠️ No historical records found for memory")


if __name__ == "__main__":
    # Quick test runner
    import sys
    
    async def run_tests():
        print("=" * 60)
        print("VIC-20 History Query Tests")
        print("=" * 60)
        
        test = TestVIC20HistoryQuery()
        
        # Test 1: Uses history
        print("\n--- Test 1: Generate recommendation uses history ---")
        sample_data = test.sample_history_data(test)
        await test.test_generate_recommendation_uses_history(sample_data)
        
        # Test 2: No history defaults
        print("\n--- Test 2: No history uses defaults ---")
        await test.test_no_history_uses_defaults()
        
        # Test 3: Alternative suggestions
        print("\n--- Test 3: Alternative action suggested ---")
        await test.test_alternative_action_suggested()
        
        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
    
    asyncio.run(run_tests())
