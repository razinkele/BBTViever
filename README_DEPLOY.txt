╔══════════════════════════════════════════════════════════════════════════════╗
║                    MARBEFES BBT - READY TO DEPLOY                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

┌──────────────────────────────────────────────────────────────────────────────┐
│ QUICK START - ONE COMMAND                                                    │
└──────────────────────────────────────────────────────────────────────────────┘

cd /home/razinka/OneDrive/HORIZON_EUROPE/MARBEFES/EMODNET_PyDeck
./deploy.sh


┌──────────────────────────────────────────────────────────────────────────────┐
│ WHAT WILL BE DEPLOYED                                                        │
└──────────────────────────────────────────────────────────────────────────────┘

✅ Logo Fix           - Logo will display in header
✅ API Fix            - BBT navigation will work
✅ WMS Click Query    - Click layers to query data (NEW!)
✅ EUNIS 2019 Only    - Full classification, no simplifications (NEW!)


┌──────────────────────────────────────────────────────────────────────────────┐
│ PASSWORD PROMPTS                                                             │
└──────────────────────────────────────────────────────────────────────────────┘

You will be asked for your password 3 times:
  1. Copy app.py
  2. Copy templates/index.html
  3. Restart service


┌──────────────────────────────────────────────────────────────────────────────┐
│ AFTER DEPLOYMENT                                                             │
└──────────────────────────────────────────────────────────────────────────────┘

Open in browser: http://laguna.ku.lt/BBTS

Verify:
  ✓ Logo appears in header
  ✓ No console errors (F12)
  ✓ BBT navigation works
  ✓ Click on EUNIS layer shows habitat info (NEW!)


┌──────────────────────────────────────────────────────────────────────────────┐
│ DOCUMENTATION                                                                │
└──────────────────────────────────────────────────────────────────────────────┘

DEPLOY.md                - Complete deployment guide (START HERE)
DEPLOY_INSTRUCTIONS.txt  - Manual step-by-step instructions
WMS_CLICK_QUERY.md      - WMS click query documentation
EUNIS_LAYER_ONLY.md     - EUNIS 2019 configuration details


╔══════════════════════════════════════════════════════════════════════════════╗
║  Ready to deploy? Run: ./deploy.sh                                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
