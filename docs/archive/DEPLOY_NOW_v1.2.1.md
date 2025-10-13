# Deploy v1.2.1 to laguna.ku.lt:5000

**Version:** 1.2.1 (BBT Fix + Version Updates)
**Date:** October 13, 2025
**Critical:** pandas 2.0.3 required for BBT display

---

## Quick Deployment

### Option 1: Automated Script (Recommended)

```bash
./DEPLOY_v1.2.1.sh
```

This will:
1. ✅ Test SSH connection
2. ✅ Stop existing processes
3. ✅ Deploy all files
4. ✅ Install dependencies (pandas 2.0.3!)
5. ✅ Verify pandas version
6. ✅ Start application
7. ✅ Run verification tests

---

## Option 2: Manual Deployment

If the automated script fails, run these commands manually:

### Step 1: Stop Existing Application

```bash
ssh razinka@laguna.ku.lt "pkill -f 'gunicorn.*app:app'"
```

### Step 2: Deploy Files

```bash
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='*.pyc' \
  --exclude='.git' --exclude='cache' --exclude='logs' \
  --exclude='*.md' --exclude='test_*.html' --exclude='_archive' \
  --exclude='FactSheets' --exclude='.env' \
  ./ razinka@laguna.ku.lt:/var/www/marbefes-bbt/
```

### Step 3: Install Dependencies

```bash
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
  source venv/bin/activate && \
  pip install pandas==2.0.3 && \
  pip install -r requirements.txt"
```

### Step 4: Start Application

```bash
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
  nohup venv/bin/gunicorn -c gunicorn_config.py app:app \
  > logs/gunicorn.log 2>&1 &"
```

---

## Verification

### 1. Check Health Endpoint

```bash
curl http://laguna.ku.lt:5000/health | jq
```

**Expected Output:**
```json
{
  "status": "healthy",
  "version": "1.2.1",
  "components": {
    "vector_support": {
      "available": true,
      "status": "operational"
    }
  }
}
```

### 2. Check BBT Vector Layers

```bash
curl http://laguna.ku.lt:5000/api/vector/layers | jq
```

**Expected Output:**
```json
{
  "layers": [
    {
      "layer_name": "merged",
      "display_name": "Bbt - Merged",
      "feature_count": 11,
      "geometry_type": "MultiPolygon"
    }
  ],
  "count": 1
}
```

### 3. Check Gunicorn Process

```bash
ssh razinka@laguna.ku.lt "pgrep -a gunicorn"
```

### 4. Check pandas Version

```bash
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
  source venv/bin/activate && \
  python -c 'import pandas; print(pandas.__version__)'"
```

**Expected:** `2.0.3`

### 5. View Logs

```bash
ssh razinka@laguna.ku.lt "tail -50 /var/www/marbefes-bbt/logs/gunicorn.log"
```

Look for:
```
✓ Cache initialized with type: simple
✓ Loaded bathymetry statistics for 11 BBT areas
✓ Loaded factsheet data for 10 BBT areas
✓ Loaded 1 vector layers from GPKG files
✓ Bbt - Merged (MultiPolygon, 11 features)
```

---

## Browser Testing

### 1. Open Application

**URL:** http://laguna.ku.lt:5000

### 2. Test Features

- ✅ Click help icon (ℹ️) → Should show **Version 1.2.1**
- ✅ Release date should show **October 13, 2025**
- ✅ Release notes should mention **BBT display fix**
- ✅ BBT navigation buttons visible in sidebar
- ✅ Click any BBT button → Map zooms to that area
- ✅ BBT polygons visible on map (11 features)
- ✅ Hover over BBT areas → Tooltip shows area calculations

### 3. Check All 11 BBT Areas

1. Archipelago ✅
2. Balearic ✅
3. Bay of Gdansk ✅
4. Gulf of Biscay ✅
5. Heraklion ✅
6. Hornsund ✅
7. Irish Sea ✅
8. Kongsfjord ✅
9. Lithuanian coastal zone ✅
10. North Sea ✅
11. Sardinia ✅

---

## What's New in v1.2.1

### Version Updates
- ✅ Help modal shows v1.2.1
- ✅ Health endpoint reports v1.2.1
- ✅ Release date: October 13, 2025

