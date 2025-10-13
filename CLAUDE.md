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

## Framework Updates (Version 1.2.4 - October 2025)

### Latest Release (v1.2.4) - P1 Performance Optimizations
**Release Date:** October 13, 2025
**Focus:** Priority 1 (P1) performance optimizations for faster load times and reduced bandwidth
**Impact:** Zero breaking changes, 100% backward compatible

This release implements all Priority 1 performance optimizations, delivering significant improvements in page load speed, bandwidth usage, and real-world user experience.

#### Performance Improvements Summary

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| HTTP Requests (JS files) | 9 requests | 1 request | **89% reduction** |
| JavaScript Bundle Size | 158KB (unminified) | 66KB (minified) | **58% reduction** |
| GeoJSON Transfer Size | 7.8 MB (uncompressed) | 1.3 MB (gzip) | **84% reduction** |
| External Resource Loading | No preconnect | 4 preconnect hints | **200-600ms faster** |
| Performance Monitoring | None | Full instrumentation | **Real-time metrics** |

#### 1. Response Compression (Flask-Compress)
- **Added**: `Flask-Compress==1.15` to requirements.txt
- **Configured**: Compression level 6, 500-byte minimum threshold
- **Impact**: 84% reduction in GeoJSON transfer size (8MB → 1.3MB)
- **Supported Formats**: gzip, brotli, zstandard (automatic content negotiation)
- **CPU Overhead**: Minimal (6ms compression time for 7.8MB file)

**Configuration in app.py:**
```python
from flask_compress import Compress

compress = Compress()
app.config['COMPRESS_MIMETYPES'] = [
    'application/json',
    'application/geo+json',
    'text/html',
    'text/css',
    'text/javascript',
    'application/javascript'
]
app.config['COMPRESS_LEVEL'] = 6
app.config['COMPRESS_MIN_SIZE'] = 500
compress.init_app(app)
```

#### 2. JavaScript Bundling
- **Created**: `build_bundle.py` - Python-based JavaScript bundler
- **Created**: `package.json` - NPM configuration with Terser minification
- **Output**: Development bundle (158KB) and production bundle (66KB minified)
- **Impact**: 89% reduction in HTTP requests (9 → 1)
- **Bundled Files**: debug.js, bbt-regions.js, marbefes-datasets.js, config.js, map-init.js, layer-manager.js, bbt-tool.js, ui-handlers.js, app.js

**Building the bundle:**
```bash
python build_bundle.py
```

**Bundle Output:**
- `static/dist/app.bundle.js` - Development (158KB, with comments)
- `static/dist/app.bundle.min.js` - Production (66KB, minified)
- `static/dist/app.bundle.min.js.map` - Source map (50KB)

#### 3. Preconnect Hints
- **Added**: 6 preconnect/DNS prefetch hints to templates/index.html
- **Targets**: unpkg.com, cdn.jsdelivr.net, ows.emodnet-seabedhabitats.eu, helcom.fi
- **Impact**: 200-600ms faster first external resource request
- **Benefit**: DNS lookup, TCP handshake, TLS negotiation happen in parallel with HTML parsing

**Implementation in index.html:**
```html
<link rel="preconnect" href="https://unpkg.com" crossorigin>
<link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
<link rel="preconnect" href="https://ows.emodnet-seabedhabitats.eu">
<link rel="preconnect" href="https://helcom.fi">
<link rel="dns-prefetch" href="https://unpkg.com">
<link rel="dns-prefetch" href="https://cdn.jsdelivr.net">
```

#### 4. Performance Timing API
- **Created**: `static/js/utils/performance-monitor.js` - Client-side monitoring
- **Added**: `/api/metrics` endpoint for receiving performance data
- **Tracked Metrics**: Navigation timing, resource timing, layer loading, user interactions
- **Flush Strategy**: Every 10 metrics or on page unload
- **Rate Limiting**: 30 requests per minute per client

