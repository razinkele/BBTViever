# MARBEFES BBT Database - Manual Deployment Instructions v1.2.7

**Version:** 1.2.7 (Zoom Threshold Alignment)
**Release Date:** 2025-10-15
**Deployment Target:** laguna.ku.lt/BBT (nginx subpath)
**Previous Version:** 1.2.6

---

## 🎯 What's New in v1.2.7

This release fixes critical edge cases in the zoom-aware popup system:

### Fixes Applied
- ✅ **Default BBT Zoom Level**: Changed from 11 → 12 (aligned with EUNIS threshold)
- ✅ **Status Display Threshold**: Changed from zoom 6 → 12 (matches data switching)
- ✅ **Zoom Level Validation**: Prevents users from setting detail zoom below 12
- ✅ **Enhanced Tooltip Guidance**: Shows current zoom and proximity to threshold

### Files Modified
- `static/js/bbt-tool.js` - BBT zoom defaults and validation
- `static/js/layer-manager.js` - Status display and tooltip enhancements

---

## 📋 Prerequisites

### Required Access
```bash
# Test SSH connection
ssh razinka@laguna.ku.lt "echo 'Connection successful'"

# If this fails, configure SSH keys:
ssh-copy-id razinka@laguna.ku.lt
```

### Required Information
- **Server**: laguna.ku.lt
- **User**: razinka
- **Application Directory**: /var/www/marbefes-bbt
- **Application URL**: http://laguna.ku.lt/BBT
- **Service Name**: marbefes-bbt
- **Current Version**: 1.2.6
- **Target Version**: 1.2.7

### Local Requirements
- SSH access to production server
- Git repository checked out at commit 787572d or later
- rsync installed (for file transfer)

---

## 🚀 Deployment Steps

### Step 1: Pre-Deployment Checklist

Before starting deployment, verify everything is ready:

```bash
# 1. Verify you're in the project directory
cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck

# 2. Verify changes are present locally
git status
# Expected output: modified: static/js/bbt-tool.js, layer-manager.js

# 3. Test SSH connection
ssh razinka@laguna.ku.lt "echo 'SSH working'"

# 4. Check current production version
ssh razinka@laguna.ku.lt "curl -s http://localhost/BBT/health | grep version"
# Expected: "version": "1.2.6"
```

**✓ Proceed only if all checks pass**

---

### Step 2: Create Backup on Production Server

**CRITICAL: Always backup before deployment**

```bash
# Connect to server
ssh razinka@laguna.ku.lt

# Create timestamped backup directory
BACKUP_DIR="/var/www/marbefes-bbt-backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
sudo mkdir -p ${BACKUP_DIR}

# Backup modified files
sudo tar -czf ${BACKUP_DIR}/backup_v1.2.6_${TIMESTAMP}.tar.gz \
    -C /var/www/marbefes-bbt \
    static/js/bbt-tool.js \
    static/js/layer-manager.js \
    app.py

# Verify backup created
ls -lh ${BACKUP_DIR}/backup_v1.2.6_${TIMESTAMP}.tar.gz

# Exit server
exit
```

**Expected Output:**
```
-rw-r--r-- 1 root root 45K Oct 15 14:30 backup_v1.2.6_20251015_143000.tar.gz
```

**✓ Backup created successfully**

---

### Step 3: Stop the Application

```bash
# Option A: Stop systemd service (recommended)
ssh razinka@laguna.ku.lt "sudo systemctl stop marbefes-bbt"

# Option B: Stop gunicorn processes directly (if no systemd service)
ssh razinka@laguna.ku.lt "pkill -f 'gunicorn.*app:app' || true"

# Verify service stopped
ssh razinka@laguna.ku.lt "sudo systemctl status marbefes-bbt"
# Expected: "Active: inactive (dead)"
```

**Why?** Stopping the service prevents file locks and ensures clean file replacement.

**⏱️ Expected downtime: 2-5 minutes**

---

### Step 4: Deploy Modified JavaScript Files

Transfer the updated JavaScript files from your local machine to the server:

```bash
# From your local project directory
cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck

# Deploy bbt-tool.js
rsync -avz --progress \
    static/js/bbt-tool.js \
    razinka@laguna.ku.lt:/var/www/marbefes-bbt/static/js/

# Deploy layer-manager.js
rsync -avz --progress \
    static/js/layer-manager.js \
    razinka@laguna.ku.lt:/var/www/marbefes-bbt/static/js/

# Verify files transferred (check file sizes and timestamps)
ssh razinka@laguna.ku.lt "ls -lh /var/www/marbefes-bbt/static/js/{bbt-tool.js,layer-manager.js}"
```

