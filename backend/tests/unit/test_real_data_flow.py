import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

# Import your actual handlers
from app.ai_agents.sir_hawkington.websocket_integration import create_sirhawkingtonwebsockethandler
from app.ai_agents.meth_snail.snails_websocket_integration import create_methsnailwebsockethandler

class TestSirHawkingtonRealIntegration:
    """Test Sir Hawkington with actual websocket data flows"""
    
    @pytest.fixture
    async def handler(self):
        return await create_sirhawkingtonwebsockethandler()
    
    @pytest.fixture
    def good_websocket_data(self):
        """Real websocket data structure"""
        return {
            "cpu_usage": 45.2,
            "memory_usage": 67.8,
            "disk_usage": 34.1,
            "network": {
                "bytes_sent": 2048,
                "bytes_recv": 1024
            },
            "process_count": 156,
            "timestamp": utc_now().isoformat()
        }
    
    async def test_real_websocket_integration(self, handler, good_websocket_data):
        """Test the full websocket → handler → decision engine flow"""
        
        print("🧐 Testing real websocket integration...")
        
        # Process through real integration
        result = await handler.process_metrics(good_websocket_data)
        
        print(f"🧐 Result: {result}")
        
        # Verify Sir Hawkington's analysis was added
        assert 'sir_hawkington' in result
        assert result['sir_hawkington']['decision_type'] in ['normal', 'concern', 'alert']
        assert 'message' in result['sir_hawkington']
        assert result['sir_hawkington']['confidence'] > 0
        
        # Verify original metrics preserved
        assert result['cpu_usage'] == 45.2
        assert result['memory_usage'] == 67.8
    
    async def test_websocket_missing_cpu_data(self, handler):
        """Test what happens when websocket sends incomplete data"""
        
        print("🧐 Testing missing CPU data...")
        
        # Missing CPU data - should trigger monocle yeet
        incomplete_data = {
            "memory_usage": 67.8,
            "disk_usage": 34.1,
            "timestamp": utc_now().isoformat()
        }
        
        result = await handler.process_metrics(incomplete_data)
        
        print(f"🧐 Result with missing CPU: {result}")
        
        # Check what Sir Hawkington does
        if 'sir_hawkington' in result:
            print(f"🧐 Sir Hawkington's response: {result['sir_hawkington']}")
        else:
            print("🧐 NO SIR HAWKINGTON RESPONSE - Integration issue?")
    
    async def test_websocket_malformed_data(self, handler):
        """Test malformed websocket data"""
        
        print("🧐 Testing malformed data...")
        
        malformed_data = {
            "cpu_usage": "not_a_number",
            "memory_usage": 67.8,
            "disk_usage": 34.1,
        }
        
        result = await handler.process_metrics(malformed_data)
        
        print(f"🧐 Result with malformed data: {result}")
    
    async def test_websocket_error_handling(self, handler):
        """Test what happens when decision engine fails"""
        
        print("🧐 Testing error handling...")
        
        # Patch the decision engine to fail
        with patch.object(handler.decision_engine, 'analyze_system_health', 
                         side_effect=Exception("Decision engine failure")):
            
            good_data = {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 34.1,
            }
            
            result = await handler.process_metrics(good_data)
            
            print(f"🧐 Result with engine failure: {result}")
            
            # Should return data with error info
            assert 'sir_hawkington' in result
            assert result['sir_hawkington']['decision_type'] == 'error'