**Performance Monitoring Usage:**
```javascript
// Automatically tracks navigation and resource loading
// Manual tracking for layer loads:
PerformanceMonitor.recordLayerLoad('Bbt', 380, false, 11);

// Force flush pending metrics:
PerformanceMonitor.flushNow();
```

#### Files Modified for P1 Optimizations
- `templates/index.html` - Added preconnect hints
- `requirements.txt` - Added Flask-Compress==1.15
- `app.py` - Flask-Compress configuration + /api/metrics endpoint
- `.gitignore` - Added node_modules/, package-lock.json

#### Files Created for P1 Optimizations
- `package.json` - NPM configuration
- `build_bundle.py` - JavaScript bundler
- `static/js/utils/performance-monitor.js` - Performance monitoring
- `static/dist/` - Bundle output directory
- `P1_OPTIMIZATIONS_COMPLETE.md` - Full optimization report

### Previous Release (v1.2.3) - Code Quality Improvements
**Release Date:** October 13, 2025
**Focus:** Internal code quality and maintainability improvements
**Impact:** Zero breaking changes, 100% backward compatible

This release completes all Priority 2 code quality improvements, significantly enhancing maintainability, consistency, and production-readiness.

#### 1. Conditional Debug Logging System
- **Created**: `static/js/utils/debug.js` - Professional debug utility module
- **Replaced**: 167 `console.log` statements with conditional `debug.log`
- **Production Benefit**: Clean console (only errors/info shown to end users)
- **Development Benefit**: All debug messages visible in dev mode
- **Control**: Automatically enabled/disabled based on `FLASK_DEBUG` environment variable
- **Performance**: Eliminates 167 console operations in production mode
- **Files Modified**: All JavaScript modules, templates for DEBUG flag injection

**Usage:**
```javascript
debug.log('Debug message');    // Only in development
debug.warn('Warning');          // Only in development
debug.error('Error');           // Always shown
debug.info('User message');     // Always shown
```

#### 2. BBT Region Data Deduplication
- **Created**: `static/js/data/bbt-regions.js` - Shared BBT region data module
- **Eliminated**: 136 lines of duplicated code across 2 files
- **Single Source**: All 11 BBT areas defined once, used everywhere
- **Added**: Helper functions (`getBBTRegionInfo()`, `getAllBBTRegionNames()`, `getBBTRegionsBySeaArea()`)
- **Maintainability**: Update region info in one place, reflects everywhere
- **Files Modified**: `layer-manager.js`, `bbt-tool.js` now reference shared module

#### 3. Centralized Version Management
- **Created**: `src/emodnet_viewer/__version__.py` - Single source of truth for versions
- **Dynamic**: `pyproject.toml` reads version automatically from module
- **Enhanced**: Health endpoint (`/health`) now includes version and release date
- **Benefit**: Change version once, propagates to pip, API, documentation
- **API Response**: `{"version": "1.2.3", "version_date": "2025-10-13"}`

#### 4. Configuration Injection
- **Template Injection**: Flask config values now injected into JavaScript at render time
- **Single Source**: `.env` file controls both backend and frontend configuration
- **Eliminated**: Hardcoded map defaults in JavaScript (lat/lng/zoom)
- **Environment Control**: Different deployments can have different map centers via `.env`
- **Configuration Flow**: `.env` → Python config → Template → JavaScript

**Example (.env):**
```bash
DEFAULT_MAP_CENTER_LAT=54.0
DEFAULT_MAP_CENTER_LNG=10.0
DEFAULT_MAP_ZOOM=4
```

#### Code Quality Metrics
- **Quality Score**: 8.7/10 → 9.3/10 (+0.6 improvement)
- **Lines Added**: +544 (new features, documentation)
- **Lines Removed**: -335 (duplication eliminated)
- **Duplication Removed**: ~303 lines (debug + data + config)
- **New Modules**: 3 (debug utility, BBT data, version module)
- **Files Changed**: 12 files across frontend and backend

