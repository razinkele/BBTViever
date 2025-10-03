# MARBEFES BBT Database - API Documentation

## Overview

The MARBEFES BBT Database provides a comprehensive RESTful API for accessing marine biodiversity and ecosystem data. The API supports both EMODnet WMS layers and local vector datasets with full metadata and geospatial operations.

**Base URL:** `http://localhost:5000/api`

**Content-Type:** `application/json`

**Authentication:** No authentication required for read-only operations

## Quick Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/layers` | GET | Get EMODnet WMS layers |
| `/api/all-layers` | GET | Get all available layers |
| `/api/vector/layers` | GET | Get vector layer metadata |
| `/api/vector/layer/<name>` | GET | Get vector layer GeoJSON |
| `/api/vector/bounds` | GET | Get vector layer bounds |
| `/api/capabilities` | GET | Get WMS capabilities XML |
| `/api/legend/<layer>` | GET | Get legend URL |

## Authentication

Currently, the API is read-only and does not require authentication. All endpoints are publicly accessible when the application is running.

## Rate Limiting

No rate limiting is currently implemented. However, external WMS services may have their own rate limits:
- EMODnet: Generally permissive for research use
- HELCOM: Standard WMS rate limits apply

## Error Handling

### Standard HTTP Status Codes

- `200 OK`: Request successful
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: External service unavailable

### Error Response Format

```json
{
  "error": "Error description",
  "reason": "Detailed reason (optional)",
  "code": "ERROR_CODE (optional)"
}
```

## Endpoints

### 1. EMODnet WMS Layers

#### Get Available WMS Layers
```http
GET /api/layers
```

**Description:** Returns a list of available EMODnet WMS layers with metadata.

**Response:**
```json
[
  {
    "name": "eusm2023_bio_full",
    "title": "EUSeaMap 2023 - European Biological Zones",
    "description": "Latest broad-scale biological habitat map for European seas"
  },
  {
    "name": "eusm2023_subs_full",
    "title": "EUSeaMap 2023 - European Substrate Types",
    "description": "Latest seabed substrate classification for European seas"
  },
  {
    "name": "eusm_2023_eunis2007_full",
    "title": "EUSeaMap 2023 - European EUNIS Classification",
    "description": "European habitat map using EUNIS 2007 classification system"
  }
]
```

**Example:**
```bash
curl -X GET "http://localhost:5000/api/layers" \
  -H "Accept: application/json"
```

---

### 2. All Available Layers

#### Get Combined Layer Information
```http
GET /api/all-layers
```

**Description:** Returns comprehensive information about all available layers including WMS, HELCOM, and vector layers.

**Response:**
```json
{
  "wms_layers": [
    {
      "name": "eusm2023_bio_full",
      "title": "EUSeaMap 2023 - European Biological Zones",
      "description": "Latest broad-scale biological habitat map"
    }
  ],
  "helcom_layers": [
    {
      "name": "Chemical_weapons_dumpsites_in_the_Baltic_Sea13404",
      "title": "Chemical weapons dumpsites in the Baltic Sea",
      "description": "Designated dumping areas for chemical weapons"
    }
  ],
  "vector_layers": [
    {
      "display_name": "Bbts - Merged",
      "geometry_type": "MultiPolygon",
      "feature_count": 6
    }
  ],
  "vector_support": true
}
```

**Example:**
```bash
curl -X GET "http://localhost:5000/api/all-layers" \
  -H "Accept: application/json"
```

---

### 3. Vector Layer Metadata

#### Get Vector Layer Information
```http
GET /api/vector/layers
```

**Description:** Returns metadata for all available vector layers including geometry information, bounds, and styling.

**Response:**
```json
{
  "count": 2,
  "layers": [
    {
      "bounds": [
        -4.049581511999923,
        39.60941008044542,
        22.753675067758007,
        79.21754600544492
      ],
      "category": "vector",
      "crs": "EPSG:4326",
      "display_name": "Bbts - Merged",
      "feature_count": 6,
      "geometry_type": "MultiPolygon",
      "layer_name": "merged",
      "source_file": "BBts.gpkg",
      "style": {
        "color": "#008B8B",
        "fillColor": "#20B2AA",
        "fillOpacity": 0.4,
        "opacity": 0.8,
        "weight": 2
      }
    },
    {
      "bounds": [
        -4.049581511999923,
        35.292039233442544,
        25.56007730516141,
        79.21754600544492
      ],
      "category": "vector",
      "crs": "EPSG:4326",
      "display_name": "Bbts - Broad Belt Transects",
      "feature_count": 9,
      "geometry_type": "MultiPolygon",
      "layer_name": "Broad Belt Transects",
      "source_file": "BBts.gpkg",
      "style": {
        "color": "#008B8B",
        "fillColor": "#20B2AA",
        "fillOpacity": 0.4,
        "opacity": 0.8,
        "weight": 2
      }
    }
  ]
}
```

**Error Response (Vector Support Disabled):**
```json
{
  "error": "Vector support not available",
  "reason": "Missing geospatial dependencies (geopandas, fiona)"
}
```

