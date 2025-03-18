# core/tests/test_optimization_suite.py

from django.test import TestCase
from core.optimization.system_optimizer import SystemOptimizer
from core.optimization.resource_monitor import ResourceMonitor
from core.optimization.pattern_analyzer import PatternAnalyzer
import asyncio

class HAWKtimizerTests(TestCase):
    """
    Test suite for the HAWKtimizer system
    (Sir Hawkington von Monitorious III presiding)
    """

    def setUp(self):
        """Prepare the HAWKtimizer for testing"""
        self.optimizer = SystemOptimizer()
        self.monitor = ResourceMonitor()
        self.analyzer = PatternAnalyzer()
        
        # Run async initialization in sync context
        asyncio.run(self._async_setup())

    async def _async_setup(self):
        """Async setup tasks"""
        await self.optimizer.initialize()
        await self.monitor.initialize()

    def test_full_optimization_cycle(self):
        """
        Test a complete optimization cycle
        (Or as Sir Hawkington would say, "Let's observe this performance")
        """
        # Run async test in sync context
        asyncio.run(self._async_test_cycle())

    async def _async_test_cycle(self):
        # Collect system metrics
        metrics = await self.monitor.collect_metrics()
        
        print("\n🦅 HAWKtimizer Monitoring Results 🦅")
        print("=" * 50)
        print(f"CPU Usage: {metrics['cpu_usage']}%")
        print(f"Memory Usage: {metrics['memory_usage']}%")
        print(f"Disk Usage: {metrics['disk_usage']}%")
        print(f"Process Count: {metrics['process_count']}")
        
        # Rest of the test remains the same...
        
        # Analyze patterns
        patterns = await self.analyzer.analyze(metrics)
        
        print("\n🧐 Sir Hawkington's Pattern Analysis 🧐")
        print("=" * 50)
        for pattern in patterns:
            print(f"\nPattern Type: {pattern['type']}")
            print(f"Confidence: {pattern['confidence']}")
            print(f"Details: {pattern['details']}")

        # Assert some basic expectations
        self.assertIsNotNone(metrics)
        self.assertIn('cpu_usage', metrics)
        self.assertIn('memory_usage', metrics)
        
        # Test pattern analysis
        pattern_summary = await self.analyzer.get_pattern_summary()
        print("\n📊 Pattern Summary")
        print("=" * 50)
        print(f"Total Patterns: {pattern_summary['total_patterns']}")
        print(f"Pattern Types: {pattern_summary['pattern_types']}")

    async def test_resource_monitoring(self):
        """Test the monitoring capabilities"""
        metrics = await self.monitor.collect_metrics()
        
        print("\n🦅 Resource Monitoring Test 🦅")
        print("=" * 50)
        print("Additional Metrics:", metrics.get('additional', {}))
        
        self.assertIsNotNone(metrics)
        self.assertGreaterEqual(metrics['cpu_usage'], 0)
        self.assertGreaterEqual(metrics['memory_usage'], 0)

    async def test_pattern_detection(self):
        """Test pattern detection capabilities"""
        # Create some test metrics
        test_metrics = {
            'cpu_usage': 85.0,
            'memory_usage': 90.0,
            'disk_usage': 70.0,
            'network_usage': 50.0,
            'process_count': 100,
            'additional': {
                'active_python_processes': 6,
                'load_average': [1.5, 1.2, 1.0]
            }
        }
        
        patterns = await self.analyzer.analyze(test_metrics)
        
        print("\n🧐 Pattern Detection Test 🧐")
        print("=" * 50)
        print(f"Detected {len(patterns)} patterns")
        for pattern in patterns:
            print(f"\nPattern: {pattern['pattern']}")
            print(f"Confidence: {pattern['confidence']}")

        self.assertTrue(len(patterns) > 0, "No patterns detected!")