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
    console.warn('AppConfig not injected by template, using fallback defaults');
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

// Base map definitions
window.BaseMaps = {
    'emodnet_bathymetry': {
        url: 'https://tiles.emodnet-bathymetry.eu/latest/mean_atlas_land/web_mercator/{z}/{x}/{y}.png',
        options: {
            attribution: '© EMODnet Bathymetry | Marine data from European seas',
            minZoom: 0,
            maxZoom: 18
        }
    },
    'osm': {
        url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        options: {
            attribution: '© OpenStreetMap contributors'
        }
    },
    'satellite': {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        options: {
            attribution: '© Esri'
        }
    },
    'ocean': {
        url: 'https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}',
        options: {
            attribution: '© Esri'
        }
    },
    'light': {
        url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        options: {
            attribution: '© CartoDB'
        }
    }
};

// Default base map
window.AppConfig.defaultBaseMap = 'satellite';
