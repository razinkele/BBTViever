#!/bin/bash
# Script to start development server accessible from network

echo "=================================="
echo "MARBEFES BBT - Start Dev Server"
echo "=================================="
echo ""

# Check if port 5000 is in use
echo "Checking port 5000..."
if netstat -tlnp 2>/dev/null | grep -q ":5000 "; then
    echo "⚠️  Port 5000 is currently in use by production server"
    echo ""
    echo "To free port 5000, run:"
    echo "  sudo systemctl stop marbefes-bbt"
    echo ""
    echo "Or use port 5001 instead (recommended for testing):"
    echo "  export FLASK_RUN_PORT=5001"
    echo ""
    read -p "Use port 5001 instead? (y/n): " choice
    if [[ "$choice" == "y" || "$choice" == "Y" ]]; then
        export FLASK_RUN_PORT=5001
        PORT=5001
    else
        echo "Please stop production server first, then run this script again"
        exit 1
    fi
else
    PORT=5000
fi

# Navigate to project directory
cd ~/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck || {
    echo "❌ Failed to change to project directory"
    exit 1
}

# Set Flask to listen on all network interfaces
export FLASK_HOST=0.0.0.0
export FLASK_DEBUG=True

# Show configuration
echo ""
echo "Starting Flask development server with:"
echo "  - Host: $FLASK_HOST (accessible from network)"
echo "  - Port: $PORT"
echo "  - Debug: $FLASK_DEBUG"
echo ""
echo "Access the application at:"
echo "  - Local: http://localhost:$PORT"
echo "  - Network: http://laguna.ku.lt:$PORT"
echo ""

# Check if firewall might block
if command -v ufw &> /dev/null; then
    echo "⚠️  Note: If you can't access from network, you may need to allow port $PORT:"
    echo "  sudo ufw allow $PORT/tcp"
    echo ""
fi

echo "Starting server... (Press Ctrl+C to stop)"
echo ""

# Start the Flask development server
python app.py
