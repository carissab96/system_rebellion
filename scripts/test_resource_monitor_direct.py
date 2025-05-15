#!/usr/bin/env python3
"""
Direct test script for ResourceMonitor with proper path handling.
"""
import sys
import os
import asyncio
import logging
from datetime import datetime, timedelta

# Add the project root to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Now import the ResourceMonitor directly
from backend.app.optimization.resource_monitor import ResourceMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('resource_monitor_test.log')
    ]
)

logger = logging.getLogger('ResourceMonitorTest')

async def test_resource_monitor():
    """Test the resource monitor with timing information."""
    monitor = ResourceMonitor()
    
    try:
        logger.info("Initializing resource monitor...")
        await monitor.initialize()
        logger.info("Resource monitor initialized")
        
        # Run for 30 seconds with 5-second intervals
        start_time = datetime.now()
        end_time = start_time + timedelta(seconds=30)
        iteration = 0
        
        while datetime.now() < end_time:
            iteration += 1
            logger.info(f"\n--- Iteration {iteration} ---")
            
            # Collect metrics
            iteration_start = datetime.now()
            try:
                metrics = await monitor.collect_metrics()
                iteration_duration = (datetime.now() - iteration_start).total_seconds()
                
                logger.info(f"Collection took {iteration_duration:.2f} seconds")
                logger.info(f"Collected metrics: {list(metrics.keys())}")
                
                # Wait for next iteration
                sleep_time = max(0, 5.0 - iteration_duration)
                if sleep_time > 0:
                    await asyncio.sleep(sleep_time)
                    
            except Exception as e:
                logger.error(f"Error during collection: {e}", exc_info=True)
                await asyncio.sleep(1)
                
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
    finally:
        logger.info("Cleaning up...")
        await monitor.cleanup()
        logger.info("Test completed")

if __name__ == "__main__":
    print("=== Resource Monitor Test ===")
    print("This will test the resource monitor for 30 seconds with 5-second intervals.")
    print("Press Ctrl+C to stop the test early\n")
    
    asyncio.run(test_resource_monitor())
