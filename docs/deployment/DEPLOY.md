# MARBEFES BBT Database - Deployment Guide

**Production URL**: http://laguna.ku.lt/BBTS/
**Status**: ✅ Running in Production
**Deployment Date**: October 2025

---

## Quick Start - Deploy Updates to Production

### Option 1: Full Production Deployment (Initial Setup)

For a complete fresh deployment from scratch:

```bash
cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck
sudo ./deploy_production.sh
```

This will:
- Set up /var/www/marbefes-bbt/
- Install Python dependencies
- Configure Gunicorn
- Set up systemd service
- Configure nginx with /BBTS subpath
- Enable and start all services

### Option 2: Quick Update Deployment (Most Common)

For updating code on an existing deployment:

```bash
cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck
./deploy.sh
```

This will:
- Copy updated files to production
- Restart the service
- Verify deployment

---

## What Gets Deployed

This deployment includes **4 major improvements**:

### 1. ✅ Logo Subpath Fix
- Logo will display correctly in the header
- Fixed URL: `/BBTS/logo/marbefes_02.png`

### 2. ✅ API Subpath Fix
- BBT navigation will work
- Vector layers will load
- Fixed URL: `/BBTS/api/vector/layer/...`

### 3. ✅ WMS Click Query (NEW!)
- Click on EMODnet layers to query feature information
- Interactive popups with habitat data
- Works on all WMS and HELCOM layers

### 4. ✅ EUNIS 2019 Only (NEW!)
- Uses full EUNIS 2019 classification everywhere
- No biological zone layers
- No zoom-based layer switching
- Consistent detailed habitat codes

---

## After Deployment

### Browser Verification

1. **Open:** http://laguna.ku.lt/BBTS

2. **Check Logo:**
   - ✓ MARBEFES logo visible in header

3. **Check Console:**
   - ✓ Press F12 to open DevTools
   - ✓ No 404 errors

4. **Test BBT Navigation:**
   - ✓ BBT dropdown works
   - ✓ Can select and view features

5. **Test WMS Click Query (NEW):**
   - ✓ Zoom to BBT area (zoom >= 8)
   - ✓ Wait for EUNIS 2019 layer to load
   - ✓ Click on colored habitat area
   - ✓ Popup shows habitat information with EUNIS codes

6. **Verify EUNIS Layer (NEW):**
   - ✓ Layer dropdown shows "EUNIS 2019"
   - ✓ No "Biological Zones" references
   - ✓ Click query shows EUNIS codes (e.g., "A5.13")

### Command Line Verification

```bash
# Test logo
curl -I http://laguna.ku.lt/BBTS/logo/marbefes_02.png
# Expected: HTTP/1.1 200 OK

# Test API
curl -I "http://laguna.ku.lt/BBTS/api/vector/layer/Bbts%20-%20Broad%20Belt%20Transects"
# Expected: HTTP/1.1 200 OK

# Test main page
curl -I http://laguna.ku.lt/BBTS
# Expected: HTTP/1.1 200 OK
```

---

## Troubleshooting

### Script Won't Run

**Error:** `Permission denied`
```bash
chmod +x deploy.sh
./deploy.sh
```

### SSH Password Prompts

If you get tired of entering password 3 times, set up SSH keys:

```bash
# Generate key (if you don't have one)
ssh-keygen -t ed25519

# Copy to server
ssh-copy-id razinka@laguna.ku.lt

# Now deploy.sh won't ask for password
```

### Service Not Running

```bash
# Check service status
ssh razinka@laguna.ku.lt "sudo systemctl status marbefes-bbt"

# Check logs
ssh razinka@laguna.ku.lt "tail -50 /var/www/marbefes-bbt/logs/emodnet_viewer.log"

# View journal
ssh razinka@laguna.ku.lt "sudo journalctl -u marbefes-bbt -n 50"
```

### Still Getting Errors

Check browser console for specific errors:
1. Open http://laguna.ku.lt/BBTS
2. Press F12
3. Go to Console tab
4. Look for red error messages

---

## Files Being Deployed

### app.py
**Changes:**
- Line 335: Added `APPLICATION_ROOT` to template context

### templates/index.html
**Changes:**
- Line 386: Logo uses `{{ APPLICATION_ROOT }}`
- Line 540: Added `API_BASE_URL` constant
- Lines 593, 1319, 1454, 2143: API calls use `API_BASE_URL`
- Line 1082: Enhanced `setupGetFeatureInfo()` for multi-WMS support
- Line 1718: Added click query to `selectWMSLayer()`
- Line 1743: Added click query to `selectWMSLayerAsOverlay()`
- Line 1779: Added click query to `selectHELCOMLayerAsOverlay()`
- Line 1928: Changed fallback to EUNIS 2019
- Line 2076: Simplified to always use EUNIS 2019

