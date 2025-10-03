# MARBEFES BBT Database - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the MARBEFES BBT Database application in various environments, from development to production. The application is designed to be flexible and can be deployed using different methods depending on your infrastructure needs.

## Table of Contents

- [Quick Deployment](#quick-deployment)
- [Environment Setup](#environment-setup)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Cloud Deployment](#cloud-deployment)
- [Configuration Management](#configuration-management)
- [Performance Tuning](#performance-tuning)
- [Monitoring and Logging](#monitoring-and-logging)
- [Security Considerations](#security-considerations)
- [Backup and Recovery](#backup-and-recovery)
- [Troubleshooting](#troubleshooting)

## Quick Deployment

### Development Environment

For local development and testing:

```bash
# Clone repository
git clone <repository-url>
cd EMODNET_PyDeck

# Setup Python environment
conda create -n marbefes python=3.9
conda activate marbefes

# Install dependencies
pip install -r requirements.txt

# Run application
python app.py
```

Access the application at `http://localhost:5000`

### Production Ready (Single Server)

```bash
# Install production dependencies
pip install -r requirements.txt gunicorn

# Run with Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Environment Setup

### System Requirements

**Minimum Requirements:**
- CPU: 2 cores, 2.4 GHz
- RAM: 4 GB
- Storage: 10 GB free space
- Network: Stable internet connection for WMS services

**Recommended Production:**
- CPU: 4+ cores, 3.0+ GHz
- RAM: 8+ GB
- Storage: 50+ GB SSD
- Network: High-speed internet with low latency

**Operating System Support:**
- Linux (Ubuntu 20.04+, CentOS 8+, RHEL 8+)
- macOS 10.15+
- Windows 10/11 (with WSL2 recommended)

### Python Environment

#### Using Conda (Recommended)

```bash
# Install Miniconda/Anaconda first
# Then create environment
conda create -n marbefes-prod python=3.9
conda activate marbefes-prod

# Install geospatial dependencies
conda install -c conda-forge geopandas fiona pyproj

# Install remaining dependencies
pip install -r requirements.txt
```

#### Using Virtual Environment

```bash
# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    python3-dev \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    build-essential

# Install Python dependencies
pip install -r requirements.txt
```

### System Dependencies

#### Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install -y \
    python3.9 \
    python3.9-dev \
    python3-pip \
    git \
    nginx \
    postgresql \
    postgresql-contrib \
    postgis \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    proj-bin \
    supervisor
```

#### CentOS/RHEL

```bash
sudo yum update
sudo yum install -y \
    python39 \
    python39-devel \
    python3-pip \
    git \
    nginx \
    postgresql-server \
    postgresql-contrib \
    postgis \
    gdal \
    gdal-devel \
    geos \
    geos-devel \
    proj \
    proj-devel \
    supervisor
```

#### macOS

```bash
# Install Homebrew first
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install \
    python@3.9 \
    gdal \
    geos \
    proj \
    nginx \
    postgresql \
    postgis \
    supervisor
```

## Production Deployment

### Application Server Options

#### 1. Gunicorn (Recommended)

**Basic Configuration:**
```bash
# Install Gunicorn
pip install gunicorn

# Run with basic settings
gunicorn -w 4 -b 0.0.0.0:5000 app:app

# Run with optimized settings
gunicorn \
    --workers 4 \
    --worker-class sync \
    --worker-connections 1000 \
    --bind 0.0.0.0:5000 \
    --timeout 30 \
    --keepalive 2 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --preload \
    app:app
```

**Gunicorn Configuration File (`gunicorn.conf.py`):**
```python
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers
max_requests = 1000
max_requests_jitter = 100
preload_app = True

# Logging
accesslog = "/var/log/marbefes/access.log"
errorlog = "/var/log/marbefes/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "marbefes-app"

# Server mechanics
daemon = False
pidfile = "/var/run/marbefes/app.pid"
user = "marbefes"
group = "marbefes"
tmp_upload_dir = "/tmp"

# SSL (if using HTTPS directly)
# keyfile = "/path/to/ssl/key.pem"
# certfile = "/path/to/ssl/cert.pem"
```

**Run with configuration:**
```bash
gunicorn -c gunicorn.conf.py app:app
```

#### 2. uWSGI

**Installation:**
```bash
pip install uwsgi
```

**Configuration file (`uwsgi.ini`):**
```ini
[uwsgi]
module = app:app
master = true
processes = 4
socket = /tmp/marbefes.sock
chmod-socket = 666
vacuum = true
die-on-term = true
logto = /var/log/marbefes/uwsgi.log
```

**Run uWSGI:**
```bash
uwsgi --ini uwsgi.ini
```

### Reverse Proxy Configuration

#### Nginx (Recommended)

**Main configuration (`/etc/nginx/sites-available/marbefes`):**
```nginx
upstream marbefes_app {
    server 127.0.0.1:5000;
    # Add more servers for load balancing
    # server 127.0.0.1:5001;
    # server 127.0.0.1:5002;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    # SSL Configuration
    ssl_certificate /path/to/ssl/fullchain.pem;
    ssl_certificate_key /path/to/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json;

    # Main application
    location / {
        proxy_pass http://marbefes_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        proxy_buffering off;

        # WebSocket support (if needed for future features)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Static files (if serving separately)
    location /static/ {
        alias /path/to/app/static/;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }

    # API endpoints with longer timeouts
    location /api/ {
        proxy_pass http://marbefes_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Longer timeouts for data processing
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;

        # Increase buffer sizes for large GeoJSON responses
        proxy_buffer_size 128k;
        proxy_buffers 4 256k;
        proxy_busy_buffers_size 256k;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://marbefes_app;
        access_log off;
    }

    # Block unwanted requests
    location ~ /\. {
        deny all;
    }

    # Custom error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
}
```

**Enable site:**
```bash
sudo ln -s /etc/nginx/sites-available/marbefes /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### Apache

**Virtual host configuration:**
```apache
<VirtualHost *:80>
    ServerName your-domain.com
    Redirect permanent / https://your-domain.com/
</VirtualHost>

<VirtualHost *:443>
    ServerName your-domain.com

    # SSL Configuration
    SSLEngine on
    SSLCertificateFile /path/to/ssl/cert.pem
    SSLCertificateKeyFile /path/to/ssl/privkey.pem
    SSLCertificateChainFile /path/to/ssl/fullchain.pem

    # Security headers
    Header always set X-Frame-Options "SAMEORIGIN"
    Header always set X-XSS-Protection "1; mode=block"
    Header always set X-Content-Type-Options "nosniff"

    # Proxy configuration
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/

    # Logging
    ErrorLog ${APACHE_LOG_DIR}/marbefes_error.log
    CustomLog ${APACHE_LOG_DIR}/marbefes_access.log combined
</VirtualHost>
```

### Process Management

#### Systemd Service

**Create service file (`/etc/systemd/system/marbefes.service`):**
```ini
[Unit]
Description=MARBEFES BBT Database Application
After=network.target postgresql.service

[Service]
Type=notify
User=marbefes
Group=marbefes
WorkingDirectory=/opt/marbefes
Environment=PATH=/opt/marbefes/venv/bin
Environment=FLASK_ENV=production
Environment=FLASK_DEBUG=0
ExecStart=/opt/marbefes/venv/bin/gunicorn -c gunicorn.conf.py app:app
ExecReload=/bin/kill -s HUP $MAINPID
KillMode=mixed
TimeoutStopSec=5
PrivateTmp=true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start service:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable marbefes
sudo systemctl start marbefes
sudo systemctl status marbefes
```

#### Supervisor

**Configuration (`/etc/supervisor/conf.d/marbefes.conf`):**
```ini
[program:marbefes]
command=/opt/marbefes/venv/bin/gunicorn -c gunicorn.conf.py app:app
directory=/opt/marbefes
user=marbefes
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/marbefes/supervisor.log
environment=PATH="/opt/marbefes/venv/bin",FLASK_ENV="production"
```

**Update supervisor:**
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start marbefes
```

## Docker Deployment

### Single Container Deployment

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 marbefes && chown -R marbefes:marbefes /app
USER marbefes

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Start application
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
```

**Build and run:**
```bash
# Build image
docker build -t marbefes-app .

# Run container
docker run -d \
    --name marbefes \
    -p 5000:5000 \
    -v $(pwd)/data:/app/data \
    -e FLASK_ENV=production \
    --restart unless-stopped \
    marbefes-app
```

### Docker Compose Deployment

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - FLASK_DEBUG=0
      - WMS_TIMEOUT=30
    depends_on:
      - redis
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl/certs
    depends_on:
      - app
    restart: unless-stopped

  redis:
    image: redis:alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped
    command: redis-server --appendonly yes

volumes:
  redis_data:
```

**Run with compose:**
```bash
docker-compose up -d
docker-compose logs -f app
```

### Multi-Stage Build (Optimized)

**Dockerfile.production:**
```dockerfile
# Build stage
FROM python:3.9 as builder

RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    build-essential

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal28 \
    libgeos-3.8.0 \
    libproj15 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Copy application
WORKDIR /app
COPY . .

# Create non-root user
RUN useradd -m -u 1000 marbefes && chown -R marbefes:marbefes /app
USER marbefes

# Update PATH
ENV PATH=/root/.local/bin:$PATH

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"]
```

## Cloud Deployment

### AWS Deployment

#### Elastic Beanstalk

**requirements.txt** (add to existing):
```
awsebcli
```

**.ebextensions/01_python.config:**
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    FLASK_DEBUG: 0
```

**Deploy:**
```bash
pip install awsebcli
eb init
eb create marbefes-prod
eb deploy
```

#### ECS with Fargate

**task-definition.json:**
```json
{
  "family": "marbefes-app",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::ACCOUNT:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "marbefes-app",
      "image": "your-account.dkr.ecr.region.amazonaws.com/marbefes:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "FLASK_ENV",
          "value": "production"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/marbefes",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform

#### App Engine

**app.yaml:**
```yaml
runtime: python39

env_variables:
  FLASK_ENV: production
  FLASK_DEBUG: 0

automatic_scaling:
  min_instances: 1
  max_instances: 10
  target_cpu_utilization: 0.6

resources:
  cpu: 1
  memory_gb: 2
  disk_size_gb: 10
```

**Deploy:**
```bash
gcloud app deploy
```

#### Cloud Run

**Build and deploy:**
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/marbefes

# Deploy to Cloud Run
gcloud run deploy marbefes \
    --image gcr.io/PROJECT-ID/marbefes \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 2Gi \
    --cpu 2 \
    --max-instances 10
```

### Azure Deployment

#### App Service

**Create resource:**
```bash
az group create --name marbefes-rg --location eastus

az appservice plan create \
    --name marbefes-plan \
    --resource-group marbefes-rg \
    --sku B2 \
    --is-linux

az webapp create \
    --resource-group marbefes-rg \
    --plan marbefes-plan \
    --name marbefes-app \
    --runtime "PYTHON|3.9"
```

**Deploy:**
```bash
az webapp deployment source config-zip \
    --resource-group marbefes-rg \
    --name marbefes-app \
    --src app.zip
```

## Configuration Management

### Environment Variables

**Production environment file (`.env.production`):**
```bash
# Flask configuration
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-very-secure-secret-key-here

# WMS service configuration
WMS_BASE_URL=https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms
HELCOM_WMS_BASE_URL=https://maps.helcom.fi/arcgis/services/MADS/Pressures/MapServer/WMSServer
WMS_TIMEOUT=30

# Data directories
VECTOR_DATA_DIR=/opt/marbefes/data/vector

# Database configuration (if using external DB)
DATABASE_URL=postgresql://user:password@localhost:5432/marbefes

# Cache configuration
REDIS_URL=redis://localhost:6379/0
CACHE_TIMEOUT=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/marbefes/app.log

# Performance settings
WORKERS=4
MAX_REQUESTS=1000
TIMEOUT=30

# Security settings
SECURE_SSL_REDIRECT=1
SESSION_COOKIE_SECURE=1
CSRF_COOKIE_SECURE=1
```

### Configuration Classes

**config/production.py:**
```python
import os
from pathlib import Path

class ProductionConfig:
    """Production configuration"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY')
    DEBUG = False
    TESTING = False

    # WMS Services
    WMS_BASE_URL = os.environ.get('WMS_BASE_URL',
                                 'https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms')
    WMS_TIMEOUT = int(os.environ.get('WMS_TIMEOUT', '30'))

    # Data
    VECTOR_DATA_DIR = Path(os.environ.get('VECTOR_DATA_DIR', '/opt/marbefes/data/vector'))

    # Database
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # Cache
    REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TIMEOUT = int(os.environ.get('CACHE_TIMEOUT', '300'))

    # Security
    SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', '1').lower() == '1'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', '/var/log/marbefes/app.log')

    @classmethod
    def validate(cls):
        """Validate critical configuration"""
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production")
        if not cls.VECTOR_DATA_DIR.exists():
            raise ValueError(f"Vector data directory {cls.VECTOR_DATA_DIR} does not exist")
        return True
```

### Secrets Management

#### Using HashiCorp Vault

```python
import hvac

class VaultConfig:
    def __init__(self, vault_url, vault_token):
        self.client = hvac.Client(url=vault_url, token=vault_token)

    def get_secret(self, path, key):
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data'][key]
        except Exception as e:
            raise ValueError(f"Failed to retrieve secret {path}/{key}: {e}")

# Usage
vault = VaultConfig(
    vault_url=os.environ.get('VAULT_URL'),
    vault_token=os.environ.get('VAULT_TOKEN')
)

SECRET_KEY = vault.get_secret('marbefes/app', 'secret_key')
DATABASE_PASSWORD = vault.get_secret('marbefes/db', 'password')
```

#### Using AWS Secrets Manager

```python
import boto3
import json

def get_secret(secret_name, region_name="us-west-2"):
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        response = client.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret
    except Exception as e:
        raise ValueError(f"Failed to retrieve secret {secret_name}: {e}")

# Usage
secrets = get_secret('marbefes/production')
SECRET_KEY = secrets['secret_key']
DATABASE_URL = secrets['database_url']
```

## Performance Tuning

### Application Performance

#### Database Optimization

```python
# Connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=20,
    max_overflow=30,
    pool_recycle=3600,
    pool_pre_ping=True
)
```

#### Caching Strategy

```python
import redis
from functools import wraps
import json
import hashlib

# Redis connection
redis_client = redis.Redis.from_url(REDIS_URL)

def cache_result(timeout=300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key_data = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = hashlib.md5(key_data.encode()).hexdigest()

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Execute function and cache result
            result = func(*args, **kwargs)
            redis_client.setex(cache_key, timeout, json.dumps(result))
            return result
        return wrapper
    return decorator

# Usage
@cache_result(timeout=600)
def get_wms_capabilities():
    # Expensive WMS operation
    pass
```

#### Asynchronous Processing

```python
from celery import Celery

# Configure Celery
celery_app = Celery('marbefes')
celery_app.config_from_object('celeryconfig')

@celery_app.task
def process_large_dataset(dataset_path):
    """Process large datasets asynchronously"""
    # Heavy processing logic
    pass

# Usage in Flask route
@app.route('/api/process', methods=['POST'])
def start_processing():
    task = process_large_dataset.delay(request.json['dataset_path'])
    return jsonify({'task_id': task.id})
```

### Server Performance

#### Nginx Optimization

```nginx
# Worker processes
worker_processes auto;
worker_rlimit_nofile 65535;

events {
    worker_connections 4096;
    use epoll;
    multi_accept on;
}

http {
    # Buffer sizes
    client_body_buffer_size 128k;
    client_max_body_size 10m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    output_buffers 1 32k;
    postpone_output 1460;

    # Timeouts
    client_body_timeout 12;
    client_header_timeout 12;
    keepalive_timeout 15;
    send_timeout 10;

    # Compression
    gzip on;
    gzip_vary on;
    gzip_min_length 10240;
    gzip_comp_level 6;
    gzip_proxied any;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/javascript
        application/xml+rss
        application/json
        application/xml
        image/svg+xml;

    # File caching
    open_file_cache max=200000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
}
```

#### System Optimization

```bash
# Increase file limits
echo '* soft nofile 65536' >> /etc/security/limits.conf
echo '* hard nofile 65536' >> /etc/security/limits.conf

# Kernel parameters
cat >> /etc/sysctl.conf << EOF
net.core.somaxconn = 65536
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_max_syn_backlog = 65536
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30
net.ipv4.tcp_keepalive_time = 1200
vm.swappiness = 10
vm.dirty_ratio = 60
vm.dirty_background_ratio = 2
EOF

# Apply changes
sysctl -p
```

## Monitoring and Logging

### Application Monitoring

#### Health Check Endpoint

```python
@app.route('/health')
def health_check():
    """Application health check"""
    try:
        # Check database connectivity
        # Check WMS service availability
        # Check disk space
        # Check memory usage

        health_status = {
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': app.config.get('VERSION', '1.0.0'),
            'checks': {
                'database': check_database(),
                'wms_service': check_wms_service(),
                'disk_space': check_disk_space(),
                'memory': check_memory_usage()
            }
        }

        return jsonify(health_status)
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500
```

#### Metrics Collection

```python
import psutil
import time
from prometheus_client import Counter, Histogram, Gauge, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'Request duration')
ACTIVE_CONNECTIONS = Gauge('active_connections', 'Active connections')

@app.before_request
def before_request():
    request.start_time = time.time()
    REQUEST_COUNT.labels(method=request.method, endpoint=request.endpoint).inc()

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    REQUEST_DURATION.observe(duration)
    return response

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()
```

### Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }

        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        return json.dumps(log_entry)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.FileHandler('/var/log/marbefes/app.log'),
        logging.StreamHandler()
    ]
)

for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

### Log Aggregation

#### ELK Stack Configuration

**Filebeat configuration (`filebeat.yml`):**
```yaml
filebeat.inputs:
- type: log
  enabled: true
  paths:
    - /var/log/marbefes/*.log
  json.keys_under_root: true
  json.add_error_key: true

output.elasticsearch:
  hosts: ["elasticsearch:9200"]

setup.kibana:
  host: "kibana:5601"
```

#### Fluentd Configuration

```yaml
<source>
  @type tail
  path /var/log/marbefes/*.log
  pos_file /var/log/fluentd/marbefes.log.pos
  tag marbefes.*
  format json
</source>

<match marbefes.**>
  @type elasticsearch
  host elasticsearch
  port 9200
  index_name marbefes
  type_name application
</match>
```

## Security Considerations

### Application Security

#### HTTPS Configuration

```python
from flask_talisman import Talisman

# Configure HTTPS and security headers
Talisman(app, force_https=True, strict_transport_security=True)
```

#### Input Validation

```python
from marshmallow import Schema, fields, validate

class VectorLayerSchema(Schema):
    layer_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    simplify = fields.Float(validate=validate.Range(min=0, max=1))

@app.route('/api/vector/layer/<layer_name>')
def get_vector_layer(layer_name):
    schema = VectorLayerSchema()
    try:
        data = schema.load({'layer_name': layer_name, **request.args})
    except ValidationError as e:
        return jsonify({'errors': e.messages}), 400

    # Process validated data
    return get_layer_data(data['layer_name'], data.get('simplify'))
```

#### Rate Limiting

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["1000 per hour"]
)

@app.route('/api/vector/layers')
@limiter.limit("100 per minute")
def api_vector_layers():
    # API logic
    pass
```

### Infrastructure Security

#### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 5000/tcp  # Block direct app access

# iptables
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 80 -j ACCEPT
iptables -A INPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -s 127.0.0.1 -j ACCEPT
iptables -A INPUT -p tcp --dport 5000 -j DROP
```

#### SSH Hardening

```bash
# /etc/ssh/sshd_config
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
Port 2222
Protocol 2
AllowUsers marbefes
```

### Secrets Management

```bash
# Environment variables for production
export SECRET_KEY=$(openssl rand -base64 32)
export DATABASE_PASSWORD=$(openssl rand -base64 32)

# Store in secure location
echo "SECRET_KEY=$SECRET_KEY" >> /etc/marbefes/secrets
chmod 600 /etc/marbefes/secrets
chown marbefes:marbefes /etc/marbefes/secrets
```

## Backup and Recovery

### Data Backup Strategy

#### Vector Data Backup

```bash
#!/bin/bash
# backup_vector_data.sh

BACKUP_DIR="/backups/marbefes/vector"
DATA_DIR="/opt/marbefes/data/vector"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Create compressed backup
tar -czf "$BACKUP_DIR/vector_data_$DATE.tar.gz" -C "$DATA_DIR" .

# Keep only last 30 days of backups
find "$BACKUP_DIR" -name "vector_data_*.tar.gz" -mtime +30 -delete

# Upload to cloud storage (optional)
aws s3 cp "$BACKUP_DIR/vector_data_$DATE.tar.gz" s3://marbefes-backups/vector/
```

#### Database Backup

```bash
#!/bin/bash
# backup_database.sh

DB_NAME="marbefes"
BACKUP_DIR="/backups/marbefes/database"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# PostgreSQL backup
pg_dump "$DB_NAME" | gzip > "$BACKUP_DIR/db_backup_$DATE.sql.gz"

# Keep only last 7 days
find "$BACKUP_DIR" -name "db_backup_*.sql.gz" -mtime +7 -delete
```

#### Automated Backup with Cron

```bash
# Add to crontab
crontab -e

# Daily vector data backup at 2 AM
0 2 * * * /opt/marbefes/scripts/backup_vector_data.sh

# Daily database backup at 3 AM
0 3 * * * /opt/marbefes/scripts/backup_database.sh

# Weekly full system backup
0 1 * * 0 /opt/marbefes/scripts/full_backup.sh
```

### Disaster Recovery

#### Recovery Procedures

```bash
#!/bin/bash
# restore_from_backup.sh

BACKUP_DATE=$1
BACKUP_DIR="/backups/marbefes"

if [ -z "$BACKUP_DATE" ]; then
    echo "Usage: $0 <backup_date>"
    echo "Available backups:"
    ls -la "$BACKUP_DIR/vector/"
    exit 1
fi

# Stop application
sudo systemctl stop marbefes

# Restore vector data
tar -xzf "$BACKUP_DIR/vector/vector_data_$BACKUP_DATE.tar.gz" -C /opt/marbefes/data/vector/

# Restore database
gunzip < "$BACKUP_DIR/database/db_backup_$BACKUP_DATE.sql.gz" | psql marbefes

# Start application
sudo systemctl start marbefes

echo "Recovery completed for backup date: $BACKUP_DATE"
```

#### High Availability Setup

```bash
# Master-slave database configuration
# Setup streaming replication

# Primary server postgresql.conf
wal_level = replica
max_wal_senders = 3
checkpoint_segments = 8
wal_keep_segments = 8

# Standby server recovery.conf
standby_mode = 'on'
primary_conninfo = 'host=primary_ip port=5432 user=replicator'
restore_command = 'cp /var/lib/postgresql/archive/%f %p'
```

## Troubleshooting

### Common Issues

#### Application Won't Start

```bash
# Check service status
sudo systemctl status marbefes

# Check logs
sudo journalctl -u marbefes -f

# Check application logs
tail -f /var/log/marbefes/app.log

# Check port availability
sudo netstat -tulpn | grep 5000

# Check file permissions
ls -la /opt/marbefes/
```

#### Vector Data Loading Issues

```bash
# Check data directory
ls -la /opt/marbefes/data/vector/

# Test GPKG file
ogrinfo data/vector/BBts.gpkg

# Check Python dependencies
python -c "import geopandas; print('OK')"
python -c "import fiona; print('OK')"

# Check GDAL installation
gdalinfo --version
```

#### Performance Issues

```bash
# Check memory usage
free -h
ps aux | grep gunicorn

# Check disk space
df -h

# Check I/O usage
iotop

# Check network connectivity
curl -I https://ows.emodnet-seabedhabitats.eu/
```

### Debug Mode

```bash
# Enable debug mode temporarily
export FLASK_DEBUG=1
export FLASK_ENV=development

# Restart application
sudo systemctl restart marbefes

# Monitor debug output
tail -f /var/log/marbefes/app.log
```

### Log Analysis

```bash
# Find errors in logs
grep ERROR /var/log/marbefes/app.log

# Check access patterns
grep "GET /api" /var/log/nginx/access.log | cut -d' ' -f1 | sort | uniq -c | sort -nr

# Monitor real-time requests
tail -f /var/log/nginx/access.log | grep -E "(GET|POST) /api"
```

### Performance Monitoring

```bash
# Monitor system resources
htop

# Check application metrics
curl http://localhost:5000/metrics

# Database performance
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"
```

---

This deployment guide provides comprehensive coverage of deploying the MARBEFES BBT Database application in various environments. For additional support, refer to the main [README](../README.md) or the [Developer Guide](DEVELOPER.md).