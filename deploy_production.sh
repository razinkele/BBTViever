#!/bin/bash
################################################################################
# MARBEFES BBT Database - Production Deployment Script
#
# This script deploys the Flask application to /var/www/marbefes-bbt/
# and sets up all necessary production components
################################################################################

set -e  # Exit on error

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROD_DIR="/var/www/marbefes-bbt"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="marbefes-bbt"
NGINX_SITE="marbefes-bbt"
USER="www-data"
GROUP="www-data"

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   MARBEFES BBT Database - Production Deployment           ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ Please run as root or with sudo${NC}"
    exit 1
fi

# Check disk space
AVAILABLE_SPACE=$(df -BG / | tail -1 | awk '{print $4}' | sed 's/G//')
if [ "$AVAILABLE_SPACE" -lt 10 ]; then
    echo -e "${RED}✗ Warning: Low disk space (${AVAILABLE_SPACE}GB available)${NC}"
    echo -e "${YELLOW}  Deployment requires at least 10GB free space${NC}"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

################################################################################
# Step 1: Create production directory and copy files
################################################################################

echo -e "\n${BLUE}[Step 1/7]${NC} Creating production directory..."

# Create production directory
mkdir -p "$PROD_DIR"
cd "$PROD_DIR"

# Copy application files
echo -e "${BLUE}→${NC} Copying application files..."
rsync -av \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    --exclude='.pytest_cache' \
    --exclude='logs/*' \
    --exclude='.env' \
    "$SOURCE_DIR/" \
    "$PROD_DIR/"

# Create necessary directories
mkdir -p "$PROD_DIR/logs"
mkdir -p "$PROD_DIR/data/vector"

echo -e "${GREEN}✓${NC} Application files copied successfully"

################################################################################
# Step 2: Set up Python virtual environment
################################################################################

echo -e "\n${BLUE}[Step 2/7]${NC} Setting up Python virtual environment..."

# Check Python version
PYTHON_VERSION=$(python3 --version | awk '{print $2}' | cut -d. -f1,2)
REQUIRED_VERSION="3.9"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}✗ Python $REQUIRED_VERSION or higher required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

# Create virtual environment
python3 -m venv "$PROD_DIR/venv"

# Activate and install dependencies
source "$PROD_DIR/venv/bin/activate"

echo -e "${BLUE}→${NC} Installing Python dependencies..."
pip install --upgrade pip wheel setuptools

# Install production requirements
if [ -f "$PROD_DIR/requirements-prod.txt" ]; then
    pip install -r "$PROD_DIR/requirements-prod.txt"
else
    pip install -r "$PROD_DIR/requirements.txt"
fi

# Install Gunicorn for production
pip install gunicorn

deactivate

echo -e "${GREEN}✓${NC} Virtual environment configured"

################################################################################
# Step 3: Create production environment file
################################################################################

echo -e "\n${BLUE}[Step 3/7]${NC} Creating production environment file..."

cat > "$PROD_DIR/.env" << 'EOF'
# Production Environment Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)

# Server Configuration
FLASK_HOST=127.0.0.1
FLASK_RUN_PORT=5000

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

# Security Headers (enabled in production)
ENABLE_HSTS=True
EOF

# Generate actual secret key
SECRET_KEY=$(openssl rand -hex 32)
sed -i "s/SECRET_KEY=.*/SECRET_KEY=${SECRET_KEY}/" "$PROD_DIR/.env"

echo -e "${GREEN}✓${NC} Environment file created"

################################################################################
# Step 4: Create Gunicorn configuration
################################################################################

echo -e "\n${BLUE}[Step 4/7]${NC} Creating Gunicorn configuration..."

cat > "$PROD_DIR/gunicorn_config.py" << 'EOF'
"""Gunicorn configuration for MARBEFES BBT Database"""

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
EOF

echo -e "${GREEN}✓${NC} Gunicorn configuration created"

################################################################################
# Step 5: Create systemd service
################################################################################

echo -e "\n${BLUE}[Step 5/7]${NC} Creating systemd service..."

cat > "/etc/systemd/system/${SERVICE_NAME}.service" << EOF
[Unit]
Description=MARBEFES BBT Database - Marine Biodiversity Flask Application
Documentation=https://github.com/marbefes/bbt-database
After=network.target

[Service]
Type=simple
User=${USER}
Group=${GROUP}
WorkingDirectory=${PROD_DIR}
Environment="PATH=${PROD_DIR}/venv/bin"
EnvironmentFile=${PROD_DIR}/.env

# Gunicorn command
ExecStart=${PROD_DIR}/venv/bin/gunicorn \
    --config ${PROD_DIR}/gunicorn_config.py \
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
ReadWritePaths=${PROD_DIR}/logs

# Resource limits
LimitNOFILE=65535
TimeoutStartSec=120
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}✓${NC} Systemd service created: ${SERVICE_NAME}.service"

################################################################################
# Step 6: Create nginx configuration
################################################################################

echo -e "\n${BLUE}[Step 6/7]${NC} Creating nginx configuration..."

