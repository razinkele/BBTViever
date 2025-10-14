"""
MARBEFES BBT Database - Marine Biodiversity and Ecosystem Functioning Database for Broad Belt Transects
"""

# Standard library imports
import os
import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

# Third-party imports
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_compress import Compress
import requests

# Add src and config directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "config"))

# Local imports
from config import get_config, EMODNET_LAYERS, BASEMAP_CONFIGS, DEFAULT_BASEMAP
from emodnet_viewer.utils.logging_config import setup_logging, get_logger
from emodnet_viewer.__version__ import __version__, __version_date__, get_version_dict

# Initialize vector support - check for geopandas availability first
VECTOR_SUPPORT = False
vector_loader = None
get_vector_layer_geojson = None
get_vector_layers_summary = None

try:
    import geopandas  # Check if geospatial deps are available
    from emodnet_viewer.utils.vector_loader import (
        vector_loader,
        get_vector_layer_geojson,
        get_vector_layers_summary,
    )
    VECTOR_SUPPORT = True
except ImportError:
    # Vector support disabled - optional dependency
    pass

# Initialize Flask app and configuration
app = Flask(__name__)
config = get_config()
app.config.from_object(config)

# Setup logging
setup_logging(config.LOG_LEVEL, config.LOG_FILE)
logger = get_logger(__name__)

# Initialize Flask-Caching with comprehensive configuration
cache_config = {
    'CACHE_TYPE': config.CACHE_TYPE,
    'CACHE_DEFAULT_TIMEOUT': config.CACHE_DEFAULT_TIMEOUT,
}

# Add Redis-specific configuration if using Redis
if config.CACHE_TYPE == 'redis':
    if config.CACHE_REDIS_URL:
        cache_config['CACHE_REDIS_URL'] = config.CACHE_REDIS_URL
    else:
        cache_config['CACHE_REDIS_HOST'] = config.CACHE_REDIS_HOST
        cache_config['CACHE_REDIS_PORT'] = config.CACHE_REDIS_PORT
        cache_config['CACHE_REDIS_DB'] = config.CACHE_REDIS_DB
        if config.CACHE_REDIS_PASSWORD:
            cache_config['CACHE_REDIS_PASSWORD'] = config.CACHE_REDIS_PASSWORD

# Add filesystem cache configuration if using filesystem
elif config.CACHE_TYPE == 'filesystem':
    cache_config['CACHE_DIR'] = config.CACHE_DIR
    cache_config['CACHE_THRESHOLD'] = config.CACHE_THRESHOLD

cache = Cache(app, config=cache_config)
logger.info(f"Cache initialized with type: {config.CACHE_TYPE}")

# Initialize Flask-Limiter for API rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
    strategy="fixed-window"
)

# Initialize Flask-Compress for response compression (P1 optimization)
# Compresses JSON, GeoJSON, HTML, CSS, JavaScript responses automatically
compress = Compress()
app.config['COMPRESS_MIMETYPES'] = [
    'application/json',
    'application/geo+json',
    'text/html',
    'text/css',
    'text/javascript',
    'application/javascript'
]
app.config['COMPRESS_LEVEL'] = 6  # Balance between speed (1=fast) and compression (9=best)
app.config['COMPRESS_MIN_SIZE'] = 500  # Only compress responses > 500 bytes
compress.init_app(app)
logger.info(f"Response compression enabled (level: {app.config['COMPRESS_LEVEL']}, min size: {app.config['COMPRESS_MIN_SIZE']} bytes)")

# Initialize requests session with connection pooling for WMS requests
# Connection pooling provides 20-40% performance improvement for repeated WMS calls
wms_session = requests.Session()
# Configure connection pool size (max connections to keep alive)
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,  # Number of connection pools to cache
    pool_maxsize=20,      # Max connections per pool
    max_retries=0,        # No retries for faster page loads
    pool_block=False      # Don't block if pool is full
)
wms_session.mount('http://', adapter)
wms_session.mount('https://', adapter)


# Security Headers Middleware
@app.after_request
def set_security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # HSTS only in production (requires HTTPS)
    if not app.config['DEBUG']:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'

    return response


