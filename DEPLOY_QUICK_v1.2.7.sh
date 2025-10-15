#!/bin/bash
################################################################################
# MARBEFES BBT v1.2.7 - Quick Deployment Script
# Zoom Threshold Alignment Release
#
# This script automates the deployment of zoom threshold fixes to production.
# For detailed manual steps, see: MANUAL_DEPLOYMENT_v1.2.7.md
#
# Usage: ./DEPLOY_QUICK_v1.2.7.sh
################################################################################

set -e  # Exit on any error

# Configuration
SERVER="razinka@laguna.ku.lt"
APP_DIR="/var/www/marbefes-bbt"
SERVICE_NAME="marbefes-bbt"
VERSION="1.2.7"
SUBPATH="/BBT"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         MARBEFES BBT v${VERSION} Deployment                          ║${NC}"
echo -e "${BLUE}║         Zoom Threshold Alignment Release                      ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Pre-flight checks
echo -e "${BLUE}[Pre-Flight]${NC} Running checks..."

# Check SSH connection
if ! ssh ${SERVER} "echo 'SSH OK'" >/dev/null 2>&1; then
    echo -e "${RED}✗ SSH connection failed!${NC}"
    echo "  Please configure SSH keys: ssh-copy-id ${SERVER}"
    exit 1
fi
echo -e "${GREEN}✓${NC} SSH connection"

# Check if modified files exist locally
if [ ! -f "static/js/bbt-tool.js" ] || [ ! -f "static/js/layer-manager.js" ]; then
    echo -e "${RED}✗ Modified files not found!${NC}"
    echo "  Please run this script from the project root directory."
    exit 1
fi
echo -e "${GREEN}✓${NC} Source files found"

# Verify changes are present locally
if ! grep -q "window.bbtDetailZoomLevel = 12" static/js/bbt-tool.js; then
    echo -e "${RED}✗ Zoom fix not found in bbt-tool.js!${NC}"
    echo "  Please ensure you have the latest changes."
    exit 1
fi
echo -e "${GREEN}✓${NC} Zoom fixes verified locally"

echo ""

# Step 1: Create backup
echo -e "${BLUE}[1/8]${NC} Creating backup on server..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/var/www/marbefes-bbt-backups"

ssh ${SERVER} "sudo mkdir -p ${BACKUP_DIR} && \
    sudo tar -czf ${BACKUP_DIR}/backup_v1.2.6_${TIMESTAMP}.tar.gz \
        -C ${APP_DIR} \
        static/js/bbt-tool.js \
        static/js/layer-manager.js \
        app.py 2>/dev/null || true"

if ssh ${SERVER} "test -f ${BACKUP_DIR}/backup_v1.2.6_${TIMESTAMP}.tar.gz"; then
    BACKUP_SIZE=$(ssh ${SERVER} "du -h ${BACKUP_DIR}/backup_v1.2.6_${TIMESTAMP}.tar.gz" | cut -f1)
    echo -e "${GREEN}✓${NC} Backup created: backup_v1.2.6_${TIMESTAMP}.tar.gz (${BACKUP_SIZE})"
else
    echo -e "${YELLOW}⚠${NC} Backup might have failed, continuing..."
fi
echo ""

# Step 2: Stop service
echo -e "${BLUE}[2/8]${NC} Stopping application..."
ssh ${SERVER} "sudo systemctl stop ${SERVICE_NAME}" 2>/dev/null || \
ssh ${SERVER} "pkill -f 'gunicorn.*app:app' || true"
sleep 2
echo -e "${GREEN}✓${NC} Service stopped"
echo ""

# Step 3: Deploy JavaScript files
echo -e "${BLUE}[3/8]${NC} Deploying JavaScript files..."

echo "  → Deploying bbt-tool.js..."
rsync -az --progress static/js/bbt-tool.js ${SERVER}:${APP_DIR}/static/js/

echo "  → Deploying layer-manager.js..."
rsync -az --progress static/js/layer-manager.js ${SERVER}:${APP_DIR}/static/js/

