# Production Server Issues and Fixes

**Date**: 2025-10-16
**Server**: laguna.ku.lt
**Application**: MARBEFES BBT Database (v1.2.7)

---

## Issues Identified

### 1. ❌ Nginx Proxy Not Stripping `/BBTS` Prefix (CRITICAL)

**Problem**: Flask receives `/BBTS/health` instead of `/health`, causing 404 errors

**Root Cause**: The `/etc/nginx/sites-available/default` file contains a **duplicate** `/BBTS` location block with incorrect proxy configuration:

```nginx
# In /etc/nginx/sites-available/default
location /BBTS {
    proxy_pass http://127.0.0.1:5000/BBTS;  # ❌ WRONG - keeps the /BBTS prefix!
    ...
}
```

The default site is configured as `default_server` and matches requests before the dedicated `marbefes-bbt` configuration.

**Evidence**:
- Gunicorn access log shows: `"GET /BBTS/health HTTP/1.1" 404`
- Direct requests to `http://localhost:5000/health` work correctly (returns 200)
- Proxied requests to `http://localhost/BBTS/health` return 404

**Solution**:
Comment out or remove the duplicate `/BBTS` location block from `/etc/nginx/sites-available/default`.

---

### 2. ⚠️ Excessive Gunicorn Worker Count

**Problem**: 57 Gunicorn workers running (28 CPUs × 2 + 1)

**Impact**:
- Excessive memory usage (~9.7 GB: 57 × 170 MB per worker)
- Slower application startup
- Unnecessary context switching overhead

**Root Cause**: `/var/www/marbefes-bbt/gunicorn_config.py` line 11:
```python
workers = multiprocessing.cpu_count() * 2 + 1  # Creates 57 workers on 28-core server!
```

**Recommended**: For this application type (I/O-bound WMS proxy), use 4-8 workers:
```python
workers = min(8, multiprocessing.cpu_count())  # Cap at 8 workers
```

---

### 3. ⚠️ Huge Error Log File

**Problem**: `/var/www/marbefes-bbt/logs/gunicorn-error.log` is **96 MB** (1.3 million lines)

**Root Cause**: No log rotation configured, accumulating worker boot messages since Oct 15

**Impact**: Disk space waste, slower log analysis

**Solution**: Truncate and enable log rotation:
```bash
sudo truncate -s 0 /var/www/marbefes-bbt/logs/gunicorn-error.log
```

Add logrotate configuration: `/etc/logrotate.d/marbefes-bbt`
```
/var/www/marbefes-bbt/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload marbefes-bbt > /dev/null 2>&1 || true
    endscript
}
```

---

### 4. ℹ️ Documentation Path Inconsistency

**Issue**: Some docs reference `/BBT`, nginx uses `/BBTS`

**Actual Path**: `/BBTS` (confirmed in nginx and production)

**Files to update**:
- `DEPLOYMENT_CHECKLIST.md` (mentions `/BBT` in several places)
- Any user-facing documentation

---

## 🔧 Manual Fix Procedure

Run these commands with sudo access:

### Step 1: Fix Nginx Proxy Configuration

```bash
# Backup the default nginx site
sudo cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup.20251016

# Option A: Comment out the /BBTS location block
sudo sed -i '/# MARBEFES BBT Database/,/^[[:space:]]*}$/s/^/#DISABLED# /' /etc/nginx/sites-available/default

# Option B: Manually edit and remove the entire location block
sudo nano /etc/nginx/sites-available/default
# Find and delete or comment out the "location /BBTS {" block (lines ~170-178)

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx

# Test the fix
curl http://localhost/BBTS/health | jq -r '.version'
# Should return: 1.2.7
```

### Step 2: Reduce Worker Count

```bash
# Edit gunicorn config
sudo nano /var/www/marbefes-bbt/gunicorn_config.py

# Change line 11 from:
#   workers = multiprocessing.cpu_count() * 2 + 1
# To:
#   workers = min(8, multiprocessing.cpu_count())

# Restart the service
sudo systemctl restart marbefes-bbt

# Verify worker count
pgrep -a gunicorn | grep marbefes | wc -l
# Should show: 9 (1 master + 8 workers)
```

### Step 3: Truncate and Rotate Logs

