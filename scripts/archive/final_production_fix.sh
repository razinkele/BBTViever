#!/bin/bash
# Final Production Fix - Complete solution
# 1. Update vector_loader.py to support .geojson
# 2. Copy bbt_factsheets.json
# 3. Remove old BBT.gpkg files
# 4. Use only MergedBBTs.geojson (12 features)
# 5. Verify everything works

if [ "$EUID" -ne 0 ]; then
    printf "Please run with sudo: sudo bash final_production_fix.sh\n"
    exit 1
fi

SRC="/home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck"
PROD="/var/www/marbefes-bbt"

printf "================================================================\n"
printf "MARBEFES BBT - Final Production Fix\n"
printf "================================================================\n\n"

printf "This will:\n"
printf "  1. Update vector_loader.py (add .geojson support)\n"
printf "  2. Copy bbt_factsheets.json\n"
printf "  3. Remove old BBT.gpkg (11 features)\n"
printf "  4. Use only MergedBBTs.geojson (12 features)\n"
printf "  5. Restart service and verify\n\n"

# Step 1: Update vector_loader.py
printf "================================================================\n"
printf "Step 1: Update vector_loader.py\n"
printf "================================================================\n\n"

cp "$SRC/src/emodnet_viewer/utils/vector_loader.py" "$PROD/src/emodnet_viewer/utils/vector_loader.py"
chown www-data:www-data "$PROD/src/emodnet_viewer/utils/vector_loader.py"
printf "Updated vector_loader.py (now supports .geojson files)\n"

# Step 2: Copy factsheets
printf "\n================================================================\n"
printf "Step 2: Copy BBT Factsheets\n"
printf "================================================================\n\n"

if [ -f "$SRC/data/bbt_factsheets.json" ]; then
    cp "$SRC/data/bbt_factsheets.json" "$PROD/data/bbt_factsheets.json"
    chown www-data:www-data "$PROD/data/bbt_factsheets.json"
    chmod 644 "$PROD/data/bbt_factsheets.json"
    SIZE=$(du -h "$PROD/data/bbt_factsheets.json" | cut -f1)
    printf "Copied bbt_factsheets.json (%s)\n" "$SIZE"
else
    printf "WARNING: Source file not found, skipping\n"
fi

# Step 3: Ensure MergedBBTs.geojson exists
printf "\n================================================================\n"
printf "Step 3: Verify MergedBBTs.geojson\n"
printf "================================================================\n\n"

if [ ! -f "$PROD/data/vector/MergedBBTs.geojson" ]; then
    printf "MergedBBTs.geojson missing, copying from source...\n"
    cp "$SRC/data/vector/MergedBBTs.geojson" "$PROD/data/vector/"
    chown www-data:www-data "$PROD/data/vector/MergedBBTs.geojson"
    chmod 644 "$PROD/data/vector/MergedBBTs.geojson"
fi

SIZE=$(du -h "$PROD/data/vector/MergedBBTs.geojson" | cut -f1)
printf "MergedBBTs.geojson present (%s)\n" "$SIZE"

# Step 4: Remove old BBT.gpkg files
printf "\n================================================================\n"
printf "Step 4: Remove Old BBT.gpkg Files\n"
printf "================================================================\n\n"

REMOVED=0

# Production vector directory
if [ -f "$PROD/data/vector/BBT.gpkg" ]; then
    mv "$PROD/data/vector/BBT.gpkg" "$PROD/data/vector/BBT.gpkg.backup_$(date +%Y%m%d_%H%M%S)"
    printf "Removed: /var/www/.../data/vector/BBT.gpkg (backed up)\n"
    REMOVED=$((REMOVED + 1))
fi

