# core/tests/test_models.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from core.models import SystemMetrics, OptimizationProfile, SystemAlert

User = get_user_model()

class ModelTests(TestCase):
    def setUp(self):
        # Create test user with optimization preferences
        self.test_user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.test_user.optimization_preferences = {
            "default_cpu_priority": "normal",
            "max_memory_limit": 8192,
            "preferred_optimization_time": "02:00",
            "notification_threshold": "medium"
        }
        self.test_user.save()

        # Create test optimization profile linked to user
        self.profile = OptimizationProfile.objects.create(
            user=self.test_user,
            name="Test Profile",
            settings={
                "cpu_priority": "high",
                "memory_limit": 4096,
                "background_processes": "minimal",
                "ide_optimization": True
            }
        )
        
        # Create test metrics
        self.metrics = SystemMetrics.objects.create(
            cpu_usage=50.0,
            memory_usage=60.0,
            disk_usage=70.0,
            network_usage=30.0,
            process_count=100,
            additional_metrics={
                "swap_usage": 15.2,
                "cpu_temperature": 45,
                "active_python_processes": 3
            }
        )

        # Create test alert linked to user
        self.alert = SystemAlert.objects.create(
            user=self.test_user,
            title="Test Alert",
            message="Test system alert message",
            severity="HIGH",
            related_metrics={
                "cpu_usage": 90.5,
                "process_name": "test_process",
                "timestamp": "2024-02-18T14:30:00Z"
            }
        )

    def test_user_preferences(self):
        """Test user optimization preferences"""
        self.assertEqual(
            self.test_user.optimization_preferences['default_cpu_priority'],
            'normal'
        )
        self.assertEqual(
            self.test_user.optimization_preferences['max_memory_limit'],
            8192
        )

    def test_optimization_profile(self):
        """Test optimization profile creation and relationships"""
        self.assertEqual(self.profile.name, "Test Profile")
        self.assertTrue(self.profile.is_active)
        self.assertEqual(self.profile.user, self.test_user)
        self.assertEqual(self.profile.settings['cpu_priority'], 'high')

    def test_system_metrics(self):
        """Test system metrics creation and values"""
        self.assertEqual(self.metrics.cpu_usage, 50.0)
        self.assertEqual(self.metrics.memory_usage, 60.0)
        self.assertEqual(
            self.metrics.additional_metrics['cpu_temperature'],
            45
        )

    def test_system_alert(self):
        """Test system alert creation and relationships"""
        self.assertEqual(self.alert.user, self.test_user)
        self.assertEqual(self.alert.severity, "HIGH")
        self.assertEqual(
            self.alert.related_metrics['cpu_usage'],
            90.5
        )