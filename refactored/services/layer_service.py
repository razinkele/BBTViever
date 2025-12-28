"""
Layer Service - Combines WMS and Vector layer operations
"""
import logging
from typing import Dict, List, Any
from .wms_service import WMSService

logger = logging.getLogger(__name__)


class LayerService:
    """Service for managing all layer types"""
    
    def __init__(self, config: dict):
        self.config = config
        self.wms_service = WMSService(
            config['WMS_BASE_URL'],
            config['WMS_VERSION']
        )
        self.helcom_service = WMSService(
            config['HELCOM_WMS_BASE_URL'],
            config['HELCOM_WMS_VERSION']
        )
        
    def get_all_layers(self) -> Dict[str, Any]:
        """Get all available layers from all sources"""
        result = {
            'wms_layers': [],
            'helcom_layers': [],
            'vector_layers': [],
            'vector_support': False
        }
        
        try:
            # Get WMS layers
            result['wms_layers'] = self.wms_service.get_available_layers()
        except Exception as e:
            logger.error(f"Error fetching WMS layers: {e}")
            result['wms_layers'] = self.config.get('DEFAULT_LAYERS', [])
        
        try:
            # Get HELCOM layers
            result['helcom_layers'] = self.helcom_service.get_helcom_layers()
        except Exception as e:
            logger.error(f"Error fetching HELCOM layers: {e}")
        
        # Check for vector support
        if self.config.get('ENABLE_VECTOR_SUPPORT'):
            try:
                from emodnet_viewer.utils.vector_loader import get_vector_layers_summary
                result['vector_layers'] = get_vector_layers_summary()
                result['vector_support'] = True
            except ImportError:
                logger.info("Vector support not available")
            except Exception as e:
                logger.error(f"Error loading vector layers: {e}")
        
        return result