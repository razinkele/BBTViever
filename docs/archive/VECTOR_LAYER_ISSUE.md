# Vector Layer Loading Issue - Technical Report

**Date:** October 13, 2025
**Status:** ⚠️ Known Issue - Workaround Implemented
**Impact:** BBT vector layers cannot load - Basemap functionality unaffected

## Summary

The MARBEFES BBT application experiences a segmentation fault when attempting to load the `BBT.gpkg` vector file. The issue is caused by a GDAL/pyogrio/fiona library incompatibility that causes Python to crash at the C extension level.

## Technical Details

### Error Description
```
Segmentation fault (core dumped)
```

This occurs during `geopandas.read_file()` operations on `data/vector/BBT.gpkg`.

### Root Cause Analysis

**Primary Issue:** GDAL library incompatibility with 3D geometry types in GeoPackage format

**Contributing Factors:**
1. **3D Geometry**: Original BBT.gpkg contains `3D Multi Polygon` geometries
2. **Library Versions**:
   - pandas: 2.0.3 (downgraded from 2.2.3 due to other compatibility issues)
   - pyogrio: 0.11.1
   - geopandas: 1.1.1
   - fiona: 1.10.1
3. **System GDAL**: Version mismatch between system GDAL and Python bindings

### Diagnostic Steps Performed

1. **Tested pandas 2.2.3**: Different error (`TypeError: Cannot convert numpy.ndarray to numpy.ndarray`)
2. **Reverted to pandas 2.0.3**: Segmentation fault persists
3. **Tested fiona engine**: Segmentation fault
4. **Tested pyogrio engine**: Segmentation fault
5. **Created 2D version**: Used `ogr2ogr` to convert 3D→2D geometry - still segfaults
6. **Tested without geometry**: Even `ignore_geometry=True` causes crash

### File Information

**Original File:** `data/vector/BBT.gpkg`
```
Layer name: merged
Geometry: 3D Multi Polygon
Feature Count: 11
CRS: ETRS89-extended / LAEA Europe (EPSG:3035)
```

**Attempted Fix:** `data/vector/BBT_fixed.gpkg`
- Converted to 2D Multi Polygon
- Still causes segmentation fault

## Current Workaround

**Solution:** Temporarily disable vector layer loading by renaming GPKG files

**Files Renamed:**
```bash
data/vector/BBT.gpkg → data/vector/BBT.gpkg.broken
data/vector/BBT_fixed.gpkg → data/vector/BBT_fixed.gpkg.broken
```

**Result:** Application starts successfully without vector layers

## Impact Assessment

### ✅ **Unaffected Functionality**
- All basemap functionality (5 basemaps)
- WMS layers (265 EMODnet layers)
- HELCOM layers (218 layers)
- All basemap test suite (26/26 tests passing)
- Main map viewer
- Legend display
- Layer switching
- UI controls

### ❌ **Affected Functionality**
- BBT vector layer visualization
- BBT area hover tooltips
- BBT area calculations
- BBT navigation zoom (buttons show 404 errors but don't crash)

## Recommended Solutions

### Option 1: Upgrade System GDAL (Recommended)
```bash
# Update system GDAL to latest stable
sudo apt-get update
sudo apt-get install --upgrade gdal-bin libgdal-dev

# Reinstall Python bindings to match
pip install --force-reinstall --no-binary :all: GDAL==$(gdal-config --version)
pip install --force-reinstall pyogrio fiona geopandas
```

**Risk:** May affect other geospatial applications on the system

### Option 2: Use Conda Environment
```bash
# Create isolated conda environment with matching versions
conda create -n marbefes python=3.10
conda activate marbefes
conda install -c conda-forge geopandas=1.1.1 pyogrio=0.11.1 pandas=2.2.3

# Test in this environment
```

**Benefit:** Isolated from system libraries

### Option 3: Export to Alternative Format
```bash
# Export BBT data to GeoJSON (more compatible)
ogr2ogr -f "GeoJSON" data/vector/BBT.geojson data/vector/BBT.gpkg.broken -nlt MULTIPOLYGON -dim XY

# Update vector_loader.py to support GeoJSON
```

**Benefit:** GeoJSON is more widely compatible

### Option 4: Use PostGIS Database
```bash
# Load data into PostGIS
ogr2ogr -f "PostgreSQL" PG:"dbname=marbefes" data/vector/BBT.gpkg.broken

# Update application to read from PostGIS
```

**Benefit:** Enterprise-grade, no file corruption issues

## Testing Procedure

After implementing a solution, test with:

```python
import geopandas as gpd

# Test basic loading
gdf = gpd.read_file('data/vector/BBT.gpkg', layer='merged')
print(f"Loaded {len(gdf)} features")
print(f"CRS: {gdf.crs}")
print(f"Geometry types: {gdf.geometry.geom_type.unique()}")

# Test conversion to GeoJSON
geojson = gdf.__geo_interface__
print(f"GeoJSON features: {len(geojson['features'])}")
```

If this runs without crashing, the issue is resolved.

## Temporary Status

**Current State:**
✅ Application running at http://localhost:5000
✅ All basemap tests passing
✅ WMS/HELCOM layers functional
❌ BBT vector layers disabled

**For Users:**
- Basemap functionality works perfectly
- WMS habitat layers display correctly
- BBT buttons will show "Layer not found" errors (non-critical)
- All other features operational

## Long-term Resolution

This issue requires system-level library updates or environment reconfiguration. The current workaround allows all basemap functionality to work while vector layer support is investigated separately.

**Priority:** Medium (affects BBT-specific features only)
**Complexity:** High (requires system library management)
**Time Estimate:** 2-4 hours for proper GDAL environment setup

## Related Files

- `data/vector/BBT.gpkg.broken` - Original problematic file
- `data/vector/BBT_fixed.gpkg.broken` - Attempted 2D fix
- `src/emodnet_viewer/utils/vector_loader.py` - Vector loading code
- `flask_final.log` - Current server logs

## References

- GeoPackage 3D geometry spec: https://www.geopackage.org/spec/
- GDAL Python bindings: https://gdal.org/api/python.html
- PyOGRIO issues: https://github.com/geopandas/pyogrio/issues
- Similar issue reports: pandas + pyogrio segfaults with certain GPKG files

---

**Last Updated:** October 13, 2025
**Next Review:** When system GDAL can be safely upgraded
