# test_authentication.py
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from core.models import User

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def make_user(username="distinguished_tester", email="monocle@testing.com"):
    return User.objects.create_user(
        username=username,
        email=email,
        password="SecureP@ssw0rd123!"
    )

@pytest.mark.django_db
class TestRegistration:
    def test_registration_valid(self, api_client, make_user):
        url = reverse('user-register')
        payload = {
            "username": "distinguished_tester",
            "email": "monocle@testing.com",
            "password": "SecureP@ssw0rd123!",
            "password2": "SecureP@ssw0rd123!"
        }
        response = api_client.post(url, payload)
        assert response.status_code == 201
        assert "username" in response.data
        assert response.data["username"] == payload["username"]

    def test_registration_duplicate_username(self, api_client, make_user):
        # Create initial user
        make_user()
        
        url = reverse('user-register')
        payload = {
            "username": "distinguished_tester",  # Already exists
            "email": "another@testing.com",
            "password": "SecureP@ssw0rd123!",
            "password2": "SecureP@ssw0rd123!"
        }
        response = api_client.post(url, payload)
        assert response.status_code == 400
        assert "username" in response.data

    def test_registration_invalid_email(self, api_client):
        url = reverse('user-register')
        payload = {
            "username": "new_tester",
            "email": "not_an_email",
            "password": "SecureP@ssw0rd123!",
            "password2": "SecureP@ssw0rd123!"
        }
        response = api_client.post(url, payload)
        assert response.status_code == 400
        assert "email" in response.data

@pytest.mark.django_db
class TestLogin:
    def test_login_valid(self, api_client, make_user):
        # Create user first
        make_user()
        
        url = reverse('token_obtain_pair')
        payload = {
            "username": "distinguished_tester",
            "password": "SecureP@ssw0rd123!"
        }
        response = api_client.post(url, payload)
        assert response.status_code == 200
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_credentials(self, api_client, make_user):
        # Create user first
        make_user()
        
        url = reverse('token_obtain_pair')
        payload = {
            "username": "distinguished_tester",
            "password": "WrongPassword123!"
        }
        response = api_client.post(url, payload)
        assert response.status_code == 401

@pytest.mark.django_db
class TestTokens:
    def test_token_refresh(self, api_client, make_user):
        # First login to get tokens
        make_user()
        login_response = api_client.post(
            reverse('token_obtain_pair'),
            {
                "username": "distinguished_tester",
                "password": "SecureP@ssw0rd123!"
            }
        )
        refresh_token = login_response.data['refresh']
        
        # Test refresh
        url = reverse('token_refresh')
        response = api_client.post(url, {"refresh": refresh_token})
        assert response.status_code == 200
        assert "access" in response.data

    def test_token_verify(self, api_client, make_user):
        # First login to get tokens
        make_user()
        login_response = api_client.post(
            reverse('token_obtain_pair'),
            {
                "username": "distinguished_tester",
                "password": "SecureP@ssw0rd123!"
            }
        )
        access_token = login_response.data['access']
        
        # Test verify
        url = reverse('token_verify')
        response = api_client.post(url, {"token": access_token})
        assert response.status_code == 200
# test_authentication_extended.py
import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from core.models import User
from datetime import timedelta
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

# Additional Password Validation Tests
@pytest.mark.django_db
class TestPasswordValidation:
    def test_password_too_short(self, api_client):
        url = reverse('user-register')
        payload = {
            "username": "new_tester",
            "email": "valid@test.com",
            "password": "Short1!",
            "password2": "Short1!"
        }
        response = api_client.post(url, payload)
        assert response.status_code == 400
        assert "password" in response.data

    def test_password_common(self, api_client):
        url = reverse('user-register')
        payload = {
            "username": "new_tester",
            "email": "valid@test.com",
            "password": "password123",
            "password2": "password123"
        }
        response = api_client.post(url, payload)
        assert response.status_code == 400
        assert "password" in response.data

    def test_password_numeric_only(self, api_client):
        url = reverse('user-register')
        payload = {
            "username": "new_tester",
            "email": "valid@test.com",
            "password": "12345678",
            "password2": "12345678"
        }
        response = api_client.post(url, payload)
        assert response.status_code == 400
        assert "password" in response.data

# Token Expiration Tests
@pytest.mark.django_db
class TestTokenExpiration:
    @pytest.fixture
    def expired_token(self, create_user):
        user = create_user()
        refresh = RefreshToken.for_user(user)
        refresh.set_exp(lifetime=timedelta(seconds=-1))
        return str(refresh)

    def test_expired_refresh_token(self, api_client, expired_token):
        url = reverse('token_refresh')
        response = api_client.post(url, {"refresh": expired_token})
        assert response.status_code == 401

    def test_token_expiry_window(self, api_client, create_user):
        user = create_user()
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        url = reverse('token_verify')
        response = api_client.post(url, {"token": access_token})
        assert response.status_code == 200

# Concurrent Login Tests
@pytest.mark.django_db
class TestConcurrentLogin:
    def test_multiple_logins(self, api_client, create_user):
        user = create_user()
        url = reverse('token_obtain_pair')
        payload = {
            "username": "distinguished_tester",
            "password": "SecureP@ssw0rd123!"
        }
        
        # First login
        response1 = api_client.post(url, payload)
        assert response1.status_code == 200
        token1 = response1.data['access']
        
        # Second login
        response2 = api_client.post(url, payload)
        assert response2.status_code == 200
        token2 = response2.data['access']
        
        # Verify both tokens work
        verify_url = reverse('token_verify')
        assert api_client.post(verify_url, {"token": token1}).status_code == 200
        assert api_client.post(verify_url, {"token": token2}).status_code == 200