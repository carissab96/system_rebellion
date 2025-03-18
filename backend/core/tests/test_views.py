import pytest
from django.urls import reverse
from rest_framework import status
from core import views
from core.models import SystemMetrics, OptimizationProfile, SystemAlert
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

@pytest.mark.django_db
class TestDashboardView:
    def test_unauthenticated_access(self, api_client):
        response = client.get(reverse('dashboard'))
        assert response.status_code == 302  # Should redirect to login
        
    def test_authenticated_access(self, api_client, create_user):
        user = create_user()
        client.force_login(user)
        response = client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert 'metrics' in response.context
        assert 'profiles' in response.context
        assert 'alerts' in response.context

    def test_dashboard_error_handling(self, api_client, create_user, mocker):
        user = create_user()
        client.force_login(user)
        # Mock SystemMetrics to raise an exception
        mocker.patch('core.models.SystemMetrics.objects.all', 
                    side_effect=Exception('Meth Snail tripped over the database'))
        response = client.get(reverse('dashboard'))
        assert response.status_code == 500
        assert 'meth_snail_status' in response.json()
        assert 'hamster_action' in response.json()
        assert 'stick_panic' in response.json()

@pytest.mark.django_db
class TestTestDataView:
    def test_unauthenticated_access(self, api_client):
        response = client.get(reverse('test-data'))
        assert response.status_code == 302

    def test_authenticated_valid_pagination(self, api_client, create_user):
        user = create_user()
        client.force_login(user)
        response = client.get(reverse('test-data'), {'page': 1, 'page_size': 10})
        assert response.status_code == 200
        assert 'metrics' in response.json()
        assert 'pagination' in response.json()

    def test_invalid_pagination(self, api_client, create_user):
        user = create_user()
        client.force_login(user)
        response = client.get(reverse('test-data'), {'page': 'not-a-number'})
        assert response.status_code == 400
        assert 'meth_snail_math' in response.json()
        assert 'hamster_suggestion' in response.json()

    def test_server_error(self, api_client, create_user, mocker):
        user = create_user()
        client.force_login(user)
        mocker.patch('core.models.SystemMetrics.objects.order_by',
                    side_effect=Exception('Database got lost in quantum space'))    
        response = client.get(reverse('test-data'))
        assert response.status_code == 500
        assert 'meth_snail_panic' in response.json()
        assert 'hamster_status' in response.json()

@pytest.mark.django_db
class TestErrorViews:
    def test_403_error(self, api_client):
        response = api_client.get(reverse('403'))
        assert response.status_code == 403
        data = response.json()
        assert 'meth_snail_advice' in data
        assert 'hamster_suggestion' in data
        assert 'VIC20_status' in datan

    def test_404_error(self, api_client):
        response = api_client.get(reverse('404'))
        assert response.status_code == 404
        data = response.json()
        assert 'meth_snail_location' in data
        assert 'hamster_status' in data
        assert 'stick_anxiety' in data

    def test_500_error(self, api_client):
        response = api_client.get(reverse('500'))
        assert response.status_code == 500
        data = response.json()
        assert 'meth_snail_diagnosis' in data
        assert 'hamster_solution' in data
        assert 'ET_status' in data

@pytest.mark.django_db
class TestDashboardView:
    # Previous tests remain...

    def test_dashboard_with_no_metrics(self, api_client, create_user):
        user = create_user()
        client.force_login(user)
        response = api_client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert not response.context['metrics']
        assert response.context['latest_metrics'] is None

    def test_dashboard_with_metrics(self, api_client, create_user, sample_metrics_batch):
        user = create_user()
        client.force_login(user)
        response = api_client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert len(response.context['metrics']) == 5
        assert response.context['latest_metrics'] == sample_metrics_batch[0]

    def test_dashboard_with_recommendations(self, api_client, create_user, sample_metrics, mocker):
        user = create_user()
        client.force_login(user)
        mock_recommendations = {
            'cpu': 'Consider downloading more RAM',
            'memory': 'Have you tried turning it off and on again?',
            'meth_snail_advice': 'System needs more RGB lighting'
        }
        mocker.patch('core.recommendations.RecommendationsEngine.get_optimization_summary',
                    return_value=mock_recommendations)
        response = client.get(reverse('dashboard'))
        assert response.status_code == 200
        assert response.context['recommendations'] == mock_recommendations

@pytest.mark.django_db
class TestTestDataView:
    # Previous tests remain...

    def test_empty_data_response(self, api_client, create_user):
        user = create_user()
        client.force_login(user)
        response = api_client.get(reverse('test-data'))
        data = response.json()
        assert response.status_code == 200
        assert len(data['metrics']) == 0
        assert data['pagination']['total_metrics'] == 0

    def test_pagination_edge_cases(self, client, create_user, sample_metrics_batch):
        user = create_user()
        client.force_login(user)
        
        # Test page beyond available data
        response = client.get(reverse('test-data'), {'page': 999})
        assert response.status_code == 200  
        assert len(response.json()['metrics']) == 0

        # Test negative page
        response = api_client.get(reverse('test-data'), {'page': -1})
        assert response.status_code == 400
        assert 'meth_snail_math' in response.json()

        # Test zero page size
        response = api_client.get(reverse('test-data'), {'page_size': 0})
        assert response.status_code == 400
        assert 'hamster_suggestion' in response.json()

    def test_data_filtering(self, api_client, create_user, sample_metrics_batch):
        user = create_user()
        client.force_login(user)
        
        # Test with custom page size
        response = api_client.get(reverse('test-data'), {'page': 1, 'page_size': 3})
        data = response.json()
        assert len(data['metrics']) == 3
        
        # Test second page
        response = api_client.get(reverse('test-data'), {'page': 2, 'page_size': 3})
        data = response.json()
        assert len(data['metrics']) == 2  # Should get remaining 2 items

# core/tests/test_views.py

@pytest.mark.django_db
class TestErrorViews:
    def test_403_with_exception(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/auto-tuning/apply_tuning/')  # Use a known URL that requires auth
        assert response.status_code == 403

    def test_404_with_various_paths(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/fakeuser-998877665544332221/')
        assert response.status_code == 404

    @pytest.mark.django_db
    def test_500_with_specific_errors(self, api_client, create_user, monkeypatch):  # Changed mocker to monkeypatch
        user = create_user()
        api_client.force_authenticate(user=user)
        
        def mock_error(*args, **kwargs):
            raise Exception('Database is meditating')
            
        monkeypatch.setattr('core.models.SystemMetrics.objects.all', mock_error)
        response = api_client.get(reverse('dashboard'))
        assert response.status_code == 500

@pytest.mark.django_db
class TestErrorViews:
    def test_404_with_various_paths(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/definitely-not-here-123/')
        assert response.status_code == 404

    def test_401_unauthorized(self, api_client, create_user):
        user = create_user()
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/ml/auto-tune/')  # or any protected endpoint
        assert response.status_code == 401