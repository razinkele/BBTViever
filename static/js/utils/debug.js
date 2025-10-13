/**
 * Conditional Debug Logging Utility
 *
 * Provides environment-aware logging that only outputs in development mode.
 * This prevents console clutter in production and improves performance.
 *
 * Usage:
 *   debug.log('Message');           // Only in development
 *   debug.warn('Warning');          // Only in development
 *   debug.error('Error');           // Always shown (critical errors)
 *   debug.info('User message');     // Always shown (user-facing info)
 *
 * @module debug
 * @requires window.AppConfig.DEBUG
 */

(function(window) {
    'use strict';

    /**
     * Check if debug mode is enabled
     * @returns {boolean} True if in development/debug mode
     */
    function isDebugMode() {
        return window.AppConfig && window.AppConfig.DEBUG === true;
    }

    /**
     * Conditional Debug Logger
     * Provides environment-aware console logging
     */
    const debug = {
        /**
         * Log debug information (development only)
         * @param {...any} args - Arguments to log
         */
        log: function(...args) {
            if (isDebugMode()) {
                console.log(...args);
            }
        },

        /**
         * Log warning messages (development only)
         * @param {...any} args - Arguments to log
         */
        warn: function(...args) {
            if (isDebugMode()) {
                console.warn(...args);
            }
        },

        /**
         * Log error messages (always shown, even in production)
         * Critical errors should always be visible for debugging production issues
         * @param {...any} args - Arguments to log
         */
        error: function(...args) {
            console.error(...args);
        },

        /**
         * Log informational messages (always shown)
         * Use for user-facing information that should be visible in production
         * @param {...any} args - Arguments to log
         */
        info: function(...args) {
            console.info(...args);
        },

        /**
         * Log table data (development only)
         * @param {any} data - Tabular data to display
         */
        table: function(data) {
            if (isDebugMode()) {
                console.table(data);
            }
        },

        /**
         * Group console messages (development only)
         * @param {string} label - Group label
         */
        group: function(label) {
            if (isDebugMode()) {
                console.group(label);
            }
        },

        /**
         * End console group (development only)
         */
        groupEnd: function() {
            if (isDebugMode()) {
                console.groupEnd();
            }
        },

        /**
         * Time operation (development only)
         * @param {string} label - Timer label
         */
        time: function(label) {
            if (isDebugMode()) {
                console.time(label);
            }
        },

        /**
         * End time operation (development only)
         * @param {string} label - Timer label
         */
        timeEnd: function(label) {
            if (isDebugMode()) {
                console.timeEnd(label);
            }
        },

        /**
         * Check if debug mode is currently enabled
         * @returns {boolean} True if in debug mode
         */
        isEnabled: function() {
            return isDebugMode();
        }
    };

    // Export to global namespace
    window.debug = debug;

    // Log initialization (only in debug mode)
    if (isDebugMode()) {
        console.log('%c🔧 Debug Mode Enabled', 'color: #ff9800; font-weight: bold;');
        console.log('Use debug.log(), debug.warn(), debug.error() for conditional logging');
    }

})(window);
