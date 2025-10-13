/**
 * Bundle Entry Point for MARBEFES BBT Database
 * This file serves as the entry point for Rollup bundling
 *
 * Note: The individual JavaScript files use IIFE pattern with window exports.
 * This entry point simply ensures they are loaded in the correct dependency order.
 */

// Import order matches the template's script loading order:
// 1. Debug utility (must load first)
// 2. Shared data modules
// 3. Application modules (in dependency order)

import './utils/debug.js';
import './data/bbt-regions.js';
import './data/marbefes-datasets.js';
import './config.js';
import './map-init.js';
import './layer-manager.js';
import './bbt-tool.js';
import './ui-handlers.js';
import './app.js';

// Export module information
export const bundleInfo = {
    version: '1.2.4',
    modules: [
        'debug',
        'bbt-regions',
        'marbefes-datasets',
        'config',
        'map-init',
        'layer-manager',
        'bbt-tool',
        'ui-handlers',
        'app'
    ],
    buildDate: new Date().toISOString()
};

console.log('📦 MARBEFES BBT Bundle loaded (v1.2.4)');
