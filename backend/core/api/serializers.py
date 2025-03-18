from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
import uuid
from ..models import (
    SystemMetrics, 
    OptimizationProfile, 
    OptimizationResult, 
    SystemAlert,
    UserPreferences,
    UserProfile,
    AutoTuner,
    AutoTuningResult
)
from core.models_configuration import SystemConfiguration
# Import Sir Hawkington's distinguished SystemConfigurationSerializer

User = get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            "operating_system",
            "os_version",
            "linux_distro",
            "linux_distro_version",
            "cpu_cores",
            "total_memory",
        )
        extra_kwargs = {
            "operating_system": {"required": True},
            "os_version": {"required": True},
        }

class UserPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreferences
        fields = '__all__'
        read_only_fields = ('id',)

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(required=True)
    preferences = UserPreferencesSerializer(required=False)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 
                 'profile', 'preferences', 'system_id')
        read_only_fields = ('id', 'system_id')

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    profile = UserProfileSerializer(required=True)
    preferences = UserPreferencesSerializer(required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 
                 'first_name', 'last_name', 'profile', 'preferences')

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'error': 'Passwords do not match',
                'meth_snail_advice': 'Your passwords are in different dimensions, man',
                'hamster_suggestion': 'Try typing with duct tape on your fingers'
            })
        return attrs

    def create(self, validated_data):
        print("🧐 Sir Hawkington is orchestrating your registration with distinguished precision!")
        profile_data = validated_data.pop('profile')
        preferences_data = validated_data.pop('preferences', {})
        validated_data.pop('password_confirm')
        
        # Create user with Sir Hawkington's guidance
        print("🎩 Creating your distinguished user account...")
        user = User.objects.create_user(**validated_data)
        user.system_id = uuid.uuid4()
        user.save()

        # Create profile while the Meth Snail validates system specs
        print("🐌 The Meth Snail is processing your system specifications...")
        UserProfile.objects.create(user=user, **profile_data)
        
        # Create preferences with the Quantum Shadow People's suggestions
        print("👻 The Quantum Shadow People are configuring your preferences...")
        UserPreferences.objects.create(
            user=user,
            theme='cyberpunk',
            notifications_enabled=True,
            **preferences_data
        )
        
        # Create initial system configurations with Sir Hawkington's recommendations
        print("🧐 Sir Hawkington is preparing your initial system configurations...")
        
        # Network configuration by the Quantum Shadow People
        SystemConfiguration.objects.create(
            user=user,
            name="Quantum Shadow People's Network Setup",
            description="A distinguished network configuration suggested by the Quantum Shadow People",
            config_type='NETWORK',
            settings={
                'dns_servers': ['8.8.8.8', '1.1.1.1'],
                'use_ipv6': True,
                'firewall_enabled': True,
                'quantum_shadow_protection': True
            },
            is_active=True
        )
        
        # Performance configuration by the Meth Snail
        SystemConfiguration.objects.create(
            user=user,
            name="Meth Snail's Speed Boost",
            description="A high-performance configuration powered by the Meth Snail's frantic energy",
            config_type='PERFORMANCE',
            settings={
                'cpu_governor': 'performance',
                'memory_compression': True,
                'disk_write_cache': True,
                'meth_snail_boost': True
            }
        )
        
        # Security configuration with The Stick's anxiety management
        SystemConfiguration.objects.create(
            user=user,
            name="The Stick's Anxiety Shield",
            description="A security configuration that keeps The Stick's anxiety at bay",
            config_type='SECURITY',
            settings={
                'firewall_level': 'high',
                'auto_updates': True,
                'port_scanning_protection': True,
                'stick_anxiety_level': 'medium'
            }
        )
        
        print("✨ Registration complete! Sir Hawkington welcomes you with a distinguished bow!")
        return user

# Your existing model serializers stay the same
class SystemMetricsSerializer(serializers.ModelSerializer):
    additional_metrics = serializers.JSONField(required=False, allow_null=True)
    
    class Meta:
        model = SystemMetrics
        fields = '__all__'

    def validate_additional_metrics(self, value):
        if value is None:
            return {}
        return value

class OptimizationProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimizationProfile
        fields = '__all__'
        
class OptimizationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = OptimizationResult
        fields = '__all__'
        
class SystemAlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemAlert
        fields = '__all__'

class AutoTuningSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoTuner
        fields = '__all__'

class AutoTuningResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = AutoTuningResult
        fields = '__all__'


class SystemConfigurationSerializer(serializers.ModelSerializer):
    """
    Serializer for Sir Hawkington's distinguished system configurations.
    
    Sir Hawkington insists on proper serialization with his monocle of inspection.
    """
    user_username = serializers.ReadOnlyField(source='user.username')
    config_type_display = serializers.ReadOnlyField(source='get_config_type_display')
    
    class Meta:
        model = SystemConfiguration
        fields = [
            'id', 'user', 'user_username', 'name', 'description', 
            'config_type', 'config_type_display', 'settings', 
            'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'user_username', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create a new configuration with the current user."""
        user = self.context['request'].user
        validated_data['user'] = user
        
        # Sir Hawkington's distinguished log
        print(f"🧐 Sir Hawkington is creating a new {validated_data.get('config_type', 'SYSTEM')} configuration with distinguished elegance!")
        
        return super().create(validated_data)
    
    def validate_settings(self, value):
        """
        Validate that settings is a proper JSON object.
        Sir Hawkington insists on proper formatting!
        """
        if not isinstance(value, dict):
            raise serializers.ValidationError(
                "Sir Hawkington is most displeased! Settings must be a proper JSON object."
            )
        return value