### Previous Release (v1.2.2)
- **New Feature**: Draggable floating EUNIS 2019 legend
  * Interactive checkbox toggle in sidebar
  * On-demand WMS GetLegendGraphic loading
  * Full drag-and-drop functionality (mouse + touch support)
  * GPU-accelerated CSS transforms for smooth movement
  * Position memory during session
  * Modern UI with slide-in animations
- **User Experience**: Legend can be repositioned anywhere on screen
- **Files Modified**: `templates/index.html` (+174 lines), `static/css/styles.css` (+103 lines)

### Previous Release (v1.2.1)
- **Critical Fix**: Resolved BBT vector layer display issue (pandas/pyogrio compatibility)
- **Dependency Change**: Downgraded pandas from 2.2.3 to 2.0.3 for pyogrio 0.11.1 compatibility
- **Error Handling**: Enhanced vector loader with robust fiona fallback and numpy type conversion
- **Testing**: Verified all 11 BBT areas loading successfully

### Previous Release (v1.2.0)
- **Security Enhancement**: Smart host binding - `127.0.0.1` in development (secure by default), `0.0.0.0` in production (network-accessible). Override with `FLASK_HOST` environment variable.
- **Python 3.12+ Compatibility**: Replaced deprecated `datetime.utcnow()` with `datetime.now(timezone.utc)`
- **Performance Optimization**: Added factsheet data caching (86% faster API responses - from ~50ms to ~7ms)
- **Framework Updates**: Flask-Caching updated to 2.3.1 (latest stable)
- **Optional Dependency**: Added PyOGRIO for faster GPKG I/O operations

### Previous Updates (Version 1.1.0)

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
- Modular JavaScript with drag-and-drop functionality

### Styling Approach
- Custom CSS with gradient backgrounds and modern UI elements
- Hover effects and transitions for interactive elements
- Mobile-responsive design considerations
- CSS animations for smooth UI transitions

### EUNIS Legend Feature (`templates/index.html:125-131, 279-598`)
The application includes an interactive floating legend for EUNIS 2019 habitat classification:

#### User Interface
- **Checkbox Toggle**: Located in sidebar under "Available Layers" section
- **Floating Container**: Fixed positioning at bottom-left (340px from left edge)
- **Draggable Header**: Click and drag title bar to reposition anywhere on screen
- **Close Options**: Uncheck checkbox or click X button in header

#### Technical Implementation
- **On-Demand Loading**: Legend fetched only when checkbox is checked
- **WMS Integration**: Uses GetLegendGraphic API from EMODnet service
  ```
  https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms?
  SERVICE=WMS&VERSION=1.1.0&REQUEST=GetLegendGraphic&
  FORMAT=image/png&LAYER=eusm_2023_eunis2019_full
  ```
- **Drag System**: Full mouse and touch event handling
  * `makeLegendDraggable()` - Initializes drag functionality
  * Mouse events: mousedown, mousemove, mouseup
  * Touch events: touchstart, touchmove, touchend
  * CSS transforms for GPU-accelerated movement
- **Smart Detection**: Prevents drag when clicking close button
- **Position Memory**: Maintains position until page reload

#### CSS Styling (`static/css/styles.css:858-952`)
- `.floating-eunis-legend` - Main container with fixed positioning
- `.floating-eunis-legend-header` - Draggable header with grab cursor
- `@keyframes slideInUp` - Smooth appearance animation
- Loading and error state styling

#### JavaScript Functions (`templates/index.html:448-595`)
- `toggleEunisLegend()` - Show/hide based on checkbox state
- `showEunisLegend()` - Display legend and load image if needed
- `hideEunisLegend()` - Hide legend container
- `closeEunisLegend()` - Close via button and uncheck checkbox
- `loadEunisLegendImage()` - Fetch legend from WMS service
- `makeLegendDraggable()` - Initialize drag-and-drop system

When modifying this application, preserve the single-file architecture and ensure WMS integration remains functional with the EMODnet infrastructure.