```bash
# Truncate the huge error log
sudo truncate -s 0 /var/www/marbefes-bbt/logs/gunicorn-error.log

# Create logrotate config
sudo tee /etc/logrotate.d/marbefes-bbt > /dev/null <<EOF
/var/www/marbefes-bbt/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload marbefes-bbt > /dev/null 2>&1 || true
    endscript
}
EOF

# Test logrotate
sudo logrotate -d /etc/logrotate.d/marbefes-bbt
```

---

## ✅ Verification Tests

After applying fixes:

```bash
# 1. Test direct app access
curl http://localhost:5000/health | jq '.status,.version'
# Expected: "healthy", "1.2.7"

# 2. Test nginx proxy
curl http://localhost/BBTS/health | jq '.status,.version'
# Expected: "healthy", "1.2.7"

# 3. Check gunicorn access log - should show "/health" not "/BBTS/health"
tail -1 /var/www/marbefes-bbt/logs/gunicorn-access.log
# Expected: "GET /health HTTP/1.1" 200

# 4. Verify worker count
pgrep -a gunicorn | grep marbefes | wc -l
# Expected: 9 (1 master + 8 workers)

# 5. Check memory usage
ps aux | grep gunicorn | awk '{sum+=$4} END {print sum "%"}'
# Expected: < 10% (down from ~30%)

# 6. Test full application
curl -I http://localhost/BBTS/ | grep "HTTP"
# Expected: HTTP/1.1 200 OK
```

---

## 🌐 External Access Test

After fixes, test from external browser:

```
http://laguna.ku.lt/BBTS
```

**Expected Behavior**:
- Page loads with MARBEFES logo
- Map initializes (Leaflet with satellite basemap)
- BBT dropdown shows 12 areas
- Vector layers load on hover
- No console errors (F12)

---

## 📊 System Status Summary

**Before Fixes**:
- ❌ Nginx proxy: Not working (404 errors)
- ⚠️ Workers: 57 (excessive)
- ⚠️ Error log: 96 MB
- ✅ Direct app: Working
- ✅ Gunicorn: Running (since Oct 15)

**After Fixes**:
- ✅ Nginx proxy: Working
- ✅ Workers: 8 (optimal)
- ✅ Error log: Truncated + rotation enabled
- ✅ Direct app: Working
- ✅ Memory usage: Reduced by ~66%

---

## 🔗 Related Files

**Nginx Configurations**:
- `/etc/nginx/sites-available/default` - Contains duplicate /BBTS config (**FIX THIS**)
- `/etc/nginx/sites-available/marbefes-bbt` - Correct config (already fixed)
- `/etc/nginx/sites-enabled/marbefes-bbt` - Symlink to config

**Application Files**:
- `/var/www/marbefes-bbt/gunicorn_config.py` - Worker count configuration
- `/var/www/marbefes-bbt/.env` - Environment configuration
- `/var/www/marbefes-bbt/app.py` - Flask application (v1.2.7)

**Service Files**:
- `/etc/systemd/system/marbefes-bbt.service` - Systemd service definition
- `/var/www/marbefes-bbt/logs/gunicorn-error.log` - Application logs
- `/var/www/marbefes-bbt/logs/gunicorn-access.log` - Access logs

---

## 📝 Quick Reference

```bash
# Service management
sudo systemctl status marbefes-bbt
sudo systemctl restart marbefes-bbt
sudo systemctl reload marbefes-bbt

# Nginx management
sudo nginx -t                  # Test configuration
sudo systemctl reload nginx    # Reload without downtime
sudo systemctl restart nginx   # Full restart

# View logs
sudo journalctl -u marbefes-bbt -f              # Follow service logs
tail -f /var/www/marbefes-bbt/logs/gunicorn-access.log  # Follow access logs
tail -f /var/www/marbefes-bbt/logs/gunicorn-error.log   # Follow error logs

# Check worker processes
pgrep -a gunicorn | grep marbefes

# Monitor memory usage
watch -n 2 "ps aux | grep gunicorn | awk '{sum+=\$4} END {print sum \"%\"}'"
```

---

**Priority**: Fix #1 (Nginx proxy) is CRITICAL and blocks all external access.

**Estimated Time**: 10 minutes for all fixes

**Risk Level**: Low (all changes have backups and can be reverted)
