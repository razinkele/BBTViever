#!/bin/bash
# Deploy version and template fixes to production

printf "Deploying version 1.2.8 and template fixes...\n\n"

# 1. Update version file
printf "[1/4] Updating version to 1.2.8...\n"
sudo cp /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/src/emodnet_viewer/__version__.py \
        /var/www/marbefes-bbt/src/emodnet_viewer/__version__.py
sudo chown www-data:www-data /var/www/marbefes-bbt/src/emodnet_viewer/__version__.py
printf "  ✓ Version file updated\n\n"

# 2. Update template with dynamic version and fixed health check URL
printf "[2/4] Updating template...\n"
sudo cp /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/templates/index.html \
        /var/www/marbefes-bbt/templates/index.html
sudo chown www-data:www-data /var/www/marbefes-bbt/templates/index.html
printf "  ✓ Template updated (dynamic version + fixed health URL)\n\n"

# 3. Restart service
printf "[3/4] Restarting service...\n"
sudo systemctl restart marbefes-bbt
sleep 4
printf "  ✓ Service restarted\n\n"

# 4. Verify deployment
printf "[4/4] Verifying deployment...\n"
HEALTH_JSON=$(curl -s http://localhost:5000/health)
VERSION=$(printf "%s" "$HEALTH_JSON" | jq -r '.version')
VERSION_DATE=$(printf "%s" "$HEALTH_JSON" | jq -r '.version_date')
STATUS=$(printf "%s" "$HEALTH_JSON" | jq -r '.status')

printf "  Version: %s\n" "$VERSION"
printf "  Date:    %s\n" "$VERSION_DATE"
printf "  Status:  %s\n\n" "$STATUS"

if [ "$VERSION" = "1.2.8" ] && [ "$VERSION_DATE" = "2025-10-16" ] && [ "$STATUS" = "healthy" ]; then
    printf "✅ SUCCESS! All fixes deployed\n\n"
    printf "Changes:\n"
    printf "  ✓ Version updated to 1.2.8 (Code Refactoring - DRY Optimization)\n"
    printf "  ✓ Template now uses dynamic {{ app_version }}\n"
    printf "  ✓ Health check URL fixed (uses API_BASE_URL)\n"
    printf "  ✓ Version date dynamically fetched from health API\n"
    printf "  ✓ BBT feature count corrected to 12\n\n"
    printf "Test the about page: http://laguna.ku.lt/BBTS\n"
    printf "  Click the ⓘ button → Should show version 1.2.8 with no errors\n"
else
    printf "⚠️  WARNING: Verification values don't match expected\n"
    printf "  Expected: 1.2.8, 2025-10-16, healthy\n"
    printf "  Got:      %s, %s, %s\n" "$VERSION" "$VERSION_DATE" "$STATUS"
fi
