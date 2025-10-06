"""
MARBEFES BBT Database - Marine Biodiversity and Ecosystem Functioning Database for Broad Belt Transects
"""

# Standard library imports
import os
import sys
import json
from pathlib import Path
from xml.etree import ElementTree as ET

# Third-party imports
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_caching import Cache
import requests

# Add src and config directories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "config"))

# Local imports
from config import get_config, EMODNET_LAYERS
from emodnet_viewer.utils.logging_config import setup_logging, get_logger

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

# Initialize Flask-Caching
cache = Cache(app, config={'CACHE_TYPE': config.CACHE_TYPE, 'CACHE_DEFAULT_TIMEOUT': config.CACHE_DEFAULT_TIMEOUT})

# Initialize requests session with connection pooling for WMS requests
# Connection pooling provides 20-40% performance improvement for repeated WMS calls
wms_session = requests.Session()
# Configure connection pool size (max connections to keep alive)
adapter = requests.adapters.HTTPAdapter(
    pool_connections=10,  # Number of connection pools to cache
    pool_maxsize=20,      # Max connections per pool
    max_retries=3,        # Retry failed requests
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

# Load bathymetry statistics on startup
BATHYMETRY_STATS = load_bathymetry_stats()


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
        WMS_BASE_URL=WMS_BASE_URL,
        HELCOM_WMS_BASE_URL=HELCOM_WMS_BASE_URL,
        APPLICATION_ROOT=app_root,
        API_BASE_URL=api_base_url,
    )


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
def api_vector_layer_geojson(layer_name):
    """API endpoint to get GeoJSON for a specific vector layer"""
    if not VECTOR_SUPPORT:
        return jsonify({"error": "Vector support not available"}), 503

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


@app.route("/api/capabilities")
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
def api_legend(layer_name):
    """API endpoint to get legend for a specific layer"""
    legend_url = (
        f"{WMS_BASE_URL}?"
        f"service=WMS&version=1.1.0&request=GetLegendGraphic&"
        f"layer={layer_name}&format=image/png"
    )
    return jsonify({"legend_url": legend_url})


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
    logger.info("  /test          - Test WMS connectivity")
    logger.info("  /api/layers    - Get WMS layers (JSON)")
    logger.info("  /api/all-layers - Get all layers (WMS + vector, JSON)")
    logger.info("  /api/vector/layers - Get vector layers (JSON)")
    logger.info("  /api/vector/layer/<name> - Get vector layer GeoJSON")
    logger.info("  /api/vector/bounds - Get vector layers bounds")
    logger.info("  /api/capabilities - Get WMS capabilities (XML)")
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
    host = os.environ.get('FLASK_HOST', '0.0.0.0')

    logger.info(f"\nServer accessible at:")
    logger.info(f"   Local:    http://127.0.0.1:{port}")
    logger.info(f"   Network:  http://{host}:{port}")

    app.run(debug=config.DEBUG, host=host, port=port)
