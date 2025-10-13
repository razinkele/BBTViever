#!/bin/bash
# Deploy MARBEFES BBT Database v1.2.1 to laguna.ku.lt:5000
# Run this script from your local machine (not from Claude Code)

set -e

SERVER="razinka@laguna.ku.lt"
APP_DIR="/var/www/marbefes-bbt"

echo "========================================"
echo "MARBEFES BBT v1.2.1 Deployment"
echo "========================================"
echo ""

# Step 1: Test SSH connection
echo "[1/6] Testing SSH connection..."
ssh ${SERVER} "echo 'Connected to laguna.ku.lt'" || exit 1
echo "✓ SSH connection successful"
echo ""

# Step 2: Stop existing processes
echo "[2/6] Stopping existing application..."
ssh ${SERVER} "pkill -f 'gunicorn.*app:app' || true"
ssh ${SERVER} "pkill -f 'python.*app.py' || true"
sleep 2
echo "✓ Stopped"
echo ""

# Step 3: Deploy files
echo "[3/6] Deploying application files..."
rsync -avz --progress \
  --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.git' --exclude='cache' --exclude='logs' \
  --exclude='*.md' --exclude='test_*.html' --exclude='_archive' \
  --exclude='FactSheets' --exclude='.env' \
  ./ ${SERVER}:${APP_DIR}/
echo "✓ Files deployed"
echo ""

# Step 4: Install dependencies (pandas 2.0.3 critical!)
echo "[4/6] Installing dependencies..."
ssh ${SERVER} "cd ${APP_DIR} && \
  source venv/bin/activate && \
  pip install -q pandas==2.0.3 && \
  pip install -q -r requirements.txt"
echo "✓ Dependencies installed"
echo ""

# Step 5: Verify pandas version
echo "[5/6] Verifying pandas version..."
PANDAS_VERSION=$(ssh ${SERVER} "cd ${APP_DIR} && \
  source venv/bin/activate && \
  python -c 'import pandas; print(pandas.__version__)'")
echo "  pandas version: ${PANDAS_VERSION}"
if [ "${PANDAS_VERSION}" != "2.0.3" ]; then
    echo "⚠ WARNING: pandas version is ${PANDAS_VERSION}, expected 2.0.3"
    echo "  BBT display may not work correctly!"
fi
echo ""

# Step 6: Start application
echo "[6/6] Starting application on port 5000..."
ssh ${SERVER} "cd ${APP_DIR} && \
  nohup venv/bin/gunicorn -c gunicorn_config.py app:app \
  > logs/gunicorn.log 2>&1 &"
sleep 3
echo "✓ Application started"
echo ""

# Verification
echo "========================================"
echo "Verifying Deployment..."
echo "========================================"
echo ""

# Check process
WORKER_COUNT=$(ssh ${SERVER} "pgrep -f 'gunicorn.*app:app' | wc -l" || echo "0")
if [ "${WORKER_COUNT}" -gt "0" ]; then
    echo "✓ Gunicorn running with ${WORKER_COUNT} workers"
else
    echo "⚠ Gunicorn not detected (may still be starting)"
fi

# Test health endpoint
sleep 2
if curl -s -f http://laguna.ku.lt:5000/health > /dev/null 2>&1; then
    VERSION=$(curl -s http://laguna.ku.lt:5000/health | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    echo "✓ Health endpoint responding"
    echo "  Version: ${VERSION}"
else
    echo "⚠ Health endpoint not responding yet (may still be starting)"
fi

# Test BBT vector layers
echo ""
echo "Testing BBT vector layer loading..."
BBT_COUNT=$(curl -s http://laguna.ku.lt:5000/api/vector/layers | grep -o '"count":[0-9]*' | cut -d':' -f2 || echo "0")
if [ "${BBT_COUNT}" = "1" ]; then
    echo "✓ BBT vector layer loaded successfully"
else
    echo "⚠ BBT vector layer not loaded (count: ${BBT_COUNT})"
fi

echo ""
echo "========================================"
echo "Deployment Complete!"
echo "========================================"
echo ""
echo "Application URL: http://laguna.ku.lt:5000"
echo "Health Check:    http://laguna.ku.lt:5000/health"
echo "Vector Layers:   http://laguna.ku.lt:5000/api/vector/layers"
echo ""
echo "View Logs:"
echo "  ssh ${SERVER} 'tail -f ${APP_DIR}/logs/gunicorn.log'"
echo ""
echo "Check Processes:"
echo "  ssh ${SERVER} 'pgrep -a gunicorn'"
echo ""
echo "Stop Application:"
echo "  ssh ${SERVER} 'pkill -f gunicorn.*app:app'"
echo ""
