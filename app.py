"""
MARBEFES BBT Database - Standalone Refactored Version
This works immediately without any dependencies on other files
"""

from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import requests
from xml.etree import ElementTree as ET
import os
import sys

# Try to import vector support if available
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
try:
    from emodnet_viewer.utils.vector_loader import (
        get_vector_layer_geojson,
        get_vector_layers_summary,
    )

    VECTOR_SUPPORT = True
except ImportError:
    VECTOR_SUPPORT = False
    print("Vector support disabled - optional dependency")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-key"
    CORS(app)

    # Configuration
    WMS_BASE_URL = (
        "https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms"
    )

    def get_wms_layers(base_url):
        """Fetch WMS layers"""
        try:
            response = requests.get(
                base_url,
                params={
                    "service": "WMS",
                    "version": "1.3.0",
                    "request": "GetCapabilities",
                },
                timeout=10,
            )

            if response.status_code == 200:
                root = ET.fromstring(response.content)
                for elem in root.iter():
                    if "}" in elem.tag:
                        elem.tag = elem.tag.split("}")[1]

                layers = []
                for layer in root.findall(".//Layer"):
                    name = layer.find("Name")
                    if name is not None and name.text:
                        title_elem = layer.find("Title")
                        abstract_elem = layer.find("Abstract")
                        layers.append(
                            {
                                "name": name.text,
                                "title": (
                                    title_elem.text
                                    if title_elem is not None
                                    else name.text
                                ),
                                "description": (
                                    abstract_elem.text
                                    if abstract_elem is not None
                                    else ""
                                ),
                            }
                        )
                print("\n[DEBUG] EMODNET layers found:")
                for layer in layers:
                    print(f"  - {layer['name']}: {layer['title']}")
                print(f"Total layers found: {len(layers)}\n")
                return layers[:50]
        except Exception:
            return []

    @app.route("/")
    def index():
        html = (
            """<!DOCTYPE html>
<html>
<head>
    <title>MARBEFES BBT - Refactored</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body { margin: 0; font-family: Arial; }
        #container { display: flex; height: 100vh; }
        #sidebar { width: 300px; padding: 20px; background: #f5f5f5; overflow-y: auto; }
        #map { flex: 1; position: relative; }
        h1 { color: #2c3e50; font-size: 20px; }
        .control { margin: 15px 0; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        select, input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; }
        .status { position: absolute; top: 10px; right: 10px; background: white; 
                 padding: 8px 15px; border-radius: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.2); z-index: 1000; }
    </style>
</head>
<body>
    <div id="container">
        <div id="sidebar">
            <h1>MARBEFES BBT Database</h1>
            <p style="color: #666; font-size: 12px;">Refactored Version</p>
            
            <div class="control">
                <label>WMS Layer:</label>
                <select id="layers"></select>
            </div>

            <div class="control">
                <label>Vector Layer:</label>
                <select id="vectorLayers">
                    <option value="">None</option>
                </select>
            </div>

            <div class="control">
                <label>Opacity: <span id="opval">70%</span></label>
                <input type="range" id="opacity" min="0" max="100" value="70">
            </div>

            <div class="control">
                <label>Base Map:</label>
                <select id="basemap">
                    <option value="osm">OpenStreetMap</option>
                    <option value="ocean" selected>Ocean</option>
                </select>
            </div>
        </div>
        
        <div id="map">
            <div class="status" id="status">Ready</div>
        </div>
    </div>
    
    <script>
        const map = L.map('map').setView([54.0, 10.0], 4);
        const baseMaps = {
            'osm': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'),
            'ocean': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}')
        };
        
        let currentBase = baseMaps['ocean'];
        currentBase.addTo(map);
        
        let wmsLayer = null;
        let vectorLayer = null;
        let currentOpacity = 0.7;

        // Load WMS layers
        fetch('/api/layers')
            .then(r => r.json())
            .then(data => {
                const sel = document.getElementById('layers');
                data.layers.forEach(l => {
                    const opt = document.createElement('option');
                    opt.value = l.name;
                    opt.textContent = l.title || l.name;
                    sel.appendChild(opt);
                });
                if (data.layers.length > 0) loadLayer(data.layers[0].name);
            });

        // Load vector layers
        fetch('/api/vector/layers')
            .then(r => r.json())
            .then(data => {
                const sel = document.getElementById('vectorLayers');
                data.layers.forEach(layer => {
                    const opt = document.createElement('option');
                    opt.value = layer.name;
                    opt.textContent = layer.title || layer.name;
                    sel.appendChild(opt);
                });
            })
            .catch(err => {
                console.log('Vector layers not available:', err);
            });

        function loadLayer(name) {
            if (wmsLayer) map.removeLayer(wmsLayer);
            document.getElementById('status').textContent = 'Loading...';
            
            wmsLayer = L.tileLayer.wms("""
            " + WMS_BASE_URL + "
            """, {
                layers: name,
                format: 'image/png',
                transparent: true,
                opacity: currentOpacity
            });
            wmsLayer.addTo(map);
            
            setTimeout(() => {
                document.getElementById('status').textContent = 'Ready';
            }, 500);
        }

        function loadVectorLayer(layerName) {
            if (vectorLayer) {
                map.removeLayer(vectorLayer);
                vectorLayer = null;
            }

            if (!layerName) return;

            document.getElementById('status').textContent = 'Loading vector layer...';

            fetch(`/api/vector/layer/${layerName}`)
                .then(r => r.json())
                .then(geojson => {
                    vectorLayer = L.geoJSON(geojson, {
                        style: function(feature) {
                            // Style polygons
                            if (feature.geometry.type === 'Polygon') {
                                return {
                                    fillColor: '#ff7800',
                                    weight: 2,
                                    opacity: 1,
                                    color: 'white',
                                    dashArray: '3',
                                    fillOpacity: 0.4
                                };
                            }
                            // Style lines
                            else if (feature.geometry.type === 'LineString') {
                                return {
                                    color: '#3388ff',
                                    weight: 4,
                                    opacity: 0.8
                                };
                            }
                            // Default style for other geometry types (Points, etc.)
                            else {
                                return {
                                    color: '#ff0000',
                                    weight: 3,
                                    opacity: 0.8,
                                    fillColor: '#ff0000',
                                    fillOpacity: 0.3
                                };
                            }
                        },
                        onEachFeature: function(feature, layer) {
                            // Add popup with feature properties
                            if (feature.properties) {
                                let popupContent = '<div style="max-width: 200px;">';
                                Object.keys(feature.properties).forEach(key => {
                                    popupContent += `<b>${key}:</b> ${feature.properties[key]}<br>`;
                                });
                                popupContent += '</div>';
                                layer.bindPopup(popupContent);
                            }
                        }
                    });

                    vectorLayer.addTo(map);

                    // Zoom to vector layer bounds
                    if (vectorLayer.getBounds().isValid()) {
                        map.fitBounds(vectorLayer.getBounds(), {padding: [20, 20]});
                    }

                    document.getElementById('status').textContent = 'Ready';
                })
                .catch(err => {
                    console.error('Error loading vector layer:', err);
                    document.getElementById('status').textContent = 'Error loading vector layer';
                });
        }

        document.getElementById('layers').onchange = e => loadLayer(e.target.value);
        document.getElementById('vectorLayers').onchange = e => loadVectorLayer(e.target.value);
        document.getElementById('opacity').oninput = function() {
            currentOpacity = this.value / 100;
            document.getElementById('opval').textContent = this.value + '%';
            if (wmsLayer) wmsLayer.setOpacity(currentOpacity);
        };
        document.getElementById('basemap').onchange = function(e) {
            map.removeLayer(currentBase);
            currentBase = baseMaps[e.target.value];
            currentBase.addTo(map);
        };
    </script>
</body>
</html>"""
        )
        return render_template_string(html, WMS_BASE_URL=WMS_BASE_URL)

    @app.route("/api/layers")
    def api_layers():
        layers = get_wms_layers(WMS_BASE_URL)
        return jsonify({"layers": layers})

    @app.route("/api/layers/debug")
    def api_layers_debug():
        layers = get_wms_layers(WMS_BASE_URL)
        # Return all details for inspection
        return jsonify({"layers": layers, "count": len(layers)})

    @app.route("/api/vector/layers")
    def api_vector_layers():
        if not VECTOR_SUPPORT:
            # Fallback to sample data when full vector support unavailable
            from sample_vector_data import get_sample_vector_layers
            return jsonify({"layers": get_sample_vector_layers()})
        return jsonify({"layers": get_vector_layers_summary()})

    @app.route("/api/vector/layer/<path:name>")
    def api_vector_layer(name):
        if not VECTOR_SUPPORT:
            # Fallback to sample data when full vector support unavailable
            from sample_vector_data import get_sample_geojson
            geojson = get_sample_geojson(name)
            return (
                jsonify(geojson)
                if geojson
                else (jsonify({"error": "Layer not found"}), 404)
            )
        geojson = get_vector_layer_geojson(name)
        return (
            jsonify(geojson)
            if geojson
            else (jsonify({"error": "Not found"}), 404)
        )

    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "vector": VECTOR_SUPPORT})

    @app.route("/debug")
    def debug():
        with open("debug_vectors.html", "r") as f:
            return f.read()

    return app


if __name__ == "__main__":
    app = create_app()
    print("\n" + "=" * 60)
    print("MARBEFES BBT - Standalone Refactored Version")
    print("=" * 60)
    print("Starting on http://localhost:5000")
    print("-" * 60)
    app.run(debug=True, port=5000)
