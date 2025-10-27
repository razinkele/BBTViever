#!/bin/bash
# Install missing Python packages in production venv
# Run this with: bash install_missing_packages.sh

set -e

echo "========================================="
echo "Installing Missing Flask Extensions"
echo "========================================="
echo

cd /var/www/marbefes-bbt

# Temporarily fix permissions
echo "[1/3] Fixing venv permissions..."
sudo chown -R razinka:www-data venv/
echo "✓ Permissions fixed"
echo

# Install packages
echo "[2/3] Installing Flask-Limiter and Flask-Compress..."
source venv/bin/activate
pip install Flask-Limiter==3.8.0 Flask-Compress==1.18
deactivate
echo "✓ Packages installed"
echo

# Restore ownership to www-data for production
echo "[3/3] Restoring production ownership..."
sudo chown -R www-data:www-data venv/
echo "✓ Ownership restored"
echo

echo "========================================="
echo "Installation Complete!"
echo "========================================="
echo
echo "Now restart the service:"
echo "  sudo systemctl restart marbefes-bbt"
echo
