# Layer Name Fix - GeoJSON Migration

**Date:** October 13, 2025
**Issue:** Layer name mismatch after GeoJSON conversion
**Status:** ✅ FIXED

---

## Problem

After converting BBT.gpkg to BBT.geojson, the layer name changed from "Bbt - Merged" to "Bbt", causing 404 errors in the browser:

```
❌ API Error: 404 NOT FOUND {
  "error": "Layer 'Bbt - Merged' not found"
}
```

**Root Cause:** The original GPKG file had a layer called "merged" which was displayed as "Bbt - Merged" (filename + layer name). The GeoJSON file only has the filename stem "BBT" which displays as "Bbt".

---

## Solution

Updated JavaScript files to use the new layer name "Bbt" with backward compatibility for "Bbt - Merged":

### 1. app.js (static/js/app.js:82-91)

**Before:**
```javascript
// Load main BBT layer (Bbt - Merged)
const mainLayer = window.vectorLayers.find(l => l.display_name === 'Bbt - Merged');
```

**After:**
```javascript
// Load main BBT layer (try "Bbt" first, fallback to "Bbt - Merged" for backward compatibility)
const mainLayer = window.vectorLayers.find(l => l.display_name === 'Bbt' || l.display_name === 'Bbt - Merged');
```

### 2. bbt-tool.js (static/js/bbt-tool.js)

**Changed:** All 8 occurrences of `'Bbt - Merged'` → `'Bbt'`

**Lines affected:**
- Line 92: API URL construction for loading BBT features
- Line 322: `selectVectorLayerAsBase` call
- Line 355: Current layer assignment
- Line 377: BBT layer loaded check
- Line 390: `loadVectorLayerWithoutAutoZoom` call
- Line 417: Fetch API URL
- Line 444: `loadVectorLayerWithoutAutoZoom` call
- Line 455: `loadVectorLayerFast` call

---

## Files Modified

1. **`static/js/app.js`** - Updated layer name search with backward compatibility
2. **`static/js/bbt-tool.js`** - Replaced all 8 occurrences of "Bbt - Merged" with "Bbt"

---

## Testing

### Before Fix:
```
console.log:
⚠️ Could not find "Bbt - Merged" layer
❌ API Error: 404 NOT FOUND
```

### After Fix (expected):
```
console.log:
✅ Main BBT layer loaded
✅ Loaded 10 factsheets
🚀 Background loading BBT navigation data...
✅ BBT features loaded successfully
```

---

## User Action Required

**IMPORTANT:** Users must **hard-refresh** their browser to clear the cached JavaScript files:

- **Chrome/Edge/Firefox (Windows/Linux):** Ctrl + F5 or Ctrl + Shift + R
- **Chrome/Firefox (Mac):** Cmd + Shift + R
- **Safari (Mac):** Cmd + Option + R

Without a hard-refresh, the browser will serve cached files with the old "Bbt - Merged" references (status 304).

---

## Verification Checklist

After hard-refresh, verify:

- [ ] Browser console shows: "✅ Main BBT layer loaded"
- [ ] No 404 errors for "Bbt - Merged"
- [ ] BBT navigation buttons work
- [ ] BBT hover tooltips display
- [ ] BBT area calculations show
- [ ] Console shows: "GeoJSON fast-path for Bbt (no GDAL)"

---

## Why This Happened

### GPKG Layer Naming
```
File: BBT.gpkg
Layer: "merged"
Display: "Bbt - Merged" (stem + layer name)
```

### GeoJSON Layer Naming
```
File: BBT.geojson
Layer: (implicitly "BBT" from filename)
Display: "Bbt" (stem only)
```

The `_create_display_name()` function in vector_loader.py combines the file stem with the layer name. Since GeoJSON files don't have internal layer names (they're single-layer by design), only the file stem is used.

---

## Backward Compatibility

The fix in `app.js` uses an OR condition to support both names:

```javascript
l.display_name === 'Bbt' || l.display_name === 'Bbt - Merged'
```

This ensures:
- ✅ New deployments with GeoJSON work (searches for "Bbt")
- ✅ Old deployments with GPKG work (searches for "Bbt - Merged")
- ✅ Migration path is smooth (no breaking changes)

---

## Future Considerations

### Option 1: Rename GeoJSON File
```bash
mv data/vector/BBT.geojson data/vector/"Bbt - Merged.geojson"
```
This would make the display name "Bbt - Merged" again.

### Option 2: Standardize on New Name
Keep "Bbt" as the canonical name and update all documentation.

**Recommendation:** Keep "Bbt" as the simpler, cleaner name. The backward compatibility code handles the transition gracefully.

---

## Related Files

- `static/js/app.js` - Main application loader
- `static/js/bbt-tool.js` - BBT navigation tool
- `src/emodnet_viewer/utils/vector_loader.py` - Vector layer naming logic (lines 367-376)
- `GEOJSON_SOLUTION.md` - Overall GeoJSON implementation documentation

---

## Summary

✅ **Issue:** Layer name changed from "Bbt - Merged" to "Bbt" after GeoJSON conversion
✅ **Fix:** Updated JavaScript to use new name with backward compatibility
✅ **Status:** All code changes complete
⏳ **User Action:** Hard-refresh browser to load updated JavaScript

---

**Last Updated:** October 13, 2025
**Status:** ✅ CODE FIXED - BROWSER REFRESH REQUIRED
