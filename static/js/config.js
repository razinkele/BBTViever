/**
 * Configuration Module
 * Centralizes all application configuration and constants
 */

/**
 * Application configuration module
 *
 * Core configuration (API URLs, map defaults) is injected by Flask template
 * from Python config (single source of truth in .env file).
 *
 * This module only adds client-side-only configuration that doesn't need
 * to be synchronized with the backend.
 */

// Ensure AppConfig exists (should be set by template, but provide fallback)
if (typeof window.AppConfig === 'undefined') {
    // AppConfig not found - using fallback (debug.warn used if available)
    if (typeof console !== 'undefined') {
        console.warn('AppConfig not injected by template, using fallback defaults');
    }
    window.AppConfig = {
        API_BASE_URL: '/api',
        WMS_BASE_URL: 'https://ows.emodnet-seabedhabitats.eu/geoserver/emodnet_view/wms',
        HELCOM_WMS_BASE_URL: 'https://maps.helcom.fi/arcgis/services/MADS/Pressures/MapServer/WMSServer',
        DEBUG: false,
        defaultView: { lat: 54.0, lng: 10.0, zoom: 4 }
    };
}

// Add client-side-only configuration (not needed in Python)
Object.assign(window.AppConfig, {
    // Default layer settings (client-side UI preferences)
    defaultLayer: 'eusm_2023_eunis2019_full',
    defaultOpacity: 0.7,

    // Map UI configuration (client-side only)
    zoomControl: false  // Leaflet zoom control (we use custom controls)
});

// Base map definitions - injected from Python config (single source of truth)
// Transform Python format to Leaflet-compatible format
window.BaseMaps = {};

if (window.AppConfig.basemapConfigs) {
    // Convert Python basemap config to Leaflet format
    for (const [key, config] of Object.entries(window.AppConfig.basemapConfigs)) {
        window.BaseMaps[key] = {
            url: config.url,
            options: {
                attribution: config.attribution,
                ...(config.minZoom !== undefined && { minZoom: config.minZoom }),
                ...(config.maxZoom !== undefined && { maxZoom: config.maxZoom })
            }
        };
    }
    debug.log(`✅ Loaded ${Object.keys(window.BaseMaps).length} basemaps from Python config`);
} else {
    // Fallback basemaps if injection failed (should never happen in production)
    debug.warn('⚠️ Basemap config not injected, using fallback definitions');
    window.BaseMaps = {
        'emodnet_bathymetry': {
            url: 'https://tiles.emodnet-bathymetry.eu/latest/mean_atlas_land/web_mercator/{z}/{x}/{y}.png',
            options: {
                attribution: '© EMODnet Bathymetry | Marine data from European seas',
                minZoom: 0,
                maxZoom: 18
            }
        },
        'satellite': {
            url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
            options: {
                attribution: '© Esri'
            }
        }
    };
    // Fallback default
    window.AppConfig.defaultBaseMap = 'satellite';
}
