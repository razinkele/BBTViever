"""
Unit tests for configuration management
"""
import pytest
import os
from unittest.mock import patch

from config import (
    Config, DevelopmentConfig, ProductionConfig, TestingConfig,
    get_config, EMODNET_LAYERS, BASEMAP_CONFIGS
)


class TestConfigClasses:
    """Test configuration classes"""

    def test_base_config_defaults(self):
        """Test base configuration defaults"""
        config = Config()

        assert config.DEBUG is False
        assert config.TESTING is False
        assert config.WMS_VERSION == '1.3.0'
        assert config.WMS_TIMEOUT == 10
        assert config.MAX_LAYERS_DISPLAY == 20
        assert config.DEFAULT_MAP_CENTER_LAT == 54.0
        assert config.DEFAULT_MAP_CENTER_LNG == 10.0
        assert config.DEFAULT_MAP_ZOOM == 4

    def test_development_config(self):
        """Test development configuration"""
        config = DevelopmentConfig()

        assert config.DEBUG is True
        assert config.LOG_LEVEL == 'DEBUG'
        assert hasattr(config, 'WMS_DEBUG_REQUESTS')
        assert config.WMS_DEBUG_REQUESTS is True

    def test_production_config(self):
        """Test production configuration"""
        config = ProductionConfig()

        assert config.DEBUG is False
        assert config.LOG_LEVEL == 'WARNING'
        assert config.SESSION_COOKIE_SECURE is True
        assert config.SESSION_COOKIE_HTTPONLY is True
        assert config.SESSION_COOKIE_SAMESITE == 'Lax'

    def test_testing_config(self):
        """Test testing configuration"""
        config = TestingConfig()

        assert config.TESTING is True
        assert config.DEBUG is True
        assert config.CACHE_TYPE == 'simple'
        assert config.CACHE_DEFAULT_TIMEOUT == 1
        assert config.WMS_TIMEOUT == 5
        assert 'mock-wms' in config.WMS_BASE_URL

    @patch.dict(os.environ, {'WMS_BASE_URL': 'http://test-wms-server.com'})
    def test_environment_variable_override(self):
        """Test that environment variables override defaults"""
        config = Config()
        assert config.WMS_BASE_URL == 'http://test-wms-server.com'

    @patch.dict(os.environ, {'WMS_TIMEOUT': '15', 'MAX_LAYERS_DISPLAY': '30'})
    def test_integer_environment_variables(self):
        """Test integer environment variable parsing"""
        config = Config()
        assert config.WMS_TIMEOUT == 15
        assert config.MAX_LAYERS_DISPLAY == 30

    @patch.dict(os.environ, {'DEFAULT_MAP_CENTER_LAT': '60.5', 'DEFAULT_MAP_CENTER_LNG': '15.2'})
    def test_float_environment_variables(self):
        """Test float environment variable parsing"""
        config = Config()
        assert config.DEFAULT_MAP_CENTER_LAT == 60.5
        assert config.DEFAULT_MAP_CENTER_LNG == 15.2


class TestGetConfig:
    """Test configuration factory function"""

    @patch.dict(os.environ, {'FLASK_ENV': 'development'})
    def test_get_development_config(self):
        """Test getting development configuration"""
        config = get_config()
        assert isinstance(config, DevelopmentConfig)
        assert config.DEBUG is True

    @patch.dict(os.environ, {'FLASK_ENV': 'production'})
    def test_get_production_config(self):
        """Test getting production configuration"""
        config = get_config()
        assert isinstance(config, ProductionConfig)
        assert config.DEBUG is False

    @patch.dict(os.environ, {'FLASK_ENV': 'testing'})
    def test_get_testing_config(self):
        """Test getting testing configuration"""
        config = get_config()
        assert isinstance(config, TestingConfig)
        assert config.TESTING is True

    @patch.dict(os.environ, {'FLASK_ENV': 'invalid'})
    def test_get_config_with_invalid_env(self):
        """Test getting config with invalid environment defaults to development"""
        config = get_config()
        assert isinstance(config, DevelopmentConfig)

    def test_get_config_without_env_variable(self):
        """Test getting config without FLASK_ENV set"""
        with patch.dict(os.environ, {}, clear=True):
            if 'FLASK_ENV' in os.environ:
                del os.environ['FLASK_ENV']
            config = get_config()
            assert isinstance(config, DevelopmentConfig)


class TestEmodnetLayers:
    """Test EMODNET_LAYERS configuration"""

    def test_layers_structure(self):
        """Test that all layers have required fields"""
        for layer in EMODNET_LAYERS:
            assert 'name' in layer
            assert 'title' in layer
            assert 'description' in layer
            assert 'category' in layer
            assert isinstance(layer['name'], str)
            assert isinstance(layer['title'], str)
            assert isinstance(layer['description'], str)
            assert isinstance(layer['category'], str)

    def test_layers_categories(self):
        """Test that layer categories are valid"""
        valid_categories = {'habitat_maps', 'conservation', 'physical', 'quality'}
        for layer in EMODNET_LAYERS:
            assert layer['category'] in valid_categories

    def test_specific_layers_exist(self):
        """Test that expected layers exist"""
        layer_names = [layer['name'] for layer in EMODNET_LAYERS]
        expected_layers = [
            'all_eusm2021', 'be_eusm2021', 'ospar_threatened',
            'substrate', 'confidence', 'annexiMaps_all'
        ]
        for expected in expected_layers:
            assert expected in layer_names


class TestBasemapConfigs:
    """Test BASEMAP_CONFIGS configuration"""

    def test_basemap_structure(self):
        """Test that all basemaps have required fields"""
        for basemap_key, basemap in BASEMAP_CONFIGS.items():
            assert 'name' in basemap
            assert 'url' in basemap
            assert 'attribution' in basemap
            assert isinstance(basemap['name'], str)
            assert isinstance(basemap['url'], str)
            assert isinstance(basemap['attribution'], str)
            assert '{z}' in basemap['url']  # Ensure tile URL template

    def test_expected_basemaps_exist(self):
        """Test that expected basemaps exist"""
        expected_basemaps = ['osm', 'satellite', 'ocean', 'light']
        for expected in expected_basemaps:
            assert expected in BASEMAP_CONFIGS

    def test_basemap_urls_are_https(self):
        """Test that basemap URLs use HTTPS where possible"""
        for basemap_key, basemap in BASEMAP_CONFIGS.items():
            # Most tile services should use HTTPS
            if 'openstreetmap.org' not in basemap['url']:
                assert basemap['url'].startswith('https://'), f"Basemap {basemap_key} should use HTTPS"