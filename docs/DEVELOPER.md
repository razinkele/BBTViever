# MARBEFES BBT Database - Developer Guide

## Overview

This guide provides comprehensive information for developers working on the MARBEFES BBT Database application. It covers architecture, development setup, code organization, testing, and best practices.

## Table of Contents

- [Architecture](#architecture)
- [Development Setup](#development-setup)
- [Code Organization](#code-organization)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Frontend Development](#frontend-development)
- [Backend Development](#backend-development)
- [Database and Data Management](#database-and-data-management)
- [Performance Optimization](#performance-optimization)
- [Security Considerations](#security-considerations)
- [Debugging](#debugging)
- [Contributing](#contributing)

## Architecture

### System Overview

The MARBEFES BBT Database follows a modern web application architecture with clear separation between frontend and backend components.

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Web Browser   │◄──►│  Flask Web App   │◄──►│  EMODnet WMS    │
│                 │    │                  │    │  Services       │
│ • Leaflet Maps  │    │ • REST API       │    │                 │
│ • PyDeck 3D     │    │ • Template Render│    │ • GetMap        │
│ • Interactive   │    │ • Vector Loader  │    │ • Capabilities  │
│   Controls      │    │ • Error Handling │    │ • Legends       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Local Vector   │
                       │     Data        │
                       │                 │
                       │ • GPKG Files    │
                       │ • GeoPandas     │
                       │ • Spatial Ops   │
                       └─────────────────┘
```

### Technology Stack

**Backend:**
- **Flask 3.1.2**: Web framework with template rendering
- **GeoPandas 1.1.1**: Geospatial data processing
- **Requests 2.32.3**: HTTP client for WMS integration
- **Fiona 1.10.1**: GPKG file reading
- **PyProj 3.7.1**: Coordinate system transformations

**Frontend:**
- **Leaflet 1.9.4**: Interactive mapping library
- **Deck.gl 8.9.0**: 3D visualization framework
- **Vanilla JavaScript**: No additional frameworks
- **CSS3**: Modern styling with flexbox and gradients

**Data Sources:**
- **EMODnet WMS**: External web map services
- **HELCOM WMS**: Baltic Sea environmental data
- **GPKG Files**: Local vector datasets

### Application Architecture

#### Flask Application Structure (`app.py`)

```python
# Core Components
app = Flask(__name__)                    # Flask application instance
VECTOR_SUPPORT = check_dependencies()    # Feature flag for vector support

# Configuration
WMS_BASE_URL = "https://..."            # EMODnet WMS endpoint
HELCOM_WMS_BASE_URL = "https://..."     # HELCOM WMS endpoint
EMODNET_LAYERS = [...]                  # Predefined layer list

# Route Handlers
@app.route("/")                         # Main web interface
@app.route("/api/layers")              # WMS layer metadata
@app.route("/api/vector/layers")       # Vector layer metadata
@app.route("/api/vector/layer/<name>") # Individual layer GeoJSON

# Utility Functions
get_available_layers()                  # WMS capabilities parsing
get_all_layers()                       # Combined layer information
load_vector_data_on_startup()          # GPKG processing
```

#### Template Structure (`templates/index.html`)

```html
<!-- HTML Structure -->
<div id="container">
    <div id="sidebar">...</div>         <!-- Controls and layer selection -->
    <div id="map">...</div>             <!-- Leaflet map container -->
    <div id="pydeck-overlay">...</div>  <!-- 3D visualization overlay -->
</div>

<!-- JavaScript Modules -->
<script>
    // Map initialization and controls
    var map = L.map('map')...

    // Layer management
    function loadVectorLayer(name)...
    function updateWMSLayer(name)...

    // BBT navigation
    function zoomToBBTArea(area)...

    // 3D visualization
    function initializePyDeck()...
</script>
```

#### Vector Processing (`src/emodnet_viewer/utils/vector_loader.py`)

```python
class VectorLayerLoader:
    def __init__(self):
        self.loaded_layers = []
        self.data_directory = Path("data/vector")

    def load_all_vector_layers(self):
        # GPKG file discovery and processing

    def get_vector_layer_geojson(self, layer_name):
        # GeoJSON conversion with CRS normalization

    def create_bounds_summary(self):
        # Spatial bounds calculation
```

## Development Setup

### Prerequisites

**Required:**
- Python 3.9+ with pip or conda
- Git for version control
- Modern web browser for testing

**Recommended:**
- VSCode or PyCharm for IDE
- Postman for API testing
- QGIS for geospatial data inspection

### Environment Setup

#### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd EMODNET_PyDeck

# Create virtual environment
conda create -n marbefes-dev python=3.9
conda activate marbefes-dev

# Or with pip
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

#### 2. Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt

# Verify geospatial dependencies
python -c "import geopandas; print('GeoPandas OK')"
python -c "import fiona; print('Fiona OK')"
```

#### 3. Development Configuration

Create `.env` file for local development:
```bash
FLASK_ENV=development
FLASK_DEBUG=1
FLASK_APP=app.py
LOG_LEVEL=DEBUG
```

#### 4. IDE Configuration

**VSCode Settings (`.vscode/settings.json`):**
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.provider": "isort"
}
```

**PyCharm Configuration:**
- Interpreter: Select virtual environment Python
- Code Style: Black formatter
- Inspections: Enable flake8
- File Watchers: Black, isort, mypy

## Code Organization

### Project Structure

```
EMODNET_PyDeck/
├── app.py                      # Main Flask application (468 lines)
├── templates/
│   └── index.html             # Web interface template (93KB)
├── src/                       # Source code modules
│   └── emodnet_viewer/
│       └── utils/
│           ├── __init__.py
│           ├── vector_loader.py      # GPKG processing
│           ├── logging_config.py     # Logging setup
│           └── monitoring.py         # Performance monitoring
├── data/                      # Data directory
│   ├── vector/               # GPKG files
│   │   └── BBts.gpkg        # Main dataset (3.5MB)
│   └── examples/            # Sample data
├── tests/                    # Test suite
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── conftest.py         # Test configuration
├── scripts/                 # Utility scripts
│   ├── dev_server.py       # Development server
│   ├── create_sample_data.py # Data generation
│   └── run_tests.py        # Test runner
├── config/                  # Configuration files
│   └── config.py           # Application configuration
├── docs/                   # Documentation
│   ├── API.md              # API documentation
│   ├── DEVELOPER.md        # This file
│   └── USER_GUIDE.md       # User documentation
├── LOGO/                   # Project branding
│   └── marbefes_02.png    # Main logo
├── requirements.txt        # Production dependencies
├── requirements-dev.txt    # Development dependencies
├── pytest.ini            # Test configuration
├── .flake8               # Linting configuration
├── pyproject.toml        # Project metadata
└── CLAUDE.md             # AI assistant instructions
```

### Code Style Guidelines

#### Python Code Style

**Follow PEP 8 with Black formatting:**
```python
# Good: Clear function names and docstrings
def get_vector_layer_geojson(layer_name: str, simplify: Optional[float] = None) -> Dict[str, Any]:
    """
    Get GeoJSON representation of a vector layer.

    Args:
        layer_name: Name of the layer to retrieve
        simplify: Geometry simplification tolerance

    Returns:
        GeoJSON dictionary with metadata
    """

# Good: Type hints and error handling
try:
    gdf = gpd.read_file(layer.file_path, layer=layer.layer_name)
    if gdf.crs and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs("EPSG:4326")
except Exception as e:
    logger.error(f"Error reading layer {layer_name}: {e}")
    raise
```

**File Organization:**
- One class per file when possible
- Group related functions into modules
- Use `__init__.py` for package exports
- Keep functions under 50 lines when possible

#### JavaScript Code Style

**Use modern ES6+ features:**
```javascript
// Good: Arrow functions and const/let
const loadVectorLayer = async (layerName) => {
    try {
        const response = await fetch(`/api/vector/layer/${encodeURIComponent(layerName)}`);
        const geojson = await response.json();
        return geojson;
    } catch (error) {
        console.error('Error loading vector layer:', error);
        throw error;
    }
};

// Good: Destructuring and template literals
const { features, metadata } = geojson;
const statusMessage = `Loaded ${features.length} features from ${metadata.layer_name}`;
```

#### CSS Organization

**Use BEM methodology for class names:**
```css
/* Block */
.bbt-nav-section {
    margin-bottom: 20px;
}

/* Element */
.bbt-nav-section__buttons {
    display: flex;
    gap: 6px;
}

/* Modifier */
.bbt-nav-btn--active {
    background: linear-gradient(135deg, #40E0D0 0%, #20B2AA 100%);
}
```

### Import Standards

**Python imports:**
```python
# Standard library imports
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Third-party imports
import requests
from flask import Flask, jsonify, render_template
import geopandas as gpd
from xml.etree import ElementTree as ET

# Local imports
from emodnet_viewer.utils.vector_loader import VectorLayerLoader
from emodnet_viewer.utils.logging_config import get_logger
```

## Development Workflow

### Git Workflow

#### Branch Strategy

```bash
# Main branch for production
main

# Development branch for integration
develop

# Feature branches for new development
feature/vector-layer-optimization
feature/api-caching
feature/3d-visualization-improvements

# Hotfix branches for urgent fixes
hotfix/wms-timeout-fix
```

#### Commit Message Format

```
<type>(<scope>): <description>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Build/tooling changes

**Examples:**
```bash
feat(vector): add geometry simplification parameter to API

Add optional simplify parameter to vector layer endpoint for
performance optimization with large datasets.

Closes #123

fix(wms): handle timeout errors gracefully

Add proper error handling for WMS service timeouts with
fallback to cached layer list.

Fixes #456
```

### Development Commands

#### Development Server

```bash
# Standard development server
python app.py

# With debug mode
FLASK_DEBUG=1 python app.py

# With specific environment
conda activate shiny && python app.py

# Using development script
python scripts/dev_server.py --port 5001 --debug
```

#### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy src/

# Run all quality checks
python scripts/quality_check.py
```

#### Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with debugging
pytest -s -v tests/test_vector_loader.py::test_load_all_layers
```

### Code Review Guidelines

#### Pull Request Checklist

- [ ] Code follows style guidelines (Black, flake8)
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] API changes are documented
- [ ] Performance impact is considered
- [ ] Security implications are reviewed
- [ ] Browser compatibility is tested

#### Review Criteria

**Code Quality:**
- Clear, self-documenting code
- Appropriate error handling
- Efficient algorithms and data structures
- Memory usage considerations

**Testing:**
- Unit tests for new functions
- Integration tests for API changes
- Test coverage above 80%
- Edge cases are covered

**Documentation:**
- API changes documented
- Code comments for complex logic
- User-facing changes in README
- Developer notes for architecture changes

## Testing

### Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── unit/                      # Unit tests
│   ├── test_vector_loader.py  # Vector processing tests
│   ├── test_wms_service.py    # WMS integration tests
│   └── test_config.py         # Configuration tests
└── integration/               # Integration tests
    ├── test_api_endpoints.py  # API endpoint tests
    ├── test_vector_api.py     # Vector API integration
    └── test_app_startup.py    # Application startup tests
```

### Test Categories

#### Unit Tests

**Vector Layer Processing:**
```python
def test_load_vector_layers(vector_loader):
    """Test vector layer loading from GPKG files."""
    layers = vector_loader.load_all_vector_layers()

    assert len(layers) == 2
    assert layers[0].display_name == "Bbts - Merged"
    assert layers[0].geometry_type == "MultiPolygon"
    assert layers[0].feature_count == 6

def test_geojson_conversion(vector_loader, sample_layer):
    """Test GeoJSON conversion with CRS normalization."""
    geojson = vector_loader.get_vector_layer_geojson(sample_layer)

    assert geojson["type"] == "FeatureCollection"
    assert "features" in geojson
    assert "metadata" in geojson
    assert geojson["metadata"]["crs"] == "EPSG:4326"
```

**WMS Integration:**
```python
def test_get_available_layers():
    """Test WMS capabilities parsing."""
    layers = get_available_layers()

    assert isinstance(layers, list)
    assert len(layers) > 0
    assert all("name" in layer for layer in layers)

@pytest.mark.external
def test_wms_connectivity():
    """Test external WMS service connectivity."""
    response = requests.get(WMS_BASE_URL, timeout=10)
    assert response.status_code == 200
```

#### Integration Tests

**API Endpoints:**
```python
def test_vector_layers_endpoint(client):
    """Test vector layers API endpoint."""
    response = client.get('/api/vector/layers')

    assert response.status_code == 200
    data = response.get_json()
    assert "layers" in data
    assert "count" in data

def test_vector_layer_geojson(client):
    """Test individual vector layer GeoJSON endpoint."""
    layer_name = "Bbts - Merged"
    response = client.get(f'/api/vector/layer/{layer_name}')

    assert response.status_code == 200
    geojson = response.get_json()
    assert geojson["type"] == "FeatureCollection"
```

### Test Fixtures

**Pytest Configuration (`conftest.py`):**
```python
import pytest
from app import app
from src.emodnet_viewer.utils.vector_loader import VectorLayerLoader

@pytest.fixture
def client():
    """Flask test client."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def vector_loader():
    """Vector loader instance for testing."""
    return VectorLayerLoader()

@pytest.fixture
def sample_geojson():
    """Sample GeoJSON data for testing."""
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"name": "Test Area"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]]
                }
            }
        ]
    }
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage reporting
pytest --cov=src --cov-report=html --cov-report=term

# Run specific test file
pytest tests/unit/test_vector_loader.py

# Run with markers
pytest -m "not external"  # Skip external service tests
pytest -m "slow"          # Run only slow tests

# Run with debugging
pytest -s -v --tb=short

# Run in parallel
pytest -n 4  # Requires pytest-xdist
```

## Frontend Development

### JavaScript Architecture

#### Module Organization

```javascript
// Map initialization and core functionality
const MapModule = {
    init: function() {
        this.map = L.map('map').setView([54.0, 10.0], 4);
        this.initializeBaseMaps();
        this.setupEventHandlers();
    },

    initializeBaseMaps: function() {
        // Base map configuration
    },

    setupEventHandlers: function() {
        // Event binding
    }
};

// Layer management
const LayerManager = {
    loadVectorLayer: async function(layerName) {
        // Vector layer loading logic
    },

    updateWMSLayer: function(layerName, opacity) {
        // WMS layer management
    }
};

// BBT navigation functionality
const BBTNavigation = {
    zoomToBBTArea: function(areaName) {
        // Area-specific zoom logic
    }
};
```

#### API Integration Patterns

```javascript
// Centralized API client
const ApiClient = {
    baseUrl: '/api',

    async get(endpoint) {
        try {
            const response = await fetch(`${this.baseUrl}${endpoint}`);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },

    async getVectorLayers() {
        return this.get('/vector/layers');
    },

    async getVectorLayer(name, options = {}) {
        const params = new URLSearchParams(options);
        return this.get(`/vector/layer/${encodeURIComponent(name)}?${params}`);
    }
};

// Usage in application
async function loadAvailableLayers() {
    try {
        const layerData = await ApiClient.getVectorLayers();
        updateLayerUI(layerData.layers);
    } catch (error) {
        showErrorMessage('Failed to load layers');
    }
}
```

### CSS Organization

#### Component-Based Styling

```css
/* Base styles */
:root {
    --primary-color: #20B2AA;
    --secondary-color: #008B8B;
    --background-color: #f0f0f0;
    --text-color: #2F4F4F;
    --border-radius: 8px;
    --shadow: 0 2px 10px rgba(0,0,0,0.1);
}

/* Layout components */
.container {
    display: flex;
    height: 100vh;
}

.sidebar {
    width: 320px;
    background: white;
    padding: 20px;
    box-shadow: var(--shadow);
    overflow-y: auto;
}

/* Interactive components */
.bbt-nav-btn {
    background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
    color: white;
    border: none;
    padding: 6px 10px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.3s ease;
}

.bbt-nav-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(102, 126, 234, 0.3);
}
```

#### Responsive Design

```css
/* Mobile-first approach */
.sidebar {
    width: 100%;
    height: auto;
    max-height: 40vh;
    overflow-y: auto;
}

.map-container {
    height: 60vh;
}

/* Tablet and up */
@media (min-width: 768px) {
    .container {
        flex-direction: row;
    }

    .sidebar {
        width: 320px;
        height: 100vh;
        max-height: none;
    }

    .map-container {
        flex: 1;
        height: 100vh;
    }
}

/* Desktop */
@media (min-width: 1024px) {
    .sidebar {
        width: 380px;
    }
}
```

### 3D Visualization (PyDeck)

#### Deck.gl Integration

```javascript
// Initialize PyDeck with proper error handling
function initializePyDeck() {
    if (!window.deck) {
        console.warn('Deck.gl not loaded');
        return;
    }

    try {
        deckInstance = new deck.Deck({
            container: 'pydeck-overlay',
            initialViewState: getInitialViewState(),
            controller: false,
            layers: [],
            onError: handleDeckError
        });

        // Sync with Leaflet
        map.on('moveend', syncDeckWithLeaflet);
        map.on('zoomend', syncDeckWithLeaflet);
    } catch (error) {
        console.error('Failed to initialize PyDeck:', error);
    }
}

// Layer creation with proper data validation
function createPyDeckLayer(layerType, data, options) {
    if (!data || !data.length) {
        console.warn('No data provided for PyDeck layer');
        return null;
    }

    switch (layerType) {
        case 'hexagon':
            return new deck.HexagonLayer({
                id: 'hexagon-layer',
                data: data,
                getPosition: d => d.position,
                getElevationWeight: d => d.biomass,
                ...options
            });

        default:
            console.warn(`Unknown layer type: ${layerType}`);
            return null;
    }
}
```

## Backend Development

### Flask Application Structure

#### Route Organization

```python
# Main application routes
@app.route("/")
def index():
    """Main page with map viewer"""
    all_layers = get_all_layers()
    return render_template('index.html', **all_layers)

@app.route("/logo/<filename>")
def serve_logo(filename):
    """Serve logo files from LOGO directory"""
    return send_from_directory("LOGO", filename)

# API routes with proper error handling
@app.route("/api/layers")
def api_layers():
    """API endpoint to get available WMS layers"""
    try:
        return jsonify(get_available_layers())
    except Exception as e:
        logger.error(f"Error fetching WMS layers: {e}")
        return jsonify({"error": "Failed to fetch layers"}), 500

@app.route("/api/vector/layers")
def api_vector_layers():
    """API endpoint to get available vector layers"""
    if not VECTOR_SUPPORT:
        return jsonify({
            "error": "Vector support not available",
            "reason": "Missing geospatial dependencies"
        }), 503

    try:
        vector_layers = get_vector_layers_summary()
        return jsonify({"layers": vector_layers, "count": len(vector_layers)})
    except Exception as e:
        logger.error(f"Error fetching vector layers: {e}")
        return jsonify({"error": str(e)}), 500
```

#### Error Handling Patterns

```python
from functools import wraps
import logging

logger = logging.getLogger(__name__)

def handle_api_errors(f):
    """Decorator for consistent API error handling."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValueError as e:
            logger.warning(f"Bad request in {f.__name__}: {e}")
            return jsonify({"error": "Invalid request parameters"}), 400
        except FileNotFoundError as e:
            logger.error(f"Resource not found in {f.__name__}: {e}")
            return jsonify({"error": "Resource not found"}), 404
        except Exception as e:
            logger.error(f"Unexpected error in {f.__name__}: {e}")
            return jsonify({"error": "Internal server error"}), 500
    return decorated_function

# Usage
@app.route("/api/vector/layer/<path:layer_name>")
@handle_api_errors
def api_vector_layer_geojson(layer_name):
    """Get GeoJSON for a specific vector layer."""
    geojson = get_vector_layer_geojson(layer_name)
    if not geojson:
        raise FileNotFoundError(f"Layer '{layer_name}' not found")
    return jsonify(geojson)
```

### Vector Data Processing

#### GeoPandas Integration

```python
class VectorLayerLoader:
    def __init__(self, data_directory: str = "data/vector"):
        self.data_directory = Path(data_directory)
        self.loaded_layers: List[VectorLayer] = []
        self.logger = get_logger(__name__)

    def load_vector_layer(self, gpkg_path: Path, layer_name: str) -> Optional[VectorLayer]:
        """Load a single vector layer from GPKG file."""
        try:
            # Read layer with error handling
            gdf = gpd.read_file(gpkg_path, layer=layer_name)

            if gdf.empty:
                self.logger.warning(f"Layer {layer_name} is empty")
                return None

            # Normalize CRS to WGS84
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs("EPSG:4326")

            # Calculate metadata
            bounds = gdf.total_bounds
            geometry_type = self._determine_geometry_type(gdf)

            return VectorLayer(
                file_path=str(gpkg_path),
                layer_name=layer_name,
                display_name=self._create_display_name(layer_name),
                geometry_type=geometry_type,
                feature_count=len(gdf),
                bounds=tuple(bounds),
                crs="EPSG:4326",
                source_file=gpkg_path.name,
                style=self._get_default_style()
            )

        except Exception as e:
            self.logger.error(f"Error loading layer {layer_name}: {e}")
            return None

    def get_vector_layer_geojson(self, layer: VectorLayer, simplify_tolerance: Optional[float] = None) -> Dict[str, Any]:
        """Convert vector layer to GeoJSON with optional simplification."""
        try:
            gdf = gpd.read_file(layer.file_path, layer=layer.layer_name)

            # Ensure WGS84
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs("EPSG:4326")

            # Simplify geometries for performance
            if simplify_tolerance and simplify_tolerance > 0:
                gdf["geometry"] = gdf.geometry.simplify(tolerance=simplify_tolerance)

            # Convert to GeoJSON
            geojson = json.loads(gdf.to_json())

            # Add metadata
            geojson["metadata"] = asdict(layer)
            geojson["metadata"].pop("file_path", None)  # Remove for security

            return geojson

        except Exception as e:
            self.logger.error(f"Error creating GeoJSON for layer {layer.display_name}: {e}")
            raise
```

### Configuration Management

```python
import os
from pathlib import Path
from typing import Optional

class Config:
    """Application configuration management."""

    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes')

    # WMS service URLs
    WMS_BASE_URL = os.environ.get('WMS_BASE_URL',
                                 'https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms')
    HELCOM_WMS_BASE_URL = os.environ.get('HELCOM_WMS_BASE_URL',
                                        'https://maps.helcom.fi/arcgis/services/MADS/Pressures/MapServer/WMSServer')

    # Data directories
    VECTOR_DATA_DIR = Path(os.environ.get('VECTOR_DATA_DIR', 'data/vector'))

    # Performance settings
    WMS_TIMEOUT = int(os.environ.get('WMS_TIMEOUT', '10'))
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', '300'))

    @classmethod
    def validate(cls) -> bool:
        """Validate configuration settings."""
        if not cls.VECTOR_DATA_DIR.exists():
            print(f"Warning: Vector data directory {cls.VECTOR_DATA_DIR} does not exist")
            return False
        return True

# Usage in application
config = Config()
if not config.validate():
    print("Configuration validation failed")
```

## Database and Data Management

### Vector Data Requirements

#### GPKG File Structure

```sql
-- Example GPKG structure for BBT data
CREATE TABLE "Broad Belt Transects" (
    fid INTEGER PRIMARY KEY,
    Name TEXT,                    -- BBT area name
    ID INTEGER,                   -- Unique identifier
    Area_km2 REAL,               -- Area in square kilometers
    Depth_min REAL,              -- Minimum depth
    Depth_max REAL,              -- Maximum depth
    Habitat_type TEXT,           -- Primary habitat classification
    geom MULTIPOLYGON            -- Geometry in WGS84
);

-- Spatial index for performance
CREATE INDEX "Broad Belt Transects_geom_idx" ON "Broad Belt Transects"
USING rtree(geom);
```

#### Data Validation

```python
def validate_gpkg_file(gpkg_path: Path) -> Dict[str, Any]:
    """Validate GPKG file structure and content."""
    validation_result = {
        "valid": True,
        "errors": [],
        "warnings": [],
        "layers": []
    }

    try:
        # Check file exists and is readable
        if not gpkg_path.exists():
            validation_result["errors"].append("File does not exist")
            validation_result["valid"] = False
            return validation_result

        # Get layer list
        layers = fiona.listlayers(gpkg_path)
        validation_result["layers"] = layers

        for layer_name in layers:
            # Validate each layer
            try:
                gdf = gpd.read_file(gpkg_path, layer=layer_name)

                # Check for empty layers
                if gdf.empty:
                    validation_result["warnings"].append(f"Layer '{layer_name}' is empty")

                # Check geometry validity
                invalid_geoms = gdf[~gdf.geometry.is_valid]
                if not invalid_geoms.empty:
                    validation_result["errors"].append(
                        f"Layer '{layer_name}' has {len(invalid_geoms)} invalid geometries"
                    )

                # Check CRS
                if gdf.crs is None:
                    validation_result["warnings"].append(
                        f"Layer '{layer_name}' has no CRS defined"
                    )

            except Exception as e:
                validation_result["errors"].append(f"Error reading layer '{layer_name}': {e}")

        if validation_result["errors"]:
            validation_result["valid"] = False

    except Exception as e:
        validation_result["errors"].append(f"Error reading GPKG file: {e}")
        validation_result["valid"] = False

    return validation_result
```

### Data Processing Pipeline

```python
class DataProcessor:
    """Handle data processing and transformation operations."""

    def __init__(self, logger=None):
        self.logger = logger or get_logger(__name__)

    def process_gpkg_file(self, gpkg_path: Path) -> List[VectorLayer]:
        """Process a GPKG file and return vector layers."""
        layers = []

        try:
            # Validate file first
            validation = validate_gpkg_file(gpkg_path)
            if not validation["valid"]:
                self.logger.error(f"GPKG validation failed: {validation['errors']}")
                return layers

            # Process each layer
            for layer_name in validation["layers"]:
                layer = self._process_layer(gpkg_path, layer_name)
                if layer:
                    layers.append(layer)

        except Exception as e:
            self.logger.error(f"Error processing GPKG file {gpkg_path}: {e}")

        return layers

    def _process_layer(self, gpkg_path: Path, layer_name: str) -> Optional[VectorLayer]:
        """Process individual layer with transformations."""
        try:
            gdf = gpd.read_file(gpkg_path, layer=layer_name)

            # Apply transformations
            gdf = self._normalize_crs(gdf)
            gdf = self._clean_geometries(gdf)
            gdf = self._calculate_attributes(gdf)

            # Create layer metadata
            return self._create_layer_metadata(gdf, gpkg_path, layer_name)

        except Exception as e:
            self.logger.error(f"Error processing layer {layer_name}: {e}")
            return None

    def _normalize_crs(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Normalize CRS to WGS84."""
        if gdf.crs and gdf.crs.to_epsg() != 4326:
            gdf = gdf.to_crs("EPSG:4326")
        elif gdf.crs is None:
            self.logger.warning("No CRS defined, assuming WGS84")
            gdf.set_crs("EPSG:4326", inplace=True)
        return gdf

    def _clean_geometries(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Clean and validate geometries."""
        # Remove invalid geometries
        valid_mask = gdf.geometry.is_valid
        if not valid_mask.all():
            invalid_count = (~valid_mask).sum()
            self.logger.warning(f"Removing {invalid_count} invalid geometries")
            gdf = gdf[valid_mask].copy()

        # Fix minor topology issues
        gdf["geometry"] = gdf.geometry.buffer(0)

        return gdf

    def _calculate_attributes(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Calculate additional attributes."""
        # Calculate area in square kilometers
        if gdf.crs.to_epsg() == 4326:
            # Convert to appropriate projected CRS for area calculation
            utm_crs = gdf.estimate_utm_crs()
            gdf_projected = gdf.to_crs(utm_crs)
            area_m2 = gdf_projected.geometry.area
            gdf["Area_km2"] = area_m2 / 1000000

        return gdf
```

## Performance Optimization

### Backend Optimization

#### Caching Strategies

```python
from functools import lru_cache
from typing import Dict, Any
import time

class CacheManager:
    """Manage application-level caching."""

    def __init__(self):
        self._cache = {}
        self._timestamps = {}
        self.default_ttl = 300  # 5 minutes

    def get(self, key: str, default=None):
        """Get cached value if still valid."""
        if key in self._cache:
            if time.time() - self._timestamps[key] < self.default_ttl:
                return self._cache[key]
            else:
                # Remove expired entry
                del self._cache[key]
                del self._timestamps[key]
        return default

    def set(self, key: str, value: Any, ttl: int = None):
        """Set cached value with TTL."""
        self._cache[key] = value
        self._timestamps[key] = time.time()

# Global cache instance
cache = CacheManager()

# Cached functions
@lru_cache(maxsize=128)
def get_wms_capabilities():
    """Cache WMS capabilities response."""
    try:
        response = requests.get(WMS_BASE_URL, params={
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetCapabilities'
        }, timeout=10)
        return response.text
    except Exception as e:
        logger.error(f"Error fetching WMS capabilities: {e}")
        return None

def get_available_layers():
    """Get WMS layers with caching."""
    cache_key = "wms_layers"
    cached_layers = cache.get(cache_key)

    if cached_layers is not None:
        return cached_layers

    # Fetch fresh data
    layers = parse_wms_capabilities()
    cache.set(cache_key, layers, ttl=600)  # Cache for 10 minutes
    return layers
```

#### Database Query Optimization

```python
def optimize_vector_queries():
    """Optimize vector data loading and processing."""

    # Use spatial indexing for GPKG files
    def create_spatial_index(gpkg_path: Path, layer_name: str):
        """Create spatial index for improved query performance."""
        import sqlite3

        conn = sqlite3.connect(gpkg_path)
        try:
            # Create R-tree spatial index
            conn.execute(f"""
                CREATE VIRTUAL TABLE IF NOT EXISTS "rtree_{layer_name}_geom"
                USING rtree(id, minx, maxx, miny, maxy)
            """)

            # Populate spatial index
            conn.execute(f"""
                INSERT OR REPLACE INTO "rtree_{layer_name}_geom"
                SELECT fid, MbrMinX(geom), MbrMaxX(geom), MbrMinY(geom), MbrMaxY(geom)
                FROM "{layer_name}"
                WHERE geom IS NOT NULL
            """)

            conn.commit()
        finally:
            conn.close()

    # Optimize GeoPandas operations
    def load_layer_optimized(gpkg_path: Path, layer_name: str, bbox=None):
        """Load layer with optimization options."""
        kwargs = {}

        # Use bounding box filter if provided
        if bbox:
            kwargs['bbox'] = bbox

        # Read only necessary columns
        kwargs['columns'] = ['Name', 'ID', 'Area_km2', 'geometry']

        return gpd.read_file(gpkg_path, layer=layer_name, **kwargs)
```

### Frontend Optimization

#### Leaflet Performance

```javascript
// Optimize marker clustering for large datasets
function createOptimizedMarkerLayer(features) {
    const markerClusterGroup = L.markerClusterGroup({
        chunkedLoading: true,
        chunkProgress: updateProgressBar,
        maxClusterRadius: 80,
        spiderfyOnMaxZoom: true,
        showCoverageOnHover: false
    });

    // Add markers in chunks to prevent UI blocking
    const chunkSize = 1000;
    let index = 0;

    function addChunk() {
        const chunk = features.slice(index, index + chunkSize);
        const markers = chunk.map(feature => {
            return L.marker([feature.lat, feature.lng])
                .bindPopup(feature.properties.name);
        });

        markerClusterGroup.addLayers(markers);
        index += chunkSize;

        if (index < features.length) {
            // Use requestIdleCallback for better performance
            if (window.requestIdleCallback) {
                requestIdleCallback(addChunk);
            } else {
                setTimeout(addChunk, 10);
            }
        }
    }

    addChunk();
    return markerClusterGroup;
}

// Optimize GeoJSON rendering for large datasets
function addOptimizedGeoJSON(geojson, map) {
    const geoJsonLayer = L.geoJSON(geojson, {
        // Use canvas renderer for better performance
        renderer: L.canvas({ padding: 0.5 }),

        // Simplify geometries at runtime
        style: function(feature) {
            return {
                fillColor: '#20B2AA',
                weight: 2,
                opacity: 1,
                color: 'white',
                dashArray: '3',
                fillOpacity: 0.7
            };
        },

        // Optimize event handling
        onEachFeature: function(feature, layer) {
            // Use event delegation instead of individual handlers
            layer.on('mouseover', handleFeatureMouseOver);
            layer.on('mouseout', handleFeatureMouseOut);
        }
    });

    return geoJsonLayer;
}
```

#### JavaScript Performance

```javascript
// Debounce expensive operations
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Optimize map updates
const updateMapView = debounce(function(bounds) {
    map.fitBounds(bounds);
    updateVisibleLayers();
}, 300);

// Use Web Workers for heavy computations
function calculateAreasInWorker(features) {
    return new Promise((resolve, reject) => {
        const worker = new Worker('/static/js/area-calculator.js');

        worker.postMessage({ features });

        worker.onmessage = function(e) {
            resolve(e.data.results);
            worker.terminate();
        };

        worker.onerror = function(error) {
            reject(error);
            worker.terminate();
        };

        // Timeout after 30 seconds
        setTimeout(() => {
            worker.terminate();
            reject(new Error('Worker timeout'));
        }, 30000);
    });
}

// Memory management for large datasets
class DataManager {
    constructor(maxCacheSize = 100) {
        this.cache = new Map();
        this.maxCacheSize = maxCacheSize;
    }

    set(key, value) {
        if (this.cache.size >= this.maxCacheSize) {
            // Remove oldest entry
            const firstKey = this.cache.keys().next().value;
            this.cache.delete(firstKey);
        }
        this.cache.set(key, value);
    }

    get(key) {
        const value = this.cache.get(key);
        if (value) {
            // Move to end (LRU)
            this.cache.delete(key);
            this.cache.set(key, value);
        }
        return value;
    }

    clear() {
        this.cache.clear();
    }
}
```

## Security Considerations

### Input Validation

```python
from werkzeug.utils import secure_filename
import re

def validate_layer_name(layer_name: str) -> bool:
    """Validate layer name to prevent injection attacks."""
    # Allow only alphanumeric, spaces, hyphens, and underscores
    pattern = r'^[a-zA-Z0-9\s\-_]+$'
    return bool(re.match(pattern, layer_name))

def sanitize_file_path(filename: str) -> str:
    """Sanitize filename for safe file operations."""
    return secure_filename(filename)

@app.route("/api/vector/layer/<path:layer_name>")
def api_vector_layer_geojson(layer_name):
    """Get GeoJSON for vector layer with input validation."""
    # Validate input
    if not validate_layer_name(layer_name):
        return jsonify({"error": "Invalid layer name"}), 400

    # Prevent directory traversal
    if '..' in layer_name or '/' in layer_name:
        return jsonify({"error": "Invalid layer name"}), 400

    try:
        geojson = get_vector_layer_geojson(layer_name)
        return jsonify(geojson)
    except Exception as e:
        logger.error(f"Error fetching layer {layer_name}: {e}")
        return jsonify({"error": "Layer not found"}), 404
```

### Data Protection

```python
def sanitize_geojson_properties(geojson: Dict[str, Any]) -> Dict[str, Any]:
    """Remove sensitive information from GeoJSON properties."""
    if "features" in geojson:
        for feature in geojson["features"]:
            if "properties" in feature:
                # Remove potential sensitive fields
                sensitive_fields = ['file_path', 'full_path', 'system_info']
                for field in sensitive_fields:
                    feature["properties"].pop(field, None)

    # Remove file paths from metadata
    if "metadata" in geojson:
        geojson["metadata"].pop("file_path", None)

    return geojson

def limit_api_response_size(data: Any, max_size_mb: float = 50) -> Any:
    """Limit API response size to prevent memory issues."""
    import sys

    data_size = sys.getsizeof(str(data)) / (1024 * 1024)  # Size in MB

    if data_size > max_size_mb:
        raise ValueError(f"Response too large: {data_size:.2f}MB (max: {max_size_mb}MB)")

    return data
```

### Error Handling Security

```python
def safe_error_response(error: Exception, debug: bool = False) -> Dict[str, Any]:
    """Create safe error response that doesn't leak sensitive information."""
    if debug:
        return {
            "error": str(error),
            "type": type(error).__name__,
            "details": str(error)
        }
    else:
        # Generic error message for production
        return {
            "error": "An error occurred processing your request",
            "code": "INTERNAL_ERROR"
        }

@app.errorhandler(500)
def handle_internal_error(error):
    """Handle internal server errors safely."""
    logger.error(f"Internal server error: {error}")

    response = safe_error_response(error, debug=app.debug)
    return jsonify(response), 500
```

## Debugging

### Logging Configuration

```python
import logging
import sys
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_file: str = None):
    """Configure application logging."""

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Suppress overly verbose libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)

# Usage
if __name__ == "__main__":
    setup_logging("DEBUG", "logs/app.log")
```

### Debug Tools

```python
import time
from functools import wraps

def profile_function(func):
    """Decorator to profile function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            end_time = time.time()
            execution_time = end_time - start_time
            logger.debug(f"{func.__name__} executed in {execution_time:.4f} seconds")
    return wrapper

def debug_geojson_structure(geojson: Dict[str, Any]):
    """Debug helper to analyze GeoJSON structure."""
    print("=== GeoJSON Debug Info ===")
    print(f"Type: {geojson.get('type', 'Unknown')}")

    if 'features' in geojson:
        features = geojson['features']
        print(f"Feature count: {len(features)}")

        if features:
            first_feature = features[0]
            print(f"First feature type: {first_feature.get('type', 'Unknown')}")
            print(f"Geometry type: {first_feature.get('geometry', {}).get('type', 'Unknown')}")
            print(f"Properties keys: {list(first_feature.get('properties', {}).keys())}")

    if 'metadata' in geojson:
        metadata = geojson['metadata']
        print(f"Metadata keys: {list(metadata.keys())}")

    print("========================")

# JavaScript debugging utilities
"""
// Add to templates/index.html for frontend debugging
function debugLayerInfo(layer) {
    console.group('Layer Debug Info');
    console.log('Layer name:', layer.display_name);
    console.log('Feature count:', layer.feature_count);
    console.log('Geometry type:', layer.geometry_type);
    console.log('Bounds:', layer.bounds);
    console.log('Style:', layer.style);
    console.groupEnd();
}

function debugMapState() {
    console.group('Map Debug Info');
    console.log('Center:', map.getCenter());
    console.log('Zoom:', map.getZoom());
    console.log('Bounds:', map.getBounds());
    console.log('Active layers:', map.eachLayer(l => console.log(l)));
    console.groupEnd();
}

// Performance monitoring
const performanceMonitor = {
    marks: {},

    start(name) {
        this.marks[name] = performance.now();
    },

    end(name) {
        const startTime = this.marks[name];
        if (startTime) {
            const duration = performance.now() - startTime;
            console.log(`${name}: ${duration.toFixed(2)}ms`);
            delete this.marks[name];
            return duration;
        }
    }
};
"""
```

### Common Issues and Solutions

#### Vector Loading Issues

```python
def diagnose_vector_issues():
    """Diagnose common vector loading problems."""
    issues = []

    # Check data directory
    data_dir = Path("data/vector")
    if not data_dir.exists():
        issues.append("Vector data directory does not exist")

    # Check GPKG files
    gpkg_files = list(data_dir.glob("*.gpkg"))
    if not gpkg_files:
        issues.append("No GPKG files found in data directory")

    # Check dependencies
    try:
        import geopandas
        import fiona
    except ImportError as e:
        issues.append(f"Missing dependency: {e}")

    # Check file permissions
    for gpkg_file in gpkg_files:
        if not os.access(gpkg_file, os.R_OK):
            issues.append(f"Cannot read file: {gpkg_file}")

    return issues

def fix_common_issues():
    """Attempt to fix common configuration issues."""
    fixes_applied = []

    # Create data directory if missing
    data_dir = Path("data/vector")
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        fixes_applied.append("Created data directory")

    # Set proper file permissions
    for gpkg_file in data_dir.glob("*.gpkg"):
        if not os.access(gpkg_file, os.R_OK):
            try:
                os.chmod(gpkg_file, 0o644)
                fixes_applied.append(f"Fixed permissions for {gpkg_file}")
            except PermissionError:
                pass

    return fixes_applied
```

## Contributing

### Getting Started

1. **Fork the repository**
2. **Set up development environment** (see Development Setup)
3. **Read existing code** to understand patterns and conventions
4. **Check open issues** for contribution opportunities
5. **Join discussions** on architecture and feature planning

### Contribution Guidelines

#### Code Quality Standards

- **Test Coverage**: Maintain > 80% test coverage
- **Documentation**: Update docs for user-facing changes
- **Code Style**: Follow Black formatting and PEP 8
- **Type Hints**: Use type annotations for new code
- **Error Handling**: Implement proper exception handling

#### Pull Request Process

1. **Create feature branch** from `develop`
2. **Write tests** for new functionality
3. **Update documentation** as needed
4. **Run quality checks** (tests, linting, formatting)
5. **Submit pull request** with clear description
6. **Address review feedback** promptly
7. **Squash commits** before merging

#### Code Review Checklist

**Functionality:**
- [ ] Code works as intended
- [ ] Edge cases are handled
- [ ] Error conditions are managed
- [ ] Performance impact is acceptable

**Code Quality:**
- [ ] Follows project conventions
- [ ] Is well-documented
- [ ] Has appropriate test coverage
- [ ] Uses efficient algorithms

**Security:**
- [ ] Validates input properly
- [ ] Doesn't expose sensitive data
- [ ] Handles authentication/authorization
- [ ] Prevents injection attacks

### Development Best Practices

1. **Start Small**: Begin with small, focused contributions
2. **Test Thoroughly**: Write comprehensive tests for new features
3. **Document Changes**: Update relevant documentation
4. **Follow Patterns**: Maintain consistency with existing code
5. **Ask Questions**: Engage with maintainers for guidance
6. **Be Patient**: Allow time for review and feedback

---

This developer guide provides comprehensive information for working on the MARBEFES BBT Database. For additional support, refer to the main [README](../README.md) or the [API documentation](API.md).