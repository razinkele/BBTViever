# MARBEFES BBT Database v1.2.4 - Deployment Instructions

## 🎯 What's New in v1.2.4

This release integrates all 24 MARBEFES datasets from the VLIZ repository into the BBT data panels:

- **Dataset Integration**: All datasets now accessible via 📊 buttons
- **VLIZ Links**: Direct links to metadata at https://www.vliz.be
- **Category Organization**: Datasets grouped by type (Biological, Environmental, Socio-Economic)
- **Coverage Status**: Clear "No MARBEFES data produced" message for incomplete coverage

### Files Changed

1. **New Files**:
   - `static/js/data/marbefes-datasets.js` - Dataset database (24 datasets, 11 BBT regions)

2. **Modified Files**:
   - `static/js/bbt-tool.js` - Updated popup to display datasets instead of editable form
   - `templates/index.html` - Added dataset module, updated tooltips, removed save button

## 📋 Prerequisites

Before deploying, ensure you have:

1. **SSH Access** to `laguna.ku.lt`
   ```bash
   ssh razinka@laguna.ku.lt
   ```

2. **SSH Keys** configured (recommended)
   ```bash
   ssh-copy-id razinka@laguna.ku.lt
   ```

3. **Directory Access** to `/var/www/marbefes-bbt`

## 🚀 Deployment Methods

### Method 1: Automated Script (Recommended)

Run the deployment script from your local machine:

```bash
cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck
./DEPLOY_v1.2.4.sh
```

The script will:
1. ✓ Test SSH connection
2. ✓ Stop running application
3. ✓ Create backup
4. ✓ Deploy all files
5. ✓ Verify new modules
6. ✓ Install dependencies
7. ✓ Start application
8. ✓ Run health checks

**Expected Output:**
```
========================================
MARBEFES BBT v1.2.4 Deployment
Dataset Integration Release
========================================

[1/7] Testing SSH connection...
✓ SSH connection successful

[2/7] Stopping existing application...
✓ Stopped

[3/7] Creating backup...
✓ Backup created: backup_20251013_201500.tar.gz

[4/7] Deploying application files...
✓ Files deployed

[5/7] Verifying new files...
✓ New dataset module deployed successfully

[6/7] Installing dependencies...
✓ Dependencies installed

[7/7] Starting application on port 5000...
✓ Application started

========================================
Verifying Deployment...
========================================

✓ Gunicorn running with 5 workers
✓ Health endpoint responding
  Version: 1.2.4 (2025-10-13)
✓ BBT vector layer loaded (11 features expected)
✓ Main page accessible

========================================
Deployment Complete! v1.2.4
========================================

🎉 New Features:
  • MARBEFES dataset integration (24 datasets)
  • Dataset panels linked to VLIZ repository
  • Category-organized display (Biological/Environmental/Socio-Economic)
  • Clickable metadata links for all datasets

📍 Application URL: http://laguna.ku.lt:5000
```

---

### Method 2: Manual Deployment

If the script doesn't work, deploy manually:

#### Step 1: Stop Application
```bash
ssh razinka@laguna.ku.lt "pkill -f 'gunicorn.*app:app' || pkill -f 'python.*app.py'"
```

#### Step 2: Sync Files
```bash
# From local machine
cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck

# Sync Python files
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='.git' \
  ./*.py razinka@laguna.ku.lt:/var/www/marbefes-bbt/

# Sync templates
rsync -avz templates/ razinka@laguna.ku.lt:/var/www/marbefes-bbt/templates/

# Sync JavaScript (including new dataset module)
rsync -avz static/js/ razinka@laguna.ku.lt:/var/www/marbefes-bbt/static/js/

# Sync data files
rsync -avz data/ razinka@laguna.ku.lt:/var/www/marbefes-bbt/data/
```

#### Step 3: Verify New Files
```bash
ssh razinka@laguna.ku.lt "ls -la /var/www/marbefes-bbt/static/js/data/marbefes-datasets.js"
```

Expected: File should exist with ~500+ lines

#### Step 4: Install Dependencies
```bash
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
  source venv/bin/activate && \
  pip install pandas==2.0.3 && \
  pip install -r requirements.txt"
```

#### Step 5: Start Application
```bash
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
  nohup venv/bin/gunicorn -c gunicorn_config.py app:app \
  > logs/gunicorn.log 2>&1 &"
```

#### Step 6: Verify Deployment
```bash
# Check processes
ssh razinka@laguna.ku.lt "pgrep -af gunicorn"

# Test health endpoint
curl http://laguna.ku.lt:5000/health

# Test main page
curl -I http://laguna.ku.lt:5000/
```

---

## ✅ Verification Checklist

After deployment, verify these items:

- [ ] Application accessible at http://laguna.ku.lt:5000
- [ ] Health endpoint returns version 1.2.4: http://laguna.ku.lt:5000/health
- [ ] All 11 BBT regions visible in sidebar
- [ ] Clicking 📊 button opens dataset panel
- [ ] Heraklion shows 11 datasets (most comprehensive)
- [ ] Lithuanian coast shows 6 datasets
- [ ] North Sea shows 4 datasets
- [ ] Sardinia shows 4 datasets
- [ ] Irish Sea shows 3 datasets
- [ ] Archipelago shows 3 datasets
- [ ] Other regions (Balearic, Bay of Gdansk, Gulf of Biscay, Hornsund, Kongsfjord) show 2 datasets each
- [ ] Each dataset has clickable "View Metadata at VLIZ" link
- [ ] Links open to https://www.vliz.be/en/imis?module=dataset&dasid=XXXX
- [ ] Datasets grouped by category (Biological, Environmental, Socio-Economic)

