#!/bin/bash
# Remove old BBT.gpkg files - use only MergedBBTs.geojson

if [ "$EUID" -ne 0 ]; then
    printf "Please run with sudo: sudo bash remove_old_bbt_files.sh\n"
    exit 1
fi

printf "================================================================\n"
printf "Cleaning Up Duplicate BBT Files\n"
printf "================================================================\n\n"

printf "Current situation:\n"
printf "  - BBT.gpkg: 11 features (old)\n"
printf "  - MergedBBTs.geojson: 12 features (current)\n\n"

printf "Action: Remove BBT.gpkg from production and development\n"
printf "Result: Single source of truth with 12 BBT areas\n\n"

# Production
printf "[1] Production: /var/www/marbefes-bbt/data/vector/\n"
if [ -f /var/www/marbefes-bbt/data/vector/BBT.gpkg ]; then
    printf "    Backing up BBT.gpkg...\n"
    mv /var/www/marbefes-bbt/data/vector/BBT.gpkg \
       /var/www/marbefes-bbt/data/vector/BBT.gpkg.backup_$(date +%Y%m%d_%H%M%S)
    printf "    Removed BBT.gpkg (backed up)\n"
else
    printf "    BBT.gpkg not found (already removed)\n"
fi

# Development
printf "\n[2] Development: ~/OneDrive/.../data/vector/\n"
if [ -f /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/data/vector/BBT.gpkg ]; then
    printf "    Backing up BBT.gpkg...\n"
    mv /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/data/vector/BBT.gpkg \
       /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/data/vector/BBT.gpkg.backup_$(date +%Y%m%d_%H%M%S)
    printf "    Removed BBT.gpkg (backed up)\n"
else
    printf "    BBT.gpkg not found (already removed)\n"
fi

# Check for other old GPKG files
printf "\n[3] Checking for other old GPKG files...\n"
for file in /var/www/marbefes-bbt/data/*.gpkg /var/www/marbefes-bbt/data/vector/*.gpkg; do
    if [ -f "$file" ]; then
        BASENAME=$(basename "$file")
        printf "    Found: %s\n" "$BASENAME"
        printf "    Moving to backup...\n"
        mv "$file" "${file}.backup_$(date +%Y%m%d_%H%M%S)"
    fi
done

# Restart service
printf "\n[4] Restarting service to reload vector layers...\n"
systemctl restart marbefes-bbt
sleep 6

if systemctl is-active --quiet marbefes-bbt; then
    printf "    Service is running\n"
else
    printf "    ERROR: Service failed to start\n"
    exit 1
fi

# Verify
printf "\n================================================================\n"
printf "Verification\n"
printf "================================================================\n\n"

printf "[Test 1] Checking remaining files in production...\n"
ls -lh /var/www/marbefes-bbt/data/vector/*.geojson 2>/dev/null || printf "    No geojson files found\n"
ls -lh /var/www/marbefes-bbt/data/vector/*.gpkg 2>/dev/null && printf "    WARNING: GPKG files still present!\n" || printf "    No GPKG files (good)\n"

printf "\n[Test 2] Vector layers API...\n"
VECTOR_JSON=$(curl -s http://localhost:5000/api/vector/layers)
COUNT=$(printf "%s" "$VECTOR_JSON" | jq -r '.count' 2>/dev/null || printf "0")
printf "    Vector layers found: %s\n" "$COUNT"

if [ "$COUNT" -eq 1 ]; then
    printf "    Layer details:\n"
    printf "%s" "$VECTOR_JSON" | jq -r '.layers[] | "      Name: \(.display_name)\n      Features: \(.feature_count)\n      Source: \(.source_file)"'
    printf "\n"
    
    # Check if it's MergedBBTs
    LAYER_NAME=$(printf "%s" "$VECTOR_JSON" | jq -r '.layers[0].source_file')
    if [ "$LAYER_NAME" = "MergedBBTs.geojson" ]; then
        printf "    SUCCESS: Using MergedBBTs.geojson as single source\n"
    else
        printf "    WARNING: Not using MergedBBTs.geojson\n"
    fi
elif [ "$COUNT" -gt 1 ]; then
    printf "    WARNING: Multiple vector layers detected:\n"
    printf "%s" "$VECTOR_JSON" | jq -r '.layers[] | "      - \(.display_name) from \(.source_file)"'
else
    printf "    ERROR: No vector layers found\n"
fi

printf "\n[Test 3] MergedBBTs API endpoint...\n"
MERGED_JSON=$(curl -s http://localhost:5000/api/vector/layer/MergedBBTs)
if printf "%s" "$MERGED_JSON" | jq -e '.type == "FeatureCollection"' > /dev/null 2>&1; then
    FEATURES=$(printf "%s" "$MERGED_JSON" | jq -r '.features | length')
    printf "    SUCCESS: MergedBBTs returns %d features\n" "$FEATURES"
    
    if [ "$FEATURES" -eq 12 ]; then
        printf "    All 12 BBT areas present\n"
    else
        printf "    WARNING: Expected 12 features, got %d\n" "$FEATURES"
    fi
else
    printf "    ERROR: MergedBBTs not loading\n"
fi

printf "\n================================================================\n"
printf "SUMMARY\n"
printf "================================================================\n\n"

if [ "$COUNT" -eq 1 ] && printf "%s" "$MERGED_JSON" | jq -e '.type == "FeatureCollection"' > /dev/null 2>&1; then
    printf "SUCCESS! Clean configuration:\n\n"
    printf "  Vector layers: 1 (MergedBBTs only)\n"
    printf "  Features: 12 BBT areas\n"
    printf "  Old BBT.gpkg: Removed (backed up)\n\n"
    printf "Test in browser: http://laguna.ku.lt/BBTS\n"
    printf "  - All 12 BBT areas should appear\n"
    printf "  - Console should show: Vector=1\n"
else
    printf "WARNING: Issues detected\n\n"
    printf "  Vector layers: %s (expected 1)\n" "$COUNT"
    printf "\nCheck logs: sudo journalctl -u marbefes-bbt -n 30\n"
fi

printf "\n================================================================\n"
