#!/bin/bash
# Deployment script for MARBEFES BBT Database

set -e

# Configuration
APP_NAME="marbefes-bbt-database"
APP_DIR="/home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck"
SERVICE_FILE="$APP_NAME.service"
NGINX_CONFIG="nginx.conf"
BACKUP_DIR="$HOME/backups/marbefes-deployments"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Check if running as root
check_permissions() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Create backup
create_backup() {
    log "Creating backup..."
    mkdir -p "$BACKUP_DIR"
    BACKUP_NAME="marbefes-backup-$(date +%Y%m%d-%H%M%S).tar.gz"

    tar -czf "$BACKUP_DIR/$BACKUP_NAME" \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        --exclude='.git' \
        -C "$(dirname "$APP_DIR")" \
        "$(basename "$APP_DIR")"

    log "Backup created: $BACKUP_DIR/$BACKUP_NAME"
}

# Install system dependencies
install_dependencies() {
    log "Installing system dependencies..."

    # Update package list
    sudo apt update

    # Install required packages
    sudo apt install -y \
        python3-pip \
        python3-venv \
        nginx \
        supervisor \
        curl \
        git \
        libgdal-dev \
        libproj-dev \
        libgeos-dev \
        libspatialite-dev

    log "System dependencies installed"
}

# Setup Python environment
setup_python_env() {
    log "Setting up Python environment..."

    cd "$APP_DIR"

    # Create virtual environment if it doesn't exist
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
        log "Virtual environment created"
    fi

    # Activate virtual environment
    source venv/bin/activate

    # Upgrade pip
    pip install --upgrade pip

    # Install Python dependencies
    pip install -r requirements.txt

    log "Python environment setup complete"
}

# Setup directories
setup_directories() {
    log "Setting up directories..."

    mkdir -p "$APP_DIR/logs"
    mkdir -p "$APP_DIR/data/vector"
    mkdir -p "$APP_DIR/static"

    # Set proper permissions
    chmod 755 "$APP_DIR/logs"
    chmod 755 "$APP_DIR/data"

    log "Directories created"
}

# Deploy systemd service
deploy_systemd_service() {
    log "Deploying systemd service..."

    # Copy service file to systemd directory
    sudo cp "$APP_DIR/$SERVICE_FILE" "/etc/systemd/system/"

    # Reload systemd
    sudo systemctl daemon-reload

    # Enable service
    sudo systemctl enable "$APP_NAME"

    log "Systemd service deployed"
}

# Deploy nginx configuration
deploy_nginx() {
    log "Deploying nginx configuration..."

    # Remove default nginx site
    sudo rm -f /etc/nginx/sites-enabled/default

    # Copy nginx configuration
    sudo cp "$APP_DIR/$NGINX_CONFIG" "/etc/nginx/sites-available/$APP_NAME"

    # Create symbolic link
    sudo ln -sf "/etc/nginx/sites-available/$APP_NAME" "/etc/nginx/sites-enabled/"

    # Test nginx configuration
    sudo nginx -t

    # Reload nginx
    sudo systemctl reload nginx

    log "Nginx configuration deployed"
}

# Start services
start_services() {
    log "Starting services..."

    # Start and enable nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx

    # Start application service
    sudo systemctl start "$APP_NAME"

    # Check service status
    sleep 5
    sudo systemctl status "$APP_NAME" --no-pager

    log "Services started"
}

# Run health check
health_check() {
    log "Running health check..."

    # Wait for application to start
    sleep 10

    # Check if application responds
    if curl -f -s http://localhost:5000/api/layers > /dev/null; then
        log "Application is healthy!"
    else
        error "Application health check failed"
        exit 1
    fi
}

# Main deployment function
main() {
    log "Starting deployment of MARBEFES BBT Database..."

    check_permissions
    create_backup
    install_dependencies
    setup_python_env
    setup_directories
    deploy_systemd_service
    deploy_nginx
    start_services
    health_check

    log "Deployment completed successfully!"
    log "Application available at: http://localhost"
    log "Logs available at: $APP_DIR/logs/"
    log "Service status: sudo systemctl status $APP_NAME"
}

# Handle script arguments
case "${1:-}" in
    "backup")
        create_backup
        ;;
    "install-deps")
        install_dependencies
        ;;
    "setup-env")
        setup_python_env
        ;;
    "deploy-service")
        deploy_systemd_service
        ;;
    "deploy-nginx")
        deploy_nginx
        ;;
    "start")
        start_services
        ;;
    "health")
        health_check
        ;;
    "full"|"")
        main
        ;;
    *)
        echo "Usage: $0 [backup|install-deps|setup-env|deploy-service|deploy-nginx|start|health|full]"
        exit 1
        ;;
esac