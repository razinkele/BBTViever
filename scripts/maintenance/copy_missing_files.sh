#!/bin/bash
# Copy missing files from local to production
set -e

echo "========================================="
echo "Copying Missing Files to Production"
echo "========================================="
echo

echo "[1/3] Copying __version__.py..."
sudo cp /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/src/emodnet_viewer/__version__.py \
    /var/www/marbefes-bbt/src/emodnet_viewer/
echo "✓ File copied"
echo

echo "[2/3] Fixing permissions..."
sudo chmod 644 /var/www/marbefes-bbt/src/emodnet_viewer/__version__.py
sudo chown www-data:www-data /var/www/marbefes-bbt/src/emodnet_viewer/__version__.py
echo "✓ Permissions fixed"
echo

echo "[3/3] Checking for __init__.py files..."
# Make sure all Python packages have __init__.py
for dir in /var/www/marbefes-bbt/src/emodnet_viewer \
           /var/www/marbefes-bbt/src/emodnet_viewer/utils \
           /var/www/marbefes-bbt/src/emodnet_viewer/api; do
    if [ -d "$dir" ] && [ ! -f "$dir/__init__.py" ]; then
        echo "  Creating $dir/__init__.py"
        sudo touch "$dir/__init__.py"
        sudo chmod 644 "$dir/__init__.py"
        sudo chown www-data:www-data "$dir/__init__.py"
    fi
done
echo "✓ __init__.py files verified"
echo

echo "========================================="
echo "Testing App Import..."
echo "========================================="
cd /var/www/marbefes-bbt
if source venv/bin/activate && python -c "import app; print('SUCCESS: App imports!')" 2>&1 | grep -q "SUCCESS"; then
    echo "✓ App imports successfully!"
    echo
    echo "Now restart the service:"
    echo "  sudo systemctl restart marbefes-bbt"
    echo "  sudo systemctl status marbefes-bbt"
else
    echo "✗ App still has import errors"
    echo "Check with: source venv/bin/activate && python -c 'import app'"
fi
echo