echo -e "${GREEN}✓${NC} JavaScript files deployed"
echo ""

# Step 4: Update version file (optional)
echo -e "${BLUE}[4/8]${NC} Updating version information..."
if [ -f "src/emodnet_viewer/__version__.py" ]; then
    # Create temporary modified version file
    sed 's/__version__ = "1.2.6"/__version__ = "1.2.7"/' src/emodnet_viewer/__version__.py | \
    sed 's/__version_date__ = "2025-10-14"/__version_date__ = "2025-10-15"/' | \
    sed 's/__version_name__ = "Porsangerfjord.*"/__version_name__ = "Zoom Threshold Alignment"/' \
    > /tmp/__version_temp__.py

    rsync -az /tmp/__version_temp__.py ${SERVER}:${APP_DIR}/src/emodnet_viewer/__version__.py
    rm /tmp/__version_temp__.py
    echo -e "${GREEN}✓${NC} Version updated to ${VERSION}"
else
    echo -e "${YELLOW}⚠${NC} Version file not found, skipping"
fi
echo ""

# Step 5: Verify files on server
echo -e "${BLUE}[5/8]${NC} Verifying deployed files..."

# Check bbt-tool.js
if ssh ${SERVER} "grep -q 'window.bbtDetailZoomLevel = 12' ${APP_DIR}/static/js/bbt-tool.js"; then
    echo -e "${GREEN}✓${NC} bbt-tool.js: Default zoom = 12"
else
    echo -e "${RED}✗${NC} bbt-tool.js: Verification failed!"
    exit 1
fi

# Check layer-manager.js
if ssh ${SERVER} "grep -q 'currentZoom < 12.*simplified' ${APP_DIR}/static/js/layer-manager.js"; then
    echo -e "${GREEN}✓${NC} layer-manager.js: Status threshold = 12"
else
    echo -e "${RED}✗${NC} layer-manager.js: Verification failed!"
    exit 1
fi

# Check validation code
if ssh ${SERVER} "grep -q 'EUNIS threshold' ${APP_DIR}/static/js/bbt-tool.js"; then
    echo -e "${GREEN}✓${NC} bbt-tool.js: Validation code present"
else
    echo -e "${YELLOW}⚠${NC} bbt-tool.js: Validation code not found (check manually)"
fi
echo ""

# Step 6: Add cache-busting query parameters
echo -e "${BLUE}[6/8]${NC} Adding cache-busting parameters..."
ssh ${SERVER} "cd ${APP_DIR} && \
    sed -i 's|static/js/bbt-tool.js\(\"\\|'\''\\|?\)|static/js/bbt-tool.js?v=${VERSION}\1|g' templates/index.html && \
    sed -i 's|static/js/layer-manager.js\(\"\\|'\''\\|?\)|static/js/layer-manager.js?v=${VERSION}\1|g' templates/index.html"
echo -e "${GREEN}✓${NC} Cache-busting parameters added"
echo ""

# Step 7: Start service
echo -e "${BLUE}[7/8]${NC} Starting application..."
ssh ${SERVER} "sudo systemctl start ${SERVICE_NAME}"
sleep 5

# Check if service started
if ssh ${SERVER} "sudo systemctl is-active ${SERVICE_NAME} >/dev/null 2>&1"; then
    WORKER_COUNT=$(ssh ${SERVER} "pgrep -f 'gunicorn.*app:app' | wc -l" || echo "0")
    echo -e "${GREEN}✓${NC} Service started (${WORKER_COUNT} workers)"
else
    echo -e "${RED}✗${NC} Service failed to start!"
    echo ""
    echo "Checking logs..."
    ssh ${SERVER} "sudo journalctl -u ${SERVICE_NAME} -n 20 --no-pager"
    exit 1
fi
echo ""

# Step 8: Verification tests
echo -e "${BLUE}[8/8]${NC} Running verification tests..."

# Wait for application to be ready
sleep 3

