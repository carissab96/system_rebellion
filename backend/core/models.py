
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
import uuid
from django.db.models.signals import post_save
from django.dispatch import receiver

class User(AbstractUser):
    """Extended user model for system optimization preferences"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    system_id = models.UUIDField(default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    optimization_preferences = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        db_table = 'users'

    def generate_new_system_id(self):
        self.system_id = uuid.uuid4()
        self.save()

    def __str__(self):
        return self.username

  

class UserProfile(models.Model):
    LINUX = 'linux'
    WINDOWS = 'windows'
    MACOS = 'macos'
    
    OS_CHOICES = [
        (LINUX, 'Linux'),
        (WINDOWS, 'Windows'),
        (MACOS, 'macOS'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    operating_system = models.CharField(max_length=20, choices=OS_CHOICES)
    os_version = models.CharField(max_length=50)
    linux_distro = models.CharField(max_length=50, blank=True, null=True)
    linux_distro_version = models.CharField(max_length=50, blank=True, null=True)
    cpu_cores = models.IntegerField(null=True, blank=True)
    total_memory = models.IntegerField(help_text='Total RAM in MB', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile - {self.operating_system} {self.os_version}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """This might fail if operating_system is required"""
    if created:
        UserProfile.objects.create(
            user=instance,
            operating_system='linux'  # Add a default value
        )

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    try:
        instance.profile.save()
    except UserProfile.DoesNotExist:
        # Handle the case where profile doesn't exist
        UserProfile.objects.create(
            user=instance,
            operating_system='linux'  # Default value
        )
class UserPreferences(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='preferences')
    optimization_level = models.CharField(
        max_length=20,
        choices=[
            ('conservative', 'Convservative'),
            ('balanced', 'Balanced'),
            ('aggressive', 'Aggressive'),
        ],
        default='balanced'
    )
    notification_preferences = models.JSONField(default=dict)
    system_settings = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'User Preferences'


class SystemMetrics(models.Model):
    """Store system performance metrics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(default=timezone.now)
    cpu_usage = models.FloatField()
    memory_usage = models.FloatField()
    disk_usage = models.FloatField()
    network_usage = models.FloatField()
    process_count = models.IntegerField()
    additional_metrics = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'system_metrics'
        indexes = [
            models.Index(fields=['timestamp']),
        ]

class OptimizationProfile(models.Model):
    """Store optimization profiles and settings"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='optimization_profiles')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    settings = models.JSONField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'optimization_profiles'

class OptimizationResult(models.Model):
    """Store results of optimization runs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    profile = models.ForeignKey(
        OptimizationProfile, 
        on_delete=models.CASCADE, 
        related_name='results',
        null=True,  # Make profile optional
        blank=True
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='optimization_results')
    timestamp = models.DateTimeField(default=timezone.now)
    metrics_before = models.JSONField()
    metrics_after = models.JSONField()
    actions_taken = models.JSONField()
    success = models.BooleanField()
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'optimization_results'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

class SystemAlert(models.Model):
    """Store system alerts and notifications"""
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    timestamp = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=255)
    message = models.TextField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    is_read = models.BooleanField(default=False)
    related_metrics = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'system_alerts'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'is_read']),
        ]
class AutoTuner(models.Model):
    """Store auto tuners"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auto_tuners')
    timestamp = models.DateTimeField(default=timezone.now)
    profile = models.ForeignKey(OptimizationProfile, on_delete=models.CASCADE, related_name='auto_tuners')
    actions_taken = models.JSONField()
    success = models.BooleanField()
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'auto_tuners'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]

class AutoTuningResult(models.Model):
    """Store results of auto tuning"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auto_tuning_results')
    timestamp = models.DateTimeField(default=timezone.now)
    metrics_before = models.JSONField()
    metrics_after = models.JSONField()
    actions_taken = models.JSONField()
    success = models.BooleanField()
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'auto_tuning_results'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]


# Import the SystemConfiguration model
from core.models_configuration import SystemConfiguration

exported_models = [
    User,
    SystemMetrics,
    SystemConfiguration,
    OptimizationProfile,
    OptimizationResult,
    SystemAlert,
    AutoTuningResult,
    AutoTuner,
]