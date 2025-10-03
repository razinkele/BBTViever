#!/usr/bin/env python3
"""
Gunicorn configuration for MARBEFES BBT Database
"""

import os
import multiprocessing

# Server socket
bind = f"0.0.0.0:{os.getenv('PORT', '5000')}"
backlog = 2048

# Worker processes
workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = int(os.getenv('TIMEOUT', '30'))
keepalive = int(os.getenv('KEEPALIVE', '2'))

# Restart workers after this many requests, with up to this much jitter
max_requests = int(os.getenv('MAX_REQUESTS', '1000'))
max_requests_jitter = int(os.getenv('MAX_REQUESTS_JITTER', '100'))

# Logging
accesslog = 'logs/gunicorn-access.log'
errorlog = 'logs/gunicorn-error.log'
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'marbefes-bbt-database'

# Server mechanics
preload_app = True
daemon = False
raw_env = [
    'FLASK_ENV=production',
]

# SSL (if needed)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

def when_ready(server):
    """Called just after the server is started."""
    server.log.info("MARBEFES BBT Database server is ready. Listening on %s", bind)

def worker_int(worker):
    """Called just after a worker has been interrupted by SIGINT"""
    worker.log.info("Worker received SIGINT signal")

def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    """Called just after a worker has been forked."""
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    """Called just after a worker has initialized the application."""
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    """Called when a worker received the SIGABRT signal."""
    worker.log.info("Worker aborted (pid: %s)", worker.pid)