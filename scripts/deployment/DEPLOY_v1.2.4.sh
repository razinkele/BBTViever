#!/bin/bash
# Deploy MARBEFES BBT Database v1.2.4 to laguna.ku.lt:5000
# Run this script from your local machine with SSH access configured
#
# New in v1.2.4:
# - MARBEFES datasets integration with VLIZ repository links
# - Dataset panels for all 11 BBT regions
# - "No MARBEFES data produced" message for incomplete coverage

set -e

SERVER="razinka@laguna.ku.lt"
APP_DIR="/var/www/marbefes-bbt"

echo "========================================"
echo "MARBEFES BBT v1.2.4 Deployment"
echo "Dataset Integration Release"
echo "========================================"
echo ""

# Step 1: Test SSH connection
echo "[1/7] Testing SSH connection..."
ssh ${SERVER} "echo 'Connected to laguna.ku.lt'" || {
    echo "❌ SSH connection failed!"
    echo "Please ensure:"
    echo "  1. SSH keys are configured: ssh-copy-id ${SERVER}"
    echo "  2. You can connect manually: ssh ${SERVER}"
    exit 1
}
echo "✓ SSH connection successful"
echo ""

# Step 2: Stop existing processes
echo "[2/7] Stopping existing application..."
ssh ${SERVER} "pkill -f 'gunicorn.*app:app' || true"
ssh ${SERVER} "pkill -f 'python.*app.py' || true"
sleep 2
echo "✓ Stopped"
echo ""

# Step 3: Backup current deployment
echo "[3/7] Creating backup..."
BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S)"
ssh ${SERVER} "cd ${APP_DIR}/.. && \
  tar -czf ${BACKUP_NAME}.tar.gz marbefes-bbt/static marbefes-bbt/templates marbefes-bbt/app.py || true"
echo "✓ Backup created: ${BACKUP_NAME}.tar.gz"
echo ""

# Step 4: Deploy files
echo "[4/7] Deploying application files..."
echo "  Syncing Python backend..."
rsync -avz --progress \
  --include='*.py' \
  --include='requirements*.txt' \
  --include='config/' \
  --include='src/' \
  --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.git' --exclude='cache' --exclude='logs' \
  --exclude='*.md' --exclude='test_*.html' --exclude='_archive' \
  --exclude='FactSheets' --exclude='.env' \
  ./ ${SERVER}:${APP_DIR}/

echo "  Syncing templates..."
rsync -avz --progress \
  templates/ ${SERVER}:${APP_DIR}/templates/

echo "  Syncing JavaScript modules..."
rsync -avz --progress \
  static/js/ ${SERVER}:${APP_DIR}/static/js/

echo "  Syncing data files..."
rsync -avz --progress \
  data/ ${SERVER}:${APP_DIR}/data/

echo "✓ Files deployed"
echo ""

# Step 5: Verify new files
echo "[5/7] Verifying new files..."
NEW_FILES=$(ssh ${SERVER} "ls -la ${APP_DIR}/static/js/data/marbefes-datasets.js 2>/dev/null || echo 'NOT FOUND'")
if [[ "${NEW_FILES}" == *"NOT FOUND"* ]]; then
    echo "⚠ WARNING: marbefes-datasets.js not found!"
    echo "  Deployment may be incomplete"
else
    echo "✓ New dataset module deployed successfully"
fi
echo ""

# Step 6: Install dependencies
echo "[6/7] Installing dependencies..."
ssh ${SERVER} "cd ${APP_DIR} && \
  source venv/bin/activate && \
  pip install -q pandas==2.0.3 && \
  pip install -q -r requirements.txt"

# Verify pandas version
PANDAS_VERSION=$(ssh ${SERVER} "cd ${APP_DIR} && \
  source venv/bin/activate && \
  python -c 'import pandas; print(pandas.__version__)'")