# WMS Service Configuration
WMS_BASE_URL = config.WMS_BASE_URL
WMS_VERSION = config.WMS_VERSION
WMS_TIMEOUT = config.WMS_TIMEOUT
WMS_CACHE_TIMEOUT = config.WMS_CACHE_TIMEOUT

# HELCOM WMS Service Configuration
HELCOM_WMS_BASE_URL = config.HELCOM_WMS_BASE_URL
HELCOM_WMS_VERSION = config.HELCOM_WMS_VERSION

# Layer Filtering Configuration
CORE_EUROPEAN_LAYER_COUNT = config.CORE_EUROPEAN_LAYER_COUNT
EUROPEAN_LAYER_TERMS = ['eusm2021', 'eusm2019', 'europe', 'substrate', 'confidence', 'annexiMaps', 'ospar']
CARIBBEAN_EXCLUDE_TERMS = ['carib', 'caribbean']

# Bathymetry Statistics Configuration
BATHYMETRY_STATS_FILE = Path("data/bbt_bathymetry_stats.json")
FACTSHEET_DATA_FILE = Path("data/bbt_factsheets.json")

def load_bathymetry_stats():
    """
    Load BBT bathymetry statistics from JSON file if available.

    Returns:
        dict: Bathymetry statistics or empty dict if not available
    """
    if BATHYMETRY_STATS_FILE.exists():
        try:
            with open(BATHYMETRY_STATS_FILE) as f:
                data = json.load(f)
                logger.info(f"Loaded bathymetry statistics for {data['metadata'].get('bbt_count', 0)} BBT areas")
                return data.get('statistics', {})
        except Exception as e:
            logger.warning(f"Failed to load bathymetry statistics: {e}")
            return {}
    else:
        logger.info("Bathymetry statistics file not found - stats will not be displayed")
        return {}

