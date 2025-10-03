# MARBEFES BBT Database - User Guide

## Welcome to the Marine Biodiversity and Ecosystem Functioning Database

This guide will help you navigate and use the MARBEFES BBT Database web interface to explore marine biodiversity and ecosystem data from European seas. The application provides an interactive mapping platform for visualizing EMODnet seabed habitat data alongside Broad Belt Transect (BBT) survey areas.

## Table of Contents

- [Getting Started](#getting-started)
- [Interface Overview](#interface-overview)
- [Navigation](#navigation)
- [Layer Management](#layer-management)
- [BBT Study Areas](#bbt-study-areas)
- [3D Visualization](#3d-visualization)
- [Data Interaction](#data-interaction)
- [Advanced Features](#advanced-features)
- [Tips and Best Practices](#tips-and-best-practices)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

## Getting Started

### Accessing the Application

1. **Open your web browser** (Chrome, Firefox, Safari, or Edge recommended)
2. **Navigate to the application URL** (typically `http://localhost:5000` for local installations)
3. **Wait for the application to load** - you'll see the MARBEFES logo and the interactive map interface

### System Requirements

**Recommended Browser Settings:**
- JavaScript enabled
- Pop-up blocker disabled for the application domain
- Minimum screen resolution: 1024x768
- Stable internet connection for external data layers

**Supported Browsers:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### First Time Setup

No registration or login is required. The application is ready to use immediately upon loading.

## Interface Overview

### Main Layout

The application interface consists of three main areas:

```
┌─────────────────┬──────────────────────────┐
│                 │                          │
│    Sidebar      │                          │
│    Controls     │        Map Area          │
│                 │                          │
│                 │                          │
├─────────────────┼──────────────────────────┤
│   3D Controls   │     Optional 3D View     │
└─────────────────┴──────────────────────────┘
```

#### Sidebar (Left Panel)

The sidebar contains all interactive controls and is divided into several sections:

1. **MARBEFES Branding** - Project logo and title
2. **BBT Quick Navigation** - Direct access to 9 study areas
3. **EMODnet WMS Layers** - Marine habitat overlay controls
4. **HELCOM Layers** - Baltic Sea environmental data
5. **Vector Layers** - Local BBT transect data
6. **Map Controls** - Basemap selection and opacity
7. **3D Visualization** - PyDeck controls (when enabled)

#### Map Area (Main Panel)

The map displays:
- **Base Maps** - Background geographic context
- **WMS Overlays** - EMODnet seabed habitat layers
- **Vector Data** - BBT transect areas and boundaries
- **Interactive Elements** - Hover tooltips and click information
- **Navigation Controls** - Zoom, pan, and home buttons

### Interface Elements

#### Buttons and Controls

- **Primary Buttons** - Teal gradient buttons for main actions
- **Toggle Switches** - Enable/disable layers
- **Sliders** - Adjust layer opacity (0-100%)
- **Dropdown Menus** - Select from multiple options
- **Information Icons** - Hover for additional details

#### Visual Indicators

- **Loading Spinners** - Indicate data is being fetched
- **Success Messages** - Confirm successful operations
- **Error Alerts** - Highlight issues or failures
- **Layer Status** - Show active/inactive layers

## Navigation

### Basic Map Navigation

#### Mouse Controls

- **Pan** - Click and drag to move the map
- **Zoom In** - Double-click or scroll wheel up
- **Zoom Out** - Shift + double-click or scroll wheel down
- **Select Features** - Single click on map features

#### Keyboard Shortcuts

- **Arrow Keys** - Pan the map in any direction
- **+ Key** - Zoom in one level
- **- Key** - Zoom out one level
- **Home Key** - Return to initial view
- **Escape** - Close any open popups or tooltips

#### Touch Controls (Mobile/Tablet)

- **Pan** - Touch and drag
- **Zoom** - Pinch to zoom in/out
- **Select** - Tap on features
- **Double Tap** - Zoom in to location

### Map Extent and Views

#### Default View

The application opens with a view centered on Europe, showing:
- **Center Point** - Latitude: 54.0°N, Longitude: 10.0°E
- **Zoom Level** - Level 4 (Continental view)
- **Visible Area** - European seas and coastlines

#### Navigation Bounds

- **Maximum Zoom Out** - Global view (level 1)
- **Maximum Zoom In** - Detailed coastal view (level 18)
- **Geographic Coverage** - Worldwide, optimized for European waters

### Quick Navigation Tools

#### Home Button
Click the home icon (🏠) in the top-left corner to return to the default European view.

#### Zoom Controls
Use the + and - buttons in the top-left corner for precise zoom control.

#### Scale Indicator
The scale bar in the bottom-left shows the current map scale and updates as you zoom.

## Layer Management

### Understanding Layer Types

The application supports three main types of data layers:

#### 1. EMODnet WMS Layers
**Source:** European Marine Observation and Data Network
**Type:** Web Map Service (WMS) overlays
**Content:** Seabed habitat classifications and environmental data

**Key Layers:**
- **EUSeaMap 2023 - European Biological Zones** - Broad-scale biological habitat map
- **EUSeaMap 2023 - European Substrate Types** - Seabed substrate classification
- **EUSeaMap 2023 - EUNIS Classification** - European habitat classification system
- **EUSeaMap 2023 - European Energy Zones** - Energy regime classification
- **Confidence Layers** - Prediction confidence levels

#### 2. HELCOM Layers
**Source:** Helsinki Commission (Baltic Marine Environment Protection Commission)
**Type:** Web Map Service (WMS) overlays
**Content:** Baltic Sea environmental pressure data

**Key Layers:**
- **Chemical weapons dumpsites** - Historical munitions disposal areas
- **Environmental pressures** - Human impact assessment
- **Transportation routes** - Shipping and maritime traffic
- **Protected areas** - Marine conservation zones

#### 3. Vector Layers
**Source:** Local MARBEFES project data
**Type:** Interactive vector features (GeoJSON)
**Content:** Broad Belt Transect survey areas

**Available Layers:**
- **Bbts - Merged** - Combined BBT areas (6 features)
- **Bbts - Broad Belt Transects** - Individual transect areas (9 features)

### Layer Controls

#### Enabling/Disabling Layers

1. **Locate the layer** in the appropriate sidebar section
2. **Click the toggle switch** next to the layer name
   - Blue switch = Layer active
   - Gray switch = Layer inactive
3. **Wait for loading** - A spinner indicates data is being fetched
4. **Verify display** - Active layers appear on the map

#### Adjusting Layer Opacity

1. **Find the opacity slider** below active layer controls
2. **Drag the slider** left (more transparent) or right (more opaque)
3. **Observe changes** in real-time on the map
4. **Set optimal visibility** - typically 60-80% for overlays

#### Layer Ordering

Layers are automatically arranged in optimal viewing order:
1. **Vector layers** (top) - Always visible and interactive
2. **WMS overlays** (middle) - Adjustable opacity
3. **Base maps** (bottom) - Provide geographic context

### Basemap Options

Choose from four different background maps:

#### OpenStreetMap (Default)
- **Style** - Clean, detailed street map
- **Best for** - General geographic context
- **Features** - Roads, cities, coastlines, topography

#### Satellite
- **Style** - High-resolution satellite imagery
- **Best for** - Visualizing coastlines and land features
- **Features** - True-color Earth imagery

#### Ocean
- **Style** - Ocean-focused bathymetric map
- **Best for** - Marine research and underwater features
- **Features** - Ocean depth, underwater topography

#### Light Gray
- **Style** - Minimal, neutral background
- **Best for** - Highlighting data layers
- **Features** - Subtle geographic boundaries

**To change basemap:**
1. Scroll to the "Map Controls" section in the sidebar
2. Select your preferred option from the dropdown
3. The map will update automatically

## BBT Study Areas

### Overview of Study Areas

The MARBEFES project focuses on nine Broad Belt Transect areas across European seas:

#### 1. **Archipelago** 🇸🇪
- **Location** - Swedish archipelago, Baltic Sea
- **Coordinates** - 59.8°N, 19.1°E
- **Environment** - Rocky archipelago with complex coastal morphology
- **Zoom Level** - 10

#### 2. **Balearic** 🇪🇸
- **Location** - Balearic Islands, Western Mediterranean
- **Coordinates** - 39.6°N, 2.8°E
- **Environment** - Mediterranean island ecosystem
- **Zoom Level** - 9

#### 3. **Bay of Gdansk** 🇵🇱
- **Location** - Polish coast, Southern Baltic Sea
- **Coordinates** - 54.4°N, 18.8°E
- **Environment** - Shallow coastal bay with sandy substrates
- **Zoom Level** - 10

#### 4. **Gulf of Biscay** 🇫🇷
- **Location** - French Atlantic coast
- **Coordinates** - 45.5°N, -1.2°W
- **Environment** - Atlantic continental shelf
- **Zoom Level** - 8

#### 5. **Heraklion** 🇬🇷
- **Location** - Crete, Eastern Mediterranean
- **Coordinates** - 35.3°N, 25.1°E
- **Environment** - Mediterranean deep-water environment
- **Zoom Level** - 10

#### 6. **Hornsund** 🇳🇴
- **Location** - Svalbard, Arctic Ocean
- **Coordinates** - 77.0°N, 15.6°E
- **Environment** - Arctic fjord ecosystem
- **Zoom Level** - 11

#### 7. **Kongsfjord** 🇳🇴
- **Location** - Svalbard, Arctic Ocean
- **Coordinates** - 78.9°N, 12.2°E
- **Environment** - Arctic fjord with glacial influence
- **Zoom Level** - 11

#### 8. **Lithuanian coastal zone** 🇱🇹
- **Location** - Lithuanian coast, Eastern Baltic Sea
- **Coordinates** - 55.7°N, 21.1°E
- **Environment** - Sandy coastal waters
- **Zoom Level** - 9

#### 9. **Sardinia** 🇮🇹
- **Location** - Sardinia, Western Mediterranean
- **Coordinates** - 40.8°N, 9.4°E
- **Environment** - Mediterranean island waters
- **Zoom Level** - 8

### Quick Navigation

#### Using BBT Buttons

1. **Find the BBT Quick Navigation** section at the top of the sidebar
2. **Click any area button** (e.g., "Archipelago", "Balearic")
3. **The map will automatically:**
   - Zoom to the selected area
   - Center on the BBT location
   - Load relevant vector layers
   - Show area boundaries

#### Navigation Tips

- **Button Layout** - Buttons are arranged in three rows for easy access
- **Loading Time** - Allow 2-3 seconds for the map to load and center
- **Auto-Loading** - Vector layers load automatically when zooming to BBT areas
- **Multiple Areas** - Click different buttons to compare areas quickly

### Area Information

#### Hover Tooltips

When you hover over BBT polygon features:
- **Area Name** - Display name of the BBT area
- **Calculated Area** - Real-time geodesic area calculation in km²
- **Feature ID** - Unique identifier for the transect
- **Coordinates** - Latitude and longitude of cursor position

#### Click Information

Click on BBT features to see detailed information:
- **Full attribute data** - All available properties
- **Geometry details** - Feature type and coordinate system
- **Metadata** - Source file and processing information

## 3D Visualization

### PyDeck 3D Features

The application includes advanced 3D visualization capabilities powered by Deck.gl:

#### Enabling 3D Mode

1. **Scroll to the 3D Visualization section** in the sidebar
2. **Click "Enable PyDeck 3D"** button
3. **Wait for initialization** - The 3D overlay will load
4. **Observe the new controls** that appear below

#### 3D Layer Types

##### Hexagon Aggregation
- **Purpose** - Spatial data aggregation and density visualization
- **Use Case** - Showing species distribution patterns
- **Controls** - Elevation scale, radius, opacity

##### Heatmap
- **Purpose** - Continuous surface representation of data intensity
- **Use Case** - Temperature, chlorophyll, or biomass distribution
- **Controls** - Intensity threshold, color scheme

##### Grid Layer
- **Purpose** - Regular grid-based data visualization
- **Use Case** - Environmental monitoring data
- **Controls** - Cell size, elevation factor

##### Contour Layer
- **Purpose** - Isolines and contour visualization
- **Use Case** - Bathymetry and depth contours
- **Controls** - Contour intervals, line thickness

##### 3D Column Layer
- **Purpose** - Vertical bar charts on map
- **Use Case** - Quantitative data by location
- **Controls** - Column height, color mapping

#### 3D Controls

##### View Controls
- **Camera Angle** - Adjust perspective (0-90 degrees)
- **Rotation** - Rotate view around center point
- **Zoom** - 3D zoom levels independent of 2D map

##### Data Controls
- **Layer Selection** - Choose which 3D layer to display
- **Color Scheme** - Select from predefined color palettes
- **Data Range** - Set min/max values for visualization

##### Performance Controls
- **Quality** - Adjust rendering quality vs. performance
- **Animation** - Enable/disable smooth transitions
- **Refresh Rate** - Control update frequency

#### Sample Data

The application includes demonstration data for 3D visualization:

##### Oceanographic Data
- **Temperature profiles** - 3D temperature distribution
- **Salinity measurements** - Water salinity gradients
- **Chlorophyll concentration** - Phytoplankton distribution
- **Bathymetry** - Seafloor depth and topography

##### Marine Biology Data
- **Species density** - Biodiversity hotspots
- **Biomass distribution** - Marine life abundance
- **Habitat suitability** - Environmental preferences

#### 3D Navigation

##### Mouse Controls in 3D
- **Rotate** - Right-click and drag
- **Pan** - Left-click and drag
- **Zoom** - Scroll wheel
- **Tilt** - Ctrl + drag up/down

##### Keyboard Shortcuts in 3D
- **R** - Reset to default view
- **F** - Fit to data extent
- **1-5** - Switch between preset views
- **Space** - Pause/resume animation

### Best Practices for 3D Visualization

#### Performance Optimization
- **Start Simple** - Begin with basic layer types
- **Limit Data Size** - Use data aggregation for large datasets
- **Monitor Performance** - Watch for slow rendering
- **Close When Not Needed** - Disable 3D to improve overall performance

#### Visual Design
- **Choose Appropriate Colors** - Use color schemes that enhance data clarity
- **Adjust Opacity** - Balance visibility with underlying data
- **Set Proper Scale** - Ensure 3D elements are appropriately sized

## Data Interaction

### Feature Selection

#### Clicking on Features

**Vector Features (BBT Areas):**
1. **Click on any colored polygon** on the map
2. **A popup window opens** with feature information
3. **View attributes** - Name, ID, area calculations
4. **Close popup** - Click the X or press Escape

**WMS Layers:**
- WMS layers support limited interaction
- Use the "Get Feature Info" tool for detailed information
- Results vary by layer complexity and server configuration

#### Feature Information Display

**Popup Content:**
- **Feature Name** - Human-readable identifier
- **Numeric Properties** - Area, depth, measurements
- **Categorical Data** - Habitat type, classification
- **Metadata** - Source, date, processing information

**Information Formatting:**
- **Area Calculations** - Displayed in km² with precision
- **Coordinates** - Shown in decimal degrees (WGS84)
- **Links** - External references when available

### Hover Interactions

#### Real-time Tooltips

**BBT Polygon Hover:**
- **Immediate Response** - Information appears instantly
- **Dynamic Calculation** - Area computed in real-time
- **Position Tracking** - Tooltip follows cursor
- **Clean Design** - Easy-to-read format

**Tooltip Content:**
- **Primary** - Feature name and area
- **Secondary** - Coordinates and additional properties
- **Formatted** - Numbers with appropriate units

#### Hover States

- **Visual Feedback** - Features highlight on hover
- **Color Changes** - Subtle highlighting indicates interaction
- **Cursor Changes** - Pointer cursor over interactive elements

### Data Export and Sharing

#### Downloading Data

**Vector Layer Export:**
1. **Use API endpoints** - Access raw GeoJSON data
2. **Browser Developer Tools** - Copy network responses
3. **External Tools** - Use REST API for programmatic access

**API Examples:**
```
# Get all vector layers
GET /api/vector/layers

# Get specific layer data
GET /api/vector/layer/Bbts%20-%20Merged

# Get layer with simplified geometry
GET /api/vector/layer/Bbts%20-%20Merged?simplify=0.001
```

#### Sharing Map Views

**URL Sharing:**
- **Current View** - Browser URL updates with map position
- **Bookmark Links** - Save current map state
- **Direct Links** - Share specific BBT areas

**Screenshot Capture:**
- **Browser Tools** - Use browser screenshot functionality
- **Print Feature** - Print map view to PDF
- **Screen Capture** - Use system screenshot tools

### Search and Discovery

#### Finding Features

**Visual Search:**
1. **Use BBT quick navigation** for known areas
2. **Pan and zoom** to explore regions
3. **Enable multiple layers** to see relationships

**Layer Filtering:**
- **Toggle layers** to isolate specific data types
- **Adjust opacity** to see through overlays
- **Use basemap changes** to highlight features

#### Data Discovery

**Exploration Workflow:**
1. **Start with overview** - Use default European view
2. **Select study area** - Click BBT navigation buttons
3. **Enable relevant layers** - Turn on appropriate overlays
4. **Interact with features** - Click and hover for details
5. **Adjust visualization** - Modify opacity and basemaps

## Advanced Features

### Layer Combination Strategies

#### Effective Layer Combinations

**Marine Habitat Analysis:**
- **Base** - Ocean basemap
- **Overlay 1** - EUSeaMap Biological Zones (60% opacity)
- **Overlay 2** - Substrate Types (40% opacity)
- **Interactive** - BBT vector boundaries

**Environmental Assessment:**
- **Base** - Satellite imagery
- **Overlay 1** - HELCOM pressure data (70% opacity)
- **Overlay 2** - Protection zones (50% opacity)
- **Interactive** - BBT areas for reference

**Research Planning:**
- **Base** - Light gray (minimal distraction)
- **Overlay 1** - Confidence layers (80% opacity)
- **Overlay 2** - Energy zones (30% opacity)
- **Interactive** - BBT study areas

#### Opacity Best Practices

**Single Layer Display:**
- **WMS Overlays** - 80-90% opacity for clear visibility
- **Multiple Overlays** - 50-70% each to avoid obscuring

**Layer Stacking:**
- **Bottom Layer** - Higher opacity (70-80%)
- **Top Layer** - Lower opacity (40-60%)
- **Interactive Features** - Always at 100% for clear interaction

### Custom Workflows

#### Research Workflow

**1. Project Planning:**
- Start with BBT area navigation
- Enable relevant habitat layers
- Assess data quality using confidence layers
- Document coordinates and extent

**2. Data Collection:**
- Use API endpoints for data export
- Combine with external datasets
- Validate using map visualization

**3. Analysis and Reporting:**
- Create screenshots for documentation
- Use feature information for reporting
- Cross-reference with external sources

#### Educational Use

**1. Teaching Marine Ecology:**
- Demonstrate habitat distribution patterns
- Show human impact through HELCOM layers
- Compare different European marine environments

**2. Student Projects:**
- Assign specific BBT areas for investigation
- Encourage layer combination experimentation
- Promote data interpretation skills

#### Management Applications

**1. Conservation Planning:**
- Identify high-value habitat areas
- Assess protection coverage
- Plan monitoring transects

**2. Impact Assessment:**
- Overlay pressure data with sensitive areas
- Evaluate cumulative effects
- Support management decisions

### Integration with External Tools

#### GIS Software Integration

**QGIS Integration:**
```
# Add WMS layers to QGIS
1. Layer → Add Layer → Add WMS/WMTS Layer
2. Create new connection
3. URL: https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms
4. Connect and add layers
```

**ArcGIS Integration:**
```
# Add EMODnet services
1. Add Data → Add Data from Web → WMS Server
2. Server URL: https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms
3. Add desired layers to map
```

#### API Integration

**Python Example:**
```python
import requests
import geopandas as gpd

# Get BBT data
response = requests.get('http://localhost:5000/api/vector/layer/Bbts%20-%20Merged')
geojson_data = response.json()

# Convert to GeoDataFrame
gdf = gpd.GeoDataFrame.from_features(geojson_data['features'])
print(f"Loaded {len(gdf)} BBT features")
```

**JavaScript Example:**
```javascript
// Fetch layer data
async function loadBBTData() {
    const response = await fetch('/api/vector/layer/Bbts%20-%20Merged');
    const geojson = await response.json();

    // Process data
    console.log(`Features: ${geojson.features.length}`);
    return geojson;
}
```

### Power User Tips

#### Keyboard Shortcuts

- **Tab** - Cycle through interactive elements
- **Ctrl + Mouse Wheel** - Fine zoom control
- **Shift + Click** - Multi-selection (where supported)
- **Alt + Click** - Alternative action context

#### Browser Developer Tools

**Console Commands:**
```javascript
// Get current map center
map.getCenter()

// Get current zoom level
map.getZoom()

// List active layers
map.eachLayer(layer => console.log(layer))
```

**Network Analysis:**
- Monitor API calls in Network tab
- Check response times and data sizes
- Debug connection issues

#### Performance Optimization

**For Large Datasets:**
- Use simplified geometry parameters
- Limit concurrent layer loading
- Close unused browser tabs
- Clear browser cache periodically

**For Slow Connections:**
- Start with vector layers (faster loading)
- Load WMS layers selectively
- Use lighter basemaps
- Reduce layer opacity for faster rendering

## Tips and Best Practices

### Getting the Best Experience

#### Browser Optimization

**Memory Management:**
- **Close unused tabs** - Frees memory for map rendering
- **Clear cache periodically** - Ensures fresh data loading
- **Disable unnecessary extensions** - Reduces resource conflicts
- **Use hardware acceleration** - Enable in browser settings

**Display Settings:**
- **Use larger screens** - Better for detailed analysis
- **Adjust zoom appropriately** - Balance detail with performance
- **Consider color blindness** - Use appropriate basemaps

#### Data Interpretation

**Understanding WMS Data:**
- **Check metadata** - Understand data sources and dates
- **Consider scale** - Some data is valid only at certain zoom levels
- **Validate with ground truth** - Cross-reference with field data

**Vector Data Quality:**
- **Check feature boundaries** - Ensure appropriate detail level
- **Understand projections** - All data normalized to WGS84
- **Consider temporal aspects** - Data represents specific time periods

#### Workflow Efficiency

**Planning Your Analysis:**
1. **Define objectives** - Know what you're looking for
2. **Select appropriate layers** - Choose relevant data types
3. **Use systematic approach** - Work methodically through areas
4. **Document findings** - Take screenshots and notes

**Collaborative Work:**
- **Share URLs** - Bookmark specific views
- **Coordinate layer settings** - Use consistent opacity and combinations
- **Document procedures** - Record successful workflows

### Common Use Cases

#### Marine Research

**Habitat Mapping:**
- Combine substrate and biological zone layers
- Use BBT areas as reference points
- Cross-validate with confidence layers

**Species Distribution Studies:**
- Overlay environmental layers with species data
- Use 3D visualization for oceanographic context
- Analyze patterns across multiple BBT areas

**Impact Assessment:**
- Enable HELCOM pressure layers
- Compare with sensitive habitat areas
- Assess cumulative effects

#### Education and Outreach

**Classroom Demonstrations:**
- Use projector-friendly basemaps
- Prepare specific layer combinations
- Practice navigation beforehand

**Student Assignments:**
- Assign specific BBT areas to groups
- Provide guided discovery questions
- Encourage hypothesis formation

**Public Engagement:**
- Focus on visually striking combinations
- Explain layer meanings clearly
- Relate to local areas when possible

#### Policy and Management

**Conservation Planning:**
- Identify priority areas using habitat data
- Assess protection gaps
- Plan monitoring networks

**Environmental Impact Assessment:**
- Overlay development plans with habitat maps
- Use pressure data for cumulative assessment
- Document baseline conditions

**International Cooperation:**
- Use consistent datasets across borders
- Facilitate data sharing discussions
- Support policy development

### Data Quality Considerations

#### Understanding Limitations

**WMS Data:**
- **Scale Dependencies** - Some layers valid only at specific zoom levels
- **Temporal Currency** - Check data collection dates
- **Processing Effects** - Understand classification methodologies
- **Server Dependencies** - External services may be temporarily unavailable

**Vector Data:**
- **Spatial Accuracy** - Based on survey methods and GPS precision
- **Attribute Completeness** - Not all features have complete attribute data
- **Update Frequency** - Local data may not reflect recent changes

#### Quality Indicators

**Confidence Layers:**
- Use confidence overlays to assess data reliability
- Higher confidence areas suitable for detailed analysis
- Lower confidence areas require additional verification

**Visual Quality Checks:**
- Look for obvious errors or inconsistencies
- Compare overlapping datasets for agreement
- Validate against known reference points

## Troubleshooting

### Common Issues and Solutions

#### Loading Problems

**Symptoms:** Layers don't appear or load indefinitely

**Solutions:**
1. **Check internet connection** - Ensure stable connectivity
2. **Refresh the page** - Clear temporary loading states
3. **Try different layers** - Test if issue is layer-specific
4. **Check browser console** - Look for error messages
5. **Disable browser extensions** - Eliminate conflicts

#### Performance Issues

**Symptoms:** Slow map response, choppy animations

**Solutions:**
1. **Reduce active layers** - Disable unnecessary overlays
2. **Lower opacity** - Reduce rendering complexity
3. **Close other applications** - Free up system resources
4. **Use simpler basemaps** - Switch to Light Gray basemap
5. **Restart browser** - Clear memory leaks

#### Display Problems

**Symptoms:** Incorrect colors, missing features, alignment issues

**Solutions:**
1. **Clear browser cache** - Remove corrupted cached data
2. **Update browser** - Ensure latest version compatibility
3. **Check zoom level** - Some features only visible at certain scales
4. **Try different basemap** - Isolate display issues
5. **Reset to default view** - Use home button to restore

#### Interaction Issues

**Symptoms:** Clicks don't register, tooltips don't appear

**Solutions:**
1. **Check layer order** - Ensure interactive layers are on top
2. **Verify layer activation** - Confirm layers are enabled
3. **Try different areas** - Test with known interactive features
4. **Disable pop-up blockers** - Allow application popups
5. **Use keyboard navigation** - Try alternative interaction methods

### Error Messages

#### Common Error Types

**"Layer failed to load"**
- **Cause** - External WMS service unavailable
- **Solution** - Try again later or use alternative layers

**"Vector support not available"**
- **Cause** - Missing backend dependencies
- **Solution** - Contact administrator for system configuration

**"Connection timeout"**
- **Cause** - Slow internet or server issues
- **Solution** - Check connection and retry

**"Invalid coordinates"**
- **Cause** - Navigation to unsupported area
- **Solution** - Return to valid geographic bounds

#### Getting Help

**Self-Help Resources:**
1. **Refresh and retry** - Many issues resolve with page refresh
2. **Check browser compatibility** - Use recommended browsers
3. **Review this guide** - Reference relevant sections
4. **Try basic functionality** - Test with default settings

**Technical Support:**
- **Document the issue** - Note exact error messages
- **Record steps** - What you were doing when error occurred
- **Check system requirements** - Verify browser and system compatibility
- **Contact administrators** - Provide detailed problem description

### Browser-Specific Issues

#### Chrome
- **Memory usage** - Monitor tab memory in Task Manager
- **Extensions** - Disable ad blockers and privacy extensions
- **Hardware acceleration** - Enable in Settings > Advanced

#### Firefox
- **Tracking protection** - Disable for application domain
- **WebGL** - Ensure WebGL is enabled for 3D features
- **Memory management** - Restart browser if performance degrades

#### Safari
- **Pop-up settings** - Allow popups for application domain
- **Cross-origin requests** - Ensure CORS is properly configured
- **Cache management** - Clear website data if needed

#### Edge
- **Compatibility mode** - Ensure modern Edge, not legacy
- **Security settings** - Allow JavaScript and mixed content
- **Extension conflicts** - Disable unnecessary extensions

## FAQ

### General Questions

**Q: Do I need to create an account to use the application?**
A: No, the application is freely accessible without registration or login.

**Q: Can I use this application on mobile devices?**
A: The application is optimized for desktop browsers but basic functionality works on tablets. Phone screens may be too small for optimal use.

**Q: Is this application free to use?**
A: Yes, the MARBEFES BBT Database is freely available for research, education, and non-commercial use.

**Q: How current is the data?**
A: EMODnet data is regularly updated. Check individual layer descriptions for specific dates. BBT vector data reflects the current project survey areas.

### Technical Questions

**Q: Why do some layers load slowly?**
A: WMS layers are loaded from external servers and depend on internet speed and server performance. Vector layers are typically faster as they're served locally.

**Q: Can I download the data for offline use?**
A: Vector data can be accessed via API endpoints. WMS data is available through standard WMS requests. See the API documentation for details.

**Q: Why do some areas appear blank on certain layers?**
A: Not all layers have global coverage. EMODnet focuses on European seas, and some specialized layers cover only specific regions.

**Q: How accurate are the area calculations?**
A: Area calculations use geodesic methods for high accuracy. Values are computed in real-time using the WGS84 coordinate system.

### Data Questions

**Q: What does "confidence" mean in the habitat layers?**
A: Confidence indicates the statistical certainty of habitat predictions. Higher confidence areas have more reliable classification.

**Q: How do I cite this data in publications?**
A: Cite the MARBEFES project and EMODnet as data sources. Specific citation formats are available in the project documentation.

**Q: Can I contribute additional data layers?**
A: Contact the MARBEFES project team to discuss data contribution opportunities and requirements.

**Q: What coordinate system is used?**
A: All data is displayed in WGS84 (EPSG:4326). Source data may be reprojected for consistency.

### Feature Questions

**Q: How do I enable 3D visualization?**
A: Scroll to the 3D Visualization section in the sidebar and click "Enable PyDeck 3D". Note that 3D features require modern browsers and good graphics support.

**Q: Can I save my map settings?**
A: Browser bookmarks will save the current map position. Layer settings reset when the page is refreshed.

**Q: Why don't all layers appear at all zoom levels?**
A: Some WMS layers have scale dependencies and only appear within certain zoom ranges. This is controlled by the data provider.

**Q: How do I report bugs or suggest improvements?**
A: Contact the development team through the project website or repository issue tracker.

### Integration Questions

**Q: Can I embed this map in my website?**
A: Contact the project team for embedding permissions and technical guidance.

**Q: Is there a mobile app version?**
A: Currently, only the web version is available. The responsive design works on tablets and larger mobile devices.

**Q: Can I use this data in GIS software?**
A: Yes, WMS layers can be added to QGIS, ArcGIS, and other GIS software. Vector data is available via API endpoints.

**Q: Are there usage limitations?**
A: The application is designed for research and educational use. High-volume automated access should be coordinated with administrators.

---

This user guide provides comprehensive coverage of the MARBEFES BBT Database web interface. For additional technical information, refer to the [API Documentation](API.md) or [Developer Guide](DEVELOPER.md).

**Project Information:**
- **Website:** [marbefes.eu](https://marbefes.eu)
- **Grant:** Horizon Europe Grant Agreement No. 101060937
- **CORDIS:** [Project Page](https://cordis.europa.eu/project/id/101060937)

**Data Sources:**
- **EMODnet:** [European Marine Observation and Data Network](https://emodnet.eu)
- **HELCOM:** [Helsinki Commission](https://helcom.fi)
- **MARBEFES:** Marine Biodiversity and Ecosystem Functioning project data