---

## 🔧 Troubleshooting

### Issue: SSH Connection Failed

**Solution:**
```bash
# Test connection
ssh razinka@laguna.ku.lt

# If password required, set up SSH keys
ssh-copy-id razinka@laguna.ku.lt
```

### Issue: Application Not Starting

**Check logs:**
```bash
ssh razinka@laguna.ku.lt "tail -50 /var/www/marbefes-bbt/logs/gunicorn.log"
```

**Common causes:**
- Port 5000 already in use
- pandas version mismatch (should be 2.0.3)
- Missing data files

**Fix:**
```bash
# Kill all gunicorn processes
ssh razinka@laguna.ku.lt "pkill -9 -f gunicorn"

# Verify pandas version
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
  source venv/bin/activate && \
  python -c 'import pandas; print(pandas.__version__)'"

# Restart
ssh razinka@laguna.ku.lt "cd /var/www/marbefes-bbt && \
  nohup venv/bin/gunicorn -c gunicorn_config.py app:app \
  > logs/gunicorn.log 2>&1 &"
```

### Issue: Dataset Panel Empty

**Check if module loaded:**
```bash
# Open browser console on http://laguna.ku.lt:5000
# Type: window.MARBEFESDatasets
# Should show dataset object with 11 BBT regions
```

**Fix:**
```bash
# Re-sync JavaScript files
rsync -avz static/js/data/ razinka@laguna.ku.lt:/var/www/marbefes-bbt/static/js/data/

# Restart application
ssh razinka@laguna.ku.lt "pkill -f gunicorn && cd /var/www/marbefes-bbt && \
  nohup venv/bin/gunicorn -c gunicorn_config.py app:app > logs/gunicorn.log 2>&1 &"

# Clear browser cache (Ctrl+Shift+R)
```

### Issue: "No MARBEFES data produced" for All Regions

**This indicates JavaScript module not loading.**

**Check:**
```bash
# Verify file exists
ssh razinka@laguna.ku.lt "ls -lh /var/www/marbefes-bbt/static/js/data/marbefes-datasets.js"

# Check file size (should be ~25-30KB)
ssh razinka@laguna.ku.lt "wc -l /var/www/marbefes-bbt/static/js/data/marbefes-datasets.js"
# Expected: ~550 lines
```

---

## 🔄 Rollback Instructions

If deployment fails, rollback to previous version:

```bash
# Find backup
ssh razinka@laguna.ku.lt "ls -lt /var/www/backup_*.tar.gz | head -1"

# Restore backup (replace with actual backup name)
ssh razinka@laguna.ku.lt "cd /var/www && \
  pkill -f gunicorn && \
  tar -xzf backup_20251013_201500.tar.gz && \
  cd marbefes-bbt && \
  nohup venv/bin/gunicorn -c gunicorn_config.py app:app > logs/gunicorn.log 2>&1 &"
```

---

## 📊 Dataset Coverage Reference

| BBT Region | Datasets | Primary Categories |
|------------|----------|-------------------|
| **Heraklion** | 11 | Biological (9), Socio-Economic (2) |
| **Lithuanian coast** | 6 | Environmental (3), Socio-Economic (2), Biological (1) |
| **North Sea** | 4 | Socio-Economic (4) |
| **Sardinia** | 4 | Socio-Economic (3), Biological (1) |
| **Irish Sea** | 3 | Environmental (1), Socio-Economic (2) |
| **Archipelago** | 3 | Biological (1), Socio-Economic (2) |
| **Balearic** | 2 | Socio-Economic (2) |
| **Bay of Gdansk** | 2 | Socio-Economic (2) |
| **Gulf of Biscay** | 2 | Socio-Economic (2) |
| **Hornsund** | 2 | Socio-Economic (2) |
| **Kongsfjord** | 2 | Socio-Economic (2) |

---

## 📞 Support

If you encounter issues:

1. Check logs: `ssh razinka@laguna.ku.lt 'tail -f /var/www/marbefes-bbt/logs/gunicorn.log'`
2. Verify processes: `ssh razinka@laguna.ku.lt 'pgrep -af gunicorn'`
3. Test endpoints:
   - Health: http://laguna.ku.lt:5000/health
   - Vector: http://laguna.ku.lt:5000/api/vector/layers
   - Main: http://laguna.ku.lt:5000/

---

## 📝 Post-Deployment Tasks

After successful deployment:

- [ ] Update project documentation with v1.2.4 release notes
- [ ] Inform team about new dataset feature
- [ ] Update CLAUDE.md if needed
- [ ] Tag release in git (if using version control)

---

**Deployed by:** Claude Code
**Deployment Date:** 2025-10-13
**Version:** 1.2.4 - Dataset Integration Release
