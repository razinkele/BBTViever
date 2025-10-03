#!/bin/bash
# MARBEFES BBT Database - Environment Setup Script
# This script sets up the complete development environment from scratch

set -e  # Exit on any error

echo "🛠️  MARBEFES BBT Database - Environment Setup"
echo "=============================================="

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python version
echo "🐍 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
echo "   Python version: $python_version"

# Check if Python version is 3.9 or higher
required_version="3.9"
if python3 -c "import sys; exit(0 if sys.version_info >= (3, 9) else 1)"; then
    echo "   ✅ Python version is compatible"
else
    echo "   ❌ Python 3.9+ required. Please upgrade Python."
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ -d "venv" ]; then
    echo "📦 Virtual environment already exists"
    read -p "   Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "   🗑️  Removing existing virtual environment..."
        rm -rf venv
    else
        echo "   📦 Using existing virtual environment"
        source venv/bin/activate
        echo "   ✅ Virtual environment activated"
        pip install --upgrade pip
        pip install -r requirements-venv.txt
        echo "   ✅ Dependencies updated"
        exit 0
    fi
fi

echo "📦 Creating virtual environment..."
python3 -m venv venv

echo "🔧 Activating virtual environment..."
source venv/bin/activate

echo "⬆️  Upgrading pip..."
pip install --upgrade pip

echo "📥 Installing dependencies..."
pip install -r requirements-venv.txt

echo "📁 Creating project directories..."
mkdir -p data/vector
mkdir -p logs
mkdir -p static
mkdir -p templates
mkdir -p config
mkdir -p scripts

echo "🔧 Creating log directory..."
touch logs/.gitkeep

echo "📄 Checking configuration files..."
if [ ! -f ".env" ]; then
    echo "   ⚠️  .env file not found, but it exists in the project"
else
    echo "   ✅ .env file exists"
fi

# Test import of critical modules
echo "🧪 Testing critical imports..."
python -c "
try:
    import flask
    print('   ✅ Flask imported successfully')
except ImportError as e:
    print(f'   ❌ Flask import failed: {e}')

try:
    import requests
    print('   ✅ Requests imported successfully')
except ImportError as e:
    print(f'   ❌ Requests import failed: {e}')

try:
    import geopandas
    print('   ✅ GeoPandas imported successfully')
except ImportError as e:
    print(f'   ⚠️  GeoPandas import failed: {e}')
    print('      Vector support will be disabled')

try:
    import fiona
    print('   ✅ Fiona imported successfully')
except ImportError as e:
    print(f'   ⚠️  Fiona import failed: {e}')
    print('      Vector support will be disabled')
"

# Test Flask app import
echo "🧪 Testing Flask application import..."
python -c "
try:
    import sys
    sys.path.insert(0, 'src')
    from app import app
    print('   ✅ Flask application imported successfully')
except ImportError as e:
    print(f'   ❌ Flask application import failed: {e}')
    print('      Check that app.py exists and is properly configured')
except Exception as e:
    print(f'   ⚠️  Flask application loaded with warnings: {e}')
"

echo ""
echo "🎉 Environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Review the .env file for configuration"
echo "   2. Place your GPKG data files in data/vector/"
echo "   3. Run: ./start_server.sh"
echo "   4. Open http://localhost:5000 in your browser"
echo ""
echo "📚 Available commands:"
echo "   ./start_server.sh     - Start the Flask development server"
echo "   ./stop_server.sh      - Stop any running Flask servers"
echo ""
echo "📖 Documentation:"
echo "   docs/README.md        - Main documentation"
echo "   docs/USER_GUIDE.md    - User guide"
echo "   docs/API.md           - API documentation"
echo "   docs/DEVELOPER.md     - Developer guide"
echo ""