**Example:**
```bash
curl -X GET "http://localhost:5000/api/vector/layers" \
  -H "Accept: application/json"
```

---

### 4. Individual Vector Layer GeoJSON

#### Get Vector Layer Data
```http
GET /api/vector/layer/<path:layer_name>
```

**Description:** Returns the complete GeoJSON representation of a specific vector layer.

**Parameters:**
- `layer_name` (path): URL-encoded layer name (e.g., "Bbts%20-%20Merged")
- `simplify` (query, optional): Geometry simplification tolerance (float)

**Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "Name": "Archipelago",
        "ID": 1,
        "Area_km2": 1234.56
      },
      "geometry": {
        "type": "MultiPolygon",
        "coordinates": [...]
      }
    }
  ],
  "metadata": {
    "layer_name": "merged",
    "display_name": "Bbts - Merged",
    "geometry_type": "MultiPolygon",
    "feature_count": 6,
    "bounds": [
      -4.049581511999923,
      39.60941008044542,
      22.753675067758007,
      79.21754600544492
    ],
    "source_file": "BBts.gpkg",
    "style": {
      "color": "#008B8B",
      "fillColor": "#20B2AA",
      "fillOpacity": 0.4,
      "opacity": 0.8,
      "weight": 2
    }
  }
}
```

**Examples:**
```bash
# Get full resolution layer
curl -X GET "http://localhost:5000/api/vector/layer/Bbts%20-%20Merged" \
  -H "Accept: application/json"

# Get simplified geometry
curl -X GET "http://localhost:5000/api/vector/layer/Bbts%20-%20Merged?simplify=0.001" \
  -H "Accept: application/json"
```

---

### 5. Vector Layer Bounds

#### Get Combined Bounds Information
```http
GET /api/vector/bounds
```

**Description:** Returns the spatial bounds of all vector layers combined, useful for map extent calculations.

**Response:**
```json
{
  "center": [
    10.755247896580745,
    57.254792619443734
  ],
  "layer_count": 2,
  "overall_bounds": [
    -4.049581511999923,
    35.292039233442544,
    25.56007730516141,
    79.21754600544492
  ]
}
```

**Bounds Format:** `[min_longitude, min_latitude, max_longitude, max_latitude]`

**Example:**
```bash
curl -X GET "http://localhost:5000/api/vector/bounds" \
  -H "Accept: application/json"
```

---

### 6. WMS Capabilities

#### Get WMS Service Capabilities
```http
GET /api/capabilities
```

**Description:** Proxies the WMS GetCapabilities request from EMODnet service.

**Response:** XML document containing WMS capabilities

**Content-Type:** `text/xml`

**Example:**
```bash
curl -X GET "http://localhost:5000/api/capabilities" \
  -H "Accept: text/xml"
```

**Sample Response:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<WMS_Capabilities version="1.3.0">
  <Service>
    <Name>WMS</Name>
    <Title>EMODnet Seabed Habitats WMS</Title>
    ...
  </Service>
  <Capability>
    <Layer>
      <Name>eusm2023_bio_full</Name>
      <Title>EUSeaMap 2023 - European Biological Zones</Title>
      ...
    </Layer>
  </Capability>
</WMS_Capabilities>
```

---

### 7. Layer Legend

#### Get Legend URL
```http
GET /api/legend/<path:layer_name>
```

**Description:** Returns the WMS GetLegendGraphic URL for a specific layer.

**Parameters:**
- `layer_name` (path): Layer name

**Response:**
```json
{
  "legend_url": "https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms?service=WMS&version=1.1.0&request=GetLegendGraphic&layer=eusm2023_bio_full&format=image/png"
}
```

**Example:**
```bash
curl -X GET "http://localhost:5000/api/legend/eusm2023_bio_full" \
  -H "Accept: application/json"
```

## Data Models

### Layer Object
```json
{
  "name": "string",           // Layer identifier
  "title": "string",          // Human-readable title
  "description": "string"     // Layer description
}
```

### Vector Layer Object
```json
{
  "display_name": "string",     // Human-readable name
  "layer_name": "string",       // Internal layer name
  "geometry_type": "string",    // Geometry type (Polygon, MultiPolygon)
  "feature_count": "number",    // Number of features
  "bounds": "array",           // Spatial bounds [minX, minY, maxX, maxY]
  "crs": "string",             // Coordinate reference system
  "source_file": "string",     // Source filename
  "category": "string",        // Layer category
  "style": "object"           // Styling information
}
```

### Style Object
```json
{
  "color": "string",          // Stroke color (hex)
  "fillColor": "string",      // Fill color (hex)
  "fillOpacity": "number",    // Fill opacity (0-1)
  "opacity": "number",        // Stroke opacity (0-1)
  "weight": "number"          // Stroke width (pixels)
}
```

### Bounds Object
```json
{
  "overall_bounds": "array",  // Combined bounds [minX, minY, maxX, maxY]
  "center": "array",         // Center point [longitude, latitude]
  "layer_count": "number"    // Number of layers included
}
```

