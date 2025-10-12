"""
MARBEFES BBT Database - Marine Biodiversity and Ecosystem Functioning Database for Broad Belt Transects
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import requests
from xml.etree import ElementTree as ET
import sys
import os
import logging
import threading
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Add config directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "config"))

try:
    from emodnet_viewer.utils.vector_loader import (
        vector_loader,
        get_vector_layer_geojson,
        get_vector_layers_summary,
    )

    VECTOR_SUPPORT = True
except ImportError as e:
    print(f"Vector support disabled - missing dependencies: {e}")
    VECTOR_SUPPORT = False

app = Flask(__name__)

# WMS Service Configuration
WMS_BASE_URL = "https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms"
WMS_VERSION = "1.3.0"

# HELCOM WMS Service Configuration
HELCOM_WMS_BASE_URL = "https://maps.helcom.fi/arcgis/services/MADS/Pressures/MapServer/WMSServer"
HELCOM_WMS_VERSION = "1.3.0"

# Enhanced EMODnet layers focusing on European EuSeaMap data
EMODNET_LAYERS = [
    # Core European EuSeaMap 2023 layers (actual names from emodnet_open)
    {
        "name": "eusm2023_bio_full",
        "title": "EUSeaMap 2023 - European Biological Zones",
        "description": "Latest broad-scale biological habitat map for European seas",
    },
    {
        "name": "eusm2023_subs_full",
        "title": "EUSeaMap 2023 - European Substrate Types",
        "description": "Latest seabed substrate classification for European seas",
    },
    {
        "name": "eusm_2023_eunis2007_full",
        "title": "EUSeaMap 2023 - European EUNIS Classification",
        "description": "European habitat map using EUNIS 2007 classification system",
    },

    # Supporting European layers
    {
        "name": "eusm2023_ene_full",
        "title": "EUSeaMap 2023 - European Energy Zones",
        "description": "Energy regime classification for European seas",
    },
    {
        "name": "overall_eusm2023_biozone_confidence",
        "title": "EUSeaMap 2023 - Biological Zone Confidence",
        "description": "Confidence levels in European biological zone predictions",
    },

    # Fallback EuSeaMap 2021/2019 layers (if 2023 not available)
    {
        "name": "all_eusm2021",
        "title": "EUSeaMap 2021 - All European Habitats",
        "description": "Complete broad-scale seabed habitat map for European seas",
    },
    {
        "name": "be_eusm2021",
        "title": "EUSeaMap 2021 - Benthic Habitats",
        "description": "Benthic broad-scale habitat map for European waters",
    },

    # Fallback generic layers
    {
        "name": "substrate",
        "title": "Seabed Substrate",
        "description": "General seabed substrate types",
    },
    {
        "name": "confidence",
        "title": "Confidence Assessment",
        "description": "General confidence in habitat predictions",
    },

    # EU Directive layers
    {
        "name": "annexiMaps_all",
        "title": "EU Habitats Directive - Annex I Habitats",
        "description": "Habitats Directive Annex I habitat types for European waters",
    },
    {
        "name": "ospar_threatened",
        "title": "OSPAR Threatened Habitats",
        "description": "OSPAR threatened and declining marine habitats",
    },
]


# Global cache for async operations
_layer_cache = {}
_cache_timestamp = {}

def fetch_wms_capabilities(base_url, version):
    """Synchronous WMS capabilities fetch for use in thread pool"""
    try:
        params = {"service": "WMS", "version": version, "request": "GetCapabilities"}
        response = requests.get(base_url, params=params, timeout=10)
        return response
    except Exception as e:
        print(f"Error fetching WMS capabilities from {base_url}: {e}")
        return None

async def get_available_layers_async():
    """Async version of get_available_layers with concurrent WMS requests"""
    try:
        loop = asyncio.get_event_loop()

        # Check cache first (5 minute cache)
        cache_key = "wms_layers"
        if (cache_key in _layer_cache and
            time.time() - _cache_timestamp.get(cache_key, 0) < 300):
            return _layer_cache[cache_key]

        # Use thread pool for concurrent WMS requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            # Submit both WMS requests concurrently
            future_emodnet = loop.run_in_executor(
                executor, fetch_wms_capabilities, WMS_BASE_URL, WMS_VERSION
            )
            future_helcom = loop.run_in_executor(
                executor, fetch_wms_capabilities, HELCOM_WMS_BASE_URL, HELCOM_WMS_VERSION
            )

            # Wait for both to complete with timeout
            try:
                emodnet_response, helcom_response = await asyncio.wait_for(
                    asyncio.gather(future_emodnet, future_helcom, return_exceptions=True),
                    timeout=15.0
                )
            except asyncio.TimeoutError:
                print("WMS requests timed out, using fallback layers")
                return EMODNET_LAYERS

        # Process EMODnet response
        wms_layers = []
        if emodnet_response and hasattr(emodnet_response, 'status_code') and emodnet_response.status_code == 200:
            wms_layers = parse_wms_capabilities(emodnet_response.content)

        # Process HELCOM response
        helcom_layers = []
        if helcom_response and hasattr(helcom_response, 'status_code') and helcom_response.status_code == 200:
            helcom_layers = parse_helcom_capabilities(helcom_response.content)

        # Combine and prioritize layers
        final_layers = prioritize_european_layers(wms_layers)

        # Cache the results
        _layer_cache[cache_key] = final_layers
        _cache_timestamp[cache_key] = time.time()

        return final_layers

    except Exception as e:
        print(f"Error in async layer fetching: {e}")
        return EMODNET_LAYERS

def parse_wms_capabilities(xml_content):
    """Parse WMS GetCapabilities XML response"""
    try:
        root = ET.fromstring(xml_content)

        # Remove namespace for easier parsing
        for elem in root.iter():
            if "}" in elem.tag:
                elem.tag = elem.tag.split("}")[1]

        wms_layers = []
        for layer in root.findall(".//Layer"):
            name_elem = layer.find("Name")
            title_elem = layer.find("Title")
            abstract_elem = layer.find("Abstract")

            if name_elem is not None and name_elem.text:
                # Skip the root layer and only get actual data layers
                if ":" not in name_elem.text:  # Skip workspace prefixed names for now
                    wms_layers.append({
                        "name": name_elem.text,
                        "title": (
                            title_elem.text
                            if title_elem is not None and title_elem.text
                            else name_elem.text
                        ),
                        "description": (
                            abstract_elem.text if abstract_elem is not None else ""
                        ),
                    })

        return wms_layers
    except Exception as e:
        print(f"Error parsing WMS capabilities: {e}")
        return []

def parse_helcom_capabilities(xml_content):
    """Parse HELCOM WMS GetCapabilities XML response"""
    try:
        root = ET.fromstring(xml_content)

        # Remove namespace for easier parsing
        for elem in root.iter():
            if "}" in elem.tag:
                elem.tag = elem.tag.split("}")[1]

        layers = []
        for layer in root.findall(".//Layer"):
            name_elem = layer.find("Name")
            title_elem = layer.find("Title")
            abstract_elem = layer.find("Abstract")

            if name_elem is not None and name_elem.text:
                layer_name = name_elem.text.strip()
                if layer_name and "_" in layer_name:  # Real layers have underscores in names
                    layers.append({
                        "name": layer_name,
                        "title": (
                            title_elem.text
                            if title_elem is not None and title_elem.text
                            else layer_name.replace("_", " ").title()
                        ),
                        "description": (
                            abstract_elem.text if abstract_elem is not None else ""
                        ),
                    })

        return layers if layers else []
    except Exception as e:
        print(f"Error parsing HELCOM capabilities: {e}")
        return []

def prioritize_european_layers(wms_layers):
    """Prioritize European layers and combine with defaults"""
    if wms_layers:
        # First, check if any of our preferred European layers exist in WMS
        preferred_layers = []
        european_terms = ['eusm2021', 'eusm2019', 'europe', 'substrate', 'confidence', 'annexiMaps', 'ospar']

        # Add European/preferred layers first
        for wms_layer in wms_layers:
            name_lower = wms_layer['name'].lower()
            title_lower = (wms_layer.get('title') or '').lower()

            # Prioritize European layers
            if any(term in name_lower or term in title_lower for term in european_terms):
                # Skip Caribbean layers
                if 'carib' not in name_lower and 'caribbean' not in title_lower:
                    preferred_layers.append(wms_layer)

        # Add other relevant layers (avoiding duplicates)
        added_names = {layer['name'] for layer in preferred_layers}
        other_layers = []
        for wms_layer in wms_layers:
            if (wms_layer['name'] not in added_names and
                'carib' not in wms_layer['name'].lower() and
                'caribbean' not in (wms_layer.get('title') or '').lower()):
                other_layers.append(wms_layer)

        # Combine: European layers first, then all others
        combined_layers = preferred_layers + other_layers

        # Always include our core European EuSeaMap layers at the top
        core_european_layers = EMODNET_LAYERS[:6]  # First 6 are core European EuSeaMap

        # Combine: Core European layers first, then discovered layers, avoiding duplicates
        final_layers = []
        added_names = set()

        # Add core European layers first
        for layer in core_european_layers:
            final_layers.append(layer)
            added_names.add(layer['name'])

        # Add discovered European layers (avoiding duplicates)
        for layer in preferred_layers:
            if layer['name'] not in added_names:
                final_layers.append(layer)
                added_names.add(layer['name'])

        # Add all other WMS layers (avoiding duplicates)
        for layer in other_layers:
            if layer['name'] not in added_names:
                final_layers.append(layer)
                added_names.add(layer['name'])

        return final_layers  # Return all available layers
    else:
        # No WMS layers found, use defaults
        return EMODNET_LAYERS

def get_available_layers():
    """Fast layer fetching with simple caching"""
    try:
        # Check cache first (5 minute cache)
        cache_key = "wms_layers"
        if (cache_key in _layer_cache and
            time.time() - _cache_timestamp.get(cache_key, 0) < 300):
            return _layer_cache[cache_key]

        # Simple synchronous request with timeout
        params = {"service": "WMS", "version": WMS_VERSION, "request": "GetCapabilities"}
        response = requests.get(WMS_BASE_URL, params=params, timeout=5)

        if response.status_code == 200:
            wms_layers = parse_wms_capabilities(response.content)
            final_layers = prioritize_european_layers(wms_layers)

            # Cache the results
            _layer_cache[cache_key] = final_layers
            _cache_timestamp[cache_key] = time.time()

            return final_layers
        else:
            return EMODNET_LAYERS

    except Exception as e:
        print(f"Error fetching layers (using fallback): {e}")
        return EMODNET_LAYERS

# Async vector loading optimization
async def load_vector_data_async():
    """Async version of vector data loading"""
    if not VECTOR_SUPPORT:
        return []

    try:
        loop = asyncio.get_event_loop()

        # Load vector data in thread pool to avoid blocking
        with concurrent.futures.ThreadPoolExecutor() as executor:
            from emodnet_viewer.utils.vector_loader import VectorLayerLoader

            # Create fresh loader and load in thread
            future = loop.run_in_executor(
                executor,
                lambda: VectorLayerLoader().load_all_vector_layers()
            )

            vector_layers = await asyncio.wait_for(future, timeout=30.0)

            print(f"✅ Async loaded {len(vector_layers)} vector layers from GPKG files")

            # Log layer information
            for layer in vector_layers:
                print(f"  - {layer.display_name} ({layer.geometry_type}, {layer.feature_count} features)")

            return vector_layers

    except asyncio.TimeoutError:
        print("⚠️ Vector loading timed out, continuing without vector layers")
        return []
    except Exception as e:
        print(f"❌ Error loading vector data async: {e}")
        return []


def get_helcom_layers():
    """Fetch available layers from HELCOM WMS GetCapabilities"""
    try:
        params = {"service": "WMS", "version": HELCOM_WMS_VERSION, "request": "GetCapabilities"}
        response = requests.get(HELCOM_WMS_BASE_URL, params=params, timeout=10)

        if response.status_code == 200:
            # Parse XML with namespace handling
            root = ET.fromstring(response.content)

            # Remove namespace for easier parsing
            for elem in root.iter():
                if "}" in elem.tag:
                    elem.tag = elem.tag.split("}")[1]

            layers = []
            for layer in root.findall(".//Layer"):
                name_elem = layer.find("Name")
                title_elem = layer.find("Title")
                abstract_elem = layer.find("Abstract")

                if name_elem is not None and name_elem.text:
                    # HELCOM layers have complex names like "Chemical_weapons_dumpsites_in_the_Baltic_Sea13404"
                    # Skip parent layers that don't have actual layer names
                    layer_name = name_elem.text.strip()
                    if layer_name and "_" in layer_name:  # Real layers have underscores in names
                        layers.append(
                            {
                                "name": layer_name,
                                "title": (
                                    title_elem.text
                                    if title_elem is not None and title_elem.text
                                    else layer_name.replace("_", " ").title()
                                ),
                                "description": (
                                    abstract_elem.text if abstract_elem is not None else ""
                                ),
                            }
                        )

            # Return found layers, limit to reasonable number
            return layers if layers else []

    except Exception as e:
        print(f"Error fetching HELCOM layers: {e}")

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
        except Exception as e:
            print(f"Error loading vector layers: {e}")
            combined_layers["vector_support"] = False

    return combined_layers


def load_vector_data_on_startup():
    """Load vector data when the application starts (now uses async in background)"""
    def async_loader():
        """Background async loader"""
        try:
            vector_layers = asyncio.run(load_vector_data_async())

            # Update the global instance if we have vector support
            if VECTOR_SUPPORT:
                vector_loader.loaded_layers = vector_layers

        except Exception as e:
            print(f"❌ Error in background vector loading: {e}")

    if VECTOR_SUPPORT:
        # Start async loading in background thread to avoid blocking startup
        print("🚀 Starting async vector data loading in background...")
        background_thread = Thread(target=async_loader, daemon=True)
        background_thread.start()
    else:
        print("📦 Vector support disabled, skipping vector layer loading")


@app.route("/")
def index():
    """Main page with map viewer"""
    all_layers = get_all_layers()
    return render_template(
        'index.html',
        layers=all_layers["wms_layers"],
        helcom_layers=all_layers["helcom_layers"],
        vector_layers=all_layers["vector_layers"],
        vector_support=all_layers["vector_support"],
        WMS_BASE_URL=WMS_BASE_URL,
        HELCOM_WMS_BASE_URL=HELCOM_WMS_BASE_URL,
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
        return jsonify({"error": str(e)}), 500


@app.route("/api/capabilities")
def api_capabilities():
    """API endpoint to get WMS capabilities"""
    params = {"service": "WMS", "version": WMS_VERSION, "request": "GetCapabilities"}
    try:
        response = requests.get(WMS_BASE_URL, params=params, timeout=10)
        return response.content, 200, {"Content-Type": "text/xml"}
    except Exception as e:
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
    print("\n" + "=" * 60)
    print("MARBEFES BBT Database - Marine Biodiversity and Ecosystem Functioning Database")
    print("=" * 60)
    print("\nInitializing application...")

    # Vector data loading already initiated at module level (line 603)
    # No need to call load_vector_data_on_startup() again here

    print("\nStarting Flask server...")
    print("Open http://localhost:5000 in your browser")
    print("\nAvailable endpoints:")
    print("  /              - Main interactive map viewer")
    print("  /test          - Test WMS connectivity")
    print("  /api/layers    - Get WMS layers (JSON)")
    print("  /api/all-layers - Get all layers (WMS + vector, JSON)")
    print("  /api/vector/layers - Get vector layers (JSON)")
    print("  /api/vector/layer/<name> - Get vector layer GeoJSON")
    print("  /api/vector/bounds - Get vector layers bounds")
    print("  /api/capabilities - Get WMS capabilities (XML)")
    print("  /api/legend/<layer> - Get legend URL for a layer")

    if VECTOR_SUPPORT:
        print("\nVector Support: Enabled")
        print(f"   Data directory: {Path('data/vector').absolute()}")
    else:
        print("\nVector Support: Disabled (missing dependencies)")
        print("   Install: pip install geopandas fiona pyproj")

    print("\nPress Ctrl+C to stop the server")
    print("-" * 60 + "\n")

    port = int(os.environ.get('FLASK_RUN_PORT', 5000))
    host = os.environ.get('FLASK_HOST', '0.0.0.0')  # Bind to all interfaces for internet access

    print(f"\n🌐 Server accessible at:")
    print(f"   Local:    http://127.0.0.1:{port}")
    print(f"   Network:  http://192.168.4.180:{port}")
    print(f"   Internet: http://193.219.76.93:{port}")
    print(f"\n⚠️  Warning: Server is accessible from the internet!")
    print(f"   Consider adding authentication for production use.\n")

    app.run(debug=True, host=host, port=port)
