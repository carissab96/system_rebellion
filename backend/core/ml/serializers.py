from rest_framework import serializers
from typing import Dict, Any

class MetricsSerializer(serializers.Serializer):
    cpu_usage = serializers.FloatField(min_value=0, max_value=100)
    memory_usage = serializers.FloatField(min_value=0, max_value=100)
    disk_usage = serializers.FloatField(min_value=0, max_value=100)
    network_usage = serializers.FloatField(min_value=0, required=False)
    process_count = serializers.IntegerField(min_value=0, required=False)
    timestamp = serializers.DateTimeField(required=False)

class PatternSerializer(serializers.Serializer):
    pattern_type = serializers.CharField()
    metrics = MetricsSerializer()
    confidence = serializers.FloatField(min_value=0, max_value=1)
    duration = serializers.IntegerField(min_value=0)

class ContextVectorSerializer(serializers.Serializer):
    platform_type = serializers.CharField()
    user_preferences = serializers.DictField(required=False)
    system_state = MetricsSerializer()
    active_patterns = serializers.ListField(
        child=PatternSerializer(),
        required=False
    )

class ValidationRequestSerializer(serializers.Serializer):
    pattern = PatternSerializer()
    metrics = MetricsSerializer()

class ValidationResponseSerializer(serializers.Serializer):
    is_valid = serializers.BooleanField()
    confidence = serializers.FloatField()
    validation_metrics = serializers.DictField()

class MatchRequestSerializer(serializers.Serializer):
    current_state = MetricsSerializer()

class MatchResponseSerializer(serializers.Serializer):
    matched_pattern = PatternSerializer(allow_null=True)
    similarity_score = serializers.FloatField()
    confidence = serializers.FloatField()

class ContextUpdateSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    platform_id = serializers.CharField()
    context_data = ContextVectorSerializer()

class PatternLearningSerializer(serializers.Serializer):
    user_id = serializers.CharField()
    context_vector = ContextVectorSerializer()
    learned_patterns = serializers.ListField(
        child=PatternSerializer(),
        required=False
    )

# ABANDON PROPRIETY ALL YE WHO ENTER HERE
class MetricsSerializer(serializers.Serializer):
    cpu_usage = serializers.FloatField(
        min_value=0, max_value=100,
        help_text="How hard we're making the hamsters run"
    )
    memory_usage = serializers.FloatField(
        min_value=0, max_value=100,
        help_text="RAM? More like DAMN!"
    )
    # The stick insisted on proper validation here
    disk_usage = serializers.FloatField(min_value=0, max_value=100)

class PatternSerializer(serializers.Serializer):
    # The quantum shadow people are watching this pattern
    pattern_type = serializers.CharField()
    metrics = MetricsSerializer()
    confidence = serializers.FloatField(
        min_value=0, max_value=1,
        help_text="How sure are the meth snails about this one"
    )