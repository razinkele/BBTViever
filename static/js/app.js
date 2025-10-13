/**
 * Main Application Orchestrator
 * Coordinates initialization of all modules and manages application lifecycle
 */

(function() {
    'use strict';

    // Application state
    let map = null;
    let vectorLayerGroup = null;
    let initializationComplete = false;

    /**
     * Main application initialization
     */
    async function initApp() {
        debug.log('🚀 MARBEFES BBT Database - Initializing application...');

        try {
            // 1. Initialize map
            debug.log('📍 Step 1: Initializing map...');
            map = window.MapInit.initMap();
            if (!map) {
                throw new Error('Failed to initialize map');
            }

            // 2. Create vector layer group
            vectorLayerGroup = L.layerGroup().addTo(map);
            debug.log('📊 Step 2: Vector layer group created');

            // 3. Initialize layer manager
            debug.log('🗺️ Step 3: Initializing layer manager...');
            window.LayerManager.init(map, vectorLayerGroup);

            // 4. Initialize UI handlers
            debug.log('🎛️ Step 4: Initializing UI handlers...');
            window.UIHandlers.init();

            // 5. Initialize BBT tool
            debug.log('🔍 Step 5: Initializing BBT navigation tool...');
            if (window.BBTTool && typeof window.BBTTool.initialize === 'function') {
                // BBT tool initializes itself with delay, just ensure it's available
                debug.log('✅ BBT Tool will initialize in background');
            } else {
                debug.warn('⚠️ BBT Tool not available');
            }

            // 6. Load initial layers
            debug.log('🌊 Step 6: Loading initial layers...');
            await loadInitialLayers();

            // 7. Setup layer dropdown options
            populateLayerDropdowns();

            // Mark initialization as complete
            initializationComplete = true;
            debug.log('✅ Application initialization complete!');

            // Update status
            window.UIHandlers.showSuccess('Application ready', 2000);

        } catch (error) {
            debug.error('❌ Application initialization failed:', error);
            window.UIHandlers.showError('Initialization failed: ' + error.message);
        }
    }

    /**
     * Load initial layers on startup
     */
    async function loadInitialLayers() {
        try {
            debug.log('🔄 Loading BBT vector layers...');
            debug.log('DEBUG: window.vectorLayers =', window.vectorLayers);

            // Get vector layers data from template
            if (window.vectorLayers && window.vectorLayers.length > 0) {
                debug.log('DEBUG: Found', window.vectorLayers.length, 'vector layers');
                debug.log('DEBUG: Available layers:', window.vectorLayers.map(l => l.display_name));

                // Load main BBT layer (try "Bbt" first, fallback to "Bbt - Merged" for backward compatibility)
                const mainLayer = window.vectorLayers.find(l => l.display_name === 'Bbt' || l.display_name === 'Bbt - Merged');
                debug.log('DEBUG: mainLayer =', mainLayer);

                if (mainLayer) {
                    debug.log('DEBUG: Calling loadVectorLayerFast with:', mainLayer.display_name);
                    await window.LayerManager.loadVectorLayerFast(mainLayer.display_name);
                    debug.log('✅ Main BBT layer loaded');
                } else {
                    debug.warn('⚠️ Could not find "Bbt" or "Bbt - Merged" layer');
                }

                // Preload other layers in background
                window.LayerManager.preloadLayersInBackground(window.vectorLayers);
            } else {
                debug.warn('⚠️ No vector layers available. window.vectorLayers =', window.vectorLayers);
            }

            // DO NOT load default EUNIS layer at startup
            // Layer will be loaded automatically when user zooms to a BBT
            debug.log('🗺️ EUNIS layer will load when zooming to BBT areas');

            // Enable automatic zoom-based layer switching
            window.LayerManager.enableAutoLayerSwitching(true);

        } catch (error) {
            debug.error('❌ Error loading initial layers:', error);
            debug.error('Stack trace:', error.stack);
            // Don't throw - app can still function
        }
    }

    /**
     * Populate layer selection dropdowns from template data
     */
    function populateLayerDropdowns() {
        const layerSelect = document.getElementById('layer-select');
        const helcomSelect = document.getElementById('helcom-select');

        // Populate WMS layers
        if (layerSelect && window.wmsLayers) {
            // Clear existing options except "None"
            layerSelect.innerHTML = '<option value="none">None (BBT only)</option>';

            // Add WMS layers
            window.wmsLayers.forEach(layer => {
                const option = document.createElement('option');
                option.value = 'wms:' + layer.name;
                option.textContent = layer.title || layer.name;
                layerSelect.appendChild(option);
            });

            debug.log(`📋 Populated ${window.wmsLayers.length} WMS layers`);

            // Update status tooltip
            const emodnetStatusTooltip = document.getElementById('emodnet-status-tooltip');
            if (emodnetStatusTooltip) {
                emodnetStatusTooltip.textContent = 'No overlay';
                emodnetStatusTooltip.style.color = '#666';
            }
        }

        // Populate HELCOM layers
        if (helcomSelect && window.helcomLayers) {
            // Clear existing options except "None"
            helcomSelect.innerHTML = '<option value="none">None</option>';

            // Add HELCOM layers
            window.helcomLayers.forEach(layer => {
                const option = document.createElement('option');
                option.value = 'helcom:' + layer.name;
                option.textContent = layer.title || layer.name;
                helcomSelect.appendChild(option);
            });

            debug.log(`📋 Populated ${window.helcomLayers.length} HELCOM layers`);

            // Update status tooltip
            const helcomStatusTooltip = document.getElementById('helcom-status-tooltip');
            if (helcomStatusTooltip) {
                helcomStatusTooltip.textContent = 'No overlay';
                helcomStatusTooltip.style.color = '#666';
            }
        }
    }

    /**
     * Get application state
     */
    function getState() {
        return {
            initialized: initializationComplete,
            map: map,
            vectorLayerGroup: vectorLayerGroup,
            currentLayer: window.LayerManager ? window.LayerManager.getCurrentLayer() : null,
            currentLayerType: window.LayerManager ? window.LayerManager.getCurrentLayerType() : null
        };
    }

    /**
     * Cleanup and reset application
     */
    function cleanup() {
        debug.log('🧹 Cleaning up application...');

        if (window.LayerManager) {
            window.LayerManager.clearLayers('all');
        }

        if (map) {
            map.remove();
            map = null;
        }

        vectorLayerGroup = null;
        initializationComplete = false;

        debug.log('✅ Cleanup complete');
    }

    // Export public API
    window.App = {
        init: initApp,
        getState: getState,
        cleanup: cleanup,
        version: '2.0.0'
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initApp);
    } else {
        // DOM already loaded
        initApp();
    }

    debug.log('📦 Main application module loaded (v2.0.0)');
})();
