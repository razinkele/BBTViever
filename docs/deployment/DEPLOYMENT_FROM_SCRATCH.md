# MARBEFES BBT Database - Complete Deployment from Scratch

**Version:** 1.2.7 (Zoom Threshold Alignment)
**Target Server:** laguna.ku.lt
**Application URL:** http://laguna.ku.lt/BBT
**Date:** October 15, 2025

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Server Preparation](#server-preparation)
3. [System Dependencies](#system-dependencies)
4. [Application Setup](#application-setup)
5. [Python Environment](#python-environment)
6. [Data Files](#data-files)
7. [Nginx Configuration](#nginx-configuration)
8. [Systemd Service](#systemd-service)
9. [Deployment](#deployment)
10. [Verification](#verification)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Information

- **Server:** laguna.ku.lt
- **User:** razinka
- **SSH Access:** Required with sudo privileges
- **Application Path:** /var/www/marbefes-bbt
- **Subpath:** /BBT
- **Port:** 5000 (internal), 80 (nginx)

### Local Requirements

- Git repository access
- SSH keys configured
- rsync installed
- Internet connection

### Server Requirements

- **OS:** Ubuntu 20.04+ or Debian 11+
- **CPU:** 2+ cores recommended
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 10GB free space minimum
- **Python:** 3.9 or higher

---

## Server Preparation

### Step 1: Initial SSH Access

```bash
# Test SSH connection from your local machine
ssh razinka@laguna.ku.lt

# If connection fails, configure SSH keys:
ssh-keygen -t ed25519 -C "your_email@example.com"
ssh-copy-id razinka@laguna.ku.lt
```

### Step 2: Update System

```bash
# Once connected to the server
sudo apt-get update
sudo apt-get upgrade -y
```

### Step 3: Create Application Directory

```bash
# Create directory structure
sudo mkdir -p /var/www/marbefes-bbt
sudo chown -R razinka:razinka /var/www/marbefes-bbt
mkdir -p /var/www/marbefes-bbt/{data/vector,logs,static,templates,config,src}
```

---

## System Dependencies

### Step 4: Install Required Packages

```bash
# Python and development tools
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential

# Geospatial libraries (required for GeoPandas)
sudo apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    libproj-dev \
    libspatialindex-dev

# Web server and tools
sudo apt-get install -y \
    nginx \
    git \
    curl \
    wget \
    htop

# Optional: Redis for distributed caching (if needed later)
# sudo apt-get install -y redis-server
```

### Step 5: Verify Python Version

```bash
python3 --version
# Expected: Python 3.9 or higher

# If version is too old, install from deadsnakes PPA:
# sudo add-apt-repository ppa:deadsnakes/ppa
# sudo apt-get update
# sudo apt-get install python3.10 python3.10-venv python3.10-dev
```

---

## Application Setup

### Step 6: Clone Repository (or Copy Files)

**Option A: Using Git (Recommended)**

```bash
# Clone the repository
cd /var/www
git clone https://github.com/razinkele/BBTViever.git marbefes-bbt

# Or if directory already exists:
cd /var/www/marbefes-bbt
git init
git remote add origin https://github.com/razinkele/BBTViever.git
git fetch
git checkout main
```

**Option B: Manual File Transfer**

```bash
# From your local machine:
rsync -avz --progress \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='logs/*' \
    /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/ \
    razinka@laguna.ku.lt:/var/www/marbefes-bbt/
```

### Step 7: Verify File Structure

```bash
cd /var/www/marbefes-bbt
ls -la

# Expected structure:
# app.py
# requirements.txt
# gunicorn_config.py
# config/
# src/
# static/
# templates/
# data/
# logs/
```

---

## Python Environment

### Step 8: Create Virtual Environment

```bash
cd /var/www/marbefes-bbt

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip and setuptools
pip install --upgrade pip wheel setuptools
```

### Step 9: Install Python Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# If requirements.txt is missing key packages, install manually:
pip install \
    Flask==3.1.2 \
    Flask-Caching==2.3.1 \
    Flask-Compress==1.18 \
    Flask-Limiter==3.8.0 \
    requests==2.32.3 \
    geopandas==1.1.1 \
    fiona==1.10.1 \
    pyproj==3.7.1 \
    werkzeug==3.1.3 \
    gunicorn==23.0.0

# Verify critical packages
pip list | grep -E "Flask|geopandas|gunicorn"
```

**Expected Output:**
```
Flask              3.1.2
Flask-Caching      2.3.1
Flask-Compress     1.18
Flask-Limiter      3.8.0
geopandas          1.1.1
gunicorn           23.0.0
```

### Step 10: Set GDAL Environment Variables

```bash
# Find GDAL version
gdal-config --version

# Export GDAL paths (add to venv/bin/activate for persistence)
export CPLUS_INCLUDE_PATH=/usr/include/gdal
export C_INCLUDE_PATH=/usr/include/gdal
export GDAL_CONFIG=/usr/bin/gdal-config

# Verify GDAL works with Python
python -c "from osgeo import gdal; print('GDAL version:', gdal.__version__)"
```

---

## Data Files

### Step 11: Deploy Vector Data

```bash
# Create data directory
mkdir -p /var/www/marbefes-bbt/data/vector

# Copy vector files from local machine
# From your local machine:
rsync -avz --progress \
    /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/data/vector/ \
    razinka@laguna.ku.lt:/var/www/marbefes-bbt/data/vector/

# Or download from repository
# Place MergedBBTs.geojson in data/vector/
```

### Step 12: Verify Data Files

```bash
# Check data files exist
ls -lh /var/www/marbefes-bbt/data/vector/

# Expected:
# MergedBBTs.geojson (should be ~10MB)

# Verify file is valid GeoJSON
file /var/www/marbefes-bbt/data/vector/MergedBBTs.geojson
# Expected: ASCII text, with very long lines (65536)
```

---

## Nginx Configuration

### Step 13: Create Nginx Configuration

```bash
# Create nginx configuration file
sudo nano /etc/nginx/sites-available/marbefes-bbt
```

Paste the following configuration:

```nginx
# MARBEFES BBT Database - Nginx Configuration
# Application served at: http://laguna.ku.lt/BBT

upstream marbefes_bbt {
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;
    server_name laguna.ku.lt;

    # Increase max upload size for large GeoJSON
    client_max_body_size 20M;

    # Logging
    access_log /var/log/nginx/marbefes-bbt-access.log;
    error_log /var/log/nginx/marbefes-bbt-error.log;

    # Main application at /BBT subpath
    location /BBT {
        proxy_pass http://marbefes_bbt;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Script-Name /BBT;

        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;

        # Buffering
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 24 4k;
        proxy_busy_buffers_size 8k;
    }

    # Static files - logo
    location /BBT/logo/ {
        alias /var/www/marbefes-bbt/LOGO/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Static files - CSS, JS, images
    location /BBT/static/ {
        alias /var/www/marbefes-bbt/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/x-javascript
        application/xml
        application/xml+rss
        application/atom+xml
        application/geo+json
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Disable server signature
    server_tokens off;
}
```

### Step 14: Enable Nginx Site

```bash
# Create symbolic link to enable site
sudo ln -sf /etc/nginx/sites-available/marbefes-bbt /etc/nginx/sites-enabled/

# Remove default nginx site (optional)
sudo rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
sudo nginx -t

# Expected output:
# nginx: configuration file /etc/nginx/nginx.conf test is successful

# Reload nginx
sudo systemctl reload nginx

# Check nginx status
sudo systemctl status nginx
```

---

## Systemd Service

### Step 15: Create Gunicorn Configuration

```bash
# Create gunicorn config file
nano /var/www/marbefes-bbt/gunicorn_config.py
```

Paste the following:

```python
"""Gunicorn configuration for MARBEFES BBT Database - Production"""

import multiprocessing
import os

# Server socket
bind = "127.0.0.1:5000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50
timeout = 120
keepalive = 5

# Logging
accesslog = "logs/gunicorn-access.log"
errorlog = "logs/gunicorn-error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "marbefes-bbt"

# Server mechanics
daemon = False
pidfile = None
user = None
group = None
umask = 0
tmp_upload_dir = None

# Security
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190
```

### Step 16: Create Environment File

```bash
# Create production environment file
nano /var/www/marbefes-bbt/.env
```

Paste the following:

```bash
# Production Environment Configuration
FLASK_ENV=production
FLASK_DEBUG=False

# Generate secure secret key (run: openssl rand -hex 32)
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE

# Server Configuration
FLASK_HOST=127.0.0.1
FLASK_RUN_PORT=5000

# Application Path (subpath deployment)
APPLICATION_ROOT=/BBT
PREFERRED_URL_SCHEME=http

# WMS Configuration
WMS_BASE_URL=https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms
WMS_VERSION=1.3.0
WMS_TIMEOUT=10

# Cache Configuration
CACHE_TYPE=SimpleCache
CACHE_DEFAULT_TIMEOUT=300

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/marbefes-bbt.log

# Security Headers
ENABLE_HSTS=False
```

**Generate SECRET_KEY:**
```bash
# Generate a secure secret key
openssl rand -hex 32

# Copy the output and paste it into .env file as SECRET_KEY value
```

### Step 17: Create Systemd Service File

```bash
# Create service file
sudo nano /etc/systemd/system/marbefes-bbt.service
```

Paste the following:

```ini
[Unit]
Description=MARBEFES BBT Database - Marine Biodiversity Flask Application
Documentation=https://github.com/marbefes/bbt-database
After=network.target

[Service]
Type=simple
User=razinka
Group=razinka
WorkingDirectory=/var/www/marbefes-bbt
Environment="PATH=/var/www/marbefes-bbt/venv/bin"
EnvironmentFile=/var/www/marbefes-bbt/.env

# Gunicorn command
ExecStart=/var/www/marbefes-bbt/venv/bin/gunicorn \
    --config /var/www/marbefes-bbt/gunicorn_config.py \
    --bind 127.0.0.1:5000 \
    app:app

# Restart policy
Restart=always
RestartSec=10
StartLimitInterval=0

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/marbefes-bbt/logs

# Resource limits
LimitNOFILE=65535
TimeoutStartSec=120
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### Step 18: Set File Permissions

```bash
# Set ownership
sudo chown -R razinka:razinka /var/www/marbefes-bbt

# Set directory permissions
sudo chmod 755 /var/www/marbefes-bbt
sudo chmod 755 /var/www/marbefes-bbt/logs
sudo chmod 755 /var/www/marbefes-bbt/data

# Set file permissions
sudo chmod 644 /var/www/marbefes-bbt/.env
sudo chmod 644 /var/www/marbefes-bbt/app.py
sudo chmod 644 /var/www/marbefes-bbt/gunicorn_config.py

# Make Python files executable if needed
sudo chmod +x /var/www/marbefes-bbt/app.py
```

---

## Deployment

### Step 19: Enable and Start Service

```bash
# Reload systemd daemon
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable marbefes-bbt

# Start service
sudo systemctl start marbefes-bbt

# Check status
sudo systemctl status marbefes-bbt
```

**Expected Output:**
```
● marbefes-bbt.service - MARBEFES BBT Database
   Loaded: loaded (/etc/systemd/system/marbefes-bbt.service; enabled)
   Active: active (running) since Wed 2025-10-15 12:00:00 UTC; 5s ago
   Main PID: 12345 (gunicorn)
   Tasks: 17 (limit: 4915)
   Memory: 450.0M
   CGroup: /system.slice/marbefes-bbt.service
           ├─12345 /var/www/marbefes-bbt/venv/bin/python...
           └─12346 /var/www/marbefes-bbt/venv/bin/python...
```

### Step 20: Check Logs

```bash
# View service logs
sudo journalctl -u marbefes-bbt -n 50 --no-pager

# View gunicorn logs
tail -50 /var/www/marbefes-bbt/logs/gunicorn-error.log

# View nginx logs
sudo tail -50 /var/log/nginx/marbefes-bbt-access.log
```

---

## Verification

### Step 21: Test Application Endpoints

```bash
# Test health endpoint (direct to application)
curl http://localhost:5000/health

# Expected output:
# {"status":"healthy","version":"1.2.7","version_date":"2025-10-15"}

# Test through nginx with subpath
curl http://localhost/BBT/health

# Test from external
curl http://laguna.ku.lt/BBT/health
```

### Step 22: Test Main Page

```bash
# Test homepage returns HTML
curl -I http://localhost/BBT/

# Expected:
# HTTP/1.1 200 OK
# Content-Type: text/html; charset=utf-8
```

### Step 23: Test Vector API

```bash
# Test vector layers endpoint
curl http://localhost/BBT/api/vector/layers | jq '.'

# Expected:
# {
#   "count": 1,
#   "layers": [
#     {
#       "name": "MergedBBTs",
#       "feature_count": 12,
#       ...
#     }
#   ]
# }
```

### Step 24: Browser Testing

Open in browser: **http://laguna.ku.lt/BBT**

✅ **Verify:**
1. Map loads without errors
2. MARBEFES logo displays
3. BBT navigation dropdown appears
4. Click any BBT button → zooms to level 12
5. Hover over BBT area → tooltip shows EUNIS data
6. No JavaScript console errors (F12)
7. Zoom to level 11 → tooltip shows gold "Zoom in 1 more level..." message
8. Status indicator shows correct simplification level

### Step 25: Performance Testing

```bash
# Test response times
time curl -s http://localhost/BBT/ > /dev/null
# Expected: < 2 seconds

# Check worker processes
pgrep -a gunicorn | grep marbefes
# Expected: Multiple worker processes (typically 17 on 8-core machine)

# Check memory usage
ps aux | grep gunicorn | grep -v grep | awk '{sum+=$4} END {print "Memory usage: " sum "%"}'
# Expected: < 50% total system memory
```

---

## Troubleshooting

### Issue 1: Service Fails to Start

**Symptoms:**
```bash
sudo systemctl status marbefes-bbt
# Active: failed (Result: exit-code)
```

**Diagnosis:**
```bash
# Check detailed logs
sudo journalctl -u marbefes-bbt -n 100 --no-pager | grep -i error

# Test manual start to see error
cd /var/www/marbefes-bbt
source venv/bin/activate
python app.py
```

**Common Causes:**
1. **Missing Python packages**
   ```bash
   pip install -r requirements.txt
   ```

2. **Port already in use**
   ```bash
   sudo lsof -i :5000
   sudo kill $(sudo lsof -t -i:5000)
   ```

3. **File permissions**
   ```bash
   sudo chown -R razinka:razinka /var/www/marbefes-bbt
   ```

### Issue 2: Nginx 502 Bad Gateway

**Symptoms:**
```bash
curl http://localhost/BBT/
# <html><body><h1>502 Bad Gateway</h1></body></html>
```

**Diagnosis:**
```bash
# Check if gunicorn is running
pgrep -a gunicorn

# Check nginx error log
sudo tail -50 /var/log/nginx/marbefes-bbt-error.log

# Test direct connection to gunicorn
curl http://127.0.0.1:5000/health
```

**Solutions:**
```bash
# Restart application
sudo systemctl restart marbefes-bbt

# Restart nginx
sudo systemctl restart nginx

# Check nginx configuration
sudo nginx -t
```

### Issue 3: Vector Layers Not Loading

**Symptoms:**
- API returns empty array: `{"count": 0, "layers": []}`
- Browser console: "No vector layers found"

**Diagnosis:**
```bash
# Check data files exist
ls -lh /var/www/marbefes-bbt/data/vector/

# Check file permissions
ls -la /var/www/marbefes-bbt/data/vector/MergedBBTs.geojson

# Test geopandas import
cd /var/www/marbefes-bbt
source venv/bin/activate
python -c "import geopandas as gpd; df = gpd.read_file('data/vector/MergedBBTs.geojson'); print(f'Loaded {len(df)} features')"
```

**Solutions:**
```bash
# Fix permissions
sudo chown razinka:razinka /var/www/marbefes-bbt/data/vector/*.geojson
sudo chmod 644 /var/www/marbefes-bbt/data/vector/*.geojson

# Reinstall geospatial libraries
pip install --force-reinstall geopandas fiona pyproj
```

### Issue 4: Static Files Return 404

**Symptoms:**
- Browser console: `GET http://laguna.ku.lt/BBT/static/js/app.js 404`

**Diagnosis:**
```bash
# Check files exist
ls -lh /var/www/marbefes-bbt/static/js/

# Check nginx static file configuration
sudo nginx -t
sudo cat /etc/nginx/sites-available/marbefes-bbt | grep -A 5 "location /BBT/static"
```

**Solutions:**
```bash
# Fix static file permissions
sudo chmod -R 755 /var/www/marbefes-bbt/static

# Reload nginx
sudo systemctl reload nginx
```

---

## Post-Deployment Checklist

After 1 hour of deployment:

- ☐ Service status: `active (running)`
- ☐ No errors in logs: `sudo journalctl -u marbefes-bbt --since "1 hour ago" | grep -i error`
- ☐ Health endpoint responding: `curl http://laguna.ku.lt/BBT/health`
- ☐ Main page loads: `curl -I http://laguna.ku.lt/BBT/`
- ☐ Vector layers load: 12 BBT features visible
- ☐ Response times < 500ms
- ☐ Memory usage stable (< 50%)
- ☐ No nginx 502 errors
- ☐ Browser testing confirms all features work
- ☐ Zoom threshold fixes working (level 12 default)

After 24 hours:

- ☐ Service uptime 100%
- ☐ No service restarts
- ☐ Log file size reasonable (< 100MB)
- ☐ No memory leaks
- ☐ Performance stable

---

## Maintenance Commands

### Daily Operations

```bash
# Check service status
sudo systemctl status marbefes-bbt

# View recent logs
sudo journalctl -u marbefes-bbt -n 100 --no-pager

# Restart service
sudo systemctl restart marbefes-bbt

# Reload nginx
sudo systemctl reload nginx
```

### Log Management

```bash
# Rotate logs manually
sudo logrotate -f /etc/logrotate.d/nginx

# Clean old logs
find /var/www/marbefes-bbt/logs -name "*.log" -mtime +30 -delete

# Monitor live logs
tail -f /var/www/marbefes-bbt/logs/gunicorn-access.log
```

### Updates

```bash
# Pull latest code
cd /var/www/marbefes-bbt
git pull origin main

# Activate venv and update dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt
deactivate

# Restart service
sudo systemctl restart marbefes-bbt
```

---

## Security Hardening (Optional but Recommended)

### Firewall Configuration

```bash
# Install UFW if not present
sudo apt-get install ufw

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### SSL/TLS Certificate (Let's Encrypt)

```bash
# Install certbot
sudo apt-get install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d laguna.ku.lt

# Test auto-renewal
sudo certbot renew --dry-run
```

### Rate Limiting (Already Configured in Flask)

The application already includes Flask-Limiter with these limits:
- Default: 200 requests/day, 50 requests/hour
- API endpoints: 10 requests/minute for expensive operations

---

## Backup Strategy

### Automated Backups

```bash
# Create backup script
sudo nano /usr/local/bin/backup-marbefes.sh
```

```bash
#!/bin/bash
BACKUP_DIR=/backup/marbefes-bbt
DATE=$(date +%Y%m%d-%H%M%S)
APP_DIR=/var/www/marbefes-bbt

mkdir -p $BACKUP_DIR

# Backup application
tar -czf $BACKUP_DIR/app-$DATE.tar.gz \
    -C $APP_DIR \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='cache' \
    --exclude='logs/*.log' \
    .

# Backup environment
cp $APP_DIR/.env $BACKUP_DIR/env-$DATE

# Keep only last 30 days
find $BACKUP_DIR -name "app-*.tar.gz" -mtime +30 -delete

echo "Backup completed: $BACKUP_DIR/app-$DATE.tar.gz"
```

```bash
# Make executable
sudo chmod +x /usr/local/bin/backup-marbefes.sh

# Add to cron (daily at 2 AM)
sudo crontab -e
# Add line:
# 0 2 * * * /usr/local/bin/backup-marbefes.sh
```

---

## Summary

You now have a complete MARBEFES BBT Database deployment with:

- ✅ Flask application running on Gunicorn
- ✅ Nginx reverse proxy with /BBT subpath
- ✅ Systemd service management
- ✅ 12 BBT areas with vector layer support
- ✅ EUNIS 2019 WMS integration
- ✅ Zoom threshold alignment (v1.2.7)
- ✅ Production-ready configuration
- ✅ Security headers and rate limiting
- ✅ Comprehensive logging
- ✅ Automated service restart

**Access URL:** http://laguna.ku.lt/BBT

---

**Document Version:** 1.0
**Last Updated:** 2025-10-15
**Prepared by:** Claude Code (Anthropic)
