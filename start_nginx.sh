#!/bin/bash
################################################################################
# Start Nginx
################################################################################

set -e

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Starting Nginx                                          ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}✗ Please run as root or with sudo${NC}"
    exit 1
fi

echo -e "${BLUE}[1/4]${NC} Testing nginx configuration..."
if nginx -t 2>&1 | grep -q "syntax is ok"; then
    echo -e "${GREEN}✓${NC} Configuration is valid"
else
    echo -e "${RED}✗${NC} Configuration has errors:"
    nginx -t
    exit 1
fi

echo ""
echo -e "${BLUE}[2/4]${NC} Starting nginx..."
if systemctl start nginx; then
    echo -e "${GREEN}✓${NC} Nginx started"
else
    echo -e "${RED}✗${NC} Failed to start nginx"
    echo -e "${YELLOW}Checking status:${NC}"
    systemctl status nginx --no-pager -l
    exit 1
fi

sleep 2

echo ""
echo -e "${BLUE}[3/4]${NC} Verifying nginx is running..."
if systemctl is-active nginx > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Nginx is active"
    systemctl status nginx --no-pager -l | head -10
else
    echo -e "${RED}✗${NC} Nginx is not active"
    systemctl status nginx --no-pager -l
    exit 1
fi

echo ""
echo -e "${BLUE}[4/4]${NC} Testing application access..."

# Test localhost
if curl -sf -I http://localhost/BBTS > /dev/null 2>&1; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/BBTS)
    echo -e "${GREEN}✓${NC} http://localhost/BBTS - HTTP $HTTP_CODE"
else
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/BBTS 2>&1)
    echo -e "${YELLOW}⚠${NC} http://localhost/BBTS - HTTP $HTTP_CODE (may need time to warm up)"
fi

# Test domain if accessible
DOMAIN="laguna.ku.lt"
if ping -c 1 -W 1 $DOMAIN > /dev/null 2>&1; then
    if curl -sf -I http://$DOMAIN/BBTS > /dev/null 2>&1; then
        HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN/BBTS)
        echo -e "${GREEN}✓${NC} http://$DOMAIN/BBTS - HTTP $HTTP_CODE"
    else
        echo -e "${YELLOW}⚠${NC} http://$DOMAIN/BBTS - Not accessible yet"
    fi
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Nginx Started Successfully!                              ║${NC}"
echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

echo -e "${BLUE}Access your application:${NC}"
echo -e "  ${YELLOW}http://localhost/BBTS${NC}"
echo -e "  ${YELLOW}http://laguna.ku.lt/BBTS${NC}"
echo -e "  ${YELLOW}http://$(hostname -I | awk '{print $1}')/BBTS${NC}"

echo ""
echo -e "${BLUE}Monitor logs:${NC}"
echo -e "  sudo tail -f /var/log/nginx/marbefes-bbt-access.log"
echo -e "  sudo tail -f /var/log/nginx/marbefes-bbt-error.log"
echo ""
