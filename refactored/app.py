"""
MARBEFES BBT Database - Refactored Main Application
"""
import os
import logging
from flask import Flask, send_from_directory
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

from config import config


def create_app(config_name=None):
    """Application factory pattern"""
    
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    initialize_extensions(app)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Setup static file serving for logos
    @app.route('/logo/<filename>')
    def serve_logo(filename):
        """Serve logo files from LOGO directory"""
        logo_dir = os.path.join(app.root_path, 'LOGO')
        return send_from_directory(logo_dir, filename)
    
    return app


def initialize_extensions(app):
    """Initialize Flask extensions"""
    
    # CORS configuration
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Add proxy fix for production deployment
    if app.config.get('ENV') == 'production':
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=1,
            x_proto=1,
            x_host=1,
            x_prefix=1
        )


def setup_logging(app):
    """Configure application logging"""
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(app.config['LOG_FILE'])
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Set up logging configuration
    logging.basicConfig(
        level=getattr(logging, app.config['LOG_LEVEL']),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Add file handler for production
    if not app.debug and app.config.get('LOG_FILE'):
        from logging.handlers import RotatingFileHandler
        
        file_handler = RotatingFileHandler(
            app.config['LOG_FILE'],
            maxBytes=app.config['LOG_MAX_BYTES'],
            backupCount=app.config['LOG_BACKUP_COUNT']
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
    app.logger.info('MARBEFES BBT Database startup')


def register_blueprints(app):
    """Register application blueprints"""

    from blueprints.main import main_bp
    from blueprints.api import api_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

    # Register vector blueprint if available
    try:
        from blueprints.vector import vector_bp
        app.register_blueprint(vector_bp, url_prefix='/api/vector')
    except ImportError:
        app.logger.info("Vector blueprint not available - skipping")


def register_error_handlers(app):
    """Register global error handlers"""
    
    @app.errorhandler(404)
    def not_found_error(error):
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Resource not found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        app.logger.error(f'Internal error: {error}')
        if request.path.startswith('/api/'):
            return jsonify({'error': 'Internal server error'}), 500
        return render_template('errors/500.html'), 500
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.error(f'Unexpected error: {error}', exc_info=True)
        if request.path.startswith('/api/'):
            return jsonify({
                'error': 'An unexpected error occurred',
                'message': str(error) if app.debug else 'Internal server error'
            }), 500
        return render_template('errors/500.html'), 500


# Import required modules after app creation to avoid circular imports
from flask import request, jsonify, render_template

if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "="*60)
    print("MARBEFES BBT Database - Refactored Version")
    print("Marine Biodiversity and Ecosystem Functioning Database")
    print("="*60)
    
    # Initialize services on startup if needed
    with app.app_context():
        if app.config['ENABLE_VECTOR_SUPPORT']:
            try:
                from services.vector_service import VectorService
                vector_service = VectorService(app.config)
                vector_service.initialize()
                print(f"✓ Vector Support: Enabled")
                print(f"  Data directory: {app.config['VECTOR_DATA_PATH'].absolute()}")
            except ImportError:
                print("X Vector Support: Service not available (vector_service.py missing)")
            except Exception as e:
                print(f"X Vector Support: Failed to initialize - {e}")
        else:
            print("X Vector Support: Disabled")
    
    print("\nStarting Flask server...")
    print(f"Environment: {app.config.get('ENV', 'development')}")
    print(f"Debug mode: {app.debug}")
    print("\nOpen http://localhost:5000 in your browser")
    print("\nPress Ctrl+C to stop the server")
    print("-"*60 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=app.debug
    )