### Release Notes
- 🐛 **Fixed:** BBT vector layer display (pandas compatibility)
- 📦 Downgraded pandas to 2.0.3 for pyogrio compatibility
- 🛠️ Enhanced error handling in vector loader
- ✅ All 11 BBT areas now loading successfully

### Previous v1.2.0 Features
- Documented in help modal under "Previous Release"
- Security enhancements, caching improvements, Python 3.12+ support

---

## Troubleshooting

### Issue: BBT Not Displaying

**Check pandas version:**
```bash
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
  source venv/bin/activate && \
  python -c 'import pandas; print(pandas.__version__)'"
```

**Fix if not 2.0.3:**
```bash
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
  source venv/bin/activate && \
  pip install pandas==2.0.3 --force-reinstall"
```

Then restart:
```bash
ssh razinka@laguna.ku.lt "pkill -f gunicorn && \
  cd /var/www/marbefes-bbt && \
  nohup venv/bin/gunicorn -c gunicorn_config.py app:app \
  > logs/gunicorn.log 2>&1 &"
```

### Issue: Version Still Shows 1.2.0

**Clear browser cache:**
- Chrome: Ctrl+Shift+Delete → Clear cached images and files
- Firefox: Ctrl+Shift+Delete → Cache
- Or: Hard refresh with Ctrl+F5

**Check server files updated:**
```bash
ssh razinka@laguna.ku.lt "grep -n '1.2.1' /var/www/marbefes-bbt/app.py"
```

Should show line with `"version": "1.2.1"`

### Issue: Application Won't Start

**Check for errors:**
```bash
ssh razinka@laguna.ku.lt "tail -100 /var/www/marbefes-bbt/logs/gunicorn.log"
```

**Test import manually:**
```bash
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
  source venv/bin/activate && \
  python -c 'from app import app; print(\"OK\")'"
```

---

## Files Modified in v1.2.1

1. **templates/index.html**
   - Version: 1.2.0 → 1.2.1
   - Release date: January 12, 2025 → October 13, 2025
   - Added v1.2.1 release notes
   - Moved v1.2.0 features to "Previous Release"

2. **app.py**
   - Health endpoint version: 1.2.0 → 1.2.1

3. **CLAUDE.md**
   - Updated framework documentation to v1.2.1
   - Added BBT fix details

4. **pyproject.toml**
   - Project version: 1.1.0 → 1.2.1

5. **requirements.txt**
   - pandas==2.0.3 (unchanged - critical for BBT display)

---

## Deployment Checklist

### Pre-Deployment
- [x] Version updated to 1.2.1 in all files
- [x] Release notes added to help modal
- [x] pandas 2.0.3 in requirements.txt
- [x] Application tested locally
- [x] All imports successful
- [x] BBT layers loading (11 features)

### During Deployment
- [ ] SSH connection successful
- [ ] Existing processes stopped
- [ ] Files deployed via rsync
- [ ] Dependencies installed
- [ ] pandas version verified (2.0.3)
- [ ] Application started

### Post-Deployment
- [ ] Health endpoint responds
- [ ] Version shows 1.2.1
- [ ] BBT layers API returns count: 1
- [ ] Application loads in browser
- [ ] Help modal shows v1.2.1
- [ ] BBT navigation works
- [ ] All 11 BBT areas accessible
- [ ] Hover tooltips functional

---

## Quick Commands

```bash
# Deploy
./DEPLOY_v1.2.1.sh

# Check health
curl http://laguna.ku.lt:5000/health | jq '.version'

# Check BBT
curl http://laguna.ku.lt:5000/api/vector/layers | jq '.count'

# View logs
ssh razinka@laguna.ku.lt "tail -f /var/www/marbefes-bbt/logs/gunicorn.log"

# Restart
ssh razinka@laguna.ku.lt "pkill -f gunicorn && \
  cd /var/www/marbefes-bbt && \
  nohup venv/bin/gunicorn -c gunicorn_config.py app:app \
  > logs/gunicorn.log 2>&1 &"
```

---

**Status:** Ready to deploy
**Version:** 1.2.1
**Critical:** pandas 2.0.3 required
**Expected Duration:** 2-3 minutes
