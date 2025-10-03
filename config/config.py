"""
Configuration management for EMODnet Seabed Habitats Viewer
"""
import os
from typing import Dict, Any


class Config:
    """Base configuration class"""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = False
    TESTING = False
    APPLICATION_ROOT = os.getenv('APPLICATION_ROOT', '')  # Subpath for mounting app (e.g., '/BBTS')

    # WMS Service Configuration
    WMS_BASE_URL = os.getenv(
        'WMS_BASE_URL',
        'https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms'
    )
    WMS_VERSION = os.getenv('WMS_VERSION', '1.3.0')
    WMS_TIMEOUT = int(os.getenv('WMS_TIMEOUT', '10'))

    # Application settings
    MAX_LAYERS_DISPLAY = int(os.getenv('MAX_LAYERS_DISPLAY', '20'))
    DEFAULT_MAP_CENTER_LAT = float(os.getenv('DEFAULT_MAP_CENTER_LAT', '54.0'))
    DEFAULT_MAP_CENTER_LNG = float(os.getenv('DEFAULT_MAP_CENTER_LNG', '10.0'))
    DEFAULT_MAP_ZOOM = int(os.getenv('DEFAULT_MAP_ZOOM', '4'))

    # Vector data settings
    VECTOR_DATA_DIR = os.getenv('VECTOR_DATA_DIR', 'data')
    VECTOR_SIMPLIFY_TOLERANCE = float(os.getenv('VECTOR_SIMPLIFY_TOLERANCE', '0.001'))
    VECTOR_MAX_FEATURES = int(os.getenv('VECTOR_MAX_FEATURES', '10000'))
    ENABLE_VECTOR_SUPPORT = os.getenv('ENABLE_VECTOR_SUPPORT', 'True').lower() == 'true'

    # Caching settings
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '3600'))

    # Logging configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/emodnet_viewer.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', '10485760'))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', '5'))


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

    # More verbose logging in development
    WMS_DEBUG_REQUESTS = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

    # Production-specific security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Production logging
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

    # Use in-memory cache for tests
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 1

    # Mock WMS for testing
    WMS_BASE_URL = 'http://localhost:8080/mock-wms'
    WMS_TIMEOUT = 5

    # Test logging
    LOG_LEVEL = 'DEBUG'


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development').lower()

    config_map = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig,
    }

    return config_map.get(env, DevelopmentConfig)()


# Predefined EMODnet layers configuration
EMODNET_LAYERS = [
    {
        "name": "all_eusm2021",
        "title": "EUSeaMap 2021 - All Habitats",
        "description": "Broad-scale seabed habitat map for Europe",
        "category": "habitat_maps"
    },
    {
        "name": "be_eusm2021",
        "title": "EUSeaMap 2021 - Benthic Habitats",
        "description": "Benthic broad-scale habitat map",
        "category": "habitat_maps"
    },
    {
        "name": "ospar_threatened",
        "title": "OSPAR Threatened Habitats",
        "description": "OSPAR threatened and/or declining habitats",
        "category": "conservation"
    },
    {
        "name": "substrate",
        "title": "Seabed Substrate",
        "description": "Seabed substrate types",
        "category": "physical"
    },
    {
        "name": "confidence",
        "title": "Confidence Assessment",
        "description": "Confidence in habitat predictions",
        "category": "quality"
    },
    {
        "name": "annexiMaps_all",
        "title": "Annex I Habitats",
        "description": "Habitats Directive Annex I habitat types",
        "category": "conservation"
    }
]

# Base map configurations
BASEMAP_CONFIGS = {
    'osm': {
        'name': 'OpenStreetMap',
        'url': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'attribution': '© OpenStreetMap contributors'
    },
    'satellite': {
        'name': 'Satellite',
        'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        'attribution': '© Esri'
    },
    'ocean': {
        'name': 'Ocean',
        'url': 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
        'attribution': '© Esri'
    },
    'light': {
        'name': 'Light Gray',
        'url': 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        'attribution': '© CartoDB'
    }
}