def load_factsheet_data():
    """
    Load BBT factsheet data from JSON file if available.

    Returns:
        dict: Factsheet data or empty dict if not available
    """
    if FACTSHEET_DATA_FILE.exists():
        try:
            with open(FACTSHEET_DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                bbt_count = len(data.get('bbts', []))
                logger.info(f"Loaded factsheet data for {bbt_count} BBT areas")
                return data
        except Exception as e:
            logger.warning(f"Failed to load factsheet data: {e}")
            return {}
    else:
        logger.info("Factsheet data file not found - factsheet endpoints will return 404")
        return {}

# Load data on startup for performance (cached in memory)
BATHYMETRY_STATS = load_bathymetry_stats()
FACTSHEET_DATA = load_factsheet_data()

def load_bundle_manifest():
    """
    Load JavaScript bundle manifest for cache-busting

    Returns:
        dict: Bundle manifest or fallback dict if not available
    """
    manifest_file = Path("static/dist/bundle-manifest.json")
    if manifest_file.exists():
        try:
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest = json.load(f)
                logger.info(f"Loaded bundle manifest: v{manifest.get('version')} (hash: {manifest.get('content_hash')})")
                return manifest
        except Exception as e:
            logger.warning(f"Failed to load bundle manifest: {e}")

    # Fallback to non-versioned bundles
    logger.info("Bundle manifest not found, using fallback bundle names")
    return {
        "version": __version__,
        "bundles": {
            "development": "app.bundle.js",
            "production": "app.bundle.min.js"
        }
    }

# Load bundle manifest on startup
BUNDLE_MANIFEST = load_bundle_manifest()


# Layer filter functions (named for clarity and debugging)
def emodnet_layer_filter(layer):
    """Filter EMODnet layers - exclude workspace-prefixed names"""
    return ":" not in layer["name"]


def helcom_layer_filter(layer):
    """Filter HELCOM layers - only include layers with underscores"""
    return "_" in layer["name"]


def parse_wms_capabilities(xml_content, filter_fn=None):
    """
    Parse WMS GetCapabilities XML response with optional filtering

    Args:
        xml_content: XML content as bytes or string
        filter_fn: Optional function to filter layers (takes layer dict, returns bool)

    Returns:
        List of layer dictionaries
    """
    try:
        root = ET.fromstring(xml_content)

        # Optimized namespace handling - strip once during element access
        def strip_ns(tag):
            """Strip namespace from tag"""
            return tag.split('}')[1] if '}' in tag else tag

        wms_layers = []
        # Use namespace-aware iteration
        for layer in root.iter():
            if strip_ns(layer.tag) == 'Layer':
                name_elem = layer.find('.//{*}Name')
                title_elem = layer.find('.//{*}Title')
                abstract_elem = layer.find('.//{*}Abstract')

                if name_elem is not None and name_elem.text:
                    layer_name = name_elem.text.strip()

                    # Skip empty layer names
                    if not layer_name:
                        continue

                    layer_dict = {
                        "name": layer_name,
                        "title": (
                            title_elem.text
                            if title_elem is not None and title_elem.text
                            else layer_name
                        ),
                        "description": (
                            abstract_elem.text if abstract_elem is not None else ""
                        ),
                    }

                    # Apply filter if provided
                    if filter_fn is None or filter_fn(layer_dict):
                        wms_layers.append(layer_dict)

        logger.info(f"Parsed {len(wms_layers)} layers from WMS capabilities")
        return wms_layers

    except ET.ParseError as e:
        logger.error(f"XML parsing error in WMS capabilities: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error parsing WMS capabilities: {e}")
        return []


def prioritize_european_layers(wms_layers):
    """Prioritize European layers and combine with defaults using single-pass algorithm"""
    if not wms_layers:
        logger.warning("No WMS layers found, using fallback layers")
        return EMODNET_LAYERS

    # Single-pass categorization of WMS layers
    preferred_layers = []
    other_layers = []

    for wms_layer in wms_layers:
        name_lower = wms_layer['name'].lower()
        title_lower = (wms_layer.get('title') or '').lower()

        # Skip Caribbean layers entirely
        if any(term in name_lower or term in title_lower for term in CARIBBEAN_EXCLUDE_TERMS):
            continue

        # Categorize as European or other
        if any(term in name_lower or term in title_lower for term in EUROPEAN_LAYER_TERMS):
            preferred_layers.append(wms_layer)
        else:
            other_layers.append(wms_layer)

    # Build final layer list with deduplication
    core_european_layers = EMODNET_LAYERS[:CORE_EUROPEAN_LAYER_COUNT] if len(EMODNET_LAYERS) >= CORE_EUROPEAN_LAYER_COUNT else EMODNET_LAYERS
    final_layers = []
    added_names = set()

    # Priority order: Core European → Discovered European → Other WMS
    for layer_list in [core_european_layers, preferred_layers, other_layers]:
        for layer in layer_list:
            if layer['name'] not in added_names:
                final_layers.append(layer)
                added_names.add(layer['name'])

    logger.info(f"Prioritized {len(final_layers)} layers (European first)")
    return final_layers


@cache.cached(timeout=WMS_CACHE_TIMEOUT, key_prefix='wms_layers')
def get_available_layers():
    """
    Fetch available WMS layers with caching

    Returns:
        List of layer dictionaries
    """
    try:
        logger.info(f"Fetching WMS capabilities from {WMS_BASE_URL}")

        # Use connection-pooled session for better performance
        params = {"service": "WMS", "version": WMS_VERSION, "request": "GetCapabilities"}
        response = wms_session.get(WMS_BASE_URL, params=params, timeout=WMS_TIMEOUT)

        if response.status_code == 200:
            # Use named filter function for EMODnet layers
            wms_layers = parse_wms_capabilities(response.content, filter_fn=emodnet_layer_filter)
            final_layers = prioritize_european_layers(wms_layers)

            logger.info(f"Successfully fetched {len(final_layers)} WMS layers")
            return final_layers
        else:
            logger.warning(f"WMS request failed with status {response.status_code}, using fallback layers")
            return EMODNET_LAYERS

    except requests.RequestException as e:
        logger.warning(f"Network error fetching WMS layers (using fallback): {e}")
        return EMODNET_LAYERS
    except ET.ParseError as e:
        logger.error(f"XML parsing error in WMS response (using fallback): {e}")
        return EMODNET_LAYERS
    except Exception as e:
        logger.error(f"Unexpected error fetching layers (using fallback): {e}", exc_info=True)
        return EMODNET_LAYERS


def get_helcom_layers():
    """Fetch available layers from HELCOM WMS GetCapabilities"""
    try:
        logger.info(f"Fetching HELCOM capabilities from {HELCOM_WMS_BASE_URL}")

        params = {"service": "WMS", "version": HELCOM_WMS_VERSION, "request": "GetCapabilities"}
        response = wms_session.get(HELCOM_WMS_BASE_URL, params=params, timeout=WMS_TIMEOUT)

        if response.status_code == 200:
            # Use named filter function for HELCOM layers
            layers = parse_wms_capabilities(response.content, filter_fn=helcom_layer_filter)

            logger.info(f"Successfully fetched {len(layers)} HELCOM layers")
            return layers
        else:
            logger.warning(f"HELCOM request failed with status {response.status_code}")
            return []

    except requests.RequestException as e:
        logger.warning(f"Network error fetching HELCOM layers: {e}")
        return []
    except ET.ParseError as e:
        logger.error(f"XML parsing error in HELCOM response: {e}")
        return []
    except Exception as e:
        logger.error(f"Unexpected error fetching HELCOM layers: {e}", exc_info=True)
        return []


def get_all_layers():
    """Get both WMS, HELCOM, and vector layers combined"""
    wms_layers = get_available_layers()
    helcom_layers = get_helcom_layers()

    combined_layers = {
        "wms_layers": wms_layers,
        "helcom_layers": helcom_layers,
        "vector_layers": [],
        "vector_support": VECTOR_SUPPORT,
    }

    if VECTOR_SUPPORT:
        try:
            vector_layers = get_vector_layers_summary()
            combined_layers["vector_layers"] = vector_layers
            logger.debug(f"Added {len(vector_layers)} vector layers to combined response")
        except Exception as e:
            logger.error(f"Error loading vector layers: {e}")
            combined_layers["vector_support"] = False

    return combined_layers


def load_vector_data_on_startup():
    """Load vector data when the application starts"""
    if not VECTOR_SUPPORT:
        logger.info("Vector support disabled, skipping vector layer loading")
        return

    try:
        logger.info("Loading vector data from GPKG files...")
        vector_layers = vector_loader.load_all_vector_layers()

        logger.info(f"Loaded {len(vector_layers)} vector layers from GPKG files")

        # Log layer information
        for layer in vector_layers:
            logger.debug(f"  - {layer.display_name} ({layer.geometry_type}, {layer.feature_count} features)")

    except Exception as e:
        logger.error(f"Error loading vector data: {e}", exc_info=True)


# Flask route handlers

@app.route("/")
def index():
    """Main page with map viewer"""
    all_layers = get_all_layers()
    app_root = app.config.get('APPLICATION_ROOT', '')
    api_base_url = f"{app_root}/api" if app_root else "/api"

    return render_template(
        'index.html',
        layers=all_layers["wms_layers"],
        helcom_layers=all_layers["helcom_layers"],
        vector_layers=all_layers["vector_layers"],
        vector_support=all_layers["vector_support"],
        bathymetry_stats=BATHYMETRY_STATS,
        bundle_manifest=BUNDLE_MANIFEST,
        app_version=__version__,
        WMS_BASE_URL=WMS_BASE_URL,
        HELCOM_WMS_BASE_URL=HELCOM_WMS_BASE_URL,
        APPLICATION_ROOT=app_root,
        API_BASE_URL=api_base_url,
        BASEMAP_CONFIGS=BASEMAP_CONFIGS,
        DEFAULT_BASEMAP=DEFAULT_BASEMAP,
    )


@app.route("/health")
@limiter.exempt  # Health checks should not be rate limited
def health_check():
    """
    Health check endpoint for monitoring and load balancers

    Returns:
        JSON with health status and component availability
    """
    # Get current timestamp (using timezone-aware datetime for Python 3.12+ compatibility)
    health_status = {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "version": __version__,
        "version_date": __version_date__,
        "components": {}
    }

    # Check vector support
    health_status["components"]["vector_support"] = {
        "available": VECTOR_SUPPORT,
        "status": "operational" if VECTOR_SUPPORT else "disabled"
    }

    # Check WMS connectivity
    wms_healthy = False
    wms_error = None
    try:
        test_response = wms_session.get(WMS_BASE_URL, params={"service": "WMS", "request": "GetCapabilities"}, timeout=3)
        wms_healthy = test_response.status_code == 200
        if not wms_healthy:
            wms_error = f"HTTP {test_response.status_code}"
    except Exception as e:
        wms_error = str(e)

    health_status["components"]["wms_service"] = {
        "url": WMS_BASE_URL,
        "status": "operational" if wms_healthy else "degraded",
        "error": wms_error
    }

    # Check HELCOM WMS connectivity
    helcom_healthy = False
    helcom_error = None
    try:
        test_response = wms_session.get(HELCOM_WMS_BASE_URL, params={"service": "WMS", "request": "GetCapabilities"}, timeout=3)
        helcom_healthy = test_response.status_code == 200
        if not helcom_healthy:
            helcom_error = f"HTTP {test_response.status_code}"
    except Exception as e:
        helcom_error = str(e)

    health_status["components"]["helcom_wms_service"] = {
        "url": HELCOM_WMS_BASE_URL,
        "status": "operational" if helcom_healthy else "degraded",
        "error": helcom_error
    }

    # Check cache
    health_status["components"]["cache"] = {
        "type": config.CACHE_TYPE,
        "status": "operational"
    }

    # Check vector data if available
    if VECTOR_SUPPORT and vector_loader:
        try:
            layer_count = len(vector_loader.loaded_layers)
            health_status["components"]["vector_data"] = {
                "status": "operational" if layer_count > 0 else "no_data",
                "layer_count": layer_count
            }
        except Exception as e:
            health_status["components"]["vector_data"] = {
                "status": "error",
                "error": str(e)
            }

    # Overall status determination
    critical_services = [wms_healthy or helcom_healthy]  # At least one WMS should work
    if not all(critical_services):
        health_status["status"] = "degraded"
        return jsonify(health_status), 503

    return jsonify(health_status), 200


@app.route("/logo/<filename>")
def serve_logo(filename):
    """Serve logo files from LOGO directory"""
    logo_dir = os.path.join(os.path.dirname(__file__), "LOGO")
    return send_from_directory(logo_dir, filename)


@app.route("/api/layers")
def api_layers():
    """API endpoint to get available WMS layers"""
    return jsonify(get_available_layers())


@app.route("/api/all-layers")
def api_all_layers():
    """API endpoint to get all layers (WMS and vector)"""
    return jsonify(get_all_layers())


@app.route("/api/vector/layers")
def api_vector_layers():
    """API endpoint to get available vector layers"""
    if not VECTOR_SUPPORT:
        return (
            jsonify(
                {
                    "error": "Vector support not available",
                    "reason": "Missing geospatial dependencies (geopandas, fiona)",
                }
            ),
            503,
        )

    try:
        vector_layers = get_vector_layers_summary()
        return jsonify({"layers": vector_layers, "count": len(vector_layers)})
    except Exception as e:
        logger.error(f"Error in api_vector_layers: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/vector/layer/<path:layer_name>")
@limiter.limit("10 per minute")  # Stricter limit for expensive GeoJSON operations
def api_vector_layer_geojson(layer_name):
    """API endpoint to get GeoJSON for a specific vector layer"""
    if not VECTOR_SUPPORT:
        return jsonify({"error": "Vector support not available"}), 503

    # Validate layer name against whitelist to prevent path traversal
    if vector_loader and vector_loader.loaded_layers:
        valid_layer_names = [layer.display_name for layer in vector_loader.loaded_layers]
        if layer_name not in valid_layer_names:
            logger.warning(f"Invalid layer name requested: {layer_name}")
            return jsonify({"error": f"Layer '{layer_name}' not found"}), 404

    try:
        # Get optional simplification parameter
        simplify = request.args.get("simplify", type=float)

        geojson = get_vector_layer_geojson(layer_name, simplify)
        if geojson:
            return jsonify(geojson)
        else:
            return jsonify({"error": f"Layer '{layer_name}' not found"}), 404

    except Exception as e:
        logger.error(f"Error in api_vector_layer_geojson: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/vector/bounds")
def api_vector_bounds():
    """API endpoint to get bounds of all vector layers"""
    if not VECTOR_SUPPORT:
        return jsonify({"error": "Vector support not available"}), 503

    try:
        bounds_summary = vector_loader.create_bounds_summary()
        return jsonify(bounds_summary)
    except Exception as e:
        logger.error(f"Error in api_vector_bounds: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/factsheets")
def api_factsheets():
    """API endpoint to get all BBT factsheet data (cached in memory)"""
    try:
        # Use cached data loaded at startup for performance
        if not FACTSHEET_DATA:
            return jsonify({"error": "Factsheet data not found"}), 404

        return jsonify(FACTSHEET_DATA)
    except Exception as e:
        logger.error(f"Error in api_factsheets: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/factsheet/<bbt_name>")
def api_factsheet(bbt_name):
    """API endpoint to get factsheet data for a specific BBT (cached in memory)"""
    try:
        # Use cached data loaded at startup for performance
        if not FACTSHEET_DATA:
            return jsonify({"error": "Factsheet data not found"}), 404

        # Normalize BBT name for matching (case-insensitive, flexible matching)
        bbt_name_normalized = bbt_name.lower().replace("_", " ").replace("-", " ")

        # Search for matching factsheet
        for bbt in FACTSHEET_DATA.get("bbts", []):
            factsheet_name_normalized = bbt["name"].lower().replace("_", " ").replace("-", " ")

            # Check for exact match or partial match
            if (bbt_name_normalized == factsheet_name_normalized or
                bbt_name_normalized in factsheet_name_normalized or
                factsheet_name_normalized in bbt_name_normalized):
                return jsonify(bbt)

        return jsonify({"error": f"No factsheet found for BBT: {bbt_name}"}), 404

    except Exception as e:
        logger.error(f"Error in api_factsheet: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/capabilities")
@limiter.limit("30 per minute")  # Moderate limit for external WMS requests
def api_capabilities():
    """API endpoint to get WMS capabilities"""
    params = {"service": "WMS", "version": WMS_VERSION, "request": "GetCapabilities"}
    try:
        response = wms_session.get(WMS_BASE_URL, params=params, timeout=WMS_TIMEOUT)
        return response.content, 200, {"Content-Type": "text/xml"}
    except Exception as e:
        logger.error(f"Error in api_capabilities: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/api/legend/<path:layer_name>")
@limiter.exempt  # Legend URLs are lightweight and can be unlimited
def api_legend(layer_name):
    """API endpoint to get legend for a specific layer"""
    legend_url = (
        f"{WMS_BASE_URL}?"
        f"service=WMS&version=1.1.0&request=GetLegendGraphic&"
        f"layer={layer_name}&format=image/png"
    )
    return jsonify({"legend_url": legend_url})


@app.route("/api/metrics", methods=["POST"])
@limiter.limit("30 per minute")  # Allow reasonable metric submission rate
def api_metrics():
    """
    API endpoint to receive client-side performance metrics (P1 Optimization)

    Collects performance data from the Performance Monitoring API for analysis
    """
    try:
        data = request.json
        if not data or 'metrics' not in data:
            return jsonify({"error": "No metrics provided"}), 400

        metrics = data.get('metrics', [])
        user_agent = data.get('userAgent', 'unknown')
        connection = data.get('connection', {})

        # Log metrics for analysis (in production, send to monitoring service)
        for metric in metrics[:10]:  # Limit to first 10 for logging
            metric_type = metric.get('type', 'unknown')

            if metric_type == 'layer_load':
                logger.info(
                    f"Performance metric: Layer load '{metric.get('name')}' "
                    f"took {metric.get('duration', 0):.0f}ms "
                    f"({'cache hit' if metric.get('cacheHit') else 'network'})"
                )
            elif metric_type == 'navigation':
                logger.info(
                    f"Performance metric: Page load took {metric.get('total_time', 0):.0f}ms "
                    f"(DOM: {metric.get('dom_load', 0):.0f}ms)"
                )
            elif metric_type == 'resource':
                if metric.get('duration', 0) > 100:  # Only log slow resources
                    logger.info(
                        f"Performance metric: Slow resource '{metric.get('name')}' "
                        f"took {metric.get('duration', 0):.0f}ms "
                        f"({metric.get('size', 0)} bytes)"
                    )

        # Log connection info if available
        if connection and connection.get('effectiveType'):
            logger.debug(
                f"Client connection: {connection.get('effectiveType')} "
                f"(downlink: {connection.get('downlink', 0)}Mbps, "
                f"rtt: {connection.get('rtt', 0)}ms)"
            )

        return jsonify({
            "status": "recorded",
            "count": len(metrics)
        })

    except Exception as e:
        logger.error(f"Error in api_metrics: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500


@app.route("/test")
def test_page():
    """Simple test page to verify WMS is working"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WMS Test</title>
    </head>
    <body>
        <h1>EMODnet WMS Test</h1>
        <p>Testing direct WMS GetMap request:</p>
        <img src="https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms?service=WMS&version=1.1.0&request=GetMap&layers=all_eusm2021&bbox=-180,-90,180,90&width=768&height=384&srs=EPSG:4326&format=image/png"
             alt="WMS Test Image" style="max-width: 100%; border: 1px solid black;">
        <p>If you see a map image above, the WMS service is working correctly.</p>
    </body>
    </html>
    """
    return html


# Initialize vector data loading when the module is imported (for WSGI servers like Gunicorn)
# This ensures vector data is loaded even when not run directly with `python app.py`
load_vector_data_on_startup()


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("MARBEFES BBT Database - Marine Biodiversity and Ecosystem Functioning Database")
    logger.info("=" * 60)
    logger.info("Initializing application...")

    # Vector data loading already initiated at module level
    logger.info("Starting Flask server...")
    logger.info("Open http://localhost:5000 in your browser")
    logger.info("\nAvailable endpoints:")
    logger.info("  /              - Main interactive map viewer")
    logger.info("  /health        - Health check endpoint for monitoring")
    logger.info("  /test          - Test WMS connectivity")
    logger.info("  /api/layers    - Get WMS layers (JSON)")
    logger.info("  /api/all-layers - Get all layers (WMS + vector, JSON)")
    logger.info("  /api/vector/layers - Get vector layers (JSON)")
    logger.info("  /api/vector/layer/<name> - Get vector layer GeoJSON (rate limited)")
    logger.info("  /api/vector/bounds - Get vector layers bounds")
    logger.info("  /api/capabilities - Get WMS capabilities (XML, rate limited)")
    logger.info("  /api/legend/<layer> - Get legend URL for a layer")

    if VECTOR_SUPPORT:
        logger.info("\nVector Support: Enabled")
        logger.info(f"   Data directory: {Path('data/vector').absolute()}")
    else:
        logger.warning("\nVector Support: Disabled (missing dependencies)")
        logger.info("   Install: pip install geopandas fiona pyproj")

    logger.info("\nPress Ctrl+C to stop the server")
    logger.info("-" * 60)

    port = int(os.environ.get('FLASK_RUN_PORT', 5000))

    # Smart default: localhost in development, network-accessible in production
    # This ensures secure-by-default development while allowing production deployment
    default_host = '127.0.0.1' if config.DEBUG else '0.0.0.0'
    host = os.environ.get('FLASK_HOST', default_host)

    # Determine public URL for deployment
    public_url = os.environ.get('PUBLIC_URL', 'http://laguna.ku.lt:5000')

    logger.info(f"\nServer Configuration:")
    logger.info(f"   Environment: {'Development' if config.DEBUG else 'Production'}")
    logger.info(f"   Binding to: {host}:{port}")
    if host == '127.0.0.1':
        logger.info(f"   Access at: http://127.0.0.1:{port}")
        logger.info(f"   (Set FLASK_HOST=0.0.0.0 to allow network access)")
    else:
        logger.info(f"   Local:    http://127.0.0.1:{port}")
        logger.info(f"   Network:  {public_url}")

    app.run(debug=config.DEBUG, host=host, port=port)
