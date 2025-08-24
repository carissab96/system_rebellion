"""
Test script for real-time metrics flow through the system.
This script tests the entire metrics collection and processing pipeline.
"""
import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Add the backend directory to the Python path
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

async def test_metrics_flow():
    """Test the complete metrics collection and processing flow."""
    from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService
    from app.ai_agents.sir_hawkington.triage_engine import process_metrics_through_triage
    
    # Test 1: Basic metrics collection
    logger.info("Testing basic metrics collection...")
    try:
        metrics_service = await SimplifiedMetricsService.get_instance()
        metrics = await metrics_service.get_metrics()
        if not metrics:
            raise ValueError("No metrics collected")
        logger.info(f"✅ Successfully collected metrics with keys: {list(metrics.keys())}")
        logger.info(f"   CPU Usage: {metrics.get('cpu_usage', 'N/A')}%")
        logger.info(f"   Memory Usage: {metrics.get('memory_usage', 'N/A')}%")
        logger.info(f"   Disk Usage: {metrics.get('disk_usage', 'N/A')}%")
    except Exception as e:
        logger.error(f"❌ Failed to collect metrics: {e}", exc_info=True)
        return False
    
    # Test 2: Process through Sir Hawkington's triage engine
    logger.info("Testing triage engine processing...")
    try:
        triage_result = await process_metrics_through_triage(metrics, user_id="test_user")
        if not triage_result:
            raise ValueError("No triage result returned")
            
        triage_decision = triage_result.get('triage_decision', {})
        logger.info("✅ Triage analysis complete.")
        logger.info(f"   Severity: {triage_decision.get('severity', 'UNKNOWN')}")
        logger.info(f"   Routing: {triage_decision.get('routing', 'UNKNOWN')}")
        logger.info(f"   Target Agents: {triage_decision.get('target_agents', [])}")
        logger.info(f"   Confidence: {triage_decision.get('confidence', 0.0):.3f}")
        logger.info(f"   Monocle Yeeted: {triage_decision.get('monocle_yeeted', False)}")
        
        # Check routing results
        routing_results = triage_result.get('triage_processing', {}).get('routing_results', {})
        if routing_results:
            logger.info(f"   Routing Type: {routing_results.get('routing_type', 'N/A')}")
            logger.info(f"   Successful Routes: {len(routing_results.get('results', {}))}")
            logger.info(f"   Routing Errors: {len(routing_results.get('errors', []))}")
        
    except Exception as e:
        logger.error(f"❌ Triage engine failed: {e}", exc_info=True)
        return False
    
    # Test 3: Check if metrics contain triage decision
    logger.info("Testing integrated metrics with triage...")
    try:
        final_metrics = await metrics_service.get_metrics()
        if 'triage_decision' in final_metrics:
            logger.info("✅ Metrics successfully integrated with triage decision")
            triage_info = final_metrics['triage_decision']
            logger.info(f"   Integrated Severity: {triage_info.get('severity', 'N/A')}")
            logger.info(f"   Integrated Routing: {triage_info.get('routing', 'N/A')}")
        else:
            logger.warning("⚠️ Triage decision not found in final metrics")
    except Exception as e:
        logger.error(f"❌ Failed to get integrated metrics: {e}", exc_info=True)
        return False
    
    return True

async def main():
    """Run the test suite."""
    logger.info("🚀 Starting real-time metrics flow test...")
    
    success = await test_metrics_flow()
    
    if success:
        logger.info("✅ All tests passed successfully!")
    else:
        logger.error("❌ Some tests failed. Check the logs above for details.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
