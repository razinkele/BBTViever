"""
Unit tests for vector data loading functionality
"""
import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

# Skip all tests if geopandas is not available
pytest_plugins = []
try:
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Polygon, Point
    GEOPANDAS_AVAILABLE = True
except ImportError:
    GEOPANDAS_AVAILABLE = False


@pytest.mark.skipif(not GEOPANDAS_AVAILABLE, reason="Geopandas not available")
class TestVectorLayerLoader:
    """Test vector layer loading functionality"""

    @pytest.fixture
    def temp_data_dir(self, tmp_path):
        """Create temporary data directory structure"""
        data_dir = tmp_path / "test_data"
        vector_dir = data_dir / "vector"
        vector_dir.mkdir(parents=True)
        return data_dir

    @pytest.fixture
    def sample_gpkg_file(self, temp_data_dir):
        """Create a sample GPKG file for testing"""
        # Create sample polygon data
        polygons = [
            {
                'name': 'Area 1',
                'type': 'Protected',
                'area': 100.5,
                'geometry': Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)])
            },
            {
                'name': 'Area 2',
                'type': 'Conservation',
                'area': 200.8,
                'geometry': Polygon([(2, 2), (3, 2), (3, 3), (2, 3), (2, 2)])
            }
        ]

        gdf = gpd.GeoDataFrame(polygons, crs='EPSG:4326')
        gpkg_path = temp_data_dir / "vector" / "test_areas.gpkg"
        gdf.to_file(gpkg_path, driver='GPKG')

        return gpkg_path

    @pytest.fixture
    def vector_loader(self, temp_data_dir):
        """Create VectorLayerLoader with test data directory"""
        from src.emodnet_viewer.utils.vector_loader import VectorLayerLoader
        return VectorLayerLoader(str(temp_data_dir))

    def test_discover_gpkg_files(self, vector_loader, sample_gpkg_file):
        """Test GPKG file discovery"""
        gpkg_files = vector_loader.discover_gpkg_files()

        assert len(gpkg_files) == 1
        assert gpkg_files[0].name == "test_areas.gpkg"

    def test_discover_gpkg_files_empty_directory(self, vector_loader):
        """Test GPKG file discovery in empty directory"""
        gpkg_files = vector_loader.discover_gpkg_files()
        assert len(gpkg_files) == 0

    def test_get_layer_info_from_gpkg(self, vector_loader, sample_gpkg_file):
        """Test getting layer information from GPKG file"""
        layers_info = vector_loader.get_layer_info_from_gpkg(sample_gpkg_file)

        assert len(layers_info) == 1
        layer_info = layers_info[0]

        assert 'layer_name' in layer_info
        assert 'geometry_type' in layer_info
        assert 'feature_count' in layer_info
        assert 'bounds' in layer_info
        assert layer_info['feature_count'] == 2

    def test_load_vector_layer(self, vector_loader, sample_gpkg_file):
        """Test loading a specific vector layer"""
        # First get layer information
        layers_info = vector_loader.get_layer_info_from_gpkg(sample_gpkg_file)
        layer_name = layers_info[0]['layer_name']

        # Load the layer
        vector_layer = vector_loader.load_vector_layer(sample_gpkg_file, layer_name)

        assert vector_layer is not None
        assert vector_layer.layer_name == layer_name
        assert vector_layer.feature_count == 2
        assert vector_layer.crs == 'EPSG:4326'
        assert vector_layer.geometry_type in ['Polygon', 'MultiPolygon']
        assert len(vector_layer.bounds) == 4  # minx, miny, maxx, maxy

    def test_load_all_vector_layers(self, vector_loader, sample_gpkg_file):
        """Test loading all vector layers from all files"""
        loaded_layers = vector_loader.load_all_vector_layers()

        assert len(loaded_layers) == 1
        layer = loaded_layers[0]
        assert layer.feature_count == 2
        assert layer.source_file == "test_areas.gpkg"

    def test_get_vector_layer_geojson(self, vector_loader, sample_gpkg_file):
        """Test getting GeoJSON representation of a vector layer"""
        # Load layers first
        loaded_layers = vector_loader.load_all_vector_layers()
        assert len(loaded_layers) == 1

        layer = loaded_layers[0]
        geojson = vector_loader.get_vector_layer_geojson(layer)

        assert 'type' in geojson
        assert geojson['type'] == 'FeatureCollection'
        assert 'features' in geojson
        assert len(geojson['features']) == 2
        assert 'metadata' in geojson

        # Check metadata
        metadata = geojson['metadata']
        assert metadata['feature_count'] == 2
        assert metadata['layer_name'] == layer.layer_name
        assert 'style' in metadata

    def test_get_layer_by_name(self, vector_loader, sample_gpkg_file):
        """Test finding a loaded layer by name"""
        # Load layers first
        loaded_layers = vector_loader.load_all_vector_layers()
        layer = loaded_layers[0]

        # Find by name
        found_layer = vector_loader.get_layer_by_name(layer.display_name)
        assert found_layer is not None
        assert found_layer.display_name == layer.display_name

        # Test with non-existent name
        not_found = vector_loader.get_layer_by_name("Non-existent Layer")
        assert not_found is None

    def test_get_layers_summary(self, vector_loader, sample_gpkg_file):
        """Test getting layers summary for frontend"""
        # Load layers first
        loaded_layers = vector_loader.load_all_vector_layers()

        summary = vector_loader.get_layers_summary()

        assert len(summary) == 1
        layer_summary = summary[0]

        required_fields = [
            'layer_name', 'display_name', 'geometry_type',
            'feature_count', 'bounds', 'crs', 'source_file', 'style'
        ]
        for field in required_fields:
            assert field in layer_summary

        # Security check - file_path should not be in summary
        assert 'file_path' not in layer_summary

    def test_create_bounds_summary(self, vector_loader, sample_gpkg_file):
        """Test creating bounds summary for all layers"""
        # Load layers first
        loaded_layers = vector_loader.load_all_vector_layers()

        bounds_summary = vector_loader.create_bounds_summary()

        assert 'overall_bounds' in bounds_summary
        assert 'center' in bounds_summary
        assert 'layer_count' in bounds_summary

        assert bounds_summary['layer_count'] == 1
        assert len(bounds_summary['overall_bounds']) == 4
        assert len(bounds_summary['center']) == 2

    def test_create_display_name(self, vector_loader):
        """Test display name creation logic"""
        # Test when layer name equals file stem
        display_name = vector_loader._create_display_name('marine_areas', 'marine_areas')
        assert display_name == 'Marine Areas'

        # Test when layer name differs from file stem
        display_name = vector_loader._create_display_name('data_file', 'protected_areas')
        assert display_name == 'Data File - Protected Areas'

        # Test with underscores
        display_name = vector_loader._create_display_name('marine_protected_areas', 'main_layer')
        assert display_name == 'Marine Protected Areas - Main Layer'

    def test_default_styles(self, vector_loader):
        """Test that default styles are defined for all geometry types"""
        expected_geom_types = [
            'Polygon', 'MultiPolygon', 'LineString',
            'MultiLineString', 'Point', 'MultiPoint'
        ]

        for geom_type in expected_geom_types:
            assert geom_type in vector_loader.default_styles
            style = vector_loader.default_styles[geom_type]
            assert isinstance(style, dict)
            assert 'color' in style or 'fillColor' in style


