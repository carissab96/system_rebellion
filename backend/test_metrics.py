import asyncio
import logging
from app.services.metrics.simplified_metrics_service import SimplifiedMetricsService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_metrics():
    try:
        logger.info("Getting metrics service instance...")
        metrics_service = await SimplifiedMetricsService.get_instance()
        
        logger.info("Fetching metrics...")
        metrics = await metrics_service.get_metrics(force_refresh=True)
        
        logger.info("Metrics received:")
        print(metrics)
        
        # Test individual metrics
        logger.info("Fetching CPU metrics...")
        cpu_metrics = await metrics_service.get_cpu_metrics()
        logger.info("CPU metrics received:")
        print(cpu_metrics)
        
        return metrics
    except Exception as e:
        logger.error(f"Error testing metrics: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = asyncio.run(test_metrics())
    print("\nFinal result:", result)
