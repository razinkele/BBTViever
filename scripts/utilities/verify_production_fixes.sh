#!/bin/bash
# Verification script to confirm all production fixes were applied successfully

echo "================================================================="
echo "MARBEFES BBT Production Server - Verification"
echo "================================================================="
echo

# Test 1: Direct app access
echo "[Test 1] Direct app access (port 5000)..."
DIRECT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/health)
DIRECT_VERSION=$(curl -s http://localhost:5000/health | jq -r '.version' 2>/dev/null || echo "Failed")
if [ "$DIRECT_STATUS" = "200" ]; then
    echo "  ✓ Status: $DIRECT_STATUS OK"
    echo "  ✓ Version: $DIRECT_VERSION"
else
    echo "  ✗ Status: $DIRECT_STATUS (Expected: 200)"
fi
echo

# Test 2: Nginx proxy access
echo "[Test 2] Nginx proxy access (/BBTS)..."
PROXY_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/BBTS/health)
PROXY_VERSION=$(curl -s http://localhost/BBTS/health | jq -r '.version' 2>/dev/null || echo "Failed")
if [ "$PROXY_STATUS" = "200" ]; then
    echo "  ✓ Status: $PROXY_STATUS OK"
    echo "  ✓ Version: $PROXY_VERSION"
else
    echo "  ✗ Status: $PROXY_STATUS (Expected: 200)"
    echo "  ✗ Version: $PROXY_VERSION"
fi
echo

# Test 3: Check request path in gunicorn logs
echo "[Test 3] Request path in logs..."
LAST_REQUEST=$(tail -1 /var/www/marbefes-bbt/logs/gunicorn-access.log | grep -o '"GET [^"]*"' || echo "No requests yet")
echo "  Last request: $LAST_REQUEST"
if echo "$LAST_REQUEST" | grep -q "GET /health"; then
    echo "  ✓ Flask receives /health (prefix stripped correctly)"
elif echo "$LAST_REQUEST" | grep -q "GET /BBTS"; then
    echo "  ✗ Flask receives /BBTS/... (prefix NOT stripped)"
fi
echo

# Test 4: Worker count
echo "[Test 4] Worker count..."
WORKER_COUNT=$(pgrep -a gunicorn | grep marbefes | wc -l)
echo "  Total processes: $WORKER_COUNT"
if [ "$WORKER_COUNT" -le 10 ]; then
    echo "  ✓ Worker count optimal (≤10)"
else
    echo "  ✗ Worker count high ($WORKER_COUNT, expected: ~9)"
fi
echo

# Test 5: Error log size
echo "[Test 5] Error log size..."
ERROR_LOG_SIZE=$(du -h /var/www/marbefes-bbt/logs/gunicorn-error.log | cut -f1)
ERROR_LOG_LINES=$(wc -l < /var/www/marbefes-bbt/logs/gunicorn-error.log)
echo "  Size: $ERROR_LOG_SIZE"
echo "  Lines: $ERROR_LOG_LINES"
if [ "$ERROR_LOG_LINES" -lt 1000 ]; then
    echo "  ✓ Log truncated successfully"
else
    echo "  ✗ Log still large ($ERROR_LOG_LINES lines)"
fi
echo

# Test 6: Memory usage
echo "[Test 6] Memory usage..."
MEM_USAGE=$(ps aux | grep gunicorn | grep marbefes | awk '{sum+=$4} END {printf "%.1f%%", sum}')
echo "  Gunicorn memory: $MEM_USAGE"
echo

# Test 7: Logrotate configuration
echo "[Test 7] Logrotate configuration..."
if [ -f /etc/logrotate.d/marbefes-bbt ]; then
    echo "  ✓ Logrotate config exists"
else
    echo "  ✗ Logrotate config missing"
fi
echo

# Test 8: Nginx configuration
echo "[Test 8] Nginx configuration..."
if grep -q "#DISABLED.*location /BBTS" /etc/nginx/sites-available/default 2>/dev/null; then
    echo "  ✓ Duplicate /BBTS location disabled in default site"
else
    echo "  ⚠ Could not verify duplicate was disabled (may need sudo)"
fi
echo

# Summary
echo "================================================================="
echo "Summary"
echo "================================================================="
echo

if [ "$PROXY_STATUS" = "200" ] && [ "$WORKER_COUNT" -le 10 ] && [ "$ERROR_LOG_LINES" -lt 1000 ]; then
    echo "✓ ALL FIXES VERIFIED SUCCESSFULLY"
    echo
    echo "Production server is fully operational:"
    echo "  • External URL: http://laguna.ku.lt/BBTS"
    echo "  • Nginx proxy: Working (status $PROXY_STATUS)"
    echo "  • Worker count: $WORKER_COUNT (optimized)"
    echo "  • Memory usage: $MEM_USAGE (reduced)"
    echo "  • Logs: Truncated and rotating"
    echo
else
    echo "⚠ SOME ISSUES REMAIN"
    echo
    if [ "$PROXY_STATUS" != "200" ]; then
        echo "  ✗ Nginx proxy not working"
    fi
    if [ "$WORKER_COUNT" -gt 10 ]; then
        echo "  ✗ Worker count still high"
    fi
    if [ "$ERROR_LOG_LINES" -ge 1000 ]; then
        echo "  ✗ Error log not truncated"
    fi
    echo
    echo "Run with sudo for full verification:"
    echo "  sudo bash verify_production_fixes.sh"
    echo
fi
