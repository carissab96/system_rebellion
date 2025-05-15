#!/usr/bin/env python3
"""
Test script for the InstrumentedResourceMonitor.
This script will help identify performance bottlenecks in the resource monitoring.
"""
import asyncio
import logging
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List
import os

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.optimization.resource_monitor_instrumented import InstrumentedResourceMonitor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('resource_monitor_test.log')
    ]
)

class ResourceMonitorTester:
    """Helper class to test the resource monitor with different configurations."""
    
    def __init__(self):
        self.monitor = InstrumentedResourceMonitor()
        self.logger = logging.getLogger('ResourceMonitorTester')
        self.results: List[Dict[str, Any]] = []
    
    async def run_test(self, duration_seconds: int = 30, collection_interval: float = 5.0):
        """Run the resource monitor test for the specified duration."""
        self.logger.info("=== Starting Resource Monitor Test ===")
        self.logger.info(f"Duration: {duration_seconds} seconds")
        self.logger.info(f"Collection interval: {collection_interval} seconds")
        
        try:
            # Initialize the monitor
            self.logger.info("Initializing resource monitor...")
            await self.monitor.initialize()
            self.logger.info("Resource monitor initialized")
            
            # Run for the specified duration
            start_time = datetime.now()
            end_time = start_time + timedelta(seconds=duration_seconds)
            iteration = 0
            
            while datetime.now() < end_time:
                iteration += 1
                self.logger.info(f"\n--- Iteration {iteration} ---")
                
                # Collect metrics
                iteration_start = datetime.now()
                try:
                    metrics = await self.monitor.collect_metrics()
                    iteration_duration = (datetime.now() - iteration_start).total_seconds()
                    
                    # Log results
                    result = {
                        'iteration': iteration,
                        'timestamp': iteration_start.isoformat(),
                        'duration_seconds': iteration_duration,
                        'metrics_keys': list(metrics.keys()) if metrics else []
                    }
                    self.results.append(result)
                    
                    self.logger.info(f"Collection took {iteration_duration:.2f} seconds")
                    
                    # Calculate sleep time, ensuring we don't sleep if we're already behind
                    sleep_time = max(0, collection_interval - iteration_duration)
                    if sleep_time > 0:
                        self.logger.debug(f"Sleeping for {sleep_time:.2f} seconds")
                        await asyncio.sleep(sleep_time)
                    
                except Exception as e:
                    self.logger.error(f"Error during collection: {e}", exc_info=True)
                    # Wait a bit before retrying
                    await asyncio.sleep(1)
                    
        except KeyboardInterrupt:
            self.logger.info("Test interrupted by user")
        except Exception as e:
            self.logger.error(f"Error during test: {e}", exc_info=True)
        finally:
            # Clean up
            self.logger.info("Cleaning up...")
            await self.monitor.cleanup()
            self.logger.info("=== Test completed ===")
    
    def print_summary(self):
        """Print a summary of the test results."""
        if not self.results:
            print("No results to summarize")
            return
        
        durations = [r['duration_seconds'] for r in self.results]
        avg_duration = sum(durations) / len(durations)
        max_duration = max(durations)
        min_duration = min(durations)
        
        print("\n=== Test Summary ===")
        print(f"Total iterations: {len(self.results)}")
        print(f"Average duration: {avg_duration:.2f} seconds")
        print(f"Maximum duration: {max_duration:.2f} seconds")
        print(f"Minimum duration: {min_duration:.2f} seconds")
        
        # Print slowest iterations
        print("\nTop 5 slowest iterations:")
        for i, result in enumerate(sorted(self.results, key=lambda x: x['duration_seconds'], reverse=True)[:5]):
            print(f"  {i+1}. Iteration {result['iteration']}: {result['duration_seconds']:.2f} seconds")

async def main():
    """Main test function."""
    print("=== Resource Monitor Performance Test ===")
    print("This will test the resource monitor for 30 seconds with 5-second collection intervals.")
    print("Detailed logs will be written to resource_monitor_test.log")
    print("Press Ctrl+C to stop the test early\n")
    
    tester = ResourceMonitorTester()
    
    try:
        # Run the test for 30 seconds with 5-second collection interval
        await tester.run_test(duration_seconds=30, collection_interval=5.0)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Print summary
        tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())
