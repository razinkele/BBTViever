"""
WSGI entry point for running Flask application under a URL prefix/subpath

This wrapper allows the application to run at http://server/BBTS instead of root.
It uses werkzeug's DispatcherMiddleware to mount the Flask app at a specific path.

Usage:
    gunicorn --config gunicorn_config.py wsgi_subpath:application
"""

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response
from app import app as flask_app

# Simple response for root path (optional - shows friendly message)
def root_app(environ, start_response):
    """Simple response when accessing root path"""
    response = Response(
        '<h1>MARBEFES Server</h1>'
        '<p>BBT Database is available at: <a href="/BBTS">/BBTS</a></p>',
        mimetype='text/html'
    )
    return response(environ, start_response)

# Mount Flask application at /BBTS
application = DispatcherMiddleware(root_app, {
    '/BBTS': flask_app
})

if __name__ == "__main__":
    from werkzeug.serving import run_simple
    run_simple('0.0.0.0', 5000, application, use_debugger=False, use_reloader=False)
