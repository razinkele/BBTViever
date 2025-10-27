#!/bin/bash
# Management script for MARBEFES BBT Database

set -e

APP_NAME="marbefes-bbt-database"
APP_DIR="/home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"; }
warning() { echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"; }
error() { echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"; }

# Service management
start_service() {
    log "Starting $APP_NAME service..."
    sudo systemctl start "$APP_NAME"
    sudo systemctl status "$APP_NAME" --no-pager
}

stop_service() {
    log "Stopping $APP_NAME service..."
    sudo systemctl stop "$APP_NAME"
}

restart_service() {
    log "Restarting $APP_NAME service..."
    sudo systemctl restart "$APP_NAME"
    sudo systemctl status "$APP_NAME" --no-pager
}

status_service() {
    sudo systemctl status "$APP_NAME" --no-pager
}

# Logs management
view_logs() {
    case "${2:-app}" in
        "app")
            tail -f "$APP_DIR/logs/marbefes-app.log"
            ;;
        "gunicorn")
            tail -f "$APP_DIR/logs/gunicorn-error.log"
            ;;
        "access")
            tail -f "$APP_DIR/logs/gunicorn-access.log"
            ;;
        "systemd")
            sudo journalctl -u "$APP_NAME" -f
            ;;
        "nginx")
            sudo tail -f /var/log/nginx/marbefes-bbt-access.log
            ;;
        *)
            echo "Available logs: app, gunicorn, access, systemd, nginx"
            ;;
    esac
}

# Health check
health_check() {
    log "Running health check..."

    # Check service status
    if systemctl is-active --quiet "$APP_NAME"; then
        log "✅ Service is active"
    else
        error "❌ Service is not active"
        return 1
    fi

    # Check HTTP response
    if curl -f -s http://localhost:5000/api/layers > /dev/null; then
        log "✅ Application responds correctly"
    else
        error "❌ Application is not responding"
        return 1
    fi

    # Check disk space
    DISK_USAGE=$(df "$APP_DIR" | awk 'NR==2 {print $5}' | sed 's/%//')
    if [[ $DISK_USAGE -lt 90 ]]; then
        log "✅ Disk space OK (${DISK_USAGE}% used)"
    else
        warning "⚠️  Disk space high (${DISK_USAGE}% used)"
    fi

    # Check log file sizes
    for log_file in "$APP_DIR/logs"/*.log; do
        if [[ -f "$log_file" ]]; then
            size=$(stat -f%z "$log_file" 2>/dev/null || stat -c%s "$log_file" 2>/dev/null || echo 0)
            size_mb=$((size / 1024 / 1024))
            if [[ $size_mb -gt 100 ]]; then
                warning "⚠️  Large log file: $(basename "$log_file") (${size_mb}MB)"
            fi
        fi
    done

    log "Health check completed"
}

# Update application
update_app() {
    log "Updating application..."

    cd "$APP_DIR"

    # Activate virtual environment
    source venv/bin/activate

    # Update Python dependencies
    pip install --upgrade -r requirements.txt

    # Restart service
    restart_service

    log "Application updated"
}

# Backup
create_backup() {
    BACKUP_DIR="$HOME/backups/marbefes"
    mkdir -p "$BACKUP_DIR"

    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/marbefes_backup_$TIMESTAMP.tar.gz"

    log "Creating backup: $BACKUP_FILE"

    tar -czf "$BACKUP_FILE" \
        --exclude='venv' \
        --exclude='__pycache__' \
        --exclude='*.pyc' \
        -C "$APP_DIR" \
        data logs static templates app.py *.conf *.service

    log "Backup created: $BACKUP_FILE"
}

# Clean logs
clean_logs() {
    log "Cleaning old log files..."

    find "$APP_DIR/logs" -name "*.log" -type f -mtime +30 -delete

    # Truncate current logs if they're too large
    find "$APP_DIR/logs" -name "*.log" -type f -size +100M -exec truncate -s 10M {} \;

    log "Log cleanup completed"
}

# Monitor resources
monitor() {
    log "System Resource Monitor"
    echo "================================"

    # CPU and Memory usage of the application
    PID=$(pgrep -f "gunicorn.*app:app" || echo "")
    if [[ -n "$PID" ]]; then
        ps -p "$PID" -o pid,ppid,%cpu,%mem,cmd
    else
        warning "Application process not found"
    fi

    echo ""
    echo "Disk Usage:"
    df -h "$APP_DIR"

    echo ""
    echo "Memory Usage:"
    free -h

    echo ""
    echo "Network Connections:"
    ss -tulpn | grep :5000 || echo "No connections on port 5000"
}

# Show configuration
show_config() {
    log "Current Configuration"
    echo "================================"
    echo "App Directory: $APP_DIR"
    echo "Service: $APP_NAME"
    echo "Python Version: $(python3 --version 2>/dev/null || echo "Not found")"
    echo ""

    if [[ -f "$APP_DIR/.env" ]]; then
        echo "Environment (.env):"
        grep -E '^[A-Z_]+=.+' "$APP_DIR/.env" | head -10
    fi

    echo ""
    echo "Service Status:"
    systemctl is-enabled "$APP_NAME" 2>/dev/null || echo "Not enabled"
    systemctl is-active "$APP_NAME" 2>/dev/null || echo "Not active"
}

# Main function
main() {
    case "${1:-}" in
        "start")
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        "status")
            status_service
            ;;
        "logs")
            view_logs "$@"
            ;;
        "health")
            health_check
            ;;
        "update")
            update_app
            ;;
        "backup")
            create_backup
            ;;
        "clean")
            clean_logs
            ;;
        "monitor")
            monitor
            ;;
        "config")
            show_config
            ;;
        *)
            echo "MARBEFES BBT Database Management Script"
            echo "======================================="
            echo "Usage: $0 {start|stop|restart|status|logs|health|update|backup|clean|monitor|config}"
            echo ""
            echo "Commands:"
            echo "  start    - Start the application service"
            echo "  stop     - Stop the application service"
            echo "  restart  - Restart the application service"
            echo "  status   - Show service status"
            echo "  logs     - View logs (app|gunicorn|access|systemd|nginx)"
            echo "  health   - Run health check"
            echo "  update   - Update application and restart"
            echo "  backup   - Create backup of application data"
            echo "  clean    - Clean old log files"
            echo "  monitor  - Show resource usage"
            echo "  config   - Show current configuration"
            exit 1
            ;;
    esac
}

main "$@"