### GeoJSON Feature
```json
{
  "type": "Feature",
  "properties": "object",     // Feature attributes
  "geometry": "object"       // GeoJSON geometry
}
```

## Usage Examples

### JavaScript/Node.js

```javascript
// Fetch all layers
async function getAllLayers() {
  const response = await fetch('http://localhost:5000/api/all-layers');
  const data = await response.json();
  return data;
}

// Get vector layer GeoJSON
async function getVectorLayer(layerName) {
  const encodedName = encodeURIComponent(layerName);
  const response = await fetch(`http://localhost:5000/api/vector/layer/${encodedName}`);
  const geojson = await response.json();
  return geojson;
}

// Get layer bounds for map initialization
async function getMapBounds() {
  const response = await fetch('http://localhost:5000/api/vector/bounds');
  const bounds = await response.json();
  return bounds.overall_bounds;
}
```

### Python

```python
import requests
import json

# Base API URL
BASE_URL = "http://localhost:5000/api"

# Get all available layers
response = requests.get(f"{BASE_URL}/all-layers")
layers = response.json()

# Get specific vector layer
layer_name = "Bbts - Merged"
response = requests.get(f"{BASE_URL}/vector/layer/{layer_name}")
geojson = response.json()

# Get vector layer with simplification
params = {"simplify": 0.001}
response = requests.get(f"{BASE_URL}/vector/layer/{layer_name}", params=params)
simplified_geojson = response.json()

# Get layer bounds
response = requests.get(f"{BASE_URL}/vector/bounds")
bounds = response.json()
```

### cURL Commands

```bash
# Get all vector layers with metadata
curl -s "http://localhost:5000/api/vector/layers" | jq .

# Get specific layer GeoJSON
curl -s "http://localhost:5000/api/vector/layer/Bbts%20-%20Merged" | jq .

# Get WMS layers
curl -s "http://localhost:5000/api/layers" | jq .

# Get legend URL
curl -s "http://localhost:5000/api/legend/eusm2023_bio_full" | jq .

# Get bounds for map initialization
curl -s "http://localhost:5000/api/vector/bounds" | jq .overall_bounds
```

## Integration Examples

### Leaflet Map Integration

```javascript
// Initialize map with API data
async function initializeMap() {
  // Get bounds for initial view
  const boundsResponse = await fetch('/api/vector/bounds');
  const boundsData = await boundsResponse.json();

  // Create map
  const map = L.map('map').fitBounds([
    [boundsData.overall_bounds[1], boundsData.overall_bounds[0]],
    [boundsData.overall_bounds[3], boundsData.overall_bounds[2]]
  ]);

  // Add vector layers
  const layersResponse = await fetch('/api/vector/layers');
  const layersData = await layersResponse.json();

  for (const layerInfo of layersData.layers) {
    const geojsonResponse = await fetch(`/api/vector/layer/${encodeURIComponent(layerInfo.display_name)}`);
    const geojson = await geojsonResponse.json();

    L.geoJSON(geojson, {
      style: layerInfo.style
    }).addTo(map);
  }
}
```

### OpenLayers Integration

```javascript
// Create vector layer from API
async function createVectorLayer(layerName) {
  const response = await fetch(`/api/vector/layer/${encodeURIComponent(layerName)}`);
  const geojson = await response.json();

  const vectorSource = new ol.source.Vector({
    features: new ol.format.GeoJSON().readFeatures(geojson, {
      featureProjection: 'EPSG:3857'
    })
  });

  return new ol.layer.Vector({
    source: vectorSource,
    style: createStyleFromMetadata(geojson.metadata.style)
  });
}
```

## Error Scenarios

### Vector Support Disabled

When geopandas or other required dependencies are not installed:

```json
{
  "error": "Vector support not available",
  "reason": "Missing geospatial dependencies (geopandas, fiona)"
}
```

**HTTP Status:** `503 Service Unavailable`

### Layer Not Found

When requesting a non-existent vector layer:

```json
{
  "error": "Layer 'NonExistent Layer' not found"
}
```

**HTTP Status:** `404 Not Found`

### WMS Service Unavailable

When EMODnet WMS service is not accessible:

```json
{
  "error": "Connection timeout",
  "reason": "Unable to connect to EMODnet WMS service"
}
```

**HTTP Status:** `500 Internal Server Error`

## Performance Considerations

### Caching
- Vector layer data is cached in memory after first load
- WMS capabilities are cached for improved performance
- Consider implementing HTTP caching headers for production

### Optimization
- Use the `simplify` parameter for large vector datasets
- Request only needed layers to reduce response size
- Implement client-side caching for frequently accessed data

### Limitations
- Maximum geometry complexity depends on available memory
- WMS requests are subject to external service rate limits
- No built-in pagination for large feature collections

## Version History

- **v1.1.0**: Added vector layer support with GPKG processing
- **v1.0.0**: Initial release with EMODnet WMS integration
- **v0.9.0**: Beta release with basic mapping functionality

## Related Documentation

- [Main Documentation](../README.md)
- [Developer Guide](DEVELOPER.md)
- [Deployment Guide](DEPLOYMENT.md)
- [User Guide](USER_GUIDE.md)