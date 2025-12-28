"""
Layer Service - Unified layer management
Combines WMS, HELCOM, and vector layers
"""

import logging
from typing import List, Dict, Any, Optional
from services.wms_service import WMSService
from utils.cache import cached

logger = logging.getLogger(__name__)


class LayerService:
    """Service for managing all types of layers"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize layer service

        Args:
            config: Application configuration
        """
        self.config = config
        self.wms_service = WMSService(
            config.get("WMS_BASE_URL"), config.get("WMS_VERSION", "1.3.0")
        )
        self.helcom_service = WMSService(
            config.get("HELCOM_WMS_BASE_URL"),
            config.get("HELCOM_WMS_VERSION", "1.3.0"),
        )

    @cached(ttl=3600)
    def get_all_layers(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get all available layers from all sources

        Returns:
            Dictionary with layers from different sources
        """
        try:
            # Get WMS layers
            wms_layers = self.wms_service.get_available_layers()

            # Get HELCOM layers
            helcom_layers = self.helcom_service.get_helcom_layers()

            # Get vector layers if available
            vector_layers = []
            if self.config.get("ENABLE_VECTOR_SUPPORT", False):
                try:
                    from emodnet_viewer.utils.vector_loader import (
                        get_vector_layers_summary,
                    )

                    vector_layers = get_vector_layers_summary()
                except ImportError:
                    logger.warning("Vector support not available")

            return {
                "wms": wms_layers,
                "helcom": helcom_layers,
                "vector": vector_layers,
                "total_count": (
                    len(wms_layers) + len(helcom_layers) + len(vector_layers)
                ),
            }
        except Exception as e:
            logger.error(f"Error getting all layers: {e}")
            return {
                "wms": [],
                "helcom": [],
                "vector": [],
                "total_count": 0,
                "error": str(e),
            }

    def get_layer_metadata(
        self, layer_name: str, source: str = "wms"
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed metadata for a specific layer

        Args:
            layer_name: Name of the layer
            source: Source type ('wms', 'helcom', 'vector')

        Returns:
            Layer metadata or None
        """
        try:
            if source == "wms":
                bounds = self.wms_service.get_layer_bounds(layer_name)
                scale_hints = self.wms_service.get_layer_scale_hints(
                    layer_name
                )
                return {
                    "name": layer_name,
                    "source": "wms",
                    "bounds": bounds,
                    "scale_hints": scale_hints,
                    "legend_url": self.wms_service.get_legend_url(layer_name),
                }
            elif source == "helcom":
                bounds = self.helcom_service.get_layer_bounds(layer_name)
                scale_hints = self.helcom_service.get_layer_scale_hints(
                    layer_name
                )
                return {
                    "name": layer_name,
                    "source": "helcom",
                    "bounds": bounds,
                    "scale_hints": scale_hints,
                    "legend_url": self.helcom_service.get_legend_url(
                        layer_name
                    ),
                }
            elif source == "vector":
                # Vector layers would need different metadata handling
                return {
                    "name": layer_name,
                    "source": "vector",
                    "bounds": None,
                    "scale_hints": {},
                    "legend_url": None,
                }
            else:
                logger.warning(f"Unknown source type: {source}")
                return None

        except Exception as e:
            logger.error(f"Error getting layer metadata: {e}")
            return None

    def search_layers(self, query: str) -> List[Dict[str, str]]:
        """
        Search for layers by name or title

        Args:
            query: Search query

        Returns:
            List of matching layers
        """
        try:
            all_layers = self.get_all_layers()
            query_lower = query.lower()
            results = []

            # Search WMS layers
            for layer in all_layers.get("wms", []):
                if (
                    query_lower in layer.get("name", "").lower()
                    or query_lower in layer.get("title", "").lower()
                    or query_lower in layer.get("description", "").lower()
                ):
                    layer["source"] = "wms"
                    results.append(layer)

            # Search HELCOM layers
            for layer in all_layers.get("helcom", []):
                if (
                    query_lower in layer.get("name", "").lower()
                    or query_lower in layer.get("title", "").lower()
                    or query_lower in layer.get("description", "").lower()
                ):
                    layer["source"] = "helcom"
                    results.append(layer)

            # Search vector layers
            for layer in all_layers.get("vector", []):
                if (
                    query_lower in layer.get("name", "").lower()
                    or query_lower in layer.get("title", "").lower()
                    or query_lower in layer.get("description", "").lower()
                ):
                    layer["source"] = "vector"
                    results.append(layer)

            return results[:20]  # Limit results

        except Exception as e:
            logger.error(f"Error searching layers: {e}")
            return []

    def get_layer_capabilities(self, source: str = "wms") -> Optional[bytes]:
        """
        Get raw capabilities document for a source

        Args:
            source: Source type ('wms' or 'helcom')

        Returns:
            Raw XML capabilities or None
        """
        try:
            if source == "wms":
                return self.wms_service.get_capabilities_xml()
            elif source == "helcom":
                return self.helcom_service.get_capabilities_xml()
            else:
                logger.warning(
                    f"Capabilities not available for source: {source}"
                )
                return None
        except Exception as e:
            logger.error(f"Error getting capabilities: {e}")
            return None
