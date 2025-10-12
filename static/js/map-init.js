/**
 * Map Initialization Module
 * Handles Leaflet map creation and base map management
 */

window.MapInit = (function() {
    'use strict';

    let map = null;
    let baseMaps = {};
    let currentBaseMap = null;
    let layerControl = null;

    /**
     * Initialize the Leaflet map
     */
    function initMap() {
        // Create map instance
        map = L.map('map', {
            zoomControl: window.AppConfig.zoomControl
        }).setView(
            [window.AppConfig.defaultView.lat, window.AppConfig.defaultView.lng],
            window.AppConfig.defaultView.zoom
        );

        // Initialize base maps
        initBaseMaps();

        // Add default base map
        const defaultKey = window.AppConfig.defaultBaseMap;
        currentBaseMap = baseMaps[defaultKey];
        currentBaseMap.addTo(map);

        // Initialize native Leaflet layer control
        initLayerControl();

        // Add scale bar to map (metric units)
        L.control.scale({
            position: 'bottomleft',
            maxWidth: 200,
            metric: true,
            imperial: false,
            updateWhenIdle: false
        }).addTo(map);
        
        console.log('✅ Scale bar added to map');

        return map;
    }

    /**
     * Initialize native Leaflet layer control widget
     */
    function initLayerControl() {
        // Create base maps object with friendly names
        const baseMapLayers = {
            '🛰️ Satellite': baseMaps['satellite'],
            '🌊 EMODnet Bathymetry': baseMaps['emodnet_bathymetry'],
            '🗺️ OpenStreetMap': baseMaps['osm'],
            '🌐 Ocean Base': baseMaps['ocean'],
            '💡 Light Map': baseMaps['light']
        };

        // Create layer control with base maps
        // Overlays will be added dynamically as layers are loaded
        layerControl = L.control.layers(baseMapLayers, null, {
            position: 'topright',
            collapsed: true,  // Collapsed by default for cleaner UI
            autoZIndex: true
        }).addTo(map);

        console.log('✅ Native Leaflet layer control initialized (collapsed by default)');
    }

    /**
     * Initialize all base map layers
     */
    function initBaseMaps() {
        Object.keys(window.BaseMaps).forEach(key => {
            const config = window.BaseMaps[key];
            baseMaps[key] = L.tileLayer(config.url, config.options);
        });
    }

    /**
     * Switch between base maps
     */
    function switchBaseMap(mapKey) {
        if (!baseMaps[mapKey]) {
            console.error('Base map not found:', mapKey);
            return;
        }

        // Remove current base map
        if (currentBaseMap) {
            map.removeLayer(currentBaseMap);
        }

        // Add new base map
        currentBaseMap = baseMaps[mapKey];
        currentBaseMap.addTo(map);
    }

    /**
     * Get the map instance
     */
    function getMap() {
        return map;
    }

    /**
     * Get all base maps
     */
    function getBaseMaps() {
        return baseMaps;
    }

    /**
     * Get the layer control instance
     */
    function getLayerControl() {
        return layerControl;
    }

    /**
     * Add overlay layer to the control
     */
    function addOverlayToControl(layer, name) {
        if (layerControl && layer) {
            layerControl.addOverlay(layer, name);
            console.log(`Added overlay to control: ${name}`);
        }
    }

    /**
     * Remove overlay layer from the control
     */
    function removeOverlayFromControl(layer) {
        if (layerControl && layer) {
            layerControl.removeLayer(layer);
        }
    }

    // Public API
    return {
        initMap,
        switchBaseMap,
        getMap,
        getBaseMaps,
        getLayerControl,
        addOverlayToControl,
        removeOverlayFromControl
    };
})();
