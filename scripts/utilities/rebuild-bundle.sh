#!/bin/bash
# Quick Bundle Rebuild Script
# Rebuilds JavaScript bundle with cache-busting for MARBEFES BBT Database

set -e  # Exit on error

echo "🔨 MARBEFES BBT - Quick Bundle Rebuild"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if we're in the project root
if [ ! -f "build_bundle.py" ]; then
    echo "❌ Error: build_bundle.py not found"
    echo "   Please run this script from the project root directory"
    exit 1
fi

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python not found"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# Run the bundler
echo ""
echo "📦 Running Python bundler..."
$PYTHON_CMD build_bundle.py

echo ""
echo "✅ Bundle rebuild complete!"
echo ""
echo "💡 Tips:"
echo "   - Development mode: Individual JS files (9 requests)"
echo "   - Production mode:  Minified bundle (1 request, 66KB)"
echo "   - Toggle with FLASK_ENV environment variable"
echo ""
echo "🚀 To restart Flask with new bundle:"
echo "   Development: FLASK_ENV=development python app.py"
echo "   Production:  FLASK_ENV=production python app.py"
echo ""
