"""
MARBEFES BBT viewer - Flask application for viewing Broad Belt Transect data and EMODnet WMS layers
"""

from flask import Flask, render_template_string, jsonify, request
import requests
from xml.etree import ElementTree as ET
import json
import os
import geopandas as gpd
from shapely.geometry import mapping

app = Flask(__name__)

# WMS Service Configuration
WMS_BASE_URL = "https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms"
WMS_VERSION = "1.3.0"

# EUSeaMap layers only (verified to exist) - descriptions set to None for title-only display
EUSEAMAP_LAYERS = [
    {
        "name": "eusm_2023_eunis2019_full",
        "title": "EUSeaMap 2023 - EUNIS 2019 Classification",
        "description": None
    },
    {
        "name": "all_eusm2021",
        "title": "EUSeaMap 2021 - All Habitats",
        "description": None
    },
    {
        "name": "be_eusm2021",
        "title": "EUSeaMap 2021 - Benthic Habitats",
        "description": None
    },
    {
        "name": "pe_eusm2021",
        "title": "EUSeaMap 2021 - Pelagic Habitats",
        "description": None
    },
    {
        "name": "all_eusm2019",
        "title": "EUSeaMap 2019 - All Habitats",
        "description": None
    },
    {
        "name": "be_eusm2019",
        "title": "EUSeaMap 2019 - Benthic Habitats",
        "description": None
    },
    {
        "name": "pe_eusm2019",
        "title": "EUSeaMap 2019 - Pelagic Habitats",
        "description": None
    }
]

def get_available_layers():
    """Fetch available layers from WMS GetCapabilities"""
    try:
        params = {
            'service': 'WMS',
            'version': WMS_VERSION,
            'request': 'GetCapabilities'
        }
        response = requests.get(WMS_BASE_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            # Parse XML with namespace handling
            root = ET.fromstring(response.content)
            
            # Remove namespace for easier parsing
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}')[1]
            
            layers = []
            for layer in root.findall('.//Layer'):
                name_elem = layer.find('Name')
                title_elem = layer.find('Title')
                abstract_elem = layer.find('Abstract')
                
                if name_elem is not None and name_elem.text:
                    # Only include EUSeaMap layers (filter by name pattern)
                    layer_name = name_elem.text
                    if ':' not in layer_name and ('eusm' in layer_name.lower() or 'euseamap' in layer_name.lower()):
                        layers.append({
                            'name': layer_name,
                            'title': title_elem.text if title_elem is not None and title_elem.text else layer_name,
                            'description': None  # Always set to None to ensure only titles are shown
                        })
            
            # Return EUSeaMap layers found or fallback to defaults
            return layers if layers else EUSEAMAP_LAYERS
            
    except Exception as e:
        print(f"Error fetching layers: {e}")
    
    return EUSEAMAP_LAYERS

def load_gpkg_layer():
    """Load the CheckedBBT.gpkg file and return as GeoJSON"""
    try:
        gpkg_path = os.path.join(os.path.dirname(__file__), 'data', 'vector', 'CheckedBBT.gpkg')
        if os.path.exists(gpkg_path):
            # Read the GeoPackage file
            gdf = gpd.read_file(gpkg_path)
            
            # Check and reproject from EPSG:3035 to EPSG:4326 if needed
            print(f"Original CRS: {gdf.crs}")
            if gdf.crs and gdf.crs.to_epsg() == 3035:
                print("Reprojecting from EPSG:3035 to EPSG:4326")
                gdf = gdf.to_crs('EPSG:4326')
            elif gdf.crs is None:
                print("No CRS detected, assuming EPSG:3035 and reprojecting to EPSG:4326")
                gdf = gdf.set_crs('EPSG:3035').to_crs('EPSG:4326')
            
            print(f"Final CRS: {gdf.crs}")
            print(f"Bounds: {gdf.total_bounds}")
            
            # Convert to GeoJSON format
            geojson = {
                "type": "FeatureCollection",
                "features": []
            }
            
            for idx, row in gdf.iterrows():
                feature = {
                    "type": "Feature",
                    "geometry": mapping(row.geometry),
                    "properties": {key: str(value) if value is not None else None 
                                 for key, value in row.drop('geometry').to_dict().items()}
                }
                geojson["features"].append(feature)
            
            return geojson
        else:
            print(f"GeoPackage file not found at: {gpkg_path}")
            return None
    except Exception as e:
        print(f"Error loading GeoPackage: {e}")
        return None

@app.route('/api/vector-layer')
def get_vector_layer():
    """API endpoint to get the vector layer data"""
    geojson_data = load_gpkg_layer()
    if geojson_data:
        return jsonify(geojson_data)
    else:
        return jsonify({"error": "Could not load vector layer"}), 404

