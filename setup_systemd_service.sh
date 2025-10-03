#!/bin/bash
# MARBEFES BBT Database - Systemd Service Setup Script
# This script sets up the Flask application as a systemd service

set -e  # Exit on any error

echo "🔧 MARBEFES BBT Database - Systemd Service Setup"
echo "================================================"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if running as root for service installation
if [[ $EUID -eq 0 ]]; then
    echo "❌ Please do not run this script as root!"
    echo "   This script will prompt for sudo when needed."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run ./setup_environment.sh first"
    exit 1
fi

# Activate virtual environment for testing
source venv/bin/activate

echo "🔍 Checking system requirements..."

# Check if systemd is available
if ! command -v systemctl &> /dev/null; then
    echo "❌ systemctl not found. This system doesn't use systemd."
    exit 1
fi

# Check if gunicorn is installed
if ! python -c "import gunicorn" 2>/dev/null; then
    echo "📦 Installing gunicorn..."
    pip install gunicorn
else
    echo "✅ Gunicorn is available"
fi

# Test Flask application import
echo "🧪 Testing Flask application..."
python -c "
import sys
sys.path.insert(0, 'src')
from app import app
print('✅ Flask application imports successfully')
"

# Check current user
CURRENT_USER=$(whoami)
echo "👤 Current user: $CURRENT_USER"

# Get absolute paths
APP_DIR="$(pwd)"
VENV_PATH="$APP_DIR/venv"
USER_HOME="$(eval echo ~$CURRENT_USER)"

echo "📁 Application directory: $APP_DIR"
echo "📁 Virtual environment: $VENV_PATH"

# Service selection
echo ""
echo "🔧 Service Configuration Options:"
echo "   1) Development Flask server (single worker, debug features)"
echo "   2) Production Gunicorn server (multiple workers, optimized)"
echo ""
read -p "Choose service type (1 or 2): " -n 1 -r
echo ""

case $REPLY in
    1)
        SERVICE_TYPE="development"
        SERVICE_FILE="flaskapp.service"
        echo "📝 Using development Flask server configuration"
        ;;
    2)
        SERVICE_TYPE="production"
        SERVICE_FILE="flaskapp-gunicorn.service"
        echo "📝 Using production Gunicorn server configuration"
        ;;
    *)
        echo "❌ Invalid selection. Exiting."
        exit 1
        ;;
esac

# Create customized service file
TEMP_SERVICE="/tmp/marbefes-$SERVICE_TYPE.service"
cp "$SERVICE_FILE" "$TEMP_SERVICE"

# Update paths in service file
sed -i "s|User=razinka|User=$CURRENT_USER|g" "$TEMP_SERVICE"
sed -i "s|Group=razinka|Group=$CURRENT_USER|g" "$TEMP_SERVICE"
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$APP_DIR|g" "$TEMP_SERVICE"
sed -i "s|Environment=PATH=.*|Environment=PATH=$VENV_PATH/bin|g" "$TEMP_SERVICE"
sed -i "s|Environment=VIRTUAL_ENV=.*|Environment=VIRTUAL_ENV=$VENV_PATH|g" "$TEMP_SERVICE"
sed -i "s|ExecStartPre=.*python|ExecStartPre=$VENV_PATH/bin/python|g" "$TEMP_SERVICE"
sed -i "s|ExecStart=.*python|ExecStart=$VENV_PATH/bin/python|g" "$TEMP_SERVICE"
sed -i "s|ExecStart=.*gunicorn|ExecStart=$VENV_PATH/bin/gunicorn|g" "$TEMP_SERVICE"
sed -i "s|ReadWritePaths=.*logs|ReadWritePaths=$APP_DIR/logs|g" "$TEMP_SERVICE"
sed -i "s|ReadWritePaths=.*data|ReadWritePaths=$APP_DIR/data|g" "$TEMP_SERVICE"

# Generate secure secret key
SECRET_KEY=$(openssl rand -base64 32)
sed -i "s|SECRET_KEY=your-production-secret-key-change-this|SECRET_KEY=$SECRET_KEY|g" "$TEMP_SERVICE"

echo "✅ Service file customized for your system"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs data/vector
touch logs/.gitkeep

# Set proper permissions
echo "🔒 Setting file permissions..."
chmod 755 "$APP_DIR"
chmod -R 755 venv/
chmod -R 755 logs/ data/
chmod +x run_flask.py

# Install the service
echo ""
echo "📋 Service file preview:"
echo "========================"
head -20 "$TEMP_SERVICE"
echo "..."
echo "========================"
echo ""

read -p "Install this service? (y/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Installing systemd service..."

    # Copy service file
    sudo cp "$TEMP_SERVICE" "/etc/systemd/system/flaskapp.service"

    # Set proper ownership and permissions
    sudo chown root:root "/etc/systemd/system/flaskapp.service"
    sudo chmod 644 "/etc/systemd/system/flaskapp.service"

    # Reload systemd
    sudo systemctl daemon-reload

    echo "✅ Service installed successfully!"

    # Ask about enabling the service
    echo ""
    read -p "Enable service to start on boot? (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        sudo systemctl enable flaskapp.service
        echo "✅ Service enabled for startup"
    fi

    # Ask about starting the service now
    echo ""
    read -p "Start the service now? (y/N): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🚀 Starting MARBEFES Flask service..."
        sudo systemctl start flaskapp.service

        # Wait a moment for startup
        sleep 3

        # Check service status
        if sudo systemctl is-active --quiet flaskapp.service; then
            echo "✅ Service started successfully!"
            echo ""
            echo "📊 Service Status:"
            sudo systemctl status flaskapp.service --no-pager -l
            echo ""
            echo "🌐 Application should be available at:"
            echo "   http://localhost:5000"
            echo "   http://$(hostname -I | awk '{print $1}'):5000"
        else
            echo "❌ Service failed to start. Checking logs..."
            sudo journalctl -u flaskapp.service --no-pager -l
        fi
    fi

    echo ""
    echo "📋 Service Management Commands:"
    echo "   sudo systemctl start flaskapp      # Start the service"
    echo "   sudo systemctl stop flaskapp       # Stop the service"
    echo "   sudo systemctl restart flaskapp    # Restart the service"
    echo "   sudo systemctl status flaskapp     # Check service status"
    echo "   sudo journalctl -u flaskapp -f     # View live logs"
    echo "   sudo systemctl enable flaskapp     # Enable startup on boot"
    echo "   sudo systemctl disable flaskapp    # Disable startup on boot"

else
    echo "ℹ️  Service file created but not installed."
    echo "   Manual installation: sudo cp $TEMP_SERVICE /etc/systemd/system/flaskapp.service"
fi

# Cleanup
rm -f "$TEMP_SERVICE"

echo ""
echo "🎉 Systemd service setup complete!"

if [ "$SERVICE_TYPE" = "production" ]; then
    echo ""
    echo "💡 Production Tips:"
    echo "   • Configure a reverse proxy (nginx/apache) for HTTPS"
    echo "   • Set up log rotation for application logs"
    echo "   • Monitor service health with systemd or external tools"
    echo "   • Consider firewall configuration for port 5000"
fi

echo ""
echo "📚 Additional Documentation:"
echo "   • Service logs: sudo journalctl -u flaskapp"
echo "   • Application logs: tail -f $APP_DIR/logs/app.log"
echo "   • Configuration: edit /etc/systemd/system/flaskapp.service"