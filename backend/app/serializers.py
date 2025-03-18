from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.serializers import TokenRefreshSerializer


User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'username': self.user.username,
            'email': self.user.email,
            'system_id': str(self.user.system_id),
           'is_active': self.user.is_active,
            'meth_snail_status': 'Authentication vibes are cosmic!',
            'hamster_approval': 'Token wrapped in quantum duct tape',
            'stick_approval': 'Welcome to the cosmic optimization realm!'
         })
        return data

class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data.update({
            'username': self.user.username,
            'email': self.user.email,
            'system_id': str(self.user.system_id),
           'is_active': self.user.is_active,
            'meth_snail_status': 'Authentication vibes are cosmic!',
            'hamster_approval': 'Token wrapped in quantum duct tape',
            'stick_approval': 'Welcome to the cosmic optimization realm!'
         })
        return data
        