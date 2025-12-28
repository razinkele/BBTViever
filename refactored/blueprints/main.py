"""
Main blueprint for web interface routes
"""
from flask import Blueprint, render_template, current_app

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Main page with map viewer"""
    # Prepare context data for template
    context = {
        'wms_base_url': current_app.config['WMS_BASE_URL'],
        'wms_version': current_app.config['WMS_VERSION'],
        'helcom_wms_base_url': current_app.config['HELCOM_WMS_BASE_URL'],
        'helcom_wms_version': current_app.config['HELCOM_WMS_VERSION'],
        'vector_support': current_app.config['ENABLE_VECTOR_SUPPORT'],
        'default_layers': current_app.config['DEFAULT_LAYERS']
    }
    
    return render_template('index.html', **context)


@main_bp.route('/test')
def test_page():
    """Simple test page to verify WMS is working"""
    context = {
        'wms_base_url': current_app.config['WMS_BASE_URL']
    }
    return render_template('test.html', **context)


@main_bp.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return {'status': 'healthy', 'service': 'MARBEFES BBT Database'}, 200