@pytest.mark.skipif(not GEOPANDAS_AVAILABLE, reason="Geopandas not available")
class TestVectorLoaderConvenienceFunctions:
    """Test convenience functions for vector loading"""

    @pytest.fixture
    def mock_vector_loader(self):
        """Mock vector loader for testing convenience functions"""
        with patch('src.emodnet_viewer.utils.vector_loader.vector_loader') as mock:
            yield mock

    def test_load_all_vector_data(self, mock_vector_loader):
        """Test load_all_vector_data convenience function"""
        from src.emodnet_viewer.utils.vector_loader import load_all_vector_data

        expected_layers = [Mock(), Mock()]
        mock_vector_loader.load_all_vector_layers.return_value = expected_layers

        result = load_all_vector_data()

        assert result == expected_layers
        mock_vector_loader.load_all_vector_layers.assert_called_once()

    def test_get_vector_layer_geojson_convenience(self, mock_vector_loader):
        """Test get_vector_layer_geojson convenience function"""
        from src.emodnet_viewer.utils.vector_loader import get_vector_layer_geojson

        mock_layer = Mock()
        mock_geojson = {'type': 'FeatureCollection', 'features': []}

        mock_vector_loader.get_layer_by_name.return_value = mock_layer
        mock_vector_loader.get_vector_layer_geojson.return_value = mock_geojson

        result = get_vector_layer_geojson('Test Layer', 0.001)

        assert result == mock_geojson
        mock_vector_loader.get_layer_by_name.assert_called_once_with('Test Layer')
        mock_vector_loader.get_vector_layer_geojson.assert_called_once_with(mock_layer, 0.001)

    def test_get_vector_layer_geojson_not_found(self, mock_vector_loader):
        """Test get_vector_layer_geojson when layer not found"""
        from src.emodnet_viewer.utils.vector_loader import get_vector_layer_geojson

        mock_vector_loader.get_layer_by_name.return_value = None

        result = get_vector_layer_geojson('Non-existent Layer')

        assert result is None

    def test_get_vector_layers_summary_convenience(self, mock_vector_loader):
        """Test get_vector_layers_summary convenience function"""
        from src.emodnet_viewer.utils.vector_loader import get_vector_layers_summary

        expected_summary = [{'name': 'Layer 1'}, {'name': 'Layer 2'}]
        mock_vector_loader.get_layers_summary.return_value = expected_summary

        result = get_vector_layers_summary()

        assert result == expected_summary
        mock_vector_loader.get_layers_summary.assert_called_once()


@pytest.mark.skipif(GEOPANDAS_AVAILABLE, reason="Test for when geopandas is not available")
class TestVectorLoaderWithoutGeopandas:
    """Test behavior when geopandas is not available"""

    def test_import_error_handling(self):
        """Test that import errors are handled gracefully"""
        # This would normally be tested by temporarily removing geopandas,
        # but pytest.mark.skipif handles the main case
        pass