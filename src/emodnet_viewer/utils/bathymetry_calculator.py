"""
Bathymetry statistics calculator for BBT areas using EMODnet data.

This module provides functionality to calculate depth statistics (min, max, average)
for BBT areas by sampling bathymetry data from EMODnet Bathymetry WMS service.

Usage:
    from emodnet_viewer.utils.bathymetry_calculator import BathymetryCalculator

    calculator = BathymetryCalculator()
    stats = calculator.calculate_all_bbt_stats()
    calculator.save_to_json('data/bbt_bathymetry_stats.json')
"""

import json
import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple, List

import geopandas as gpd
import numpy as np
import requests
from shapely.geometry import Point

from .logging_config import get_logger


class BathymetryCalculator:
    """Calculate bathymetry statistics for BBT areas using EMODnet data."""

    # EMODnet Bathymetry WMS endpoint
    WMS_URL = "https://ows.emodnet-bathymetry.eu/wms"

    # Default layer for bathymetry queries
    DEFAULT_LAYER = "emodnet:mean_atlas_land"

    def __init__(self, gpkg_path: str = "data/vector/BBT.gpkg", layer_name: str = "BBT areas"):
        """
        Initialize the bathymetry calculator.

        Args:
            gpkg_path: Path to the GPKG file containing BBT areas
            layer_name: Name of the layer in the GPKG file
        """
        self.logger = get_logger(__name__)
        self.gpkg_path = Path(gpkg_path)
        self.layer_name = layer_name
        self.gdf: Optional[gpd.GeoDataFrame] = None
        self.results: Dict = {}

    def load_bbt_areas(self) -> gpd.GeoDataFrame:
        """Load BBT areas from GPKG file."""
        self.logger.info(f"Loading BBT areas from {self.gpkg_path}...")
        self.gdf = gpd.read_file(str(self.gpkg_path), layer=self.layer_name)

        # Reproject to WGS84 if needed
        if self.gdf.crs.to_epsg() != 4326:
            self.logger.info(f"Reprojecting from {self.gdf.crs} to EPSG:4326")
            self.gdf = self.gdf.to_crs("EPSG:4326")

        self.logger.info(f"Loaded {len(self.gdf)} BBT areas")
        return self.gdf

    def get_depth_at_point(self, lon: float, lat: float, timeout: int = 5) -> Optional[float]:
        """
        Get depth at a specific point using EMODnet WMS GetFeatureInfo.

        Args:
            lon: Longitude in WGS84
            lat: Latitude in WGS84
            timeout: Request timeout in seconds

        Returns:
            Depth in meters (positive value) or None if not available
        """
        # Use a small bbox around the point
        buffer = 0.001  # ~100m
        bbox = f"{lon-buffer},{lat-buffer},{lon+buffer},{lat+buffer}"

        params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetFeatureInfo',
            'layers': self.DEFAULT_LAYER,
            'query_layers': self.DEFAULT_LAYER,
            'crs': 'EPSG:4326',
            'bbox': bbox,
            'width': 10,
            'height': 10,
            'i': 5,  # x pixel
            'j': 5,  # y pixel
            'info_format': 'application/json'
        }

        try:
            response = requests.get(self.WMS_URL, params=params, timeout=timeout)

            if response.status_code == 200:
                data = response.json()
                if 'features' in data and len(data['features']) > 0:
                    properties = data['features'][0].get('properties', {})
                    # Look for depth value (field name may vary)
                    for key in ['GRAY_INDEX', 'depth', 'value', 'elevation']:
                        if key in properties:
                            value = properties[key]
                            if value is not None and value != 'null':
                                # Convert to positive depth if negative
                                return abs(float(value))

        except Exception as e:
            self.logger.debug(f"Error querying depth at ({lon}, {lat}): {e}")

        return None

    def calculate_stats_for_area(
        self,
        geometry,
        name: str,
        num_samples: int = 25
    ) -> Optional[Dict]:
        """
        Calculate bathymetry statistics for a single BBT area.

        Args:
            geometry: Shapely geometry of the BBT area
            name: Name of the BBT area
            num_samples: Number of sample points per dimension (total = num_samples²)

        Returns:
            Dictionary with statistics or None if no data available
        """
        self.logger.info(f"Processing: {name}")

        # Get bounds
        bounds = geometry.bounds  # (minx, miny, maxx, maxy)
        minx, miny, maxx, maxy = bounds

        # Create a grid of sample points
        x_points = np.linspace(minx, maxx, num_samples)
        y_points = np.linspace(miny, maxy, num_samples)

        depths = []
        sampled = 0

        for x in x_points:
            for y in y_points:
                point = Point(x, y)

                # Check if point is inside polygon
                if geometry.contains(point):
                    sampled += 1
                    # Query bathymetry at this point
                    depth = self.get_depth_at_point(x, y)
                    if depth is not None and 0 < depth < 10000:  # Sanity check
                        depths.append(depth)

                    # Log progress every 50 points
                    if sampled % 50 == 0:
                        self.logger.debug(
                            f"  Sampled {sampled} points, {len(depths)} valid depths..."
                        )

        if depths:
            stats = {
                'min_depth_m': round(float(np.min(depths)), 1),
                'max_depth_m': round(float(np.max(depths)), 1),
                'avg_depth_m': round(float(np.mean(depths)), 1),
                'std_depth_m': round(float(np.std(depths)), 1),
                'sample_count': len(depths)
            }
            self.logger.info(
                f"  ✅ {name}: Min={stats['min_depth_m']}m, "
                f"Max={stats['max_depth_m']}m, Avg={stats['avg_depth_m']}m "
                f"({len(depths)} samples)"
            )
            return stats
        else:
            self.logger.warning(f"  No valid depth data found for {name}")
            return None

    def calculate_all_bbt_stats(self, num_samples: int = 25) -> Dict:
        """
        Calculate bathymetry statistics for all BBT areas.

        Args:
            num_samples: Number of sample points per dimension

        Returns:
            Dictionary mapping BBT names to their statistics
        """
        if self.gdf is None:
            self.load_bbt_areas()

        self.logger.info(
            f"Calculating bathymetry statistics for {len(self.gdf)} BBT areas "
            f"(this may take several minutes)..."
        )

        self.results = {}

        for idx, row in self.gdf.iterrows():
            name = row['Name']
            stats = self.calculate_stats_for_area(row.geometry, name, num_samples)
            self.results[name] = stats

        return self.results

    def save_to_json(self, output_path: str) -> Path:
        """
        Save bathymetry statistics to JSON file.

        Args:
            output_path: Path to output JSON file

        Returns:
            Path object of the saved file
        """
        output_file = Path(output_path)

        # Prepare output data with metadata
        output_data = {
            'metadata': {
                'source': 'EMODnet Bathymetry',
                'url': 'https://portal.emodnet-bathymetry.eu/',
                'wms_endpoint': self.WMS_URL,
                'layer': self.DEFAULT_LAYER,
                'method': 'Point sampling across BBT polygons using WMS GetFeatureInfo',
                'unit': 'meters below sea level',
                'generated': datetime.datetime.now().isoformat(),
                'bbt_count': len(self.results),
                'valid_count': sum(1 for v in self.results.values() if v is not None)
            },
            'statistics': self.results
        }

        # Save to JSON
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)

        self.logger.info(f"Results saved to: {output_file}")
        self.logger.info(f"File size: {output_file.stat().st_size} bytes")

        return output_file

    def get_summary(self) -> Dict:
        """Get a summary of the calculated statistics."""
        if not self.results:
            return {'error': 'No results available'}

        valid_count = sum(1 for v in self.results.values() if v is not None)

        return {
            'total_bbt_areas': len(self.results),
            'with_bathymetry_data': valid_count,
            'without_data': len(self.results) - valid_count,
            'areas': list(self.results.keys())
        }