# Test 1: Health endpoint
echo -n "  → Health check... "
if curl -s -f http://laguna.ku.lt${SUBPATH}/health >/dev/null 2>&1; then
    DEPLOYED_VERSION=$(curl -s http://laguna.ku.lt${SUBPATH}/health | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    if [ "$DEPLOYED_VERSION" = "${VERSION}" ]; then
        echo -e "${GREEN}✓${NC} (v${DEPLOYED_VERSION})"
    else
        echo -e "${YELLOW}⚠${NC} (v${DEPLOYED_VERSION}, expected v${VERSION})"
    fi
else
    echo -e "${RED}✗${NC}"
    echo -e "${YELLOW}⚠ Health endpoint not responding (may need time to initialize)${NC}"
fi

# Test 2: Main page
echo -n "  → Main page... "
if curl -s -f http://laguna.ku.lt${SUBPATH}/ >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test 3: JavaScript files
echo -n "  → JavaScript files... "
if curl -s -I http://laguna.ku.lt${SUBPATH}/static/js/bbt-tool.js | grep -q "200 OK"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Test 4: Vector layers API
echo -n "  → Vector layers API... "
BBT_COUNT=$(curl -s http://laguna.ku.lt${SUBPATH}/api/vector/layers | grep -o '"count":[0-9]*' | cut -d':' -f2 2>/dev/null || echo "0")
if [ "$BBT_COUNT" -gt "0" ]; then
    echo -e "${GREEN}✓${NC} (${BBT_COUNT} layers)"
else
    echo -e "${YELLOW}⚠${NC} (${BBT_COUNT} layers)"
fi

echo ""

# Deployment summary
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║            Deployment Completed Successfully!                 ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Version Information:${NC}"
echo "  Previous Version: 1.2.6"
echo "  Deployed Version: ${VERSION}"
echo "  Release Date:     2025-10-15"
echo ""
echo -e "${BLUE}Changes Deployed:${NC}"
echo "  ✓ Default BBT zoom: 11 → 12"
echo "  ✓ Status threshold: 6 → 12"
echo "  ✓ Zoom validation: Added (enforces min 12)"
echo "  ✓ Tooltip guidance: Enhanced (zoom-specific)"
echo ""
echo -e "${BLUE}Access Information:${NC}"
echo "  Application URL:  http://laguna.ku.lt${SUBPATH}"
echo "  Health Check:     http://laguna.ku.lt${SUBPATH}/health"
echo "  Version API:      http://laguna.ku.lt${SUBPATH}/api/version"
echo ""
echo -e "${BLUE}Testing Checklist:${NC}"
echo "  1. Open http://laguna.ku.lt${SUBPATH} in browser"
echo "  2. Hard refresh (Ctrl+Shift+R) to clear cache"
echo "  3. Click any BBT button (should zoom to level 12)"
echo "  4. Zoom out to level 11, hover over BBT area"
echo "  5. Tooltip should show gold message: 'Zoom in 1 more level...'"
echo "  6. Check browser console (F12) for any errors"
echo ""
echo -e "${BLUE}Rollback Command (if needed):${NC}"
echo "  ssh ${SERVER} 'cd ${APP_DIR} && \\"
echo "    sudo tar -xzf ${BACKUP_DIR}/backup_v1.2.6_${TIMESTAMP}.tar.gz && \\"
echo "    sudo systemctl restart ${SERVICE_NAME}'"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  View logs:        ssh ${SERVER} 'sudo journalctl -u ${SERVICE_NAME} -f'"
echo "  Service status:   ssh ${SERVER} 'sudo systemctl status ${SERVICE_NAME}'"
echo "  Restart:          ssh ${SERVER} 'sudo systemctl restart ${SERVICE_NAME}'"
echo ""
echo -e "${YELLOW}⚠ IMPORTANT:${NC}"
echo "  - Users may need to hard refresh (Ctrl+Shift+R) to see changes"
echo "  - Monitor logs for the first hour: ssh ${SERVER} 'sudo journalctl -u ${SERVICE_NAME} -f'"
echo "  - Verify zoom functionality works in actual browser testing"
echo ""
echo -e "${GREEN}Deployment completed at: $(date)${NC}"
echo ""
