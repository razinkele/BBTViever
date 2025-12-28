"""
Sample vector data generator for testing
Creates simple GeoJSON data that can be displayed on the map
"""

import json


def get_sample_vector_layers():
    """Return sample vector layers for testing"""
    return [
        {
            "name": "sample_marine_protected_areas",
            "title": "Sample Marine Protected Areas",
            "description": "Example protected areas in European waters"
        },
        {
            "name": "sample_shipping_routes",
            "title": "Sample Shipping Routes",
            "description": "Example shipping corridors"
        }
    ]


def get_sample_geojson(layer_name):
    """Return sample GeoJSON data based on layer name"""

    if layer_name == "sample_marine_protected_areas":
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "North Sea MPA",
                        "protection_level": "High",
                        "area_km2": 1250
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [2.5, 54.5],
                            [4.5, 54.5],
                            [4.5, 56.0],
                            [2.5, 56.0],
                            [2.5, 54.5]
                        ]]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Baltic Sea Reserve",
                        "protection_level": "Medium",
                        "area_km2": 890
                    },
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[
                            [18.0, 57.0],
                            [20.0, 57.0],
                            [20.0, 58.5],
                            [18.0, 58.5],
                            [18.0, 57.0]
                        ]]
                    }
                }
            ]
        }

    elif layer_name == "sample_shipping_routes":
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Main Atlantic Route",
                        "traffic_density": "High"
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [-5.0, 50.0],
                            [-3.0, 52.0],
                            [-1.0, 53.5],
                            [1.0, 54.0]
                        ]
                    }
                },
                {
                    "type": "Feature",
                    "properties": {
                        "name": "Baltic Corridor",
                        "traffic_density": "Medium"
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [
                            [10.0, 55.0],
                            [15.0, 56.0],
                            [19.0, 57.5],
                            [22.0, 58.0]
                        ]
                    }
                }
            ]
        }

    return None