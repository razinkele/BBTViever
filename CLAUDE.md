# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Flask-based web application for visualizing EMODnet (European Marine Observation and Data Network) Seabed Habitats WMS (Web Map Service) layers with comprehensive vector layer support. The application provides an interactive map viewer that displays seabed habitat datasets from EMODnet infrastructure alongside local GPKG vector data with real-time hover tooltips and area calculations.

## Key Architecture

### Single-File Application Structure
- **app.py** - Complete Flask application with embedded HTML template
- Self-contained web server with no external template files
- Uses Jinja2 template rendering with `render_template_string()`

### Core Components
1. **WMS Integration** (`app.py:12-91`)
   - Connects to EMODnet WMS service at `https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms`
   - Parses GetCapabilities XML responses to discover available layers
   - Fallback to predefined layer list if service is unavailable

2. **Interactive Map Interface** (`app.py:96-464`)
   - Leaflet-based mapping interface with multiple basemap options
   - Layer selection sidebar with predefined EMODnet habitat layers
   - Dynamic opacity control and legend display
   - Responsive design optimized for desktop browsers

3. **API Endpoints** (WMS + Vector support)
   - `/api/layers` - Returns available WMS layers as JSON
   - `/api/capabilities` - Proxies WMS GetCapabilities requests
   - `/api/legend/<layer_name>` - Provides legend URLs for layers
   - `/api/vector/layers` - Returns available vector layers with metadata
   - `/api/vector/layer/<name>` - Returns GeoJSON for specific vector layer
   - `/api/vector/bounds` - Returns combined bounds of all vector layers
   - `/api/all-layers` - Returns combined WMS + vector layer information

4. **Vector Layer Support** (`src/emodnet_viewer/utils/vector_loader.py`)
   - Automatic GPKG file discovery in `data/vector/` directory
   - GeoPandas-based data processing and coordinate system normalization
   - Real-time hover tooltips with geodesic area calculations
   - Leaflet GeometryUtil integration for accurate geometric measurements

### Data Flow
- Application queries EMODnet WMS GetCapabilities on startup
- Parses XML to extract layer names, titles, and descriptions
- Serves interactive interface that makes client-side WMS requests
- Legend images are fetched directly from WMS GetLegendGraphic requests

## Framework Updates (Version 1.1.0)

### Major Updates Applied
- **Flask**: 2.3.3 → 3.1.2 (security updates, better performance)
- **GeoPandas**: 0.14.0 → 1.1.1 (major version with enhanced features)
- **Testing Framework**: Pytest 7.4.2 → 8.4.2 (improved compatibility)
- **Code Quality**: Black 23.7.0 → 25.1.0, Flake8 6.0.0 → 7.3.0
- **Python Support**: Minimum version raised from 3.8 → 3.9

### Security Improvements
- Updated Flask to address CVE-2024 vulnerabilities
- Enhanced dependency versions for better security posture
- Added explicit Werkzeug dependency for security
- Updated requests library for latest security patches

## Development Commands

### Running the Application
```bash
python app.py
```
- Starts Flask development server on port 5000
- Accessible at http://localhost:5000
- Debug mode enabled by default

### Dependencies
This application requires (updated to latest stable versions):
- Flask 3.1.2 (web framework) - Updated for security and performance
- requests 2.32.3 (HTTP client for WMS requests) - Security updates
- xml.etree.ElementTree (XML parsing, built into Python)
- geopandas 1.1.1 (geospatial data processing) - Major version upgrade
- Fiona 1.10.1 (GPKG file reading) - Compatibility updates
- pyproj 3.7.1 (coordinate system transformations) - Latest features
- Werkzeug 3.1.0+ (WSGI utilities) - Explicit security dependency

Install dependencies:
```bash
# For production
pip install -r requirements.txt

# For development (includes testing and code quality tools)
pip install -r requirements-dev.txt

# Or using the project configuration
pip install -e .[dev]
```

### Testing Endpoints
- Main interface: http://localhost:5000
- WMS connectivity test: http://localhost:5000/test
- API endpoints: http://localhost:5000/api/layers

## EMODnet Integration Details

### Default Layer Configuration
The application includes predefined layers from EMODnet (`app.py:17-48`):
- `all_eusm2021` - EUSeaMap 2021 comprehensive habitat map
- `be_eusm2021` - Benthic habitat classifications
- `ospar_threatened` - OSPAR threatened habitat types
- `substrate` - Seabed substrate classifications
- `confidence` - Habitat prediction confidence levels
- `annexiMaps_all` - EU Habitats Directive Annex I habitats

### WMS Service Integration
- Base URL: `https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms`
- Uses WMS version 1.3.0 for capabilities, 1.1.0 for map requests
- Supports GetMap, GetCapabilities, and GetLegendGraphic operations
- Handles XML namespace processing for capabilities parsing

### Error Handling
- Graceful fallback to predefined layers if WMS service is unavailable
- Client-side loading indicators and error states
- 10-second timeout on external WMS requests

## Development Notes

### Frontend Architecture
- No build process required - uses CDN resources (Leaflet 1.9.4)
- Inline CSS and JavaScript within the HTML template
- Responsive design with sidebar/map layout

### Styling Approach
- Custom CSS with gradient backgrounds and modern UI elements
- Hover effects and transitions for interactive elements
- Mobile-responsive design considerations

When modifying this application, preserve the single-file architecture and ensure WMS integration remains functional with the EMODnet infrastructure.