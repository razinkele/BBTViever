# Data Directory

This directory contains geospatial data files that are automatically loaded by the EMODnet Viewer application.

## Directory Structure

- `vector/` - GeoPackage (.gpkg) files containing vector data
- `examples/` - Example GPKG files for testing

## Supported Formats

### GeoPackage (.gpkg) Files

The application automatically discovers and loads GeoPackage files from the `vector/` subdirectory.

**Supported geometry types:**
- Polygon (recommended for area maps)
- MultiPolygon
- LineString
- MultiLineString
- Point
- MultiPoint

## File Requirements

### Naming Convention
- Files should have descriptive names (e.g., `marine_protected_areas.gpkg`)
- Avoid spaces and special characters
- Use underscores for word separation

### Spatial Reference
- Data should be in WGS84 (EPSG:4326) for optimal display
- Other coordinate systems will be reprojected automatically if possible

### Layer Structure
- Each GPKG file can contain multiple layers
- Layers with area geometries (Polygon/MultiPolygon) will be styled as filled areas
- Other geometry types will be styled appropriately

## Styling

The application automatically applies styling based on geometry type:

- **Area features (Polygons)**: Semi-transparent fill with colored border
- **Line features**: Colored lines with appropriate width
- **Point features**: Circular markers with appropriate size

## Adding Data

1. Place your `.gpkg` files in the `vector/` subdirectory
2. Restart the application to load new files
3. Vector layers will appear in the layer selection panel

## Example Data Sources

You can obtain GPKG data from:
- **EMODnet Data Portals**: Various marine datasets
- **Natural Earth**: Administrative boundaries and features
- **OpenStreetMap**: Extract and convert data to GPKG
- **GBIF**: Biodiversity occurrence data
- **Marine Protected Areas databases**

## Troubleshooting

If layers don't appear:
1. Check file format is valid GPKG
2. Ensure coordinate system is supported
3. Verify layer names don't contain special characters
4. Check application logs for error messages

## Performance Considerations

- Large files (>50MB) may affect loading times
- Complex geometries may impact rendering performance
- Consider simplifying geometries for web display if needed