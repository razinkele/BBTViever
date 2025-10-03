#!/usr/bin/env python3
"""
Development server script with auto-reload and enhanced debugging
"""
import os
import sys
import argparse
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

from app import app
from config.config import get_config
from src.emodnet_viewer.utils.logging_config import setup_logging, log_application_startup


class CodeChangeHandler(FileSystemEventHandler):
    """Handler for code file changes"""

    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.watched_extensions = {'.py', '.html', '.css', '.js'}

    def on_modified(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix in self.watched_extensions:
                print(f"🔄 File changed: {file_path.name}")
                self.restart_callback()


def setup_development_environment():
    """Set up development environment"""
    # Load environment variables
    load_dotenv()

    # Set Flask environment
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'

    # Get configuration
    config = get_config()

    # Setup logging
    logger = setup_logging(
        log_level=config.LOG_LEVEL,
        log_file=None,  # Console only for development
        enable_console=True
    )

    return config, logger


def run_with_auto_reload(host='localhost', port=5000, watch_dirs=None):
    """Run development server with auto-reload functionality"""
    if watch_dirs is None:
        watch_dirs = [
            project_root / 'src',
            project_root / 'config',
            project_root / 'app.py'
        ]

    print("🚀 Starting EMODnet Viewer Development Server")
    print("=" * 50)

    config, logger = setup_development_environment()
    log_application_startup('Development', logger)

    # Configure Flask app
    app.config.from_object(config)

    def restart_server():
        """Restart server callback"""
        print("🔄 Restarting server due to file changes...")
        # In a real implementation, you might want to use a process manager
        # For now, we'll just reload the modules
        import importlib
        import app as app_module
        importlib.reload(app_module)

    # Set up file watching
    if watch_dirs:
        observer = Observer()
        handler = CodeChangeHandler(restart_server)

        for watch_dir in watch_dirs:
            if watch_dir.exists():
                observer.schedule(handler, str(watch_dir), recursive=True)
                print(f"👀 Watching: {watch_dir}")

        observer.start()

    print(f"🌐 Server running at: http://{host}:{port}")
    print("📊 Available endpoints:")
    print(f"  • Main app:        http://{host}:{port}/")
    print(f"  • Health check:    http://{host}:{port}/health")
    print(f"  • Test page:       http://{host}:{port}/test")
    print(f"  • API layers:      http://{host}:{port}/api/layers")
    print(f"  • API capabilities: http://{host}:{port}/api/capabilities")
    print("\n💡 Tips:")
    print("  • Press Ctrl+C to stop the server")
    print("  • Files are automatically watched for changes")
    print("  • Check logs for detailed request information")
    print("=" * 50)

    try:
        app.run(
            host=host,
            port=port,
            debug=True,
            use_reloader=False,  # We handle reloading manually
            threaded=True
        )
    except KeyboardInterrupt:
        print("\n🛑 Stopping development server...")
    finally:
        if 'observer' in locals():
            observer.stop()
            observer.join()


def add_health_check_endpoint():
    """Add health check endpoint for development"""
    from src.emodnet_viewer.utils.monitoring import create_health_checker

    @app.route('/health')
    def health_check():
        """Development health check endpoint"""
        from flask import jsonify
        config = get_config()
        health_checker = create_health_checker(config.WMS_BASE_URL, config.WMS_TIMEOUT)

        try:
            health_report = health_checker.get_comprehensive_health_report()
            status_code = 200 if health_report['overall_status'] in ['healthy', 'warning'] else 503
            return jsonify(health_report), status_code
        except Exception as e:
            return jsonify({
                'overall_status': 'error',
                'error': str(e),
                'timestamp': health_checker.datetime.utcnow().isoformat()
            }), 503


def main():
    """Main development server entry point"""
    parser = argparse.ArgumentParser(description='EMODnet Viewer Development Server')
    parser.add_argument('--host', '-H', default='localhost', help='Host to bind to (default: localhost)')
    parser.add_argument('--port', '-p', type=int, default=5000, help='Port to bind to (default: 5000)')
    parser.add_argument('--no-reload', action='store_true', help='Disable auto-reload functionality')
    parser.add_argument('--log-level', default='DEBUG', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
                        help='Logging level (default: DEBUG)')

    args = parser.parse_args()

    # Add health check endpoint
    add_health_check_endpoint()

    # Set log level
    os.environ['LOG_LEVEL'] = args.log_level

    if args.no_reload:
        # Simple Flask development server
        config, logger = setup_development_environment()
        app.config.from_object(config)
        log_application_startup('Development (no reload)', logger)

        print(f"🚀 Starting EMODnet Viewer at http://{args.host}:{args.port}")
        app.run(host=args.host, port=args.port, debug=True)
    else:
        # Enhanced development server with auto-reload
        run_with_auto_reload(args.host, args.port)


if __name__ == '__main__':
    main()