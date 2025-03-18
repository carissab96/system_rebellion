from django.db import models
from django.utils import timezone
import uuid
from app.models import User

class SystemConfiguration(models.Model):
    """
    Store system configurations managed by Sir Hawkington with distinguished elegance.
    
    Sir Hawkington maintains these configurations with his monocle of inspection,
    ensuring that your system remains in a state of distinguished order.
    """
    CONFIG_TYPE_CHOICES = [
        ('NETWORK', 'Network'),
        ('SYSTEM', 'System'),
        ('SECURITY', 'Security'),
        ('PERFORMANCE', 'Performance'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='configurations')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    config_type = models.CharField(max_length=20, choices=CONFIG_TYPE_CHOICES, default='SYSTEM')
    settings = models.JSONField()
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'system_configurations'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['config_type']),
        ]
        verbose_name = "Sir Hawkington's Configuration"
        verbose_name_plural = "Sir Hawkington's Distinguished Configurations"

    def __str__(self):
        return f"{self.name} ({self.get_config_type_display()}) - {'Active' if self.is_active else 'Inactive'}"

    def save(self, *args, **kwargs):
        # If this configuration is being set to active, deactivate all other configurations
        # of the same type for this user
        if self.is_active:
            SystemConfiguration.objects.filter(
                user=self.user,
                config_type=self.config_type,
                is_active=True
            ).exclude(pk=self.pk).update(is_active=False)
        
        super().save(*args, **kwargs)