echo "  pandas version: ${PANDAS_VERSION}"
if [ "${PANDAS_VERSION}" != "2.0.3" ]; then
    echo "⚠ WARNING: pandas version is ${PANDAS_VERSION}, expected 2.0.3"
    echo "  BBT display may not work correctly!"
fi
echo "✓ Dependencies installed"
echo ""

# Step 7: Start application
echo "[7/7] Starting application on port 5000..."
ssh ${SERVER} "cd ${APP_DIR} && \
  mkdir -p logs && \
  nohup venv/bin/gunicorn -c gunicorn_config.py app:app \
  > logs/gunicorn.log 2>&1 &"
sleep 4
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
    echo "⚠ Gunicorn not detected - checking logs..."
    ssh ${SERVER} "tail -20 ${APP_DIR}/logs/gunicorn.log"
    exit 1
fi

# Test health endpoint
sleep 2
echo ""
echo "Testing endpoints..."
if curl -s -f http://laguna.ku.lt:5000/health > /dev/null 2>&1; then
    VERSION=$(curl -s http://laguna.ku.lt:5000/health | grep -o '"version":"[^"]*"' | cut -d'"' -f4)
    VERSION_DATE=$(curl -s http://laguna.ku.lt:5000/health | grep -o '"version_date":"[^"]*"' | cut -d'"' -f4)
    echo "✓ Health endpoint responding"
    echo "  Version: ${VERSION} (${VERSION_DATE})"
else
    echo "⚠ Health endpoint not responding"
fi

# Test BBT vector layers
BBT_COUNT=$(curl -s http://laguna.ku.lt:5000/api/vector/layers | grep -o '"count":[0-9]*' | cut -d':' -f2 || echo "0")
if [ "${BBT_COUNT}" = "1" ]; then
    echo "✓ BBT vector layer loaded (11 features expected)"
else
    echo "⚠ BBT vector layer issue (count: ${BBT_COUNT})"
fi

# Test main page
if curl -s -f http://laguna.ku.lt:5000/ > /dev/null 2>&1; then
    echo "✓ Main page accessible"
else
    echo "⚠ Main page not accessible"
fi

echo ""
echo "========================================"
echo "Deployment Complete! v1.2.4"
echo "========================================"
echo ""
echo "🎉 New Features:"
echo "  • MARBEFES dataset integration (24 datasets)"
echo "  • Dataset panels linked to VLIZ repository"
echo "  • Category-organized display (Biological/Environmental/Socio-Economic)"
echo "  • Clickable metadata links for all datasets"
echo ""
echo "📍 Application URL: http://laguna.ku.lt:5000"
echo "🏥 Health Check:    http://laguna.ku.lt:5000/health"
echo "📊 Vector Layers:   http://laguna.ku.lt:5000/api/vector/layers"
echo ""
echo "📖 Usage:"
echo "  1. Click any 📊 button next to BBT region names"
echo "  2. View MARBEFES datasets with VLIZ links"
echo "  3. Regions without data show 'No MARBEFES data produced'"
echo ""
echo "🔧 Useful Commands:"
echo ""
echo "View Logs:"
echo "  ssh ${SERVER} 'tail -f ${APP_DIR}/logs/gunicorn.log'"
echo ""
echo "Check Processes:"
echo "  ssh ${SERVER} 'pgrep -a gunicorn'"
echo ""
echo "Restart Application:"
echo "  ssh ${SERVER} 'pkill -f gunicorn.*app:app && cd ${APP_DIR} && nohup venv/bin/gunicorn -c gunicorn_config.py app:app > logs/gunicorn.log 2>&1 &'"
echo ""
echo "Stop Application:"
echo "  ssh ${SERVER} 'pkill -f gunicorn.*app:app'"
echo ""
echo "Restore Backup:"
echo "  ssh ${SERVER} 'cd ${APP_DIR}/.. && tar -xzf ${BACKUP_NAME}.tar.gz'"
echo ""
