import pytest
from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model

@pytest.mark.django_db
class TestUserAuthentication:
    def test_user_registration(self, client):
        url = reverse('user-register')
        data = {
            'username': 'test_user',
            'email': 'test@hawkington.tech',
            'password': 'SuperSecure123!',
            'password_confirm': 'SuperSecure123!',
            'system_name': 'TestStystem',
            'preferences': {
                'optimization_level': 'meth_snail',
                'notification_prefences': {
                    'enable_snail_alerts': True,
                    'hamster_notifications': 'duct_tape_priority'
                }
            }
        }
        response = cleint.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'system_id' in response.data
        assert 'meth_snail_welcome' in response.data

    def test_user_login(self, client, test_user):
        url = revers('user-login')
        response = client.post(url, {
            'username': test_user.username,
            'password': 'test_password'
        })
        assert response.status_code == status.HTTP_200_OK
        assert 'Sir Hawkington' in response.data['message']

    @pytest.fixture
    def test_user(self, django_user_model):
        return django_user_model.objects.create_user(
            username='test_user',
            password='test_password',
            system_id=uuid.uuid4(),
            system_name='TestSystem',
            preferences={
                'optimization_level': 'meth_snail',
                'notification_prefences': {
                    'enable_snail_alerts': True,
                    'hamster_notifications': 'duct_tape_priority'
                }
            }
        )
        