"""
Configuration settings for MARBEFES BBT Database Application
"""
import os
from pathlib import Path

class Config:
    """Base configuration"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # WMS Service Configuration
    WMS_BASE_URL = os.getenv(
        'WMS_BASE_URL',
        'https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms'
    )
    WMS_VERSION = "1.3.0"
    
    # HELCOM WMS Service Configuration
    HELCOM_WMS_BASE_URL = os.getenv(
        'HELCOM_WMS_BASE_URL',
        'https://maps.helcom.fi/arcgis/services/MADS/Pressures/MapServer/WMSServer'
    )
    HELCOM_WMS_VERSION = "1.3.0"
    
    # Vector data configuration
    VECTOR_DATA_PATH = Path('data/vector')
    ENABLE_VECTOR_SUPPORT = True
    MAX_VECTOR_FEATURES = 10000
    SIMPLIFICATION_TOLERANCE = 0.001
    
    # Caching configuration
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 3600  # 1 hour
    CACHE_KEY_PREFIX = 'marbefes_'
    
    # Security settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'gpkg', 'geojson', 'shp', 'json'}
    CORS_ORIGINS = '*'  # Configure appropriately for production
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'logs/marbefes.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 10
    
    # Performance settings
    REQUEST_TIMEOUT = 30  # seconds
    MAX_WORKERS = 4
    CONNECTION_POOL_SIZE = 10
    
    # Default layer configuration - EUSeaMap 2023 layers
    DEFAULT_LAYERS = [
        {
            "name": "eusm2023_msfd_full",
            "title": "EUSeaMap 2023 - MSFD Benthic Broad Habitat Types",
            "description": "Broad-scale seabed habitat map for Europe using MSFD classification"
        },
        {
            "name": "eusm2023_bio_full",
            "title": "EUSeaMap 2023 - Biological Zones",
            "description": "Biological zones habitat descriptor"
        },
        {
            "name": "eusm2023_subs_full",
            "title": "EUSeaMap 2023 - Substrate Types",
            "description": "Seabed substrate types habitat descriptor"
        },
        {
            "name": "eusm2023_ene_full",
            "title": "EUSeaMap 2023 - Energy Classes",
            "description": "Energy class habitat descriptor"
        },
        {
            "name": "eusm_2023_eunis2019_full",
            "title": "EUSeaMap 2023 - EUNIS 2019 Classification",
            "description": "EUNIS 2019 habitat classification system"
        },
        {
            "name": "eusm_helcom_2023_full",
            "title": "EUSeaMap 2023 - HELCOM Classification",
            "description": "HELCOM HUB habitat classification"
        }
    ]


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    CACHE_TYPE = 'simple'
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    CACHE_TYPE = 'redis'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    LOG_LEVEL = 'WARNING'
    
    # Stricter security in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    WTF_CSRF_ENABLED = False
    CACHE_TYPE = 'null'


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