@app.route('/api/bbts')
def get_bbts():
    """API endpoint to get BBT features for navigation"""
    try:
        gpkg_path = os.path.join(os.path.dirname(__file__), 'data', 'vector', 'CheckedBBT.gpkg')
        if os.path.exists(gpkg_path):
            # Read the GeoPackage file
            gdf = gpd.read_file(gpkg_path)
            
            # Check and reproject from EPSG:3035 to EPSG:4326 if needed
            if gdf.crs and gdf.crs.to_epsg() == 3035:
                gdf = gdf.to_crs('EPSG:4326')
            elif gdf.crs is None:
                gdf = gdf.set_crs('EPSG:3035').to_crs('EPSG:4326')
            
            bbts = []
            for i, (idx, row) in enumerate(gdf.iterrows()):
                # Get bounds for each feature
                bounds = row.geometry.bounds  # (minx, miny, maxx, maxy)
                
                # Try to get a name from common BBT name fields
                name = None
                for field in ['BBT_name', 'Name', 'name', 'BBT', 'Site', 'site', 'Location', 'location']:
                    if field in row and row[field] is not None and str(row[field]).strip():
                        name = str(row[field]).strip()
                        break
                
                if not name:
                    name = f"BBT {i + 1}"
                
                bbts.append({
                    'id': i,
                    'name': name,
                    'bounds': {
                        'west': bounds[0],
                        'south': bounds[1], 
                        'east': bounds[2],
                        'north': bounds[3]
                    }
                })
            
            return jsonify(bbts)
        else:
            return jsonify({"error": "GeoPackage file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    """Main page with map viewer"""
    
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>MARBEFES BBT Database Viewer</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body { 
                margin: 0; 
                padding: 0; 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: #f0f0f0;
            }
            #container {
                display: flex;
                height: 100vh;
            }
            #sidebar {
                width: 320px;
                background: white;
                padding: 20px;
                box-shadow: 2px 0 10px rgba(0,0,0,0.1);
                overflow-y: auto;
                z-index: 1000;
            }
            #map {
                flex: 1;
                position: relative;
            }
            h1 {
                color: #2c3e50;
                font-size: 24px;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .help-icon {
                font-size: 18px;
                color: #667eea;
                cursor: help;
                border-radius: 50%;
                width: 24px;
                height: 24px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                background: rgba(102, 126, 234, 0.1);
                border: 1px solid rgba(102, 126, 234, 0.3);
                transition: all 0.3s ease;
                white-space: pre-line;
            }
            .help-icon:hover {
                background: rgba(102, 126, 234, 0.2);
                border-color: rgba(102, 126, 234, 0.5);
                transform: scale(1.1);
            }
            .subtitle {
                color: #7f8c8d;
                font-size: 12px;
                margin-bottom: 20px;
            }
            h3 {
                color: #34495e;
                font-size: 16px;
                margin-top: 20px;
                margin-bottom: 10px;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5px;
            }

            #info {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                font-size: 13px;
                line-height: 1.6;
            }
            .controls {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #dee2e6;
            }
            .control-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-size: 13px;
                color: #495057;
                font-weight: 600;
            }
            input[type="range"] {
                width: 100%;
                height: 6px;
                border-radius: 3px;
                background: #ddd;
                outline: none;
                -webkit-appearance: none;
            }
            input[type="range"]::-webkit-slider-thumb {
                -webkit-appearance: none;
                appearance: none;
                width: 18px;
                height: 18px;
                border-radius: 50%;
                background: #667eea;
                cursor: pointer;
            }
            input[type="range"]::-moz-range-thumb {
                width: 18px;
                height: 18px;
                border-radius: 50%;
                background: #667eea;
                cursor: pointer;
            }
            .value-display {
                text-align: center;
                font-size: 14px;
                color: #667eea;
                font-weight: bold;
                margin-top: 5px;
            }
            input[type="checkbox"] {
                margin-right: 8px;
                accent-color: #667eea;
                transform: scale(1.1);
            }
            label input[type="checkbox"] {
                cursor: pointer;
            }
            .links-section {
                display: flex;
                flex-direction: column;
                gap: 8px;
            }
            .project-link {
                display: flex;
                align-items: center;
                padding: 10px 12px;
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
                border: 1px solid #dee2e6;
                border-radius: 6px;
                text-decoration: none;
                color: #495057;
                font-size: 13px;
                font-weight: 500;
                transition: all 0.2s ease;
                position: relative;
                overflow: hidden;
            }
            .project-link:hover {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-color: #667eea;
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
            }
            .project-link:active {
                transform: translateY(0);
            }
            .bbt-navigation {
                margin-bottom: 20px;
            }
            .bbt-buttons-grid {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 8px;
            }
            .bbt-button {
                padding: 8px 12px;
                background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
                border: none;
                border-radius: 6px;
                color: white;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                text-align: center;
                display: flex;
                align-items: center;
                justify-content: center;
                min-height: 36px;
            }
            .bbt-button:hover {
                background: linear-gradient(135deg, #2980b9 0%, #1f4e79 100%);
                transform: translateY(-1px);
                box-shadow: 0 4px 8px rgba(52, 152, 219, 0.3);
            }
            .bbt-button:active {
                transform: translateY(0);
            }
            .legend-container {
                position: absolute;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
                background: white;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
                border: 3px solid #3498db;
                max-width: 500px;
                min-width: 300px;
                cursor: move;
                user-select: none;
            }
            .legend-container.dragging {
                cursor: grabbing;
                transform: rotate(2deg);
                box-shadow: 0 8px 30px rgba(0, 0, 0, 0.5);
                pointer-events: none;
            }
            .legend-container.dragging * {
                pointer-events: none;
                user-select: none;
            }
            .legend-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
                border-bottom: 3px solid #3498db;
                padding-bottom: 12px;
                cursor: move;
                user-select: none;
                position: relative;
            }
            .legend-header:hover::after {
                content: "Drag to move";
                position: absolute;
                bottom: -25px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                white-space: nowrap;
                z-index: 1001;
                pointer-events: none;
            }
            .legend-container h4 {
                margin: 0;
                font-size: 24px;
                color: #2c3e50;
                font-weight: 700;
                cursor: move;
                user-select: none;
            }
            .legend-close {
                background: none;
                border: none;
                font-size: 24px;
                color: #6c757d;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.2s ease;
            }
            .legend-close:hover {
                background: #e9ecef;
                color: #495057;
            }
            #legend-image {
                width: 100%;
                height: auto;
                min-height: 200px;
                border-radius: 10px;
                border: 2px solid #dee2e6;
                image-rendering: -webkit-optimize-contrast;
                image-rendering: crisp-edges;
                display: block;
                margin: 0 auto;
                background: #f8f9fa;
            }
            .status {
                position: absolute;
                top: 10px;
                right: 10px;
                background: white;
                padding: 8px 15px;
                border-radius: 20px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.2);
                z-index: 1000;
                font-size: 12px;
                color: #27ae60;
                font-weight: 600;
            }
            .loading {
                color: #f39c12;
            }
            .error {
                color: #e74c3c;
            }
            /* Dot pattern for BBT polygons */
            .bbt-polygon {
                fill: url(#dotPattern) !important;
            }
            
            /* BBT Tooltip Styling */
            .bbt-tooltip {
                background: white;
                border: 2px solid #3498db;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                padding: 0;
                font-size: 12px;
                max-width: 300px;
                z-index: 9999;
            }
            
            .bbt-tooltip .leaflet-tooltip-content {
                margin: 8px 12px;
                padding: 0;
            }
            
            .leaflet-tooltip.bbt-tooltip::before {
                border-top-color: #3498db;
            }
            
            /* Popup Styling - Force Override */
            .leaflet-popup-content-wrapper {
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                max-width: 700px !important;
                width: 700px !important;
                min-width: 600px !important;
            }
            
            .leaflet-popup {
                max-width: 700px !important;
                min-width: 600px !important;
            }
            
            .feature-info-popup .leaflet-popup-content-wrapper {
                width: 700px !important;
                min-width: 600px !important;
            }
            
            .feature-info-popup .leaflet-popup-content {
                width: 700px !important;
                min-width: 600px !important;
            }
            
            .leaflet-popup-content {
                margin: 0 !important;
                padding: 0 !important;
                max-width: 700px !important;
                width: 700px !important;
                min-width: 600px !important;
                box-sizing: border-box !important;
                overflow: hidden !important;
            }
            
            .popup-container {
                width: 600px !important;
                min-width: 600px !important;
                max-width: 700px !important;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                box-sizing: border-box !important;
                overflow: hidden !important;
                word-wrap: break-word !important;
                overflow-wrap: break-word !important;
            }
            
            .popup-container * {
                box-sizing: border-box;
                word-wrap: break-word !important;
                overflow-wrap: break-word !important;
                word-break: break-all !important;
                hyphens: auto !important;
                max-width: 100% !important;
            }
            
            /* Force text wrapping for long content */
            .popup-container table, .popup-container th, .popup-container td {
                word-break: break-all !important;
                overflow-wrap: anywhere !important;
                hyphens: auto !important;
            }
            
            .popup-container table {
                width: 100%;
                border-collapse: collapse;
                font-size: 13px;
                word-wrap: break-word;
                table-layout: fixed;
                word-break: break-all;
                overflow-wrap: anywhere;
            }
            
            .popup-container th {
                background: #3498db;
                color: white;
                padding: 8px 12px;
                text-align: left;
                border: 1px solid #ddd;
                word-wrap: break-word;
                overflow-wrap: anywhere;
                word-break: break-all;
                hyphens: auto;
                width: 25%;
                max-width: 150px;
                font-size: 13px;
            }
            
            .popup-container td {
                padding: 8px 12px;
                border: 1px solid #ddd;
                word-wrap: break-word;
                overflow-wrap: anywhere;
                word-break: break-all;
                hyphens: auto;
                white-space: pre-wrap;
                width: 75%;
                max-width: 430px;
                font-size: 13px;
                line-height: 1.4;
            }
        </style>
    </head>
    <body>
        <div id="container">
            <div id="sidebar">
                <h1>
                    <img src="/www/img/marbefes.png" alt="MARBEFES" style="height: 32px; margin-right: 10px; vertical-align: middle;" 
                         onerror="this.src='/www/img/marbefes.svg'"> MARBEFES BBT Database Viewer
                    <span class="help-icon" title="Interactive Map Viewer&#10;&#10;• Select a layer to visualize different seabed habitat datasets&#10;• Use your mouse to pan and zoom the map&#10;• Click on the map to get detailed information about features at that location&#10;• Adjust opacity to see through to the base map&#10;• Different layers may be visible at different zoom levels">ⓘ</span>
                </h1>
                <div class="subtitle">Marine Biodiversity and Ecosystem Functioning Database</div>
                
                <div id="info">
                    <strong>🌊 About this Viewer:</strong><br>
                    This interactive map displays <strong>Broad Belt Transect (BBT)</strong> data from the MARBEFES project, overlaid with European seabed habitat classifications. BBTs are research transects spanning from river to ocean across four EU marine regions: Arctic, Baltic, Atlantic, and Mediterranean.
                </div>
                
                <h3>🗺️ BBT Navigation</h3>
                <div id="bbt-navigation" class="bbt-navigation">
                    <p style="font-size: 12px; color: #6c757d; margin-bottom: 10px;">
                        Click a BBT to zoom to its location:
                    </p>
                    <div id="bbt-buttons" class="bbt-buttons-grid">
                        <!-- BBT buttons will be populated by JavaScript -->
                    </div>
                </div>
                
                <h3>Available Layers</h3>
                <div class="control-group">
                    <label for="layer-select">Select Layer</label>
                    <select id="layer-select" style="width: 100%; padding: 8px; border-radius: 4px; border: 1px solid #ddd;">
                    </select>
                </div>
                
                <div class="controls">
                    <div class="control-group">
                        <label for="opacity">Layer Opacity</label>
                        <input type="range" id="opacity" min="0" max="100" value="70">
                        <div class="value-display" id="opacity-value">70%</div>
                    </div>
                    
                    <div class="control-group">
                        <label>
                            <input type="checkbox" id="show-legend" checked> Show Legend
                        </label>
                    </div>
                </div>
                
                <h3>🔗 MARBEFES Project</h3>
                <div class="links-section">
                    <a href="https://marbefes.eu" target="_blank" class="project-link">
                        🏠 Project Homepage
                    </a>
                    <a href="https://marbefes.eu/article/main-concept" target="_blank" class="project-link">
                        📋 About MARBEFES
                    </a>
                    <a href="https://marbefes.eu/articles/bbts" target="_blank" class="project-link">
                        🗺️ Broad Belt Transects (BBTs)
                    </a>
                    <a href="https://marbefes.eu/articles/publications" target="_blank" class="project-link">
                        📚 Publications
                    </a>
                    <a href="https://marbefes.eu/articles/database" target="_blank" class="project-link">
                        💾 Database & Data
                    </a>
                    <a href="https://marbefes.eu/articles/partners" target="_blank" class="project-link">
                        🤝 Partners
                    </a>
                    <a href="https://marbefes.eu/articles/news" target="_blank" class="project-link">
                        📰 Latest News
                    </a>
                    <a href="mailto:marbefes@iopan.pl" class="project-link">
                        ✉️ Contact
                    </a>
                </div>
            </div>
            
            <div id="map">
                <!-- Floating legend container -->
                <div class="legend-container" id="legend-container" style="display: none;">
                    <div class="legend-header" title="Click and drag to move legend">
                        <h4 id="legend-title">Legend</h4>
                        <button class="legend-close" id="legend-close">×</button>
                    </div>
                    <img id="legend-image" src="" alt="Layer legend">
                </div>
            </div>
            <div class="status" id="status">Ready</div>
            
            <!-- SVG pattern for dot fill -->
            <svg width="0" height="0">
                <defs>
                    <pattern id="dotPattern" patternUnits="userSpaceOnUse" width="8" height="8">
                        <rect width="8" height="8" fill="none"/>
                        <circle cx="4" cy="4" r="1.5" fill="#6c757d" fill-opacity="0.6"/>
                    </pattern>
                </defs>
            </svg>
        </div>
        
        <script>
            // Initialize map with EPSG:4326 CRS and default view (will be updated when vector layer loads)
            var map = L.map('map', {
                crs: L.CRS.EPSG4326
            }).setView([54.0, 10.0], 4);
            
            // Variable to hold the vector layer
            var vectorLayer = null;
            
            // Fixed EMODnet Bathymetry base layer
            var bathymetryLayer = L.tileLayer.wms('https://ows.emodnet-bathymetry.eu/wms', {
                layers: 'emodnet:mean_atlas_land',
                format: 'image/png',
                transparent: false,
                version: '1.3.0',
                crs: L.CRS.EPSG4326,
                maxZoom: 13,
                attribution: '© EMODnet Bathymetry Consortium'
            });
            
            // Add fixed bathymetry base layer
            bathymetryLayer.addTo(map);
            
            // Function to load BBT navigation buttons
            function loadBBTNavigation() {
                fetch('/api/bbts')
                    .then(response => response.json())
                    .then(bbts => {
                        const buttonsContainer = document.getElementById('bbt-buttons');
                        buttonsContainer.innerHTML = '';
                        
                        bbts.forEach(bbt => {
                            const button = document.createElement('button');
                            button.className = 'bbt-button';
                            button.textContent = bbt.name;
                            button.title = `Zoom to ${bbt.name}`;
                            
                            button.onclick = () => {
                                // Zoom to BBT bounds
                                const bounds = [
                                    [bbt.bounds.south, bbt.bounds.west],
                                    [bbt.bounds.north, bbt.bounds.east]
                                ];
                                map.fitBounds(bounds, {
                                    padding: [20, 20],
                                    maxZoom: 12
                                });
                                
                                // Add visual feedback
                                button.style.background = 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)';
                                setTimeout(() => {
                                    button.style.background = '';
                                }, 1000);
                            };
                            
                            buttonsContainer.appendChild(button);
                        });
                        
                        console.log(`Loaded ${bbts.length} BBT navigation buttons`);
                    })
                    .catch(error => {
                        console.error('Error loading BBT navigation:', error);
                        document.getElementById('bbt-buttons').innerHTML = 
                            '<p style="color: #e74c3c; font-size: 12px;">Error loading BBT navigation</p>';
                    });
            }
            
            // Function to load and display vector layer
            function loadVectorLayer() {
                fetch('/api/vector-layer')
                    .then(response => response.json())
                    .then(data => {
                        if (data && data.features) {
                            // Create and add vector layer to map
                            vectorLayer = L.geoJSON(data, {
                                style: {
                                    color: '#6c757d',
                                    weight: 2,
                                    opacity: 0.8,
                                    fillOpacity: 0.3,
                                    fillColor: '#6c757d',
                                    dashArray: null,
                                    fillRule: 'evenodd'
                                },
                                onEachFeature: function(feature, layer) {
                                    // Add click handler for WMS GetFeatureInfo
                                    layer.on('click', function(e) {
                                        // Highlight the clicked feature
                                        highlightFeature(layer);
                                        
                                        // Perform WMS GetFeatureInfo request for the current layer
                                        getFeatureInfo(e.latlng.lat, e.latlng.lng);
                                    });
                                    
                                    // Add hover handlers for BBT information
                                    layer.on('mouseover', function(e) {
                                        // Only show BBT tooltip at regional/global scale (zoom < 8)
                                        if (map.getZoom() < 8) {
                                            showBBTTooltip(e, feature);
                                        }
                                    });
                                    
                                    layer.on('mouseout', function(e) {
                                        // Hide BBT tooltip
                                        hideBBTTooltip();
                                    });
                                    
                                    // Add dot pattern class once layer is added to map
                                    layer.on('add', function() {
                                        if (this._path) {
                                            this._path.classList.add('bbt-polygon');
                                        }
                                    });
                                }
                            }).addTo(map);
                            
                            // Zoom to vector layer bounds
                            if (vectorLayer.getBounds().isValid()) {
                                map.fitBounds(vectorLayer.getBounds(), {padding: [20, 20]});
                            }
                            
                            console.log('Vector layer loaded and map zoomed to bounds');
                        }
                    })
                    .catch(error => {
                        console.error('Error loading vector layer:', error);
                    });
            }
            
            // Layer data
            const layers = {{ layers | tojson }};
            // Use EUSeaMap EUNIS 2019 descriptor as default
            let currentLayer = 'eusm_2023_eunis2019_full';
            let currentOpacity = 0.7;
            let wmsLayer = null;
            
            // Function to update WMS layer
            function updateWMSLayer(layerName, opacity) {
                document.getElementById('status').textContent = 'Loading layer...';
                document.getElementById('status').className = 'status loading';
                
                // Remove existing WMS layer if present
                if (wmsLayer) {
                    map.removeLayer(wmsLayer);
                }
                
                // Add new WMS layer
                wmsLayer = L.tileLayer.wms('{{ WMS_BASE_URL }}', {
                    layers: layerName,
                    format: 'image/png',
                    transparent: true,
                    version: '1.1.0',
                    opacity: opacity,
                    attribution: 'MARBEFES BBT Database | EMODnet',
                    tiled: true
                });
                
                wmsLayer.addTo(map);
                
                // Update legend
                updateLegend(layerName);
                
                // Update status
                setTimeout(() => {
                    document.getElementById('status').textContent = 'Layer loaded';
                    document.getElementById('status').className = 'status';
                }, 500);
            }
            
            // Function to update legend
            function updateLegend(layerName) {
                const legendUrl = `{{ WMS_BASE_URL }}?service=WMS&version=1.1.0&request=GetLegendGraphic&layer=${layerName}&format=image/png`;
                const legendImg = document.getElementById('legend-image');
                const legendContainer = document.getElementById('legend-container');
                const legendTitle = document.getElementById('legend-title');
                const showLegendCheckbox = document.getElementById('show-legend');
                
                // Find the layer title from the layers array
                const selectedLayer = layers.find(layer => layer.name === layerName);
                const layerTitle = selectedLayer ? selectedLayer.title : layerName;
                legendTitle.textContent = layerTitle;
                
                legendImg.src = legendUrl;
                legendImg.onload = () => {
                    // Only show legend if checkbox is checked
                    if (showLegendCheckbox.checked) {
                        legendContainer.style.display = 'block';
                    }
                };
                legendImg.onerror = () => {
                    legendContainer.style.display = 'none';
                };
            }
            
            // Function to get feature info from WMS
            function getFeatureInfo(lat, lng) {
                // Get map size and convert lat/lng to pixel coordinates
                const mapSize = map.getSize();
                const bounds = map.getBounds();
                const point = map.latLngToContainerPoint([lat, lng]);
                
                // Build GetFeatureInfo URL
                const params = {
                    service: 'WMS',
                    version: '1.1.0',
                    request: 'GetFeatureInfo',
                    layers: currentLayer,
                    query_layers: currentLayer,
                    styles: '',
                    bbox: `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`,
                    width: mapSize.x,
                    height: mapSize.y,
                    format: 'image/png',
                    info_format: 'text/html',
                    srs: 'EPSG:4326',
                    x: Math.round(point.x),
                    y: Math.round(point.y),
                    feature_count: 10
                };
                
                const url = '{{ WMS_BASE_URL }}?' + Object.keys(params).map(key => 
                    encodeURIComponent(key) + '=' + encodeURIComponent(params[key])
                ).join('&');
                
                console.log('🚀 Creating popup with options:', {
                    maxWidth: 700,
                    minWidth: 600,
                    maxHeight: 500,
                    className: 'feature-info-popup'
                });
                
                // Show loading popup with forced width
                const popup = L.popup({
                    maxWidth: 700,
                    minWidth: 600,
                    maxHeight: 500,
                    className: 'feature-info-popup',
                    autoPan: true,
                    keepInView: true
                })
                    .setLatLng([lat, lng])
                    .setContent('<div class="popup-container" style="text-align: center; padding: 15px; width: 600px; min-width: 600px;"><i class="loading">Loading feature info...</i></div>')
                    .openOn(map);
                
                console.log('✅ Popup created and opened');
                
                // Force popup width after opening
                setTimeout(() => {
                    console.log('⏰ First timeout executing...');
                    const popupElement = document.querySelector('.leaflet-popup-content');
                    if (popupElement) {
                        console.log('📐 Found popup element, current width:', popupElement.offsetWidth);
                        popupElement.style.width = '600px';
                        popupElement.style.minWidth = '600px';
                        popupElement.style.maxWidth = '600px';
                        console.log('📐 Set popup element width, new width:', popupElement.offsetWidth);
                    } else {
                        console.log('❌ Popup element not found in first timeout');
                    }
                }, 100);
                
                // Fetch feature info
                fetch(url)
                    .then(response => response.text())
                    .then(html => {
                        if (html && html.trim() && !html.includes('no features were found')) {
                            console.log('📄 Got feature info HTML:', html.length, 'characters');
                            
                            // Clean up the HTML response
                            let content = html;
                            
                            // Remove existing table styling
                            content = content.replace(/<table[^>]*>/gi, '<table>');
                            content = content.replace(/<th[^>]*>/gi, '<th>');
                            content = content.replace(/<td[^>]*>/gi, '<td>');
                            
                            console.log('🧹 Cleaned HTML content');
                            
                            // Wrap in a properly styled container with scroll and force width
                            content = `<div class="popup-container" style="max-height: 400px; overflow-y: auto; overflow-x: hidden; padding: 15px; width: 600px; min-width: 600px; box-sizing: border-box; word-wrap: break-word; word-break: break-all; overflow-wrap: anywhere;">${content}</div>`;
                            
                            console.log('📦 Wrapped content in container');
                            
                            // Force popup width after content is set
                            setTimeout(() => {
                                console.log('⏰ Second timeout executing...');
                                const popupElement = document.querySelector('.leaflet-popup-content');
                                if (popupElement) {
                                    console.log('📐 Found popup element in second timeout, width:', popupElement.offsetWidth);
                                    popupElement.style.width = '600px';
                                    popupElement.style.minWidth = '600px';
                                    popupElement.style.maxWidth = '600px';
                                    console.log('📐 Updated popup element width:', popupElement.offsetWidth);
                                } else {
                                    console.log('❌ Popup element not found in second timeout');
                                }
                            }, 100);
                            
                            console.log('🔄 Setting popup content...');
                            popup.setContent(content);
                            console.log('✅ Content set, calling forcePopupStyling...');
                            forcePopupStyling();
                        } else {
                            popup.setContent(`
                                <div class="popup-container" style="text-align: center; color: #6c757d; font-size: 12px; padding: 15px;">
                                    <strong>No feature information available</strong><br>
                                    at this location for layer:<br>
                                    <em>${currentLayer}</em>
                                </div>
                            `);
                            forcePopupStyling();
                        }
                    })
                    .catch(error => {
                        console.error('GetFeatureInfo error:', error);
                        popup.setContent(`
                            <div class="popup-container" style="text-align: center; color: #e74c3c; font-size: 12px; padding: 15px;">
                                <strong>Error loading feature info</strong><br>
                                ${error.message}
                            </div>
                        `);
                        forcePopupStyling();
                    });
            }
            
            // Variable to track currently highlighted feature
            let highlightedLayer = null;
            
            // BBT information from MARBEFES website
            const bbtInfo = {
                'Bay of Biscay': {
                    location: 'Northern Spain',
                    leader: 'Environmental Hydraulic Institute of the University of Cantabria',
                    description: 'A largely coastal area in northern Spain focusing on marine biodiversity and ecosystem functioning.'
                },
                'Archipelago Sea': {
                    location: 'Finland',
                    leader: 'AboAkademi',
                    description: 'Highly complex coastline with tens of thousands of tiny islands scattered across over 5,000 square kilometres. Focus on biodiversity and future changes research.'
                },
                'Porsangerfjord': {
                    location: 'North Norway',
                    leader: 'AkvaplanNiva',
                    description: 'Major challenges include decline in fish stocks due to deterioration of kelp beds and overfishing. Studies invasive red king crab impacts.'
                },
                'Sardinia': {
                    location: 'Gulf of Oristano, Italy',
                    leader: 'Institute of Anthropic Impacts and Sustainability in the Marine Environment',
                    description: 'Scenic locations with important species such as noble pen shell (Pinna nobilis) and Neptune grass/seagrass (Posidonia oceanica).'
                },
                'Irish Sea': {
                    location: 'Dublin/Dundalk Bays to Liverpool/Morecambe Bay',
                    leader: 'University College Dublin, CEFAS, University of East Anglia, IECS Ltd., University of Hull',
                    description: 'The largest of all MARBEFES BBTs, stretching from Irish to English coasts. Focus on threats to biodiversity and ecosystem services.'
                },
                'Lithuanian Coast': {
                    location: 'South East Baltic Sea',
                    leader: 'Marine Research Institute of Klaipeda University',
                    description: 'Includes Curonian Spit (UNESCO World Heritage Site) and Curonian Lagoon (largest lagoon in Europe). Blue carbon assessment and biogeochemical processes.'
                },
                'North Spitsbergen': {
                    location: 'Svalbard, Norway (Arctic)',
                    leader: 'Institute of Oceanology Polish Academy of Sciences',
                    description: 'Northernmost BBT studying impacts of anthropogenic pressures on Arctic marine biodiversity.'
                },
                'South Spitsbergen': {
                    location: 'Svalbard, Norway (Arctic)',
                    leader: 'Institute of Oceanology Polish Academy of Sciences',
                    description: 'Arctic research focusing on anthropogenic impacts on marine biodiversity in polar regions.'
                },
                'North Sea': {
                    location: 'Ostend to Dogger Bank (450 km transect)',
                    leader: 'Flanders Marine Institute',
                    description: 'Long transect for ecological value assessment. Provides scientific advice to policymakers and environmental managers.'
                },
                'Heraklion Gulf': {
                    location: 'Crete, Greece',
                    leader: 'HCMR',
                    description: 'Testing project tools to better understand marine biodiversity in Mediterranean waters.'
                },
                'Bay of Gdańsk': {
                    location: 'Northern Poland, Baltic Sea',
                    leader: 'Institute of Oceanology PAS',
                    description: 'Shallow waters serving as important habitat for fish, birds, and marine mammals including grey seals. Focus on conservation actions.'
                },
                'default': {
                    location: 'MARBEFES Research Site',
                    leader: 'MARBEFES Consortium',
                    description: 'Broad Belt Transect studying marine biodiversity and ecosystem functioning from river to ocean.'
                }
            };
            
            // Function to highlight a feature
            function highlightFeature(layer) {
                // Reset previous highlight
                if (highlightedLayer) {
                    resetHighlight(highlightedLayer);
                }
                
                // Apply highlight styling
                layer.setStyle({
                    color: '#ff6b35',
                    weight: 4,
                    opacity: 1,
                    fillOpacity: 0.7,
                    fillColor: '#ff6b35'
                });
                
                // Bring to front
                if (layer.bringToFront) {
                    layer.bringToFront();
                }
                
                // Store reference to highlighted layer
                highlightedLayer = layer;
                
                // Auto-reset highlight after 3 seconds
                setTimeout(() => {
                    if (highlightedLayer === layer) {
                        resetHighlight(layer);
                        highlightedLayer = null;
                    }
                }, 3000);
            }
            
            // Function to reset feature highlighting
            function resetHighlight(layer) {
                // Reset to original styling
                layer.setStyle({
                    color: '#6c757d',
                    weight: 2,
                    opacity: 0.8,
                    fillOpacity: 0.3,
                    fillColor: '#6c757d',
                    dashArray: null,
                    fillRule: 'evenodd'
                });
            }
            
            // Variable to track BBT tooltip
            let bbtTooltip = null;
            
            // Function to show BBT information tooltip
            function showBBTTooltip(e, feature) {
                // Get BBT name from feature properties
                let bbtName = null;
                for (let field of ['BBT_name', 'Name', 'name', 'BBT', 'Site', 'site', 'Location', 'location']) {
                    if (feature.properties[field]) {
                        bbtName = feature.properties[field].trim();
                        break;
                    }
                }
                
                // Find matching BBT info or use default
                let info = bbtInfo['default'];
                if (bbtName) {
                    // Try exact match first
                    if (bbtInfo[bbtName]) {
                        info = bbtInfo[bbtName];
                    } else {
                        // Try partial matches for common BBT names
                        for (let key in bbtInfo) {
                            if (bbtName.toLowerCase().includes(key.toLowerCase()) || 
                                key.toLowerCase().includes(bbtName.toLowerCase())) {
                                info = bbtInfo[key];
                                break;
                            }
                        }
                    }
                }
                
                // Create tooltip content
                const tooltipContent = `
                    <div style="min-width: 250px; font-family: 'Segoe UI', sans-serif;">
                        <div style="background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%); color: white; padding: 8px 12px; margin: -8px -12px 8px -12px; border-radius: 6px 6px 0 0;">
                            <strong style="font-size: 14px;">🌊 ${bbtName || 'MARBEFES BBT'}</strong>
                        </div>
                        <div style="font-size: 12px; line-height: 1.4;">
                            <div style="margin-bottom: 6px;">
                                <strong style="color: #3498db;">📍 Location:</strong><br>
                                <span style="color: #555;">${info.location}</span>
                            </div>
                            <div style="margin-bottom: 6px;">
                                <strong style="color: #3498db;">🏛️ Leading Partner:</strong><br>
                                <span style="color: #555;">${info.leader}</span>
                            </div>
                            <div>
                                <strong style="color: #3498db;">📋 Description:</strong><br>
                                <span style="color: #555;">${info.description}</span>
                            </div>
                        </div>
                        <div style="text-align: center; margin-top: 8px; padding-top: 6px; border-top: 1px solid #e9ecef;">
                            <small style="color: #6c757d; font-size: 10px;">MARBEFES Broad Belt Transect</small>
                        </div>
                    </div>
                `;
                
                // Create and show tooltip
                bbtTooltip = L.tooltip({
                    permanent: false,
                    direction: 'top',
                    className: 'bbt-tooltip'
                })
                .setContent(tooltipContent)
                .setLatLng(e.latlng);
                
                bbtTooltip.addTo(map);
            }
            
            // Function to hide BBT tooltip
            function hideBBTTooltip() {
                if (bbtTooltip) {
                    map.removeLayer(bbtTooltip);
                    bbtTooltip = null;
                }
            }
            
            // Function to force popup styling with debugging
            function forcePopupStyling() {
                console.log('🔧 forcePopupStyling() called');
                setTimeout(() => {
                    const popupWrapper = document.querySelector('.leaflet-popup-content-wrapper');
                    const popupContent = document.querySelector('.leaflet-popup-content');
                    const popupContainer = document.querySelector('.popup-container');
                    
                    console.log('📏 Popup elements found:', {
                        wrapper: !!popupWrapper,
                        content: !!popupContent, 
                        container: !!popupContainer
                    });
                    
                    if (popupWrapper) {
                        console.log('📐 Original wrapper width:', popupWrapper.style.width, popupWrapper.offsetWidth);
                        popupWrapper.style.width = '700px';
                        popupWrapper.style.minWidth = '600px';
                        popupWrapper.style.maxWidth = '700px';
                        console.log('📐 New wrapper width:', popupWrapper.style.width, popupWrapper.offsetWidth);
                    }
                    
                    if (popupContent) {
                        console.log('📐 Original content width:', popupContent.style.width, popupContent.offsetWidth);
                        popupContent.style.width = '700px';
                        popupContent.style.minWidth = '600px';
                        popupContent.style.maxWidth = '700px';
                        popupContent.style.margin = '0';
                        popupContent.style.padding = '0';
                        console.log('📐 New content width:', popupContent.style.width, popupContent.offsetWidth);
                    }
                    
                    if (popupContainer) {
                        console.log('📐 Original container width:', popupContainer.style.width, popupContainer.offsetWidth);
                        popupContainer.style.width = '600px';
                        popupContainer.style.minWidth = '600px';
                        popupContainer.style.wordWrap = 'break-word';
                        popupContainer.style.wordBreak = 'break-all';
                        popupContainer.style.overflowWrap = 'anywhere';
                        console.log('📐 New container width:', popupContainer.style.width, popupContainer.offsetWidth);
                        
                        // Force table styling
                        const table = popupContainer.querySelector('table');
                        if (table) {
                            console.log('📊 Table found, applying styling');
                            table.style.width = '100%';
                            table.style.tableLayout = 'fixed';
                            table.style.wordWrap = 'break-word';
                            table.style.wordBreak = 'break-all';
                            
                            const cells = table.querySelectorAll('td, th');
                            console.log('📊 Cells found:', cells.length);
                            cells.forEach(cell => {
                                cell.style.wordWrap = 'break-word';
                                cell.style.wordBreak = 'break-all';
                                cell.style.overflowWrap = 'anywhere';
                                cell.style.whiteSpace = 'pre-wrap';
                            });
                        } else {
                            console.log('❌ No table found in popup container');
                        }
                    } else {
                        console.log('❌ No popup container found');
                    }
                }, 150);
            }
            
            // Create layer select options
            const layerSelect = document.getElementById('layer-select');
            layers.forEach((layer, index) => {
                const option = document.createElement('option');
                option.value = layer.name;
                option.textContent = layer.title || layer.name;
                if (layer.name === 'eusm_2023_eunis2019_full') {
                    option.selected = true;
                }
                layerSelect.appendChild(option);
            });
            
            // Layer select change handler
            layerSelect.onchange = function(e) {
                selectLayer(e.target.value);
            };
            
            // Function to select layer
            function selectLayer(layerName) {
                // Update map
                currentLayer = layerName;
                updateWMSLayer(currentLayer, currentOpacity);
                // Update legend
                updateLegend(layerName);
            }
            
            // Opacity control
            const opacitySlider = document.getElementById('opacity');
            const opacityValue = document.getElementById('opacity-value');
            
            opacitySlider.oninput = function() {
                currentOpacity = this.value / 100;
                opacityValue.textContent = this.value + '%';
                if (wmsLayer) {
                    wmsLayer.setOpacity(currentOpacity);
                }
            };
            
            // Legend checkbox control
            const showLegendCheckbox = document.getElementById('show-legend');
            const legendContainer = document.getElementById('legend-container');
            const legendCloseBtn = document.getElementById('legend-close');
            
            showLegendCheckbox.onchange = function() {
                if (this.checked) {
                    // Show legend if it has content
                    const legendImg = document.getElementById('legend-image');
                    if (legendImg.src && legendImg.complete && legendImg.naturalWidth > 0) {
                        legendContainer.style.display = 'block';
                    }
                } else {
                    // Hide legend
                    legendContainer.style.display = 'none';
                }
            };
            
            // Legend close button
            legendCloseBtn.onclick = function() {
                legendContainer.style.display = 'none';
                showLegendCheckbox.checked = false;
            };
            
            // Make legend draggable
            let isDragging = false;
            let dragOffset = { x: 0, y: 0 };
            
            legendContainer.onmousedown = function(e) {
                // Don't drag if clicking on close button
                if (e.target === legendCloseBtn) return;
                
                isDragging = true;
                legendContainer.classList.add('dragging');
                
                // Disable map dragging
                map.dragging.disable();
                map.touchZoom.disable();
                map.doubleClickZoom.disable();
                map.scrollWheelZoom.disable();
                map.boxZoom.disable();
                map.keyboard.disable();
                
                const rect = legendContainer.getBoundingClientRect();
                dragOffset.x = e.clientX - rect.left;
                dragOffset.y = e.clientY - rect.top;
                
                e.preventDefault();
                e.stopPropagation();
            };
            
            document.onmousemove = function(e) {
                if (!isDragging) return;
                
                e.preventDefault();
                e.stopPropagation();
                
                const mapRect = map.getContainer().getBoundingClientRect();
                let x = e.clientX - mapRect.left - dragOffset.x;
                let y = e.clientY - mapRect.top - dragOffset.y;
                
                // Keep legend within map bounds
                const legendRect = legendContainer.getBoundingClientRect();
                x = Math.max(0, Math.min(x, mapRect.width - legendRect.width));
                y = Math.max(0, Math.min(y, mapRect.height - legendRect.height));
                
                legendContainer.style.left = x + 'px';
                legendContainer.style.top = y + 'px';
                legendContainer.style.right = 'auto';
                legendContainer.style.bottom = 'auto';
            };
            
            document.onmouseup = function() {
                if (isDragging) {
                    isDragging = false;
                    legendContainer.classList.remove('dragging');
                    
                    // Re-enable map interactions
                    map.dragging.enable();
                    map.touchZoom.enable();
                    map.doubleClickZoom.enable();
                    map.scrollWheelZoom.enable();
                    map.boxZoom.enable();
                    map.keyboard.enable();
                }
            };
            
            // Load initial layer
            updateWMSLayer(currentLayer, currentOpacity);
            updateLegend(currentLayer);
            
            // Load vector layer and zoom to its bounds
            loadVectorLayer();
            
            // Load BBT navigation buttons
            loadBBTNavigation();
            
            // Add scale control
            L.control.scale().addTo(map);
            
            // Add zoom control with custom position
            map.zoomControl.setPosition('topright');
            
            // Add map click handler to clear highlights when clicking on empty areas
            map.on('click', function(e) {
                // Only clear highlight if not clicking on a feature
                // The feature click will handle its own highlighting
                if (highlightedLayer && !e.layer) {
                    resetHighlight(highlightedLayer);
                    highlightedLayer = null;
                }
            });
        </script>
    </body>
    </html>
    """
    
    layers = get_available_layers()
    return render_template_string(html_template, layers=layers, WMS_BASE_URL=WMS_BASE_URL)

@app.route('/api/layers')
def api_layers():
    """API endpoint to get available layers"""
    return jsonify(get_available_layers())

@app.route('/api/capabilities')
def api_capabilities():
    """API endpoint to get WMS capabilities"""
    params = {
        'service': 'WMS',
        'version': WMS_VERSION,
        'request': 'GetCapabilities'
    }
    try:
        response = requests.get(WMS_BASE_URL, params=params, timeout=10)
        return response.content, 200, {'Content-Type': 'text/xml'}
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/legend/<path:layer_name>')
def api_legend(layer_name):
    """API endpoint to get legend for a specific layer"""
    legend_url = (
        f"{WMS_BASE_URL}?"
        f"service=WMS&version=1.1.0&request=GetLegendGraphic&"
        f"layer={layer_name}&format=image/png"
    )
    return jsonify({"legend_url": legend_url})

@app.route('/test')
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

@app.route('/www/<path:filename>')
def serve_static(filename):
    """Serve static files from www directory"""
    from flask import send_from_directory
    import os
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'www'), filename)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🌊 MARBEFES BBT Database Viewer")
    print("="*60)
    print("\nStarting Flask server...")
    print("Open http://localhost:5000 in your browser")
    print("\nAvailable endpoints:")
    print("  /              - Main interactive map viewer")
    print("  /test          - Test WMS connectivity")
    print("  /api/layers    - Get list of available layers (JSON)")
    print("  /api/capabilities - Get WMS capabilities (XML)")
    print("  /api/legend/<layer> - Get legend URL for a layer")
    print("\nPress Ctrl+C to stop the server")
    print("-"*60 + "\n")
    
    app.run(debug=True, port=5000)