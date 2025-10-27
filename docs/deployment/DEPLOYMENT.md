# MARBEFES BBT Application - Production Deployment Guide

## Overview

This guide will help you deploy the MARBEFES BBT interactive map application to a production server.

**Application Details:**
- Size: ~10MB (core application without venv)
- Data Files: ~5.5MB (2 GPKG vector files)
- Python: 3.9+ required
- Dependencies: Flask, GeoPandas, Fiona, PyProj

---

## Quick Transfer Methods

### Method 1: rsync (Recommended - Fastest)

```bash
# From current server
cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck

# Transfer directly to production server
rsync -avz --exclude='venv' --exclude='__pycache__' --exclude='.git' \
  ./ user@production-server:/var/www/marbefes_bbt/
```

### Method 2: Create Archive and Transfer

```bash
# Create deployment package
cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck

tar --exclude='venv' --exclude='__pycache__' --exclude='.git' \
    -czf /tmp/marbefes_deploy.tar.gz \
    app.py requirements.txt src/ data/ LOGO/ CLAUDE.md

# Transfer
scp /tmp/marbefes_deploy.tar.gz user@production-server:/tmp/
```

---

## Production Server Setup

### 1. Extract and Install

```bash
# On production server
cd /var/www
mkdir -p marbefes_bbt
cd marbefes_bbt

# If using tar archive
tar -xzf /tmp/marbefes_deploy.tar.gz

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Test Application

```bash
# Test run
python app.py

# Should see:
# 🌐 Server accessible at:
#    Local:    http://127.0.0.1:5000
#    ...
```

### 3. Create systemd Service

Create `/etc/systemd/system/marbefes-bbt.service`:

```ini
[Unit]
Description=MARBEFES BBT Flask Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/marbefes_bbt
Environment="PATH=/var/www/marbefes_bbt/venv/bin"
ExecStart=/var/www/marbefes_bbt/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable marbefes-bbt
sudo systemctl start marbefes-bbt
sudo systemctl status marbefes-bbt
```

### 4. Configure Nginx (Optional but Recommended)

Install nginx:
```bash
sudo apt install nginx
```

Create `/etc/nginx/sites-available/marbefes-bbt`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_read_timeout 300;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/marbefes-bbt /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Production Checklist

- [ ] Disable debug mode in app.py (line 648: `debug=False`)
- [ ] Configure firewall (allow port 5000 or 80)
- [ ] Setup systemd service for auto-start
- [ ] Configure nginx reverse proxy
- [ ] Add SSL certificate (certbot)
- [ ] Test vector data loading
- [ ] Monitor logs

---

## Files to Transfer

**Essential:**
- app.py
- requirements.txt
- src/ directory
- data/vector/ (BBts.gpkg, CheckedBBT.gpkg)
- LOGO/marbefes_02.png

**Optional:**
- CLAUDE.md (documentation)
- templates/ (if separated from app.py)
- static/ (additional assets)

---

## System Requirements

**Ubuntu/Debian:**
```bash
sudo apt install python3 python3-pip python3-venv libgdal-dev libgeos-dev libproj-dev
```

**CentOS/RHEL:**
```bash
sudo yum install python3 python3-devel gdal-devel geos-devel proj-devel gcc
```

---

## Troubleshooting

**Vector layers not loading:**
```bash
ls -lh data/vector/*.gpkg
python -c "from src.emodnet_viewer.utils.vector_loader import load_all_vector_data; print(len(load_all_vector_data()))"
```

**Port already in use:**
```bash
sudo lsof -i :5000
# Kill process or change port in .env
```

**Check logs:**
```bash
sudo journalctl -u marbefes-bbt -f
```

---

## Security Notes

⚠️ **Important for Production:**

1. Disable debug mode (`debug=False` in app.py)
2. Use nginx reverse proxy
3. Add SSL/HTTPS (Let's Encrypt)
4. Configure firewall properly
5. Consider adding authentication
6. Regular system updates

---

For detailed information, see CLAUDE.md in the project directory.
