import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from datetime import datetime

class TestSirHawkingtonRealIntegration:
    """Test Sir Hawkington with actual websocket data flows"""
    
    @pytest.fixture
    async def handler(self):
        from app.ai_agents.sir_hawkington.websocket_integration import create_sir_hawkington_handler
        return await create_sir_hawkington_handler()
    
    @pytest.fixture
    def mock_websocket_data(self):
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
            "timestamp": utc_now()
        }
    
    async def test_real_websocket_integration(self, handler, mock_websocket_data):
        """Test the full websocket → handler → decision engine flow"""
        
        # Process through real integration
        result = await handler.process_metrics(mock_websocket_data)
        
        # Verify Sir Hawkington's analysis was added
        assert 'sir_hawkington' in result
        assert result['sir_hawkington']['decision_type'] in ['normal', 'concern', 'alert']
        assert 'message' in result['sir_hawkington']
        assert result['sir_hawkington']['confidence'] > 0
        
        # Verify original metrics preserved
        assert result['cpu_usage'] == 45.2
        assert result['memory_usage'] == 67.8
    
    async def test_websocket_missing_data_integration(self, handler):
        """Test what happens when websocket sends incomplete data"""
        
        # Missing CPU data - should trigger monocle yeet
        incomplete_data = {
            "memory_usage": 67.8,
            "disk_usage": 34.1,
            "timestamp": utc_now().isoformat()
        }
        
        result = await handler.process_metrics(incomplete_data)
        
        # Should still return data, but what does Sir Hawkington do?
        # This tests the REAL integration behavior
        print(f"🧐 Result with missing CPU: {result}")
        
        # Check if monocle was yeeted or if integration handles it differently
        if 'sir_hawkington' in result:
            print(f"🧐 Sir Hawkington's response: {result['sir_hawkington']}")
    
    async def test_websocket_malformed_data_integration(self, handler):
        """Test malformed websocket data"""
        
        malformed_data = {
            "cpu_usage": "not_a_number",
            "memory_usage": 67.8,
            "disk_usage": 34.1,
        }
        
        result = await handler.process_metrics(malformed_data)
        
        # What does the integration do with bad data?
        print(f"🧐 Result with malformed data: {result}")
    
    async def test_websocket_error_handling(self, handler):
        """Test what happens when decision engine fails"""
        
        # Patch the decision engine to fail
        with patch.object(handler.decision_engine, 'analyze_system_health', 
                         side_effect=Exception("Decision engine failure")):
            
            good_data = {
                "cpu_usage": 45.2,
                "memory_usage": 67.8,
                "disk_usage": 34.1,
            }
            
            result = await handler.process_metrics(good_data)
            
            # Should return data with error info
            assert 'sir_hawkington' in result
            assert result['sir_hawkington']['decision_type'] == 'error'
            assert 'fogged up' in result['sir_hawkington']['message']