# core/tests/test_recommendations.py
from django.test import TestCase
from core.models import SystemMetrics
from core.recommendations import RecommendationsEngine
from datetime import datetime

class RecommendationEngineTests(TestCase):
    def setUp(self):
        """Set up test scenarios"""
        # Stress test metrics
        self.stress_metrics = SystemMetrics.objects.create(
            cpu_usage=95.0,
            memory_usage=88.0,
            disk_usage=92.0,
            network_usage=75.0,
            process_count=187,
            additional_metrics={
                'swap_usage': 45.2,
                'cpu_temperature': 85,
                'active_python_processes': 12,
                'chrome_tabs': 'way too many',
                'stackoverflow_visits': 'astronomical'
            }
        )

        # Development metrics
        self.dev_metrics = SystemMetrics.objects.create(
            cpu_usage=45.0,
            memory_usage=60.0,
            disk_usage=55.0,
            network_usage=30.0,
            process_count=84,
            additional_metrics={
                'active_python_processes': 6,
                'ide_running': True,
                'git_operations_pending': 3,
                'coffee_level': 'needs refill'
            }
        )

        self.engine = RecommendationsEngine()

    def test_stress_scenario(self):
        """Test recommendations for stress scenario"""
        results = self.engine.get_optimization_summary(self.stress_metrics)
        
        print("\n🔥 STRESS TEST RESULTS 🔥")
        print("=" * 50)
        self._print_recommendations(results)

        # Actual test assertions
        self.assertTrue(results['high_priority'] > 0)
        self.assertGreater(float(results['potential_improvement'].strip('%')), 20)

    def test_dev_scenario(self):
        """Test recommendations for development scenario"""
        results = self.engine.get_optimization_summary(self.dev_metrics)
        
        print("\n👩‍💻 DEVELOPMENT SCENARIO RESULTS 👩‍💻")
        print("=" * 50)
        self._print_recommendations(results)

        # Actual test assertions
        self.assertIn('development', 
                     [r['type'] for r in results['recommendations']])

    def _print_recommendations(self, results):
        """Helper to print formatted recommendations"""
        print(f"Total Recommendations: {results['total_recommendations']}")
        print(f"High Priority Issues: {results['high_priority']}")
        print(f"Potential Improvement: {results['potential_improvement']}")
        print("\nDetailed Recommendations:")
        for rec in results['recommendations']:
            print(f"\n📊 {rec['title']}")
            print(f"Severity: {rec['severity']}")
            print(f"Suggestion: {rec['suggestion']}")
            if 'potential_gain' in rec:
                print(f"Potential Gain: {rec['potential_gain']}")