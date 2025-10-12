#!/bin/bash
# Production startup script for MARBEFES BBT Database
# This script starts the application using Gunicorn with production settings

set -e  # Exit on error

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}MARBEFES BBT Database - Production Start${NC}"
echo -e "${GREEN}========================================${NC}"

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Please copy .env.example to .env and configure it:"
    echo "  cp .env.example .env"
    echo "  nano .env"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

# Validate required environment variables for production
if [ "$FLASK_ENV" = "production" ] && [ -z "$SECRET_KEY" ]; then
    echo -e "${RED}ERROR: SECRET_KEY not set in .env file!${NC}"
    echo "Generate a secure key and add it to .env:"
    echo "  python -c 'import secrets; print(secrets.token_hex(32))'"
    exit 1
fi

# Create necessary directories
mkdir -p logs
mkdir -p data/vector

# Check if gunicorn is installed
if ! command -v gunicorn &> /dev/null; then
    echo -e "${YELLOW}WARNING: Gunicorn not found. Installing...${NC}"
    pip install gunicorn>=21.2.0
fi

# Check if application imports successfully
echo -e "${YELLOW}Checking application integrity...${NC}"
if ! python -c "from app import app; print('✓ OK')" 2>&1 | grep -q "✓ OK"; then
    echo -e "${RED}ERROR: Application failed to import!${NC}"
    echo "Check logs above for error details."
    exit 1
fi
echo -e "${GREEN}✓ Application imports successfully${NC}"

# Determine number of workers
WORKERS=${GUNICORN_WORKERS:-$(python -c "import multiprocessing; print(multiprocessing.cpu_count() * 2 + 1)")}
BIND=${GUNICORN_BIND:-"0.0.0.0:5000"}

echo ""
echo -e "${GREEN}Configuration:${NC}"
echo "  Environment: ${FLASK_ENV:-development}"
echo "  Workers: $WORKERS"
echo "  Bind: $BIND"
echo "  Config: gunicorn_config.py"
echo ""

# Stop existing gunicorn processes
if [ -f "logs/gunicorn.pid" ]; then
    OLD_PID=$(cat logs/gunicorn.pid)
    if ps -p $OLD_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}Stopping existing Gunicorn process (PID: $OLD_PID)...${NC}"
        kill $OLD_PID
        sleep 2
    fi
fi

# Start Gunicorn
echo -e "${GREEN}Starting Gunicorn...${NC}"
gunicorn -c gunicorn_config.py app:app

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Server started successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