# Production data directory
for gpkg in "$PROD/data"/*.gpkg; do
    if [ -f "$gpkg" ]; then
        mv "$gpkg" "${gpkg}.backup_$(date +%Y%m%d_%H%M%S)"
        printf "Removed: %s (backed up)\n" "$(basename "$gpkg")"
        REMOVED=$((REMOVED + 1))
    fi
done

if [ "$REMOVED" -eq 0 ]; then
    printf "No old GPKG files found (already clean)\n"
else
    printf "Removed %d old GPKG file(s)\n" "$REMOVED"
fi

# Step 5: Restart service
printf "\n================================================================\n"
printf "Step 5: Restart Service\n"
printf "================================================================\n\n"

systemctl restart marbefes-bbt
printf "Service restart issued\n"
printf "Waiting for startup...\n"
sleep 6

if systemctl is-active --quiet marbefes-bbt; then
    printf "Service is running\n"
else
    printf "ERROR: Service failed to start\n"
    journalctl -u marbefes-bbt -n 20 --no-pager
    exit 1
fi

# Verification
printf "\n================================================================\n"
printf "VERIFICATION TESTS\n"
printf "================================================================\n\n"

printf "[Test 1] Vector Layers API\n"
VECTOR_JSON=$(curl -s http://localhost:5000/api/vector/layers)
COUNT=$(printf "%s" "$VECTOR_JSON" | jq -r '.count' 2>/dev/null || printf "0")
printf "  Found: %s vector layer(s)\n" "$COUNT"

if [ "$COUNT" -ge 1 ]; then
    printf "%s" "$VECTOR_JSON" | jq -r '.layers[] | "  - \(.display_name): \(.feature_count) features from \(.source_file)"'
fi

printf "\n[Test 2] MergedBBTs API Endpoint\n"
MERGED_JSON=$(curl -s http://localhost:5000/api/vector/layer/MergedBBTs)
if printf "%s" "$MERGED_JSON" | jq -e '.type == "FeatureCollection"' > /dev/null 2>&1; then
    FEATURES=$(printf "%s" "$MERGED_JSON" | jq -r '.features | length')
    printf "  Status: Working\n"
    printf "  Features: %d BBT areas\n" "$FEATURES"
    
    if [ "$FEATURES" -eq 12 ]; then
        printf "  All 12 BBT areas present\n"
    fi
else
    printf "  Status: ERROR - Not loading\n"
    printf "  Response: %s\n" "$(printf "%s" "$MERGED_JSON" | jq -c '.' | head -c 100)"
fi

printf "\n[Test 3] Factsheets API\n"
FACTSHEETS_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5000/api/factsheets)
printf "  HTTP Status: %s\n" "$FACTSHEETS_CODE"

if [ "$FACTSHEETS_CODE" = "200" ]; then
    FACTSHEETS_JSON=$(curl -s http://localhost:5000/api/factsheets)
    FACT_COUNT=$(printf "%s" "$FACTSHEETS_JSON" | jq '. | length' 2>/dev/null || printf "0")
    printf "  Factsheets: %s\n" "$FACT_COUNT"
fi

printf "\n[Test 4] Files in Production\n"
printf "  Vector files:\n"
ls -lh "$PROD/data/vector/" | grep -E "\.geojson|\.gpkg" | awk '{printf "    %s  %s\n", $9, $5}'

# Summary
printf "\n================================================================\n"
printf "FINAL SUMMARY\n"
printf "================================================================\n\n"

SUCCESS=0
if [ "$COUNT" -eq 1 ] && printf "%s" "$MERGED_JSON" | jq -e '.type == "FeatureCollection"' > /dev/null 2>&1 && [ "$FACTSHEETS_CODE" = "200" ]; then
    SUCCESS=1
fi

if [ "$SUCCESS" -eq 1 ]; then
    FEATURES=$(printf "%s" "$MERGED_JSON" | jq -r '.features | length')
    printf "SUCCESS! Production server fully operational\n\n"
    printf "Configuration:\n"
    printf "  Vector layers: 1 (MergedBBTs.geojson only)\n"
    printf "  BBT areas: %d features\n" "$FEATURES"
    printf "  Factsheets: Working (HTTP 200)\n"
    printf "  Old BBT.gpkg: Removed\n\n"
    printf "Test in browser: http://laguna.ku.lt/BBTS\n"
    printf "  Expected console: Vector=1 (not Vector=2)\n"
    printf "  Expected map: All %d BBT areas visible\n" "$FEATURES"
    printf "  Expected errors: None\n"
else
    printf "ISSUES DETECTED:\n\n"
    [ "$COUNT" -ne 1 ] && printf "  Vector layers: %s (expected 1)\n" "$COUNT"
    ! printf "%s" "$MERGED_JSON" | jq -e '.type == "FeatureCollection"' > /dev/null 2>&1 && printf "  MergedBBTs: Not loading\n"
    [ "$FACTSHEETS_CODE" != "200" ] && printf "  Factsheets: HTTP %s (expected 200)\n" "$FACTSHEETS_CODE"
    printf "\nCheck logs: sudo journalctl -u marbefes-bbt -n 50\n"
fi

printf "\n================================================================\n"
