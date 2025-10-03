#!/bin/bash
# MARBEFES BBT Database - Flask Server Startup Script
# This script activates the virtual environment and starts the Flask development server

set -e  # Exit on any error

echo "🚀 MARBEFES BBT Database - Starting Flask Server"
echo "=================================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup_environment.sh first to create the virtual environment."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python -c "import flask, requests" 2>/dev/null || {
    echo "❌ Required packages not installed!"
    echo "Installing dependencies..."
    pip install -r requirements-venv.txt
}

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/vector
mkdir -p logs
mkdir -p static
mkdir -p templates

# Load environment variables
if [ -f ".env" ]; then
    echo "🔧 Loading environment variables from .env"
    export $(grep -v '^#' .env | xargs)
fi

# Set default values if not set
export FLASK_APP=${FLASK_APP:-app.py}
export FLASK_ENV=${FLASK_ENV:-development}
export FLASK_DEBUG=${FLASK_DEBUG:-1}
export HOST=${HOST:-127.0.0.1}
export PORT=${PORT:-5000}

echo ""
echo "✅ Environment ready!"
echo "🌐 Starting Flask server on http://${HOST}:${PORT}"
echo "📊 Debug mode: ${FLASK_DEBUG}"
echo ""
echo "Press Ctrl+C to stop the server"
echo "--------------------------------------------------"

# Start the Flask application
python run_flask.py