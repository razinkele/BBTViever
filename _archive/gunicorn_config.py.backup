"""
Gunicorn configuration file for MARBEFES BBT Database production deployment

This configuration optimizes the application for production use with:
- Multiple worker processes for concurrent request handling
- Appropriate timeouts for WMS requests
- Access logging and error logging
- Security settings

Usage:
    gunicorn -c gunicorn_config.py app:app
"""

import multiprocessing
import os

# Server Socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:5000')
backlog = 2048

# Worker Processes
# Rule of thumb: (2 x $num_cores) + 1
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'  # Use 'gevent' or 'eventlet' for async if needed
worker_connections = 1000
max_requests = 1000  # Restart workers after this many requests (prevents memory leaks)
max_requests_jitter = 50  # Add randomness to prevent all workers restarting simultaneously
timeout = 30  # Worker timeout (seconds) - important for WMS requests
keepalive = 5  # Seconds to wait for requests on a Keep-Alive connection

# Logging
accesslog = os.getenv('GUNICORN_ACCESS_LOG', 'logs/gunicorn_access.log')
errorlog = os.getenv('GUNICORN_ERROR_LOG', 'logs/gunicorn_error.log')
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')  # Options: debug, info, warning, error, critical
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process Naming
proc_name = 'marbefes_bbt_database'

# Server Mechanics
daemon = False  # Don't run as daemon (better for systemd/docker)
pidfile = os.getenv('GUNICORN_PIDFILE', 'logs/gunicorn.pid')
user = None  # Run as current user (or set to www-data for production)
group = None
umask = 0
tmp_upload_dir = None

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# Application Loading
preload_app = True  # Load application code before forking workers (better memory efficiency)

# Hooks
def on_starting(server):
    """Called just before the master process is initialized."""
    print("=" * 60)
    print("MARBEFES BBT Database - Starting Gunicorn Server")
    print("=" * 60)
    print(f"Workers: {workers}")
    print(f"Bind: {bind}")
    print(f"Timeout: {timeout}s")
    print(f"Access Log: {accesslog}")
    print(f"Error Log: {errorlog}")
    print("=" * 60)

def on_reload(server):
    """Called to recycle workers during a reload."""
    print("Reloading workers...")

def when_ready(server):
    """Called just after the server is started."""
    print(f"Server is ready. Listening on {bind}")

def worker_int(worker):
    """Called when a worker receives the INT or QUIT signal."""
    print(f"Worker {worker.pid} received INT/QUIT signal")

def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    print(f"Worker {worker.pid} aborted (SIGABRT)")