**Expected Output:**
```
-rw-r--r-- 1 razinka razinka 89K Oct 15 14:32 bbt-tool.js
-rw-r--r-- 1 razinka razinka 67K Oct 15 14:32 layer-manager.js
```

**✓ Files deployed successfully**

---

### Step 5: Update Version Information (Optional but Recommended)

Update the version file to reflect the new release:

```bash
# Option A: Update version locally, then deploy
# Edit src/emodnet_viewer/__version__.py locally:
# Change: __version__ = "1.2.7"
# Change: __version_date__ = "2025-10-15"
# Change: __version_name__ = "Zoom Threshold Alignment"

# Then deploy the updated file
rsync -avz \
    src/emodnet_viewer/__version__.py \
    razinka@laguna.ku.lt:/var/www/marbefes-bbt/src/emodnet_viewer/

# Option B: Update version directly on server
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt/src/emodnet_viewer && \
    sed -i 's/__version__ = \"1.2.6\"/__version__ = \"1.2.7\"/' __version__.py && \
    sed -i 's/__version_date__ = \"2025-10-14\"/__version_date__ = \"2025-10-15\"/' __version__.py && \
    sed -i 's/__version_name__ = \"Porsangerfjord.*\"/__version_name__ = \"Zoom Threshold Alignment\"/' __version__.py"
```

---

### Step 6: Verify File Integrity

Confirm the changes are present in production files:

```bash
# Check bbt-tool.js contains the fix (default zoom = 12)
ssh razinka@laguna.ku.lt \
    "grep -n 'window.bbtDetailZoomLevel = 12' /var/www/marbefes-bbt/static/js/bbt-tool.js"
# Expected: Line number + "window.bbtDetailZoomLevel = 12;"

# Check layer-manager.js contains the fix (status threshold = 12)
ssh razinka@laguna.ku.lt \
    "grep -n 'currentZoom < 12.*simplified' /var/www/marbefes-bbt/static/js/layer-manager.js"
# Expected: Line number + "const simplificationLevel = currentZoom < 12..."

# Check validation code exists in bbt-tool.js
ssh razinka@laguna.ku.lt \
    "grep -n 'EUNIS threshold' /var/www/marbefes-bbt/static/js/bbt-tool.js | head -2"
# Expected: Two lines with EUNIS threshold comments/code
```

**✓ All changes verified in production files**

---

### Step 7: Clear Browser Caches (Important!)

Since JavaScript files are cached with long expiry times, you need to force cache invalidation:

**Option A: Filename Hash (Recommended)**

```bash
# Add cache-busting query parameter to static file references
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
    sed -i 's|static/js/bbt-tool.js|static/js/bbt-tool.js?v=1.2.7|g' templates/index.html && \
    sed -i 's|static/js/layer-manager.js|static/js/layer-manager.js?v=1.2.7|g' templates/index.html"
```

**Option B: Nginx Cache Purge (If configured)**

```bash
# Clear nginx cache (if caching is enabled)
ssh razinka@laguna.ku.lt "sudo rm -rf /var/cache/nginx/*"
ssh razinka@laguna.ku.lt "sudo systemctl reload nginx"
```

**Option C: Manual Browser Cache Clear**

Instruct users to clear browser cache:
- Chrome: Ctrl+Shift+Delete → Clear cached images and files
- Firefox: Ctrl+Shift+Delete → Cache
- Or use Hard Refresh: Ctrl+Shift+R (Ctrl+F5)

---

### Step 8: Start the Application

```bash
# Start systemd service
ssh razinka@laguna.ku.lt "sudo systemctl start marbefes-bbt"

# Wait for service to initialize (3-5 seconds)
sleep 5

# Check service status
ssh razinka@laguna.ku.lt "sudo systemctl status marbefes-bbt"
# Expected: "Active: active (running)"

# Check worker processes
ssh razinka@laguna.ku.lt "pgrep -a gunicorn | grep marbefes"
# Expected: Multiple gunicorn worker processes
```

**Expected Output:**
```
● marbefes-bbt.service - MARBEFES BBT Database
   Loaded: loaded (/etc/systemd/system/marbefes-bbt.service; enabled)
   Active: active (running) since Mon 2025-10-15 14:35:00 UTC; 5s ago
```

**✓ Application started successfully**

---

### Step 9: Verify Deployment

Run comprehensive verification tests:

#### 9.1 Health Check

