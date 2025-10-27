#!/bin/bash
echo "=== API ENDPOINT CONSISTENCY CHECK ==="
echo ""
echo "1. Checking config.js for API_BASE_URL:"
grep -n "API_BASE_URL" /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/static/js/config.js | head -5

echo ""
echo "2. Checking template injection:"
grep -n "API_BASE_URL" /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/templates/index.html | head -3

echo ""
echo "3. Checking JavaScript usage of API_BASE_URL:"
grep -rn "AppConfig.API_BASE_URL\|window.API_BASE_URL" /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck/static/js/ | grep -v "\/\/" | head -10

echo ""
echo "4. Testing actual API endpoints:"
echo "   /api/vector/layers:"
curl -s -w "HTTP %{http_code}\n" http://localhost:5000/api/vector/layers -o /dev/null
echo "   /api/vector/layer/Bbt%20-%20Merged:"
curl -s -w "HTTP %{http_code}\n" "http://localhost:5000/api/vector/layer/Bbt%20-%20Merged" -o /dev/null
