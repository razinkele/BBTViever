#!/bin/bash
# Update vector_loader.py to support .geojson files

if [ "$EUID" -ne 0 ]; then
    printf "Please run with sudo: sudo bash update_vector_loader.sh\n"
    exit 1
fi

printf "Updating vector_loader.py to support .geojson files...\n"

cp /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/src/emodnet_viewer/utils/vector_loader.py \
   /var/www/marbefes-bbt/src/emodnet_viewer/utils/vector_loader.py

chown www-data:www-data /var/www/marbefes-bbt/src/emodnet_viewer/utils/vector_loader.py
printf "File updated and ownership set\n"

printf "\nRestarting service...\n"
systemctl restart marbefes-bbt
sleep 6

printf "\nChecking vector layers...\n"
curl -s http://localhost:5000/api/vector/layers | jq -r '.count as $c | "Found \($c) vector layers:"' 
curl -s http://localhost:5000/api/vector/layers | jq -r '.layers[] | "  - \(.display_name) (\(.feature_count) features from \(.source_file))"'

printf "\nTesting MergedBBTs API...\n"
RESPONSE=$(curl -s http://localhost:5000/api/vector/layer/MergedBBTs)
if echo "$RESPONSE" | jq -e '.type == "FeatureCollection"' > /dev/null 2>&1; then
    FEATURES=$(echo "$RESPONSE" | jq -r '.features | length')
    printf "SUCCESS: MergedBBTs returns %d features\n" "$FEATURES"
else
    printf "ERROR: %s\n" "$(echo "$RESPONSE" | jq -c '.')"
fi
