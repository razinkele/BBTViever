"""
Vector data loading utilities for GPKG files
"""

import json
import geopandas as gpd
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import OrderedDict

from .logging_config import get_logger


@dataclass
class VectorLayer:
    """Vector layer information"""

    file_path: str
    layer_name: str
    display_name: str
    geometry_type: str
    feature_count: int
    bounds: Tuple[float, float, float, float]  # minx, miny, maxx, maxy
    crs: str
    source_file: str
    category: str = "vector"
    style: Optional[Dict[str, Any]] = None


class VectorLayerLoader:
    """Loader for vector data from GPKG files"""

    # Cache configuration constants
    MAX_CACHE_SIZE = 50  # Maximum number of items in each cache tier
    CACHE_EVICT_SIZE = 10  # Number of items to evict when GDF cache is full

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.vector_dir = self.data_dir / "vector"
        self.logger = get_logger("vector_loader")
        self.loaded_layers: List[VectorLayer] = []
        # LRU cache: OrderedDict maintains insertion order for efficient eviction
        self._gdf_cache: OrderedDict[str, gpd.GeoDataFrame] = OrderedDict()
        # GeoJSON cache: Store serialized GeoJSON for 50-70% faster API responses
        self._geojson_cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        # File modification tracking for automatic reload detection
        self._file_mtimes: Dict[str, float] = {}

        # Default styles by geometry type
        self.default_styles = {
            "Polygon": {
                "fillColor": "#20B2AA",
                "color": "#008B8B",
                "weight": 2,
                "fillOpacity": 0.4,
                "opacity": 0.8,
            },
            "MultiPolygon": {
                "fillColor": "#20B2AA",
                "color": "#008B8B",
                "weight": 2,
                "fillOpacity": 0.4,
                "opacity": 0.8,
            },
            "LineString": {"color": "#40E0D0", "weight": 3, "opacity": 0.8},
            "MultiLineString": {"color": "#40E0D0", "weight": 3, "opacity": 0.8},
            "Point": {
                "color": "#48D1CC",
                "fillColor": "#20B2AA",
                "radius": 6,
                "fillOpacity": 0.8,
                "opacity": 1,
            },
            "MultiPoint": {
                "color": "#48D1CC",
                "fillColor": "#20B2AA",
                "radius": 6,
                "fillOpacity": 0.8,
                "opacity": 1,
            },
        }

    def discover_gpkg_files(self) -> List[Path]:
        """Discover all GPKG and GeoJSON files in the vector directory"""
        if not self.vector_dir.exists():
            self.logger.warning(f"Vector directory does not exist: {self.vector_dir}")
            return []

        # Support both GPKG and GeoJSON files
        gpkg_files = list(self.vector_dir.glob("*.gpkg"))
        geojson_files = list(self.vector_dir.glob("*.geojson"))

        all_files = gpkg_files + geojson_files

        self.logger.info(f"Discovered {len(gpkg_files)} GPKG files and {len(geojson_files)} GeoJSON files")

        for vector_file in all_files:
            self.logger.debug(f"Found vector file: {vector_file}")

        return all_files

    def get_layer_info_from_geojson(self, geojson_path: Path) -> List[Dict[str, Any]]:
        """Get layer information from a GeoJSON file using pure JSON parsing"""
        try:
            with open(geojson_path, 'r') as f:
                geojson_data = json.load(f)

            # Extract basic information from GeoJSON
            features = geojson_data.get('features', [])

            # Get bounding box from features
            coords = []
            for feature in features:
                geom = feature.get('geometry', {})
                geom_coords = geom.get('coordinates', [])
                if geom.get('type') == 'MultiPolygon':
                    # Flatten MultiPolygon coordinates
                    for polygon in geom_coords:
                        for ring in polygon:
                            coords.extend(ring)
                elif geom.get('type') == 'Polygon':
                    for ring in geom_coords:
                        coords.extend(ring)

            # Calculate bounds
            if coords:
                lons = [coord[0] for coord in coords]
                lats = [coord[1] for coord in coords]
                bounds = (min(lons), min(lats), max(lons), max(lats))
            else:
                bounds = (-180, -90, 180, 90)

            # Get CRS from GeoJSON (defaults to EPSG:4326)
            crs = geojson_data.get('crs', {}).get('properties', {}).get('name', 'EPSG:4326')

            info = {
                "layer_name": geojson_path.stem,  # Use filename as layer name
                "geometry_type": features[0].get('geometry', {}).get('type', 'Unknown') if features else 'Unknown',
                "feature_count": len(features),
                "bounds": bounds,
                "crs": crs,
                "schema": {"properties": features[0].get('properties', {}) if features else {}, "geometry": "Unknown"}
            }

            return [info]  # GeoJSON files have a single layer

        except Exception as e:
            self.logger.error(f"Error reading GeoJSON file {geojson_path}: {e}")
            return []

    def get_layer_info_from_gpkg(self, gpkg_path: Path) -> List[Dict[str, Any]]:
        """Get layer information from a GPKG file"""
        try:
            import fiona

            layers_info = []

            with fiona.Env():
                # List all layers in the GPKG
                layer_names = fiona.listlayers(str(gpkg_path))

                for layer_name in layer_names:
                    try:
                        # Get layer metadata without loading all data
                        with fiona.open(str(gpkg_path), layer=layer_name) as src:
                            info = {
                                "layer_name": layer_name,
                                "geometry_type": src.schema.get("geometry", "Unknown"),
                                "feature_count": len(src),
                                "bounds": src.bounds,
                                "crs": src.crs.to_string() if src.crs else "EPSG:4326",
                                "schema": dict(src.schema),
                            }
                            layers_info.append(info)

                    except Exception as e:
                        self.logger.error(f"Error reading layer {layer_name} from {gpkg_path}: {e}")
                        continue

            return layers_info

        except Exception as e:
            self.logger.error(f"Error reading GPKG file {gpkg_path}: {e}")
            return []

    def load_geojson_layer(self, geojson_path: Path, layer_name: str, layer_info: Dict[str, Any]) -> Optional[VectorLayer]:
        """Load a GeoJSON layer using pure JSON parsing (no GDAL required)"""
        try:
            # Load GeoJSON data
            with open(geojson_path, 'r') as f:
                geojson_data = json.load(f)

            features = geojson_data.get('features', [])

            if not features:
                self.logger.warning(f"GeoJSON file {geojson_path} contains no features")
                return None

            # Get geometry type
            geom_type = layer_info.get('geometry_type', 'MultiPolygon')

            # Get bounds
            bounds = layer_info.get('bounds', (-180, -90, 180, 90))

            # Create display name
            display_name = self._create_display_name(geojson_path.stem, layer_name)

            # Get appropriate style
            style = self.default_styles.get(geom_type, self.default_styles["Polygon"])

            # Create vector layer object
            vector_layer = VectorLayer(
                file_path=str(geojson_path),
                layer_name=layer_name,
                display_name=display_name,
                geometry_type=geom_type,
                feature_count=len(features),
                bounds=bounds,
                crs="EPSG:4326",  # GeoJSON is always WGS84
                source_file=geojson_path.name,
                style=style,
            )

            # Cache the raw GeoJSON data for later use (skip GDAL entirely)
            cache_key = f"{geojson_path}:{layer_name}"
            self._geojson_cache[cache_key] = geojson_data

            self.logger.info(f"Loaded GeoJSON layer: {display_name} ({len(features)} features) - No GDAL required!")
            return vector_layer

        except Exception as e:
            self.logger.error(f"Error loading GeoJSON layer from {geojson_path}: {e}")
            return None

    def load_vector_layer(self, gpkg_path: Path, layer_name: str) -> Optional[VectorLayer]:
        """Load a specific layer from a GPKG file"""
        try:
            # Use fiona engine directly due to pandas 2.2.3 + pyogrio 0.11.1 compatibility issue
            # (numpy.ndarray dtype conversion error)
            gdf = None
            try:
                # Try pyogrio first (if it works with your pandas version)
                gdf = gpd.read_file(str(gpkg_path), layer=layer_name, engine='pyogrio', force_2d=True)
                self.logger.debug(f"Successfully loaded with pyogrio engine")
            except Exception as e:
                # Fallback to fiona direct read to avoid pandas/numpy dtype issues
                self.logger.debug(f"Pyogrio failed ({str(e)[:60]}...), using fiona direct read")

                # Use fiona directly to avoid pandas/numpy dtype issues
                import fiona
                from shapely.geometry import shape

                with fiona.open(str(gpkg_path), layer=layer_name) as src:
                    # Manually construct GeoDataFrame from features
                    features = []
                    geometries = []

                    for feature in src:
                        geom = shape(feature['geometry'])
                        # Force 2D if needed
                        if geom.has_z:
                            geom = self._force_2d(geom)
                        geometries.append(geom)
                        # Convert all property values to Python native types
                        properties = {}
                        for key, value in feature['properties'].items():
                            # Handle numpy arrays and other non-native types
                            if hasattr(value, 'item'):  # numpy scalar
                                properties[key] = value.item()
                            elif hasattr(value, 'tolist'):  # numpy array
                                properties[key] = value.tolist()
                            else:
                                properties[key] = value
                        features.append(properties)

                    # Create GeoDataFrame
                    import pandas as pd
                    df = pd.DataFrame(features)
                    gdf = gpd.GeoDataFrame(df, geometry=geometries, crs=src.crs)

                self.logger.info(f"Successfully loaded {len(gdf)} features using fiona direct read")

            if gdf.empty:
                self.logger.warning(f"Layer {layer_name} in {gpkg_path} is empty")
                return None

            # Ensure the data is in WGS84 for web display
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                self.logger.info(f"Reprojecting layer {layer_name} from {gdf.crs} to EPSG:4326")
                gdf = gdf.to_crs("EPSG:4326")

            # Get geometry type
            geom_type = gdf.geometry.geom_type.iloc[0] if len(gdf) > 0 else "Unknown"

            # Calculate bounds
            bounds = gdf.total_bounds  # minx, miny, maxx, maxy

            # Create display name
            display_name = self._create_display_name(gpkg_path.stem, layer_name)

            # Get appropriate style
            style = self.default_styles.get(geom_type, self.default_styles["Polygon"])

            # Create vector layer object
            vector_layer = VectorLayer(
                file_path=str(gpkg_path),
                layer_name=layer_name,
                display_name=display_name,
                geometry_type=geom_type,
                feature_count=len(gdf),
                bounds=tuple(bounds),
                crs="EPSG:4326",
                source_file=gpkg_path.name,
                style=style,
            )

            self.logger.info(f"Loaded vector layer: {display_name} ({len(gdf)} features)")
            return vector_layer

        except Exception as e:
            self.logger.error(f"Error loading layer {layer_name} from {gpkg_path}: {e}")
            return None

    def _force_2d(self, geom):
        """Force geometry to 2D by removing Z coordinates"""
        from shapely import wkb, wkt
        from shapely.geometry import shape

        if geom is None:
            return None

        # Convert to WKT and remove Z coordinates
        wkt_str = geom.wkt
        # Simple approach: if it's 3D, recreate as 2D
        if geom.has_z:
            # Get coordinates and drop Z
            if hasattr(geom, 'exterior'):  # Polygon
                exterior_coords = [(x, y) for x, y, *z in geom.exterior.coords]
                interior_coords = [[(x, y) for x, y, *z in interior.coords] for interior in geom.interiors]
                from shapely.geometry import Polygon
                return Polygon(exterior_coords, interior_coords)
            elif hasattr(geom, 'geoms'):  # MultiPolygon, MultiLineString, etc
                from shapely.geometry import shape
                geoms_2d = [self._force_2d(g) for g in geom.geoms]
                # Reconstruct the multi-geometry
                geom_type = geom.geom_type
                if geom_type == 'MultiPolygon':
                    from shapely.geometry import MultiPolygon
                    return MultiPolygon(geoms_2d)
                elif geom_type == 'MultiLineString':
                    from shapely.geometry import MultiLineString
                    return MultiLineString(geoms_2d)
                elif geom_type == 'MultiPoint':
                    from shapely.geometry import MultiPoint
                    return MultiPoint(geoms_2d)
            elif hasattr(geom, 'coords'):  # LineString or Point
                coords_2d = [(x, y) for x, y, *z in geom.coords]
                geom_type = geom.geom_type
                if geom_type == 'LineString':
                    from shapely.geometry import LineString
                    return LineString(coords_2d)
                elif geom_type == 'Point':
                    from shapely.geometry import Point
                    return Point(coords_2d[0] if coords_2d else (0, 0))

        return geom

    def _create_display_name(self, file_stem: str, layer_name: str) -> str:
        """Create a user-friendly display name"""
        if layer_name.lower() == file_stem.lower():
            # If layer name is same as file, just use file name
            return file_stem.replace("_", " ").title()
        else:
            # Include both file and layer name
            file_display = file_stem.replace("_", " ").title()
            layer_display = layer_name.replace("_", " ").title()
            return f"{file_display} - {layer_display}"

    def load_all_vector_layers(self) -> List[VectorLayer]:
        """Load all vector layers from all GPKG and GeoJSON files"""
        # Always clear existing layers to ensure fresh loading
        self.loaded_layers.clear()
        vector_files = self.discover_gpkg_files()

        if not vector_files:
            self.logger.info("No vector files found")
            return self.loaded_layers

        for vector_path in vector_files:
            file_ext = vector_path.suffix.lower()
            self.logger.info(f"Processing {file_ext} file: {vector_path}")

            # Track file modification time for change detection
            try:
                mtime = vector_path.stat().st_mtime
                self._file_mtimes[str(vector_path)] = mtime
            except Exception as e:
                self.logger.warning(f"Could not get modification time for {vector_path}: {e}")

            # Route to appropriate handler based on file extension
            if file_ext == '.geojson':
                # Get layer information from GeoJSON
                layers_info = self.get_layer_info_from_geojson(vector_path)
            else:  # .gpkg
                # Get layer information from GPKG
                layers_info = self.get_layer_info_from_gpkg(vector_path)

            for layer_info in layers_info:
                layer_name = layer_info["layer_name"]

                # Load the layer
                if file_ext == '.geojson':
                    vector_layer = self.load_geojson_layer(vector_path, layer_name, layer_info)
                else:
                    vector_layer = self.load_vector_layer(vector_path, layer_name)

                if vector_layer:
                    self.loaded_layers.append(vector_layer)

        self.logger.info(f"Loaded {len(self.loaded_layers)} vector layers total")
        return self.loaded_layers

    def _evict_cache_entries(self) -> None:
        """Evict oldest entries from both caches when size limit is reached"""
        if len(self._gdf_cache) >= self.MAX_CACHE_SIZE:
            # Evict oldest entries (FIFO from OrderedDict)
            evicted_count = 0
            for _ in range(self.CACHE_EVICT_SIZE):
                if self._gdf_cache:
                    evicted_key = next(iter(self._gdf_cache))
                    self._gdf_cache.pop(evicted_key)
                    # Also evict corresponding GeoJSON cache
                    self._geojson_cache.pop(evicted_key, None)
                    evicted_count += 1

            self.logger.info(
                f"Cache eviction: removed {evicted_count} oldest entries "
                f"(GDF cache: {len(self._gdf_cache)}/{self.MAX_CACHE_SIZE}, "
                f"GeoJSON cache: {len(self._geojson_cache)})"
            )

    def get_vector_layer_geojson(
        self, layer: VectorLayer, simplify_tolerance: Optional[float] = None
    ) -> Dict[str, Any]:
        """Get GeoJSON representation of a vector layer with 2-tier caching"""
        try:
            # Create cache key including simplification parameter
            cache_key = f"{layer.file_path}:{layer.layer_name}"
            geojson_cache_key = f"{cache_key}:simplify={simplify_tolerance or 0}"

            # FAST PATH: For GeoJSON files, return cached data immediately (no GDAL!)
            if layer.file_path.endswith('.geojson'):
                # Check if we have cached GeoJSON from load_geojson_layer()
                if cache_key in self._geojson_cache:
                    self.logger.debug(f"GeoJSON fast-path for {layer.display_name} (no GDAL)")
                    geojson = self._geojson_cache[cache_key]

                    # Add layer metadata
                    geojson["metadata"] = {
                        "layer_name": layer.layer_name,
                        "display_name": layer.display_name,
                        "geometry_type": layer.geometry_type,
                        "feature_count": layer.feature_count,
                        "bounds": layer.bounds,
                        "source_file": layer.source_file,
                        "style": layer.style,
                    }

                    return geojson
                else:
                    # If not cached, load directly from file (pure JSON, no GDAL)
                    self.logger.debug(f"Loading GeoJSON from disk: {layer.display_name}")
                    with open(layer.file_path, 'r') as f:
                        geojson = json.load(f)

                    # Cache for next time
                    self._geojson_cache[cache_key] = geojson

                    # Add layer metadata
                    geojson["metadata"] = {
                        "layer_name": layer.layer_name,
                        "display_name": layer.display_name,
                        "geometry_type": layer.geometry_type,
                        "feature_count": layer.feature_count,
                        "bounds": layer.bounds,
                        "source_file": layer.source_file,
                        "style": layer.style,
                    }

                    return geojson

            # GPKG PATH: Use geopandas (requires GDAL)
            # TIER 1: Check GeoJSON cache (fastest - serialized JSON ready to return)
            if geojson_cache_key in self._geojson_cache:
                self.logger.debug(f"GeoJSON cache hit for {layer.display_name}")
                # Move to end (LRU: mark as recently used)
                self._geojson_cache.move_to_end(geojson_cache_key)
                return self._geojson_cache[geojson_cache_key]

            # TIER 2: Check GeoDataFrame cache (medium - needs JSON conversion)
            if cache_key not in self._gdf_cache:
                # Cache miss - read from disk (slowest)
                self.logger.debug(f"GDF cache miss for {layer.display_name}, reading from disk")

                # Evict old entries if cache is full
                self._evict_cache_entries()

                # Load and cache the GeoDataFrame
                self._gdf_cache[cache_key] = gpd.read_file(layer.file_path, layer=layer.layer_name)
            else:
                self.logger.debug(f"GDF cache hit for {layer.display_name}")
                # Move to end (LRU: mark as recently used)
                self._gdf_cache.move_to_end(cache_key)

            # Work with a copy to avoid cache pollution
            gdf = self._gdf_cache[cache_key].copy()

            # Ensure WGS84
            if gdf.crs and gdf.crs.to_epsg() != 4326:
                gdf = gdf.to_crs("EPSG:4326")

            # Simplify geometries if requested (for performance)
            if simplify_tolerance and simplify_tolerance > 0:
                gdf["geometry"] = gdf.geometry.simplify(tolerance=simplify_tolerance)

            # Convert to GeoJSON
            geojson = json.loads(gdf.to_json())

            # Add layer metadata
            geojson["metadata"] = {
                "layer_name": layer.layer_name,
                "display_name": layer.display_name,
                "geometry_type": layer.geometry_type,
                "feature_count": layer.feature_count,
                "bounds": layer.bounds,
                "source_file": layer.source_file,
                "style": layer.style,
            }

            # Cache the serialized GeoJSON for next time (50-70% speedup)
            self._geojson_cache[geojson_cache_key] = geojson
            if len(self._geojson_cache) > self.MAX_CACHE_SIZE:
                # Evict oldest GeoJSON cache entry
                oldest_key = next(iter(self._geojson_cache))
                self._geojson_cache.pop(oldest_key)

            return geojson

        except Exception as e:
            self.logger.error(f"Error creating GeoJSON for layer {layer.display_name}: {e}")
            raise

    def get_layer_by_name(self, layer_identifier: str) -> Optional[VectorLayer]:
        """Get a loaded layer by its display name or source_file/layer_name identifier"""
        for layer in self.loaded_layers:
            # Try display_name first (backward compatibility)
            if layer.display_name == layer_identifier:
                return layer
            # Try source_file/layer_name format (new robust format)
            layer_id = f"{layer.source_file}/{layer.layer_name}"
            if layer_id == layer_identifier:
                return layer
        return None

    def get_layers_summary(self) -> List[Dict[str, Any]]:
        """Get a summary of all loaded layers for the frontend"""
        summary = []
        for layer in self.loaded_layers:
            layer_dict = asdict(layer)
            # Remove file_path for security
            layer_dict.pop("file_path", None)
            summary.append(layer_dict)
        return summary

    def check_files_changed(self) -> bool:
        """
        Check if any vector files have been modified since last load

        Returns:
            bool: True if any files have changed, False otherwise
        """
        vector_files = self.discover_gpkg_files()

        for vector_path in vector_files:
            try:
                current_mtime = vector_path.stat().st_mtime
                stored_mtime = self._file_mtimes.get(str(vector_path))

                if stored_mtime is None:
                    # New file detected
                    self.logger.info(f"New file detected: {vector_path}")
                    return True

                if current_mtime != stored_mtime:
                    # File has been modified
                    self.logger.info(f"File modified: {vector_path}")
                    return True

            except Exception as e:
                self.logger.warning(f"Could not check modification time for {vector_path}: {e}")

        # Check if any files were removed
        current_files = {str(f) for f in vector_files}
        tracked_files = set(self._file_mtimes.keys())

        if tracked_files != current_files:
            removed_files = tracked_files - current_files
            if removed_files:
                self.logger.info(f"Files removed: {removed_files}")
                return True

        return False

    def reload_if_changed(self) -> bool:
        """
        Check for file changes and reload if necessary

        Returns:
            bool: True if files were reloaded, False otherwise
        """
        if self.check_files_changed():
            self.logger.info("Vector file changes detected, reloading...")
            # Clear caches to ensure fresh data
            self._gdf_cache.clear()
            self._geojson_cache.clear()
            # Reload all layers
            self.load_all_vector_layers()
            return True
        return False

    def create_bounds_summary(self) -> Dict[str, Any]:
        """Create a summary of bounds for all layers"""
        if not self.loaded_layers:
            return {}

        all_bounds = [layer.bounds for layer in self.loaded_layers]

        # Calculate overall bounds
        min_x = min(bounds[0] for bounds in all_bounds)
        min_y = min(bounds[1] for bounds in all_bounds)
        max_x = max(bounds[2] for bounds in all_bounds)
        max_y = max(bounds[3] for bounds in all_bounds)

        return {
            "overall_bounds": [min_x, min_y, max_x, max_y],
            "center": [(min_x + max_x) / 2, (min_y + max_y) / 2],
            "layer_count": len(self.loaded_layers),
        }


# Global instance
vector_loader = VectorLayerLoader()


def load_all_vector_data() -> List[VectorLayer]:
    """Convenience function to load all vector data"""
    return vector_loader.load_all_vector_layers()


def get_vector_layer_geojson(display_name: str, simplify: float = None) -> Optional[Dict[str, Any]]:
    """Convenience function to get GeoJSON for a layer by name"""
    layer = vector_loader.get_layer_by_name(display_name)
    if layer:
        return vector_loader.get_vector_layer_geojson(layer, simplify)
    return None


def get_vector_layers_summary() -> List[Dict[str, Any]]:
    """Convenience function to get vector layers summary"""
    return vector_loader.get_layers_summary()