```bash
# Test health endpoint
curl -s http://laguna.ku.lt/BBT/health | jq '.'

# Expected output:
# {
#   "status": "healthy",
#   "version": "1.2.7",
#   "version_date": "2025-10-15"
# }
```

#### 9.2 Test Main Page

```bash
# Test homepage loads
curl -I http://laguna.ku.lt/BBT/
# Expected: HTTP/1.1 200 OK

# Check if JavaScript files are served
curl -I http://laguna.ku.lt/BBT/static/js/bbt-tool.js
curl -I http://laguna.ku.lt/BBT/static/js/layer-manager.js
# Expected: HTTP/1.1 200 OK for both
```

#### 9.3 Test API Endpoints

```bash
# Test vector layers API
curl -s http://laguna.ku.lt/BBT/api/vector/layers | jq '.count'
# Expected: Number of vector layers (e.g., 12)

# Test WMS layers API
curl -s http://laguna.ku.lt/BBT/api/layers | jq 'length'
# Expected: Number of WMS layers
```

#### 9.4 Check Application Logs

```bash
# View recent logs (last 50 lines)
ssh razinka@laguna.ku.lt "sudo journalctl -u marbefes-bbt -n 50 --no-pager"

# Look for any errors or warnings
ssh razinka@laguna.ku.lt "sudo journalctl -u marbefes-bbt --since '5 minutes ago' | grep -i error"
# Expected: No critical errors
```

#### 9.5 Browser Verification (Manual)

Open browser and test:

1. **Homepage**: http://laguna.ku.lt/BBT
   - ✅ Map loads without errors
   - ✅ No JavaScript errors in console (F12)
   - ✅ MARBEFES logo displays

2. **BBT Navigation**:
   - ✅ Click any BBT button (e.g., "Skagerrak")
   - ✅ Map zooms to level 12 (not 11)
   - ✅ Tooltip shows EUNIS habitat data immediately

3. **Zoom Level Testing**:
   - ✅ Zoom out to level 11
   - ✅ Hover over BBT area
   - ✅ Tooltip shows "Zoom in 1 more level..." message in gold color
   - ✅ Status shows "800m (simplified)"

4. **Zoom Level Validation**:
   - ✅ Open browser console (F12)
   - ✅ Try setting low zoom: `window.updateBBTZoomLevel(8)`
   - ✅ Console shows warning: "Zoom level 8 is below EUNIS threshold, enforcing minimum of 12"

**✓ All verification tests passed**

---

### Step 10: Monitor for Issues

Keep the application monitored for the first hour after deployment:

```bash
# Monitor logs in real-time
ssh razinka@laguna.ku.lt "sudo journalctl -u marbefes-bbt -f"

# In another terminal, monitor nginx access logs
ssh razinka@laguna.ku.lt "sudo tail -f /var/log/nginx/marbefes-bbt-access.log"

# In another terminal, monitor nginx error logs
ssh razinka@laguna.ku.lt "sudo tail -f /var/log/nginx/marbefes-bbt-error.log"
```

**Watch for:**
- ❌ 500 Internal Server Error
- ❌ JavaScript console errors from users
- ❌ High response times (>1000ms)
- ✅ 200 OK responses for all endpoints
- ✅ Fast response times (<200ms for most requests)

---

## 🔄 Rollback Procedure

If issues are discovered after deployment, rollback to v1.2.6:

### Quick Rollback

```bash
# 1. Stop service
ssh razinka@laguna.ku.lt "sudo systemctl stop marbefes-bbt"

# 2. Restore from backup (use the backup created in Step 2)
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
    sudo tar -xzf /var/www/marbefes-bbt-backups/backup_v1.2.6_TIMESTAMP.tar.gz"

# 3. Restart service
ssh razinka@laguna.ku.lt "sudo systemctl start marbefes-bbt"

# 4. Verify rollback
curl -s http://laguna.ku.lt/BBT/health | jq '.version'
# Expected: "1.2.6"
```

### Manual Rollback (If Backup Missing)

```bash
# Get previous version from git
git checkout HEAD~1 static/js/bbt-tool.js static/js/layer-manager.js

# Re-deploy old files
rsync -avz static/js/bbt-tool.js razinka@laguna.ku.lt:/var/www/marbefes-bbt/static/js/
rsync -avz static/js/layer-manager.js razinka@laguna.ku.lt:/var/www/marbefes-bbt/static/js/

# Restart service
ssh razinka@laguna.ku.lt "sudo systemctl restart marbefes-bbt"

# Don't forget to reset local git state
git checkout HEAD static/js/bbt-tool.js static/js/layer-manager.js
```

---

## 🐛 Troubleshooting

