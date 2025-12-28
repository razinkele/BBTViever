"""
Input validation utilities for security
"""
import re
from flask import abort
from werkzeug.utils import secure_filename
from typing import Any, List, Optional
import logging

logger = logging.getLogger(__name__)


def validate_layer_name(layer_name: str) -> str:
    """
    Validate layer name to prevent injection attacks
    
    Args:
        layer_name: The layer name to validate
        
    Returns:
        Sanitized layer name
        
    Raises:
        BadRequest: If layer name contains invalid characters
    """
    if not layer_name:
        abort(400, "Layer name cannot be empty")
    
    # Allow alphanumeric, spaces, hyphens, underscores, and dots
    if not re.match(r'^[\w\s\-\.]+$', layer_name):
        logger.warning(f"Invalid layer name attempted: {layer_name}")
        abort(400, "Invalid layer name format")
    
    # Additional length check
    if len(layer_name) > 255:
        abort(400, "Layer name too long")
    
    return secure_filename(layer_name)


def validate_bbox(bbox: List[float]) -> List[float]:
    """
    Validate bounding box coordinates
    
    Args:
        bbox: List of [minx, miny, maxx, maxy]
        
    Returns:
        Validated bbox
        
    Raises:
        BadRequest: If bbox is invalid
    """
    if not bbox or len(bbox) != 4:
        abort(400, "Invalid bounding box format")
    
    try:
        bbox = [float(coord) for coord in bbox]
    except (ValueError, TypeError):
        abort(400, "Bounding box must contain numeric values")
    
    # Validate coordinate ranges
    minx, miny, maxx, maxy = bbox
    
    if not (-180 <= minx <= 180 and -180 <= maxx <= 180):
        abort(400, "Longitude must be between -180 and 180")
    
    if not (-90 <= miny <= 90 and -90 <= maxy <= 90):
        abort(400, "Latitude must be between -90 and 90")
    
    if minx >= maxx or miny >= maxy:
        abort(400, "Invalid bounding box: min values must be less than max values")
    
    return bbox


def validate_coordinates(x: float, y: float) -> tuple:
    """
    Validate coordinate pair
    
    Args:
        x: Longitude
        y: Latitude
        
    Returns:
        Validated (x, y) tuple
        
    Raises:
        BadRequest: If coordinates are invalid
    """
    try:
        x = float(x)
        y = float(y)
    except (ValueError, TypeError):
        abort(400, "Coordinates must be numeric")
    
    if not -180 <= x <= 180:
        abort(400, "Longitude must be between -180 and 180")
    
    if not -90 <= y <= 90:
        abort(400, "Latitude must be between -90 and 90")
    
    return x, y


def validate_pixel_coordinates(x: int, y: int, width: int, height: int) -> tuple:
    """
    Validate pixel coordinates for click events
    
    Args:
        x: X pixel coordinate
        y: Y pixel coordinate
        width: Map width in pixels
        height: Map height in pixels
        
    Returns:
        Validated (x, y) tuple
        
    Raises:
        BadRequest: If coordinates are invalid
    """
    try:
        x = int(x)
        y = int(y)
        width = int(width)
        height = int(height)
    except (ValueError, TypeError):
        abort(400, "Pixel coordinates must be integers")
    
    if width <= 0 or height <= 0:
        abort(400, "Width and height must be positive")
    
    if not (0 <= x < width):
        abort(400, f"X coordinate must be between 0 and {width-1}")
    
    if not (0 <= y < height):
        abort(400, f"Y coordinate must be between 0 and {height-1}")
    
    return x, y


def sanitize_url_parameter(param: str) -> str:
    """
    Sanitize URL parameters to prevent XSS
    
    Args:
        param: Parameter to sanitize
        
    Returns:
        Sanitized parameter
    """
    if not param:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '&', '"', "'", '`', 'javascript:', 'data:', 'vbscript:']
    
    sanitized = str(param)
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, '')
    
    return sanitized[:1000]  # Limit length


def validate_file_extension(filename: str, allowed_extensions: set) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: Set of allowed extensions
        
    Returns:
        True if valid, False otherwise
    """
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in allowed_extensions


def validate_geojson(geojson: dict) -> bool:
    """
    Validate GeoJSON structure
    
    Args:
        geojson: GeoJSON dictionary
        
    Returns:
        True if valid GeoJSON
    """
    required_keys = ['type', 'features']
    
    if not all(key in geojson for key in required_keys):
        return False
    
    if geojson['type'] != 'FeatureCollection':
        return False
    
    if not isinstance(geojson['features'], list):
        return False
    
    # Basic validation of features
    for feature in geojson['features']:
        if not isinstance(feature, dict):
            return False
        
        if 'type' not in feature or feature['type'] != 'Feature':
            return False
        
        if 'geometry' not in feature or 'properties' not in feature:
            return False
    
    return True


def validate_zoom_level(zoom: int) -> int:
    """
    Validate map zoom level
    
    Args:
        zoom: Zoom level
        
    Returns:
        Validated zoom level
        
    Raises:
        BadRequest: If zoom level is invalid
    """
    try:
        zoom = int(zoom)
    except (ValueError, TypeError):
        abort(400, "Zoom level must be an integer")
    
    if not 0 <= zoom <= 22:
        abort(400, "Zoom level must be between 0 and 22")
    
    return zoom


def validate_opacity(opacity: float) -> float:
    """
    Validate opacity value
    
    Args:
        opacity: Opacity value
        
    Returns:
        Validated opacity (0.0 to 1.0)
        
    Raises:
        BadRequest: If opacity is invalid
    """
    try:
        opacity = float(opacity)
    except (ValueError, TypeError):
        abort(400, "Opacity must be a number")
    
    if not 0.0 <= opacity <= 1.0:
        abort(400, "Opacity must be between 0.0 and 1.0")
    
    return opacity
