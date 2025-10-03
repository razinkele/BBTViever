#!/bin/bash
#
# Simple Nginx Fix for Encoded Slashes
#

set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "======================================================================"
echo "           Quick Fix: Nginx Encoded Slashes"
echo "======================================================================"

# Step 1: Add merge_slashes off to nginx.conf
if ! grep -q "merge_slashes off" /etc/nginx/nginx.conf; then
    echo -e "${BLUE}→${NC} Adding 'merge_slashes off' to nginx.conf..."
    sed -i '/http {/a \    merge_slashes off;' /etc/nginx/nginx.conf
    echo -e "${GREEN}✓${NC} Added merge_slashes directive"
else
    echo -e "${GREEN}✓${NC} merge_slashes already configured"
fi

# Step 2: Test and reload nginx
echo ""
echo -e "${BLUE}→${NC} Testing nginx configuration..."
nginx -t

echo ""
echo -e "${BLUE}→${NC} Reloading nginx..."
systemctl reload nginx

echo ""
echo -e "${GREEN}✅ Nginx configured to allow encoded slashes${NC}"
echo ""
echo "Now run the backend fix:"
echo "  sudo /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/apply_vector_fix.sh"
echo ""