### Issue 1: Service Won't Start

**Symptoms:**
```
systemctl status marbefes-bbt
# Active: failed (Result: exit-code)
```

**Solution:**
```bash
# Check detailed error logs
ssh razinka@laguna.ku.lt "sudo journalctl -u marbefes-bbt -n 100 --no-pager"

# Common causes:
# 1. Port already in use
ssh razinka@laguna.ku.lt "sudo lsof -i :5000"
# Kill conflicting process if found

# 2. Python syntax error (unlikely for JS-only changes)
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
    source venv/bin/activate && python -m py_compile app.py"

# 3. Permission issues
ssh razinka@laguna.ku.lt "sudo chown -R razinka:razinka /var/www/marbefes-bbt"
```

---

### Issue 2: JavaScript Not Loading / Cached Version

**Symptoms:**
- Browser console shows old code
- BBT buttons still zoom to level 11
- Status still shows "full detail" at zoom 8

**Solution:**
```bash
# 1. Verify files on server have correct content
ssh razinka@laguna.ku.lt "grep 'window.bbtDetailZoomLevel = 12' \
    /var/www/marbefes-bbt/static/js/bbt-tool.js"

# 2. Check if nginx is caching
ssh razinka@laguna.ku.lt "curl -I http://localhost/BBT/static/js/bbt-tool.js | grep Cache"

# 3. Force cache invalidation by adding version query parameter
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
    sed -i 's|bbt-tool.js|bbt-tool.js?v=1.2.7|g' templates/index.html && \
    sudo systemctl reload nginx"

# 4. Hard refresh browser (Ctrl+Shift+R)
```

---

### Issue 3: 502 Bad Gateway

**Symptoms:**
```
curl http://laguna.ku.lt/BBT/
# <html><body><h1>502 Bad Gateway</h1></body></html>
```

**Solution:**
```bash
# 1. Check if gunicorn is running
ssh razinka@laguna.ku.lt "pgrep -a gunicorn"

# 2. Check nginx can reach gunicorn
ssh razinka@laguna.ku.lt "curl -I http://127.0.0.1:5000/BBT/"

# 3. Check nginx configuration
ssh razinka@laguna.ku.lt "sudo nginx -t"

# 4. View nginx error log
ssh razinka@laguna.ku.lt "sudo tail -50 /var/log/nginx/marbefes-bbt-error.log"

# 5. Restart both services
ssh razinka@laguna.ku.lt "sudo systemctl restart marbefes-bbt && \
    sudo systemctl restart nginx"
```

---

### Issue 4: Zoom Fixes Not Working

**Symptoms:**
- BBT buttons still zoom to level 11
- Validation not preventing zoom < 12
- Tooltips show old messages

**Solution:**
```bash
# 1. Verify exact code in production
ssh razinka@laguna.ku.lt "cat /var/www/marbefes-bbt/static/js/bbt-tool.js | \
    grep -A 2 'window.bbtDetailZoomLevel ='"
# Must show: window.bbtDetailZoomLevel = 12;

# 2. Check validation code exists
ssh razinka@laguna.ku.lt "cat /var/www/marbefes-bbt/static/js/bbt-tool.js | \
    grep -A 4 'EUNIS threshold'"
# Must show validation if-block

# 3. Clear ALL caches
ssh razinka@laguna.ku.lt "sudo systemctl restart marbefes-bbt nginx"

# 4. Browser: Hard refresh (Ctrl+Shift+R) or clear all caches

# 5. Verify in browser console
# Open F12 console and type:
window.bbtDetailZoomLevel
# Expected output: 12
```

---

## 📊 Post-Deployment Checklist

After 24 hours of deployment, verify stability:

```bash
# Check uptime
ssh razinka@laguna.ku.lt "systemctl status marbefes-bbt | grep Active"

# Check for errors in logs (last 24 hours)
ssh razinka@laguna.ku.lt "sudo journalctl -u marbefes-bbt --since '24 hours ago' | \
    grep -c ERROR"
# Expected: 0 or very low count

# Check memory usage
ssh razinka@laguna.ku.lt "ps aux | grep gunicorn | grep -v grep | \
    awk '{sum+=\$4} END {print \"Memory Usage: \" sum \"%\"}'"

# Check response times from nginx logs
ssh razinka@laguna.ku.lt "sudo awk '{print \$(NF-1)}' \
    /var/log/nginx/marbefes-bbt-access.log | \
    awk '{sum+=\$1; count++} END {print \"Avg Response Time: \" sum/count \"s\"}'"
# Expected: < 0.5s average
```

