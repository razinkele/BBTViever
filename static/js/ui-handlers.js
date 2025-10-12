/**
 * UI Handlers Module
 * Manages all user interface event handlers and interactions
 */

window.UIHandlers = (function() {
    'use strict';

    // Private variables
    let initialized = false;

    /**
     * Initialize all UI event handlers
     */
    function init() {
        if (initialized) {
            console.warn('UIHandlers already initialized');
            return;
        }

        setupLayerSelectHandlers();
        setupBaseMapSwitcher();
        setupOpacityControl();
        setupThemeHandlers();
        setupKeyboardHandlers();
        setupPopupHandlers();

        initialized = true;
        console.log('✅ UI Handlers initialized');
    }

    /**
     * Setup layer selection dropdown handlers
     */
    function setupLayerSelectHandlers() {
        const layerSelect = document.getElementById('layer-select');
        const helcomSelect = document.getElementById('helcom-select');

        if (layerSelect) {
            // WMS overlay layer select handler
            layerSelect.onchange = function(e) {
                const selectedValue = e.target.value;
                const statusTooltip = document.getElementById('emodnet-status-tooltip');

                if (selectedValue === 'none') {
                    // Remove WMS overlay
                    window.LayerManager.clearLayers('wms');
                    const legendContainer = document.getElementById('legend-container');
                    if (legendContainer) legendContainer.style.display = 'none';

                    // Update tooltip
                    if (statusTooltip) {
                        statusTooltip.textContent = 'No overlay';
                        statusTooltip.style.color = '#666';
                    }
                } else if (selectedValue.startsWith('wms:')) {
                    const layerName = selectedValue.substring(4);

                    // Update tooltip with layer name
                    if (statusTooltip) {
                        const selectedOption = e.target.options[e.target.selectedIndex];
                        const layerTitle = selectedOption ? selectedOption.textContent : layerName;
                        statusTooltip.textContent = layerTitle;
                        statusTooltip.style.color = '#20B2AA';
                        statusTooltip.title = layerTitle;
                    }

                    window.LayerManager.selectWMSLayerAsOverlay(layerName);
                }
            };
        }

        if (helcomSelect) {
            // HELCOM layer select handler
            helcomSelect.onchange = function(e) {
                const selectedValue = e.target.value;
                const statusTooltip = document.getElementById('helcom-status-tooltip');

                if (selectedValue === 'none') {
                    // Remove HELCOM overlay
                    window.LayerManager.clearLayers('helcom');

                    // Update tooltip
                    if (statusTooltip) {
                        statusTooltip.textContent = 'No overlay';
                        statusTooltip.style.color = '#666';
                    }
                } else if (selectedValue.startsWith('helcom:')) {
                    const layerName = selectedValue.substring(7);

                    // Update tooltip with layer name
                    if (statusTooltip) {
                        const selectedOption = e.target.options[e.target.selectedIndex];
                        const layerTitle = selectedOption ? selectedOption.textContent : layerName;
                        statusTooltip.textContent = layerTitle;
                        statusTooltip.style.color = '#20B2AA';
                        statusTooltip.title = layerTitle;
                    }

                    window.LayerManager.selectHELCOMLayerAsOverlay(layerName);
                }
            };
        }
    }

    /**
     * Setup base map switcher
     */
    function setupBaseMapSwitcher() {
        const basemapBtns = document.querySelectorAll('.basemap-btn');

        basemapBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const basemapType = this.getAttribute('data-basemap');

                // Update active state
                basemapBtns.forEach(b => b.classList.remove('active'));
                this.classList.add('active');

                // Switch base map
                window.MapInit.switchBaseMap(basemapType);

                console.log('🗺️ Switched to base map:', basemapType);
            });
        });
    }

    /**
     * Setup opacity slider control
     */
    function setupOpacityControl() {
        const opacitySlider = document.getElementById('opacity');
        const opacityValue = document.getElementById('opacity-value');

        if (opacitySlider && opacityValue) {
            opacitySlider.oninput = function() {
                const opacity = parseFloat(this.value);
                opacityValue.textContent = Math.round(opacity * 100) + '%';
                window.LayerManager.setOpacity(opacity);
            };
        }
    }

    /**
     * Setup theme switching handlers
     */
    function setupThemeHandlers() {
        const themeSelect = document.getElementById('theme');

        if (themeSelect) {
            themeSelect.onchange = function(e) {
                changeTheme(e.target.value);
            };
        }

        // Initialize theme from localStorage
        initializeTheme();
    }

    /**
     * Change application theme
     */
    function changeTheme(themeName) {
        console.log('🎨 Changing theme to:', themeName);
        document.body.setAttribute('data-theme', themeName);

        // Save theme preference to localStorage
        localStorage.setItem('selected-theme', themeName);

        // Update status to show theme changed
        const statusEl = document.getElementById('status');
        if (statusEl) {
            const currentStatus = statusEl.textContent;
            statusEl.textContent = `Theme changed to ${themeName.charAt(0).toUpperCase() + themeName.slice(1)}`;
            statusEl.className = 'status';

            // Restore original status after 2 seconds
            setTimeout(() => {
                statusEl.textContent = currentStatus;
            }, 2000);
        }
    }

    /**
     * Initialize theme from localStorage
     */
    function initializeTheme() {
        const savedTheme = localStorage.getItem('selected-theme') || 'ocean';
        document.body.setAttribute('data-theme', savedTheme);

        // Update the select element to match
        const themeSelect = document.getElementById('theme');
        if (themeSelect) {
            themeSelect.value = savedTheme;
        }

        console.log('🎨 Theme initialized:', savedTheme);
    }

    /**
     * Setup keyboard event handlers
     */
    function setupKeyboardHandlers() {
        document.addEventListener('keydown', function(e) {
            // ESC key closes popups
            if (e.key === 'Escape') {
                if (window.BBTTool && typeof window.BBTTool.closeBBTDataPopup === 'function') {
                    window.BBTTool.closeBBTDataPopup();
                }
            }
        });
    }

    /**
     * Setup popup overlay handlers
     */
    function setupPopupHandlers() {
        const popupOverlay = document.getElementById('bbt-popup-overlay');

        if (popupOverlay) {
            // Close popup when clicking overlay background
            popupOverlay.addEventListener('click', function(e) {
                if (e.target === popupOverlay) {
                    if (window.BBTTool && typeof window.BBTTool.closeBBTDataPopup === 'function') {
                        window.BBTTool.closeBBTDataPopup();
                    }
                }
            });
        }
    }

    /**
     * Toggle panel visibility
     */
    function togglePanel(panelId) {
        const panel = document.getElementById(panelId);
        if (panel) {
            const isVisible = panel.style.display !== 'none';
            panel.style.display = isVisible ? 'none' : 'block';
            return !isVisible;
        }
        return false;
    }

    /**
     * Show/hide loading indicator
     */
    function setLoading(isLoading, message = 'Loading...') {
        const statusEl = document.getElementById('status');
        if (statusEl) {
            if (isLoading) {
                statusEl.textContent = message;
                statusEl.className = 'status loading';
            } else {
                statusEl.textContent = 'Ready';
                statusEl.className = 'status';
            }
        }
    }

    /**
     * Display error message
     */
    function showError(message) {
        const statusEl = document.getElementById('status');
        if (statusEl) {
            statusEl.textContent = message;
            statusEl.className = 'status error';
        }
        console.error(message);
    }

    /**
     * Display success message
     */
    function showSuccess(message, duration = 3000) {
        const statusEl = document.getElementById('status');
        if (statusEl) {
            const currentStatus = statusEl.textContent;
            statusEl.textContent = message;
            statusEl.className = 'status';

            if (duration > 0) {
                setTimeout(() => {
                    statusEl.textContent = currentStatus;
                }, duration);
            }
        }
    }

    /**
     * Toggle Advanced Controls Panel
     */
    function toggleAdvancedPanel() {
        const panel = document.getElementById('advanced-panel');
        const icon = document.getElementById('advanced-toggle-icon');

        if (!panel || !icon) {
            console.error('Advanced panel or icon not found');
            return;
        }

        if (panel.style.display === 'none' || panel.style.display === '') {
            panel.style.display = 'block';
            icon.textContent = '▼';
            console.log('Advanced panel opened');
        } else {
            panel.style.display = 'none';
            icon.textContent = '▶';
            console.log('Advanced panel closed');
        }
    }

    // Public API
    return {
        init,
        changeTheme,
        togglePanel,
        toggleAdvancedPanel,
        setLoading,
        showError,
        showSuccess
    };
})();

// Export toggleAdvancedPanel globally for onclick handlers
window.toggleAdvancedPanel = function() {
    window.UIHandlers.toggleAdvancedPanel();
};
