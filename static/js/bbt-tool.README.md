# BBT Tool Module - Usage Guide

## Overview

The BBT (Broad-scale Biotope) Tool Module provides comprehensive navigation, data management, and bathymetry visualization for the MARBEFES project's marine biodiversity analysis across European seas.

**File**: `static/js/bbt-tool.js`
**Version**: 1.1.0
**Size**: 45 KB (1,097 lines)

## Features

- **BBT Feature Loading**: Async API integration for GeoJSON data
- **Smart Navigation**: Optimized zoom with caching and no-bounce behavior
- **Geodesic Calculations**: Accurate area measurements using L.GeometryUtil
- **Enhanced Tooltips**: MARBEFES project context with research information
- **Data Management**: Editable popup with bathymetry statistics integration
- **Auto-initialization**: Background loading with graceful error handling

## Quick Start

### 1. Include in HTML

```html
<!-- After Leaflet and other dependencies -->
<script src="{{ url_for('static', filename='js/bbt-tool.js') }}"></script>
```

### 2. Basic Usage

The module auto-initializes when the DOM is ready. No manual initialization needed!

```javascript
// Zoom to a specific BBT area
BBTTool.zoomToBBTArea('Archipelago');

// Open data popup for editing
BBTTool.openBBTDataPopup('Bay of Gdansk');

// Get information about all BBT regions
const regions = BBTTool.getBBTRegionInfo();
console.log(regions['Kongsfjord']); // Arctic Ocean info
```

### 3. Advanced Usage

```javascript
// Manual feature loading (optional, auto-loads in background)
BBTTool.loadBBTFeatures()
    .then(data => {
        console.log('Loaded', data.features.length, 'BBT areas');
    })
    .catch(error => {
        console.error('Failed to load BBT features:', error);
    });

// Calculate area of a GeoJSON feature
const area = BBTTool.calculateFeatureArea(feature);
console.log('Area:', area, 'km²');

// Generate enhanced tooltip content
const tooltipHTML = BBTTool.generateTooltipContent(feature, 'Bbt - Bbt Areas');
```

## Public API Reference

### Feature Loading

- `loadBBTFeatures()` → `Promise<Object>` - Loads BBT features from API
- `showBBTLoadingError(message)` - Displays error message
- `createBBTNavigationButtons()` - Upgrades static buttons to interactive

### Zoom Functions

- `zoomToBBTFeature(feature, buttonElement)` - Zoom to specific feature
- `zoomToBBTArea(areaName)` - Optimized direct zoom by name
- `zoomToBBTFeatureDirect(feature, areaName)` - No-bounce zoom helper
- `zoomToGeneralBBTArea(areaName)` - Fallback zoom to general area

### Area Calculation

- `calculateFeatureArea(feature)` → `number|null` - Geodesic area in km²

### Tooltip Functions

- `createTooltip(content, x, y)` - Display hover tooltip
- `removeTooltip()` - Remove current tooltip
- `updateTooltip(x, y)` - Update tooltip position
- `generateTooltipContent(feature, layerName)` → `string` - Generate HTML content

### Data Management

- `initializeBBTData()` - Initialize data store with templates
- `openBBTDataPopup(bbtName)` - Open data editor popup
- `closeBBTDataPopup()` - Close data popup
- `saveBBTData()` - Save edited data (client-side only, backend TODO)

### Initialization

- `initialize()` → `Promise<void>` - Background BBT navigation initialization
- `initializePopupListeners()` - Setup popup event listeners

### Data Access (Read-only)

- `getBBTRegionInfo()` → `Object` - Get MARBEFES region information
- `getCurrentActiveBBT()` → `string|null` - Get currently active BBT name
- `getBBTDataStore()` → `Object` - Get copy of data store

## MARBEFES BBT Regions

The module includes detailed research context for 11 BBT study areas:

| Region | Sea | Research Focus |
|--------|-----|----------------|
| **Archipelago** | Baltic Sea | Benthic-pelagic coupling in coastal zones |
| **Balearic** | Mediterranean | Climate change impacts on Mediterranean ecosystems |
| **Bay of Gdansk** | Baltic Sea | Land-sea connectivity and nutrient cycling |
| **Gulf of Biscay** | Atlantic | Ocean-shelf biodiversity gradients |
| **Heraklion** | Mediterranean | Deep-sea connectivity and endemic biodiversity |
| **Hornsund** | Arctic Ocean | Arctic ecosystem resilience and tipping points |
| **Kongsfjord** | Arctic Ocean | Climate-driven Arctic "atlantification" |
| **Lithuanian coast** | Baltic Sea | Coastal zone management and eutrophication |
| **North Sea** | North Sea | Anthropogenic impacts and ecosystem services |
| **Irish Sea** | Irish Sea | Marine spatial planning and biodiversity conservation |
| **Sardinia** | Mediterranean | Island biogeography and connectivity |

## Dependencies

### Required

- **Leaflet.js** - Core mapping library
- **L.GeometryUtil** - For geodesic area calculations
- **window.MapInit** - Map instance provider (from `map-init.js`)
- **window.API_BASE_URL** - Backend API endpoint (from `config.js`)

### Optional

- `window.bathymetryStats` - Bathymetry data for popup display
- `window.vectorLayerGroup` - Vector layer management
- `window.currentLayer`, `window.currentLayerType` - Layer state tracking
- `window.isManualZoom` - Zoom behavior coordination

## Integration with HTML Template

The module expects the following HTML elements to be present:

```html
<!-- Navigation buttons container -->
<div id="bbt-nav-buttons">
    <button class="bbt-nav-btn" onclick="BBTTool.zoomToBBTArea('Archipelago')">Archipelago</button>
    <!-- More buttons... -->
</div>

<!-- Loading indicator -->
<div id="bbt-loading" style="display: none;">Loading...</div>

<!-- Status display -->
<div id="status"></div>

<!-- Data popup modal -->
<div class="bbt-popup-overlay" id="bbt-popup-overlay">
    <div class="bbt-popup">
        <div class="bbt-popup-header">
            <h2 class="bbt-popup-title" id="bbt-popup-title"></h2>
            <button class="bbt-popup-close" onclick="BBTTool.closeBBTDataPopup()">×</button>
        </div>
        <div class="bbt-popup-content" id="bbt-popup-content"></div>
        <div class="bbt-popup-actions">
            <button onclick="BBTTool.closeBBTDataPopup()">Cancel</button>
            <button onclick="BBTTool.saveBBTData()">Save Changes</button>
        </div>
    </div>
</div>
```

## Bathymetry Integration

The module integrates with bathymetry statistics from the backend:

```javascript
// Expected data structure from backend
const bathymetryStats = {
    'Archipelago': {
        min_depth_m: 5.2,
        max_depth_m: 45.8,
        avg_depth_m: 23.5,
        sample_count: 1500,
        notes: 'Shallow coastal waters with variable depth'
    },
    // ... more BBT areas
};
```

When `openBBTDataPopup()` is called, the module automatically looks up and displays bathymetry statistics if available in `window.bathymetryStats`.

## Error Handling

The module includes comprehensive error handling:

- **503 Service Unavailable**: Treated as warning, not error
- **Network Failures**: Graceful degradation with fallback behavior
- **Missing Data**: Uses general zoom instead of specific feature zoom
- **Invalid Bounds**: Falls back to European marine area view

## Performance Optimizations

- **Caching**: BBT feature data cached after first load
- **Background Loading**: 2-second delay for non-blocking initialization
- **Layer Reuse**: Skips re-rendering if BBT layer already visible
- **Smart Zoom**: Detects manual zoom to prevent auto-reload bouncing
- **Minimal Delays**: Optimized timing (50-100ms) for responsive UX

## TODO: Backend Integration

The data saving function has a TODO for backend API integration:

```javascript
// TODO: Implement in backend
fetch(`${API_BASE_URL}/bbt/data/${encodeURIComponent(bbtName)}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(updatedData)
});
```

## Browser Compatibility

- Modern browsers (ES6+ required)
- Uses `async/await`, arrow functions, template literals
- Requires DOM APIs: `querySelector`, `classList`, `dataset`
- No transpilation needed for modern browsers

## License

MARBEFES Project - Horizon Europe

---

**Module Author**: MARBEFES Project Team
**Last Updated**: October 2025
**Documentation Version**: 1.0
