"""
WMS Service Layer
Handles all WMS-related operations with proper error handling and caching
"""
import requests
from xml.etree import ElementTree as ET
import logging
from typing import List, Dict, Optional, Any
from urllib.parse import urlencode

logger = logging.getLogger(__name__)


class ServiceError(Exception):
    """Custom exception for service layer errors"""
    pass


class WMSService:
    """Service for handling WMS operations"""
    
    def __init__(self, base_url: str, version: str = "1.3.0"):
        self.base_url = base_url
        self.version = version
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MARBEFES-BBT-Database/1.0'
        })
        
    def get_available_layers(self) -> List[Dict[str, str]]:
        """
        Fetch available layers from WMS GetCapabilities
        
        Returns:
            List of layer dictionaries with name, title, and description
        """
        try:
            capabilities = self._get_capabilities()
            return self._parse_layers(capabilities)
        except Exception as e:
            logger.error(f"Error fetching WMS layers: {e}")
            # Return default layers as fallback
            from flask import current_app
            return current_app.config.get('DEFAULT_LAYERS', [])
    
    def get_helcom_layers(self) -> List[Dict[str, str]]:
        """
        Fetch available HELCOM layers
        
        Returns:
            List of HELCOM layer dictionaries
        """
        try:
            capabilities = self._get_capabilities()
            layers = self._parse_layers(capabilities)
            
            # Filter for HELCOM-specific layers
            helcom_layers = []
            for layer in layers:
                layer_name = layer.get('name', '').strip()
                if layer_name and '_' in layer_name:  # HELCOM naming convention
                    layer['title'] = layer.get('title') or layer_name.replace('_', ' ').title()
                    helcom_layers.append(layer)
                    
            return helcom_layers[:15]  # Limit to reasonable number
        except Exception as e:
            logger.error(f"Error fetching HELCOM layers: {e}")
            return []
    
    def get_capabilities_xml(self) -> bytes:
        """
        Get raw GetCapabilities XML document
        
        Returns:
            XML content as bytes
        """
        params = {
            'service': 'WMS',
            'version': self.version,
            'request': 'GetCapabilities'
        }
        
        try:
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            logger.error(f"Failed to fetch capabilities: {e}")
            raise ServiceError(f"Failed to fetch capabilities: {e}")
    
    def get_legend_url(self, layer_name: str) -> str:
        """
        Generate legend URL for a specific layer
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            URL for the layer legend
        """
        params = {
            'service': 'WMS',
            'version': '1.1.0',
            'request': 'GetLegendGraphic',
            'layer': layer_name,
            'format': 'image/png'
        }
        return f"{self.base_url}?{urlencode(params)}"
    
    def get_feature_info(
        self,
        layer_name: str,
        bbox: List[float],
        width: int,
        height: int,
        x: int,
        y: int,
        info_format: str = 'text/html'
    ) -> str:
        """
        Get feature information for a specific location
        
        Args:
            layer_name: Name of the layer
            bbox: Bounding box [minx, miny, maxx, maxy]
            width: Map width in pixels
            height: Map height in pixels
            x: Click x coordinate
            y: Click y coordinate
            info_format: Response format
            
        Returns:
            Feature information content
        """
        params = {
            'service': 'WMS',
            'version': '1.1.0',
            'request': 'GetFeatureInfo',
            'layers': layer_name,
            'query_layers': layer_name,
            'styles': '',
            'bbox': ','.join(map(str, bbox)),
            'width': width,
            'height': height,
            'format': 'image/png',
            'info_format': info_format,
            'srs': 'EPSG:4326',
            'x': x,
            'y': y
        }
        
        try:
            response = self.session.get(
                self.base_url,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Failed to get feature info: {e}")
            raise ServiceError(f"Failed to get feature info: {e}")
    
    def _get_capabilities(self) -> ET.Element:
        """
        Internal method to fetch and parse GetCapabilities
        
        Returns:
            Parsed XML root element
        """
        xml_content = self.get_capabilities_xml()
        root = ET.fromstring(xml_content)
        
        # Remove namespaces for easier parsing
        for elem in root.iter():
            if '}' in elem.tag:
                elem.tag = elem.tag.split('}')[1]
                
        return root
    
    def _parse_layers(self, root: ET.Element) -> List[Dict[str, str]]:
        """
        Parse layers from GetCapabilities XML

        Args:
            root: XML root element

        Returns:
            List of parsed layer dictionaries
        """
        layers = []

        for layer in root.findall('.//Layer'):
            name_elem = layer.find('Name')
            title_elem = layer.find('Title')
            abstract_elem = layer.find('Abstract')

            if name_elem is not None and name_elem.text:
                layer_name = name_elem.text
                # Filter for layers starting with 'eusm' and skip workspace-prefixed names
                if ':' not in layer_name and layer_name.lower().startswith('eusm'):
                    layers.append({
                        'name': layer_name,
                        'title': title_elem.text if title_elem is not None else layer_name,
                        'description': abstract_elem.text if abstract_elem is not None else ''
                    })

        return layers[:50] if layers else []  # Increased limit for eusm layers
    
    def get_layer_bounds(self, layer_name: str) -> Optional[List[float]]:
        """
        Get geographic bounds for a specific layer
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            Bounds as [west, south, east, north] or None
        """
        try:
            capabilities = self._get_capabilities()
            
            for layer in capabilities.findall('.//Layer'):
                name_elem = layer.find('Name')
                if name_elem is not None and name_elem.text == layer_name:
                    # Look for bounding box
                    bbox = layer.find('EX_GeographicBoundingBox')
                    if bbox is not None:
                        west = float(bbox.find('westBoundLongitude').text)
                        south = float(bbox.find('southBoundLatitude').text)
                        east = float(bbox.find('eastBoundLongitude').text)
                        north = float(bbox.find('northBoundLatitude').text)
                        return [west, south, east, north]
                        
                    # Try alternative format
                    bbox = layer.find('LatLonBoundingBox')
                    if bbox is not None:
                        return [
                            float(bbox.get('minx')),
                            float(bbox.get('miny')),
                            float(bbox.get('maxx')),
                            float(bbox.get('maxy'))
                        ]
                        
        except Exception as e:
            logger.error(f"Error getting layer bounds: {e}")
            
        return None
    
    def get_layer_scale_hints(self, layer_name: str) -> Dict[str, Optional[float]]:
        """
        Get scale denominators for a layer
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            Dictionary with 'min_scale' and 'max_scale'
        """
        result = {'min_scale': None, 'max_scale': None}
        
        try:
            capabilities = self._get_capabilities()
            
            for layer in capabilities.findall('.//Layer'):
                name_elem = layer.find('Name')
                if name_elem is not None and name_elem.text == layer_name:
                    min_scale = layer.find('MinScaleDenominator')
                    max_scale = layer.find('MaxScaleDenominator')
                    
                    if min_scale is not None:
                        result['min_scale'] = float(min_scale.text)
                    if max_scale is not None:
                        result['max_scale'] = float(max_scale.text)
                        
                    break
                    
        except Exception as e:
            logger.error(f"Error getting layer scale hints: {e}")
            
        return result
