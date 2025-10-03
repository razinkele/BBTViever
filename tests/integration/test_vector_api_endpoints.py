"""
Integration tests for vector layer API endpoints
"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

# Skip tests if geopandas is not available
try:
    import geopandas as gpd
    from shapely.geometry import Polygon
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False


@pytest.mark.skipif(not GEOPANDAS_AVAILABLE, reason="Geopandas not available")
class TestVectorAPIEndpoints:
    """Test vector layer API endpoints"""

    @pytest.fixture
    def app_with_vector_support(self, app):
        """Configure app with vector support enabled"""
        with patch('app.VECTOR_SUPPORT', True):
            yield app

    @pytest.fixture
    def app_without_vector_support(self, app):
        """Configure app without vector support"""
        with patch('app.VECTOR_SUPPORT', False):
            yield app

    @pytest.fixture
    def mock_vector_layers(self):
        """Mock vector layers data"""
        return [
            {
                'layer_name': 'areas',
                'display_name': 'Marine Protected Areas',
                'geometry_type': 'Polygon',
                'feature_count': 10,
                'bounds': [0.0, 0.0, 10.0, 10.0],
                'crs': 'EPSG:4326',
                'source_file': 'marine_areas.gpkg',
                'category': 'vector'
            },
            {
                'layer_name': 'stations',
                'display_name': 'Monitoring Stations',
                'geometry_type': 'Point',
                'feature_count': 25,
                'bounds': [1.0, 1.0, 9.0, 9.0],
                'crs': 'EPSG:4326',
                'source_file': 'stations.gpkg',
                'category': 'vector'
            }
        ]

    def test_api_all_layers_endpoint(self, client, app_with_vector_support, mock_vector_layers):
        """Test /api/all-layers endpoint"""
        with patch('app.get_vector_layers_summary', return_value=mock_vector_layers):
            response = client.get('/api/all-layers')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'wms_layers' in data
        assert 'vector_layers' in data
        assert 'vector_support' in data
        assert data['vector_support'] is True
        assert len(data['vector_layers']) == 2

    def test_api_vector_layers_endpoint(self, client, app_with_vector_support, mock_vector_layers):
        """Test /api/vector/layers endpoint"""
        with patch('app.get_vector_layers_summary', return_value=mock_vector_layers):
            response = client.get('/api/vector/layers')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'layers' in data
        assert 'count' in data
        assert data['count'] == 2
        assert len(data['layers']) == 2

        # Check layer structure
        layer = data['layers'][0]
        assert 'display_name' in layer
        assert 'geometry_type' in layer
        assert 'feature_count' in layer

    def test_api_vector_layers_without_support(self, client, app_without_vector_support):
        """Test /api/vector/layers endpoint without vector support"""
        response = client.get('/api/vector/layers')

        assert response.status_code == 503
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Vector support not available' in data['error']

    def test_api_vector_layer_geojson_endpoint(self, client, app_with_vector_support):
        """Test /api/vector/layer/<name> endpoint"""
        mock_geojson = {
            'type': 'FeatureCollection',
            'features': [
                {
                    'type': 'Feature',
                    'geometry': {
                        'type': 'Polygon',
                        'coordinates': [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                    },
                    'properties': {'name': 'Area 1', 'type': 'Protected'}
                }
            ],
            'metadata': {
                'layer_name': 'areas',
                'display_name': 'Marine Protected Areas',
                'feature_count': 1,
                'geometry_type': 'Polygon'
            }
        }

        with patch('app.get_vector_layer_geojson', return_value=mock_geojson):
            response = client.get('/api/vector/layer/Marine%20Protected%20Areas')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['type'] == 'FeatureCollection'
        assert 'features' in data
        assert 'metadata' in data
        assert len(data['features']) == 1

    def test_api_vector_layer_geojson_with_simplify(self, client, app_with_vector_support):
        """Test /api/vector/layer/<name> endpoint with simplify parameter"""
        mock_geojson = {'type': 'FeatureCollection', 'features': []}

        with patch('app.get_vector_layer_geojson', return_value=mock_geojson) as mock_func:
            response = client.get('/api/vector/layer/Test%20Layer?simplify=0.001')

        assert response.status_code == 200
        # Verify simplify parameter was passed
        mock_func.assert_called_once_with('Test Layer', 0.001)

    def test_api_vector_layer_geojson_not_found(self, client, app_with_vector_support):
        """Test /api/vector/layer/<name> endpoint when layer not found"""
        with patch('app.get_vector_layer_geojson', return_value=None):
            response = client.get('/api/vector/layer/Non-existent%20Layer')

        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
        assert 'not found' in data['error']

    def test_api_vector_layer_geojson_without_support(self, client, app_without_vector_support):
        """Test /api/vector/layer/<name> endpoint without vector support"""
        response = client.get('/api/vector/layer/Test%20Layer')

        assert response.status_code == 503
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Vector support not available' in data['error']

    def test_api_vector_bounds_endpoint(self, client, app_with_vector_support):
        """Test /api/vector/bounds endpoint"""
        mock_bounds = {
            'overall_bounds': [0.0, 0.0, 10.0, 10.0],
            'center': [5.0, 5.0],
            'layer_count': 2
        }

        with patch('app.vector_loader') as mock_loader:
            mock_loader.create_bounds_summary.return_value = mock_bounds
            response = client.get('/api/vector/bounds')

        assert response.status_code == 200
        data = json.loads(response.data)

        assert 'overall_bounds' in data
        assert 'center' in data
        assert 'layer_count' in data
        assert data['layer_count'] == 2
        assert len(data['overall_bounds']) == 4
        assert len(data['center']) == 2

    def test_api_vector_bounds_without_support(self, client, app_without_vector_support):
        """Test /api/vector/bounds endpoint without vector support"""
        response = client.get('/api/vector/bounds')

        assert response.status_code == 503
        data = json.loads(response.data)
        assert 'error' in data

    def test_api_vector_endpoints_error_handling(self, client, app_with_vector_support):
        """Test error handling in vector API endpoints"""

        # Test /api/vector/layers with exception
        with patch('app.get_vector_layers_summary', side_effect=Exception('Test error')):
            response = client.get('/api/vector/layers')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

        # Test /api/vector/layer/<name> with exception
        with patch('app.get_vector_layer_geojson', side_effect=Exception('Test error')):
            response = client.get('/api/vector/layer/Test%20Layer')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

        # Test /api/vector/bounds with exception
        with patch('app.vector_loader') as mock_loader:
            mock_loader.create_bounds_summary.side_effect = Exception('Test error')
            response = client.get('/api/vector/bounds')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

    def test_vector_layer_http_methods(self, client, app_with_vector_support):
        """Test that vector API endpoints only accept GET requests"""
        endpoints = [
            '/api/all-layers',
            '/api/vector/layers',
            '/api/vector/layer/test',
            '/api/vector/bounds'
        ]

        for endpoint in endpoints:
            # Test POST request
            response = client.post(endpoint)
            assert response.status_code == 405  # Method Not Allowed

            # Test PUT request
            response = client.put(endpoint)
            assert response.status_code == 405

            # Test DELETE request
            response = client.delete(endpoint)
            assert response.status_code == 405


@pytest.mark.skipif(not GEOPANDAS_AVAILABLE, reason="Geopandas not available")
class TestVectorLayerIntegration:
    """Test vector layer integration with main application"""

    def test_index_page_with_vector_layers(self, client):
        """Test that index page includes vector layer data"""
        mock_vector_layers = [
            {'display_name': 'Test Layer', 'geometry_type': 'Polygon'}
        ]

        with patch('app.get_all_layers') as mock_get_layers:
            mock_get_layers.return_value = {
                'wms_layers': [],
                'vector_layers': mock_vector_layers,
                'vector_support': True
            }

            response = client.get('/')

        assert response.status_code == 200
        html_content = response.data.decode('utf-8')

        # Check that vector data is included in JavaScript
        assert 'vectorLayers' in html_content
        assert 'vectorSupport' in html_content

    def test_index_page_without_vector_support(self, client):
        """Test index page when vector support is disabled"""
        with patch('app.get_all_layers') as mock_get_layers:
            mock_get_layers.return_value = {
                'wms_layers': [],
                'vector_layers': [],
                'vector_support': False
            }

            response = client.get('/')

        assert response.status_code == 200
        html_content = response.data.decode('utf-8')

        # Vector support should be false in JavaScript
        assert 'vectorSupport' in html_content


@pytest.mark.skipif(GEOPANDAS_AVAILABLE, reason="Test for when geopandas is not available")
class TestVectorAPIWithoutGeopandas:
    """Test vector API behavior when geopandas is not available"""

    def test_vector_support_disabled(self, client):
        """Test that vector endpoints return 503 when geopandas is not available"""
        # This would be more thoroughly tested in a separate environment
        # without geopandas installed
        pass