**✓ Deployment stable and performing well**

---

## 📝 Version Comparison

### Changes from v1.2.6 → v1.2.7

| Component | v1.2.6 (Old) | v1.2.7 (New) | Impact |
|-----------|-------------|-------------|--------|
| **Default BBT Zoom** | 11 | 12 | Users immediately see EUNIS data |
| **Status Display Threshold** | 6 | 12 | Status matches actual data state |
| **Zoom Validation** | None | Enforces min 12 | Prevents invalid configurations |
| **Tooltip Guidance** | Generic | Zoom-specific | Better user experience |
| **Backend** | Unchanged | Unchanged | No Python changes required |
| **Database** | Unchanged | Unchanged | No migrations required |

**Breaking Changes:** None (100% backward compatible)
**Database Changes:** None
**Configuration Changes:** None
**Restart Required:** Yes (service restart only)

---

## 🔗 Useful Commands Reference

### Service Management
```bash
# Status
ssh razinka@laguna.ku.lt "sudo systemctl status marbefes-bbt"

# Start
ssh razinka@laguna.ku.lt "sudo systemctl start marbefes-bbt"

# Stop
ssh razinka@laguna.ku.lt "sudo systemctl stop marbefes-bbt"

# Restart
ssh razinka@laguna.ku.lt "sudo systemctl restart marbefes-bbt"

# Reload nginx
ssh razinka@laguna.ku.lt "sudo systemctl reload nginx"
```

### Log Viewing
```bash
# Live logs
ssh razinka@laguna.ku.lt "sudo journalctl -u marbefes-bbt -f"

# Last 100 lines
ssh razinka@laguna.ku.lt "sudo journalctl -u marbefes-bbt -n 100 --no-pager"

# Errors only (last hour)
ssh razinka@laguna.ku.lt "sudo journalctl -u marbefes-bbt --since '1 hour ago' | grep ERROR"

# Nginx access log
ssh razinka@laguna.ku.lt "sudo tail -f /var/log/nginx/marbefes-bbt-access.log"

# Nginx error log
ssh razinka@laguna.ku.lt "sudo tail -f /var/log/nginx/marbefes-bbt-error.log"
```

### File Verification
```bash
# Check file sizes
ssh razinka@laguna.ku.lt "ls -lh /var/www/marbefes-bbt/static/js/*.js"

# Check file timestamps
ssh razinka@laguna.ku.lt "stat /var/www/marbefes-bbt/static/js/bbt-tool.js | grep Modify"

# Check file content
ssh razinka@laguna.ku.lt "head -20 /var/www/marbefes-bbt/static/js/bbt-tool.js"
```

### Testing Endpoints
```bash
# Health check
curl -s http://laguna.ku.lt/BBT/health | jq '.'

# API endpoints
curl -s http://laguna.ku.lt/BBT/api/layers | jq 'length'
curl -s http://laguna.ku.lt/BBT/api/vector/layers | jq '.count'

# Test with headers
curl -I http://laguna.ku.lt/BBT/

# Test response time
time curl -s http://laguna.ku.lt/BBT/ > /dev/null
```

---

## 📞 Support & Documentation

### Related Documentation
- **Main Deployment Guide**: `DEPLOYMENT_GUIDE.md`
- **Subpath Configuration**: `deploy_subpath.sh`
- **Version History**: `src/emodnet_viewer/__version__.py`
- **Git Log**: `git log --oneline`

### Getting Help
```bash
# Check current git state
git status
git log --oneline -10

# View deployment script documentation
cat DEPLOYMENT_GUIDE.md

# Check server status
ssh razinka@laguna.ku.lt "systemctl status marbefes-bbt"
```

---

## ✅ Deployment Summary

After completing all steps, you should have:

- ✅ v1.2.6 backed up to `/var/www/marbefes-bbt-backups/`
- ✅ Updated JavaScript files deployed to production
- ✅ Version updated to 1.2.7 (optional)
- ✅ Service restarted and running
- ✅ All verification tests passing
- ✅ No errors in logs
- ✅ Browser cache cleared
- ✅ Zoom threshold fixes working correctly

**Total Deployment Time:** 10-15 minutes
**Downtime:** 2-5 minutes
**Risk Level:** Low (JavaScript-only changes, no backend modifications)

---

**Deployed By:** _____________
**Date:** _____________
**Deployment Time:** _____________ UTC
**Issues Encountered:** _____________
**Rollback Performed:** ☐ Yes ☐ No

---

**Last Updated:** 2025-10-15
**Document Version:** 1.0
**Author:** Claude Code (Anthropic)
