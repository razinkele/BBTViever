#!/usr/bin/env python3
"""
Script to create sample GPKG data for testing vector layer functionality
"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    import geopandas as gpd
    import pandas as pd
    from shapely.geometry import Polygon, Point
    import numpy as np

    def create_sample_marine_areas():
        """Create sample marine protected areas"""
        # Define some sample marine areas in European waters
        areas = [
            {
                'name': 'Baltic Sea Protected Area',
                'type': 'Marine Protected Area',
                'area_km2': 1250.5,
                'established': 2010,
                'protection_level': 'High',
                'geometry': Polygon([
                    (15.0, 55.0), (17.0, 55.0), (17.0, 57.0), (15.0, 57.0), (15.0, 55.0)
                ])
            },
            {
                'name': 'North Sea Conservation Zone',
                'type': 'Conservation Zone',
                'area_km2': 2100.8,
                'established': 2008,
                'protection_level': 'Medium',
                'geometry': Polygon([
                    (3.0, 52.0), (5.0, 52.0), (5.0, 54.0), (3.0, 54.0), (3.0, 52.0)
                ])
            },
            {
                'name': 'Mediterranean Marine Reserve',
                'type': 'Marine Reserve',
                'area_km2': 850.3,
                'established': 2015,
                'protection_level': 'Very High',
                'geometry': Polygon([
                    (8.0, 42.0), (10.0, 42.0), (10.0, 44.0), (8.0, 44.0), (8.0, 42.0)
                ])
            },
            {
                'name': 'Atlantic Sanctuary',
                'type': 'Marine Sanctuary',
                'area_km2': 3200.1,
                'established': 2012,
                'protection_level': 'High',
                'geometry': Polygon([
                    (-10.0, 48.0), (-8.0, 48.0), (-8.0, 50.0), (-10.0, 50.0), (-10.0, 48.0)
                ])
            }
        ]

        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(areas, crs='EPSG:4326')
        return gdf

    def create_sample_monitoring_stations():
        """Create sample monitoring station points"""
        # Generate random monitoring stations in European waters
        np.random.seed(42)

        # Define bounding box for European waters
        lon_min, lon_max = -15.0, 20.0
        lat_min, lat_max = 40.0, 60.0

        n_stations = 25

        stations = []
        for i in range(n_stations):
            lon = np.random.uniform(lon_min, lon_max)
            lat = np.random.uniform(lat_min, lat_max)

            stations.append({
                'station_id': f'MON_{i+1:03d}',
                'station_name': f'Monitoring Station {i+1}',
                'type': np.random.choice(['Water Quality', 'Biodiversity', 'Oceanographic']),
                'depth_m': np.random.randint(10, 500),
                'established': np.random.randint(2005, 2020),
                'active': np.random.choice([True, False], p=[0.8, 0.2]),
                'geometry': Point(lon, lat)
            })

        gdf = gpd.GeoDataFrame(stations, crs='EPSG:4326')
        return gdf

    def create_sample_shipping_routes():
        """Create sample shipping route lines"""
        from shapely.geometry import LineString

        routes = [
            {
                'route_name': 'North Sea Corridor',
                'route_type': 'Commercial Shipping',
                'traffic_level': 'High',
                'length_km': 450.2,
                'geometry': LineString([
                    (1.0, 51.5), (3.0, 52.0), (5.0, 53.0), (7.0, 54.0)
                ])
            },
            {
                'route_name': 'Baltic Gateway',
                'route_type': 'Commercial Shipping',
                'traffic_level': 'Medium',
                'length_km': 320.8,
                'geometry': LineString([
                    (10.0, 54.0), (12.0, 55.0), (15.0, 56.0), (18.0, 57.0)
                ])
            },
            {
                'route_name': 'Mediterranean Express',
                'route_type': 'Ferry Route',
                'traffic_level': 'Medium',
                'length_km': 280.5,
                'geometry': LineString([
                    (5.0, 43.0), (8.0, 42.0), (12.0, 41.0), (15.0, 40.0)
                ])
            }
        ]

        gdf = gpd.GeoDataFrame(routes, crs='EPSG:4326')
        return gdf

    def main():
        """Create sample GPKG files"""
        data_dir = project_root / 'data' / 'vector'

        # Ensure directory exists
        data_dir.mkdir(parents=True, exist_ok=True)

        print("Creating sample vector data...")

        # Create marine protected areas
        marine_areas = create_sample_marine_areas()
        marine_areas_path = data_dir / 'marine_protected_areas.gpkg'
        marine_areas.to_file(marine_areas_path, driver='GPKG')
        print(f"Created: {marine_areas_path}")
        print(f"   - {len(marine_areas)} marine protected areas")

        # Create monitoring stations
        monitoring_stations = create_sample_monitoring_stations()
        stations_path = data_dir / 'monitoring_stations.gpkg'
        monitoring_stations.to_file(stations_path, driver='GPKG')
        print(f"Created: {stations_path}")
        print(f"   - {len(monitoring_stations)} monitoring stations")

        # Create shipping routes
        shipping_routes = create_sample_shipping_routes()
        routes_path = data_dir / 'shipping_routes.gpkg'
        shipping_routes.to_file(routes_path, driver='GPKG')
        print(f"Created: {routes_path}")
        print(f"   - {len(shipping_routes)} shipping routes")

        # Create a multi-layer GPKG
        multi_path = data_dir / 'european_marine_data.gpkg'
        marine_areas.to_file(multi_path, layer='protected_areas', driver='GPKG')
        monitoring_stations.to_file(multi_path, layer='monitoring_stations', driver='GPKG', append=True)
        shipping_routes.to_file(multi_path, layer='shipping_routes', driver='GPKG', append=True)
        print(f"Created: {multi_path}")
        print(f"   - Multi-layer GPKG with 3 layers")

        print("\nSample data creation complete!")
        print(f"Data location: {data_dir.absolute()}")
        print("\nTo test vector layers:")
        print("1. Run the application: python app.py")
        print("2. Open http://localhost:5000")
        print("3. Select vector layers from the dropdown")

except ImportError as e:
    print(f"Missing required dependencies: {e}")
    print("Install geospatial dependencies:")
    print("pip install geopandas fiona pyproj shapely")
    sys.exit(1)

if __name__ == '__main__':
    main()