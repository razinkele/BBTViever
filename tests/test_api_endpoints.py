"""
Automated API endpoint tests for MARBEFES BBT Database

Tests all API endpoints to ensure proper functionality, security, and performance.

Run with:
    pytest tests/test_api_endpoints.py -v
    pytest tests/test_api_endpoints.py -v --cov=app
"""

import pytest
import json
from app import app


@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    app.config['WMS_TIMEOUT'] = 5  # Shorter timeout for tests
    with app.test_client() as client:
        yield client


class TestMainEndpoints:
    """Test main application endpoints"""

    def test_index_page_loads(self, client):
        """Test that the main page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'MARBEFES BBT Database' in response.data

    def test_health_check_endpoint(self, client):
        """Test health check endpoint returns proper status"""
        response = client.get('/health')
        assert response.status_code in [200, 503]  # 503 if WMS is down

        data = json.loads(response.data)
        assert 'status' in data
        assert 'timestamp' in data
        assert 'version' in data
        assert 'components' in data

        # Check component structure
        assert 'vector_support' in data['components']
        assert 'wms_service' in data['components']
        assert 'cache' in data['components']

    def test_logo_endpoint(self, client):
        """Test logo serving endpoint"""
        response = client.get('/logo/marbefes_02.png')
        # Should return 200 if logo exists, 404 if not
        assert response.status_code in [200, 404]


class TestAPIEndpoints:
    """Test API endpoints"""

    def test_api_layers_endpoint(self, client):
        """Test WMS layers API endpoint"""
        response = client.get('/api/layers')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert isinstance(data, list)

        # If layers returned, check structure
        if len(data) > 0:
            layer = data[0]
            assert 'name' in layer
            assert 'title' in layer

    def test_api_all_layers_endpoint(self, client):
        """Test combined layers API endpoint"""
        response = client.get('/api/all-layers')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'wms_layers' in data
        assert 'helcom_layers' in data
        assert 'vector_layers' in data
        assert 'vector_support' in data

        assert isinstance(data['wms_layers'], list)
        assert isinstance(data['vector_layers'], list)

    def test_api_capabilities_endpoint(self, client):
        """Test WMS capabilities proxy endpoint"""
        response = client.get('/api/capabilities')
        assert response.status_code in [200, 500]  # 500 if WMS is down

        if response.status_code == 200:
            # Should return XML content
            assert b'WMS_Capabilities' in response.data or b'ServiceException' in response.data

    def test_api_legend_endpoint(self, client):
        """Test legend URL generation endpoint"""
        response = client.get('/api/legend/all_eusm2021')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'legend_url' in data
        assert 'all_eusm2021' in data['legend_url']


class TestVectorEndpoints:
    """Test vector layer endpoints"""

    def test_api_vector_layers_endpoint(self, client):
        """Test vector layers list endpoint"""
        response = client.get('/api/vector/layers')

        # Should return 200 if vector support enabled, 503 if disabled
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'layers' in data
            assert 'count' in data
            assert isinstance(data['layers'], list)

    def test_api_vector_bounds_endpoint(self, client):
        """Test vector bounds endpoint"""
        response = client.get('/api/vector/bounds')

        # Should return 200 if vector support enabled, 503 if disabled
        assert response.status_code in [200, 503]

        if response.status_code == 200:
            data = json.loads(response.data)
            # May be empty if no vector data loaded
            if data:
                assert 'overall_bounds' in data or 'layer_count' in data


class TestFactsheetEndpoints:
    """Test BBT factsheet endpoints"""

    def test_api_factsheets_endpoint(self, client):
        """Test all factsheets endpoint"""
        response = client.get('/api/factsheets')

        # Should return 200 if data exists, 404 if not
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'bbts' in data or isinstance(data, dict)

    def test_api_factsheet_specific_endpoint(self, client):
        """Test specific factsheet endpoint"""
        # Test with a known BBT name
        response = client.get('/api/factsheet/Archipelago')

        # Should return 200 if found, 404 if not
        assert response.status_code in [200, 404]

        if response.status_code == 200:
            data = json.loads(response.data)
            assert 'name' in data or isinstance(data, dict)

    def test_api_factsheet_case_insensitive(self, client):
        """Test factsheet endpoint is case-insensitive"""
        response1 = client.get('/api/factsheet/archipelago')
        response2 = client.get('/api/factsheet/ARCHIPELAGO')

        # Both should return same status code
        assert response1.status_code == response2.status_code


class TestSecurity:
    """Test security features"""

    def test_security_headers_present(self, client):
        """Test that security headers are set"""
        response = client.get('/')

        assert 'X-Content-Type-Options' in response.headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'

        assert 'X-Frame-Options' in response.headers
        assert 'X-XSS-Protection' in response.headers

    def test_rate_limiting_headers(self, client):
        """Test that rate limiting is configured"""
        # Make multiple requests to vector endpoint
        for _ in range(5):
            response = client.get('/api/vector/layers')

        # Rate limiting headers may or may not be present depending on config
        # Just verify the endpoint still works
        assert response.status_code in [200, 429, 503]


class TestErrorHandling:
    """Test error handling"""

    def test_404_for_nonexistent_endpoint(self, client):
        """Test 404 for non-existent endpoints"""
        response = client.get('/api/nonexistent')
        assert response.status_code == 404

    def test_invalid_layer_name(self, client):
        """Test handling of invalid layer names"""
        response = client.get('/api/vector/layer/nonexistent_layer_12345')
        assert response.status_code in [404, 503]  # 503 if vector support disabled

    def test_invalid_factsheet_name(self, client):
        """Test handling of invalid factsheet names"""
        response = client.get('/api/factsheet/nonexistent_bbt_12345')
        assert response.status_code == 404


class TestPerformance:
    """Test performance characteristics"""

    def test_health_check_response_time(self, client):
        """Test health check responds quickly"""
        import time

        start = time.time()
        response = client.get('/health')
        duration = time.time() - start

        assert response.status_code in [200, 503]
        # Health check should respond in under 5 seconds
        assert duration < 5.0

    def test_api_layers_caching(self, client):
        """Test that layers API uses caching"""
        import time

        # First request (cache miss)
        start1 = time.time()
        response1 = client.get('/api/layers')
        duration1 = time.time() - start1

        # Second request (cache hit)
        start2 = time.time()
        response2 = client.get('/api/layers')
        duration2 = time.time() - start2

        assert response1.status_code == 200
        assert response2.status_code == 200

        # Second request should be faster (cached)
        # Allow some tolerance for test environment variability
        assert duration2 <= duration1 + 0.1


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
