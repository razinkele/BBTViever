"""
Vector data blueprint for handling vector layer endpoints
"""
from flask import Blueprint, jsonify, request, current_app
from werkzeug.exceptions import BadRequest
import logging

from utils.validators import validate_layer_name, sanitize_url_parameter
from utils.cache import cached

vector_bp = Blueprint('vector', __name__)
logger = logging.getLogger(__name__)


@vector_bp.route('/layers')
@cached(ttl=3600)
def get_vector_layers():
    """Get available vector layers"""
    if not current_app.config['ENABLE_VECTOR_SUPPORT']:
        return jsonify({
            "error": "Vector support not available",
            "reason": "Missing geospatial dependencies or disabled in configuration"
        }), 503
    
    try:
        from services.vector_service import VectorService
        vector_service = VectorService(current_app.config)
        layers = vector_service.get_layers_summary()
        
        return jsonify({
            "layers": layers,
            "count": len(layers),
            "vector_support": True
        })
    except ImportError as e:
        logger.error(f"Vector dependencies not installed: {e}")
        return jsonify({
            "error": "Vector support not available",
            "reason": "Missing geospatial dependencies (geopandas, fiona)"
        }), 503
    except Exception as e:
        logger.error(f"Error fetching vector layers: {e}")
        return jsonify({"error": str(e)}), 500


@vector_bp.route('/layer/<path:layer_name>')
def get_vector_layer_geojson(layer_name):
    """Get GeoJSON for a specific vector layer"""
    if not current_app.config['ENABLE_VECTOR_SUPPORT']:
        return jsonify({"error": "Vector support not available"}), 503
    
    try:
        # Validate and sanitize layer name
        layer_name = validate_layer_name(layer_name)
        
        # Get optional simplification parameter
        simplify = request.args.get('simplify', type=float)
        
        from services.vector_service import VectorService
        vector_service = VectorService(current_app.config)
        geojson = vector_service.get_layer_geojson(layer_name, simplify)
        
        if geojson:
            return jsonify(geojson)
        else:
            return jsonify({"error": f"Layer '{layer_name}' not found"}), 404
            
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except ImportError as e:
        logger.error(f"Vector dependencies not installed: {e}")
        return jsonify({"error": "Vector support not available"}), 503
    except Exception as e:
        logger.error(f"Error fetching vector layer: {e}")
        return jsonify({"error": str(e)}), 500


@vector_bp.route('/bounds')
@cached(ttl=3600)
def get_vector_bounds():
    """Get bounds of all vector layers"""
    if not current_app.config['ENABLE_VECTOR_SUPPORT']:
        return jsonify({"error": "Vector support not available"}), 503
    
    try:
        from services.vector_service import VectorService
        vector_service = VectorService(current_app.config)
        bounds_summary = vector_service.create_bounds_summary()
        
        return jsonify(bounds_summary)
    except ImportError as e:
        logger.error(f"Vector dependencies not installed: {e}")
        return jsonify({"error": "Vector support not available"}), 503
    except Exception as e:
        logger.error(f"Error getting vector bounds: {e}")
        return jsonify({"error": str(e)}), 500


@vector_bp.route('/search')
def search_vector_features():
    """Search for features across vector layers"""
    if not current_app.config['ENABLE_VECTOR_SUPPORT']:
        return jsonify({"error": "Vector support not available"}), 503
    
    try:
        # Get search parameters
        query = sanitize_url_parameter(request.args.get('q', ''))
        layer = sanitize_url_parameter(request.args.get('layer', ''))
        limit = min(int(request.args.get('limit', 100)), 1000)  # Cap at 1000
        
        if not query:
            return jsonify({"error": "Search query required"}), 400
        
        from services.vector_service import VectorService
        vector_service = VectorService(current_app.config)
        
        results = vector_service.search_features(
            query=query,
            layer_name=layer if layer else None,
            limit=limit
        )
        
        return jsonify({
            "query": query,
            "results": results,
            "count": len(results)
        })
        
    except Exception as e:
        logger.error(f"Error searching vector features: {e}")
        return jsonify({"error": str(e)}), 500


@vector_bp.route('/bbt/<area_name>')
def get_bbt_area(area_name):
    """Get specific BBT area information"""
    try:
        # Validate area name
        area_name = validate_layer_name(area_name)
        
        from services.vector_service import VectorService
        vector_service = VectorService(current_app.config)
        
        # Look for BBT layer and specific area
        bbt_data = vector_service.get_bbt_feature(area_name)
        
        if bbt_data:
            return jsonify(bbt_data)
        else:
            return jsonify({"error": f"BBT area '{area_name}' not found"}), 404
            
    except BadRequest as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Error fetching BBT area: {e}")
        return jsonify({"error": str(e)}), 500


# Error handlers for this blueprint
@vector_bp.errorhandler(ImportError)
def handle_import_error(error):
    logger.error(f"Import error in vector blueprint: {error}")
    return jsonify({
        'error': 'Vector support not available',
        'message': 'Please install geopandas and related dependencies'
    }), 503


@vector_bp.errorhandler(Exception)
def handle_exception(error):
    logger.error(f'Unhandled exception in vector API: {error}', exc_info=True)
    return jsonify({
        'error': 'An unexpected error occurred',
        'message': str(error) if current_app.debug else None
    }), 500
