"""
API blueprint for RESTful endpoints
"""
from flask import Blueprint, jsonify, request, current_app
from werkzeug.exceptions import BadRequest
import logging

from services.wms_service import WMSService
from services.layer_service import LayerService
from utils.validators import validate_layer_name
from utils.cache import cached

api_bp = Blueprint('api', __name__)
logger = logging.getLogger(__name__)


@api_bp.route('/layers')
@cached(ttl=3600)
def get_layers():
    """Get available WMS layers"""
    try:
        wms_service = WMSService(
            current_app.config['WMS_BASE_URL'],
            current_app.config['WMS_VERSION']
        )
        layers = wms_service.get_available_layers()
        return jsonify({
            'layers': layers,
            'count': len(layers),
            'source': 'EMODnet'
        })
    except Exception as e:
        logger.error(f"Error fetching layers: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/helcom-layers')
@cached(ttl=3600)
def get_helcom_layers():
    """Get available HELCOM WMS layers"""
    try:
        helcom_service = WMSService(
            current_app.config['HELCOM_WMS_BASE_URL'],
            current_app.config['HELCOM_WMS_VERSION']
        )
        layers = helcom_service.get_helcom_layers()
        return jsonify({
            'layers': layers,
            'count': len(layers),
            'source': 'HELCOM'
        })
    except Exception as e:
        logger.error(f"Error fetching HELCOM layers: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/all-layers')
@cached(ttl=3600)
def get_all_layers():
    """Get all available layers (WMS, HELCOM, and vector)"""
    try:
        layer_service = LayerService(current_app.config)
        all_layers = layer_service.get_all_layers()
        return jsonify(all_layers)
    except Exception as e:
        logger.error(f"Error fetching all layers: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/capabilities')
@cached(ttl=7200)
def get_capabilities():
    """Get WMS GetCapabilities document"""
    try:
        wms_service = WMSService(
            current_app.config['WMS_BASE_URL'],
            current_app.config['WMS_VERSION']
        )
        capabilities = wms_service.get_capabilities_xml()
        return capabilities, 200, {'Content-Type': 'text/xml'}
    except Exception as e:
        logger.error(f"Error fetching capabilities: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/legend/<path:layer_name>')
def get_legend(layer_name):
    """Get legend URL for a specific layer"""
    try:
        # Validate layer name
        layer_name = validate_layer_name(layer_name)
        
        wms_service = WMSService(
            current_app.config['WMS_BASE_URL'],
            current_app.config['WMS_VERSION']
        )
        legend_url = wms_service.get_legend_url(layer_name)
        
        return jsonify({
            'layer': layer_name,
            'legend_url': legend_url
        })
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating legend URL: {e}")
        return jsonify({'error': str(e)}), 500


@api_bp.route('/feature-info', methods=['POST'])
def get_feature_info():
    """Get feature information for a specific location"""
    try:
        data = request.get_json()
        
        # Validate required parameters
        required = ['layer', 'bbox', 'width', 'height', 'x', 'y']
        missing = [field for field in required if field not in data]
        if missing:
            return jsonify({'error': f'Missing required fields: {missing}'}), 400
        
        # Validate layer name
        layer_name = validate_layer_name(data['layer'])
        
        wms_service = WMSService(
            current_app.config['WMS_BASE_URL'],
            current_app.config['WMS_VERSION']
        )
        
        feature_info = wms_service.get_feature_info(
            layer_name=layer_name,
            bbox=data['bbox'],
            width=data['width'],
            height=data['height'],
            x=data['x'],
            y=data['y']
        )
        
        return jsonify({
            'layer': layer_name,
            'feature_info': feature_info
        })
    except BadRequest as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error getting feature info: {e}")
        return jsonify({'error': str(e)}), 500


# Error handlers for this blueprint
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal error in API: {error}')
    return jsonify({'error': 'Internal server error'}), 500


@api_bp.errorhandler(Exception)
def handle_exception(error):
    logger.error(f'Unhandled exception in API: {error}', exc_info=True)
    return jsonify({
        'error': 'An unexpected error occurred',
        'message': str(error) if current_app.debug else None
    }), 500
