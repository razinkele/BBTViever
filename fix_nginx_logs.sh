#!/bin/bash
################################################################################
# Quick Fix for Nginx Log Directory Issue
#
# This script creates the nginx log directory that was missing
################################################################################

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Fixing Nginx Log Directory                              ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ Please run as root or with sudo${NC}"
    exit 1
fi

echo -e "${BLUE}[1/4]${NC} Creating /var/log/nginx directory..."
mkdir -p /var/log/nginx

echo -e "${BLUE}[2/4]${NC} Setting ownership to www-data..."
chown www-data:www-data /var/log/nginx 2>/dev/null || chown nginx:nginx /var/log/nginx 2>/dev/null || true

echo -e "${BLUE}[3/4]${NC} Setting permissions..."
chmod 755 /var/log/nginx

echo -e "${BLUE}[4/4]${NC} Creating initial log files..."
touch /var/log/nginx/error.log
touch /var/log/nginx/access.log
chown www-data:www-data /var/log/nginx/*.log 2>/dev/null || chown nginx:nginx /var/log/nginx/*.log 2>/dev/null || true
chmod 644 /var/log/nginx/*.log

echo ""
echo -e "${GREEN}✓ Nginx log directory created successfully!${NC}"
echo ""

echo -e "${BLUE}Verifying:${NC}"
ls -ld /var/log/nginx
ls -l /var/log/nginx/

echo ""
echo -e "${BLUE}Testing nginx configuration:${NC}"
if nginx -t; then
    echo ""
    echo -e "${GREEN}✓ Nginx configuration is valid!${NC}"
    echo ""
    echo -e "${BLUE}You can now:${NC}"
    echo -e "  1. Continue with deployment: ${GREEN}sudo ./deploy_subpath.sh${NC}"
    echo -e "  2. Or reload nginx: ${GREEN}sudo systemctl reload nginx${NC}"
else
    echo ""
    echo -e "${RED}✗ Nginx configuration still has issues${NC}"
    echo -e "${BLUE}Check configuration with: ${NC}sudo nginx -t"
    exit 1
fi