# Ensure nginx log directory exists
mkdir -p /var/log/nginx
chown www-data:www-data /var/log/nginx 2>/dev/null || chown nginx:nginx /var/log/nginx 2>/dev/null || true
chmod 755 /var/log/nginx

echo -e "${BLUE}→${NC} Nginx log directory created/verified"

cat > "/etc/nginx/sites-available/${NGINX_SITE}" << 'EOF'
# MARBEFES BBT Database - Nginx Configuration
# Production deployment with reverse proxy to Gunicorn

upstream marbefes_bbt {
    server 127.0.0.1:5000 fail_timeout=0;
}

server {
    listen 80;
    listen [::]:80;

    # Update with your actual domain
    server_name bbt.marbefes.eu www.bbt.marbefes.eu;

    # For local testing, comment out above and use:
    # server_name localhost;

    # Max upload size
    client_max_body_size 10M;

    # Logging
    access_log /var/log/nginx/marbefes-bbt-access.log;
    error_log /var/log/nginx/marbefes-bbt-error.log;

    # Main application
    location / {
        proxy_pass http://marbefes_bbt;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support (if needed in future)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts for WMS requests
        proxy_connect_timeout 120s;
        proxy_send_timeout 120s;
        proxy_read_timeout 120s;

        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 24 4k;
        proxy_busy_buffers_size 8k;
    }

    # Static files - logos
    location /logo/ {
        alias /var/www/marbefes-bbt/LOGO/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Static files - if you have a static directory
    location /static/ {
        alias /var/www/marbefes-bbt/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }

    # Health check endpoint (optional)
    location /health {
        access_log off;
        proxy_pass http://marbefes_bbt;
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
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
}

# HTTPS configuration (uncomment after obtaining SSL certificate)
# server {
#     listen 443 ssl http2;
#     listen [::]:443 ssl http2;
#     server_name bbt.marbefes.eu www.bbt.marbefes.eu;
#
#     ssl_certificate /etc/letsencrypt/live/bbt.marbefes.eu/fullchain.pem;
#     ssl_certificate_key /etc/letsencrypt/live/bbt.marbefes.eu/privkey.pem;
#
#     # SSL configuration
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384;
#     ssl_prefer_server_ciphers off;
#     ssl_session_cache shared:SSL:10m;
#     ssl_session_timeout 10m;
#
#     # HSTS
#     add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
#
#     # Same location blocks as HTTP
#     location / {
#         proxy_pass http://marbefes_bbt;
#         # ... (same proxy settings)
#     }
# }

# HTTP to HTTPS redirect (enable after SSL is configured)
# server {
#     listen 80;
#     listen [::]:80;
#     server_name bbt.marbefes.eu www.bbt.marbefes.eu;
#     return 301 https://$server_name$request_uri;
# }
EOF

# Enable nginx site
ln -sf "/etc/nginx/sites-available/${NGINX_SITE}" "/etc/nginx/sites-enabled/${NGINX_SITE}"

# Test nginx configuration
nginx -t

echo -e "${GREEN}✓${NC} Nginx configuration created and enabled"

################################################################################
# Step 7: Set permissions and enable services
################################################################################

echo -e "\n${BLUE}[Step 7/7]${NC} Setting permissions and enabling services..."

# Set ownership
chown -R ${USER}:${GROUP} "$PROD_DIR"

# Set appropriate permissions
chmod 755 "$PROD_DIR"
chmod 644 "$PROD_DIR/.env"
chmod 755 "$PROD_DIR/logs"

# Reload systemd
systemctl daemon-reload

# Enable and start service
systemctl enable ${SERVICE_NAME}
systemctl start ${SERVICE_NAME}

# Reload nginx
systemctl reload nginx

echo -e "${GREEN}✓${NC} Services enabled and started"

################################################################################
# Deployment Summary
################################################################################

echo -e "\n${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          Deployment Completed Successfully!               ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo -e "${BLUE}Application Details:${NC}"
echo -e "  Location:       ${PROD_DIR}"
echo -e "  Service:        ${SERVICE_NAME}.service"
echo -e "  Nginx Config:   /etc/nginx/sites-available/${NGINX_SITE}"
echo ""
echo -e "${BLUE}Access URLs:${NC}"
echo -e "  Local:          http://localhost"
echo -e "  Network:        http://$(hostname -I | awk '{print $1}')"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo -e "  Status:         ${YELLOW}sudo systemctl status ${SERVICE_NAME}${NC}"
echo -e "  Logs:           ${YELLOW}sudo journalctl -u ${SERVICE_NAME} -f${NC}"
echo -e "  Restart:        ${YELLOW}sudo systemctl restart ${SERVICE_NAME}${NC}"
echo -e "  Nginx Logs:     ${YELLOW}sudo tail -f /var/log/nginx/marbefes-bbt-*.log${NC}"
echo ""
echo -e "${BLUE}Next Steps:${NC}"
echo -e "  1. Update domain in nginx config: /etc/nginx/sites-available/${NGINX_SITE}"
echo -e "  2. Test application: ${YELLOW}curl -I http://localhost${NC}"
echo -e "  3. Setup SSL: ${YELLOW}sudo certbot --nginx -d your-domain.com${NC}"
echo -e "  4. Monitor logs for any issues"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