---

## Manual Deployment (Alternative)

If the script doesn't work, deploy manually:

```bash
cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck

# Copy files (enter password for each)
scp app.py razinka@laguna.ku.lt:/var/www/marbefes-bbt/
scp templates/index.html razinka@laguna.ku.lt:/var/www/marbefes-bbt/templates/

# Restart service (enter password)
ssh razinka@laguna.ku.lt "sudo systemctl restart marbefes-bbt"

# Check status
ssh razinka@laguna.ku.lt "sudo systemctl status marbefes-bbt"
```

---

## Documentation

**Complete Documentation Available:**

| File | Description |
|------|-------------|
| **DEPLOY.md** | This file - Quick deployment guide |
| DEPLOY_INSTRUCTIONS.txt | Step-by-step manual instructions |
| WMS_CLICK_QUERY.md | WMS click query technical docs |
| EUNIS_LAYER_ONLY.md | EUNIS 2019 layer configuration |
| LOGO_FIX.md | Subpath URL fixes technical docs |
| DEPLOYMENT_READY.md | Comprehensive deployment guide |

---

## Summary

**Before deployment:**
```
❌ Logo not loading (404)
❌ API calls failing (404)
❌ No click query on WMS layers
❌ Mixed biological zones and EUNIS
```

**After deployment:**
```
✅ Logo displays correctly
✅ API calls work
✅ Click on WMS layers shows data
✅ EUNIS 2019 full classification only
```

---

## Ready to Deploy?

Run the deployment script:

```bash
cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck
./deploy.sh
```

Enter your password when prompted (3 times), then verify in browser!

---

## Architecture Overview

```
Internet → nginx (laguna.ku.lt/BBTS) → Gunicorn (127.0.0.1:5000) → Flask App
                ↓
           URL Rewriting: /BBTS/* → /*
           Static Files: /BBTS/logo/, /BBTS/static/
```

### Key Components:

1. **Nginx**: Reverse proxy handling external requests
   - Config: `/etc/nginx/sites-available/marbefes-bbt`
   - Rewrites `/BBTS/*` URLs to Flask's `/`
   - Serves static files directly

2. **Gunicorn**: WSGI server
   - Config: `/var/www/marbefes-bbt/gunicorn_config.py`
   - Auto-scaled workers (CPU cores × 2 + 1)
   - 120s timeout for WMS requests

3. **Systemd**: Service management
   - Service: `marbefes-bbt.service`
   - Auto-start on boot
   - Auto-restart on failure

4. **Flask Application**:
   - Location: `/var/www/marbefes-bbt/app.py`
   - Vector data: `/var/www/marbefes-bbt/data/vector/`
   - Logs: `/var/www/marbefes-bbt/logs/`

---

## Useful Commands

### Service Management

```bash
# Check status
sudo systemctl status marbefes-bbt

# Restart service
sudo systemctl restart marbefes-bbt

# View real-time logs
sudo journalctl -u marbefes-bbt -f

# Stop service
sudo systemctl stop marbefes-bbt

# Start service
sudo systemctl start marbefes-bbt
```

### Log Files

```bash
# Application logs
tail -f /var/www/marbefes-bbt/logs/emodnet_viewer.log

# Gunicorn access logs
tail -f /var/www/marbefes-bbt/logs/gunicorn-access.log

# Gunicorn error logs
tail -f /var/www/marbefes-bbt/logs/gunicorn-error.log

# Nginx access logs
sudo tail -f /var/log/nginx/marbefes-bbt-access.log

# Nginx error logs
sudo tail -f /var/log/nginx/marbefes-bbt-error.log
```

### Testing Deployment

```bash
# Test main page
curl -I http://laguna.ku.lt/BBTS/

# Test vector API
curl http://laguna.ku.lt/BBTS/api/vector/layers | python3 -m json.tool

# Test WMS layers
curl http://laguna.ku.lt/BBTS/api/layers | python3 -m json.tool | head -20

# Test health endpoint
curl http://laguna.ku.lt/BBTS/health
```

---

**Last Updated:** 2025-10-05
**Version:** 1.3
**Status:** ✅ Running in Production at http://laguna.ku.lt/BBTS/
