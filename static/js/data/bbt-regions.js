/**
 * BBT (Biodiversity and Ecosystem Functioning) Region Information Database
 *
 * This module provides detailed information about all 12 BBT study areas
 * across European marine regions. Data is shared between layer-manager.js
 * and bbt-tool.js to maintain consistency and reduce duplication.
 *
 * @module BBTRegionData
 * @version 1.2.6
 * @description Comprehensive metadata for MARBEFES BBT areas
 *
 * Each region contains:
 * - region: Geographic region/sea area
 * - description: Research context and ecosystem type
 * - habitat: Characteristic habitat types
 * - research_focus: Primary research objectives
 *
 * Usage:
 *   const regionInfo = window.BBTRegionData['Archipelago'];
 *   console.log(regionInfo.region); // "Baltic Sea"
 */

(function(window) {
    'use strict';

    /**
     * BBT Region Information Database
     * 12 study areas across European seas (including Porsangerfjord added in v1.2.6)
     */
    window.BBTRegionData = {
        'Archipelago': {
            region: 'Baltic Sea',
            description: 'Marine ecosystem functioning in the Swedish archipelago region',
            habitat: 'Coastal archipelago with complex habitat mosaic',
            research_focus: 'Benthic-pelagic coupling in coastal zones'
        },
        'Balearic': {
            region: 'Mediterranean Sea',
            description: 'Subtropical Mediterranean marine biodiversity hotspot',
            habitat: 'Mediterranean endemic species and Posidonia meadows',
            research_focus: 'Climate change impacts on Mediterranean ecosystems'
        },
        'Bay of Gdansk': {
            region: 'Baltic Sea',
            description: 'Semi-enclosed bay ecosystem with riverine influence',
            habitat: 'Brackish water transitional zone',
            research_focus: 'Land-sea connectivity and nutrient cycling'
        },
        'Gulf of Biscay': {
            region: 'Atlantic Ocean',
            description: 'Continental shelf ecosystem with upwelling dynamics',
            habitat: 'Deep-water Atlantic marine communities',
            research_focus: 'Ocean-shelf biodiversity gradients'
        },
        'Heraklion': {
            region: 'Mediterranean Sea',
            description: 'Eastern Mediterranean oligotrophic ecosystem',
            habitat: 'Deep Mediterranean basinal communities',
            research_focus: 'Deep-sea connectivity and endemic biodiversity'
        },
        'Hornsund': {
            region: 'Arctic Ocean',
            description: 'High Arctic fjord system with glacial influence',
            habitat: 'Arctic marine communities under climate change',
            research_focus: 'Arctic ecosystem resilience and tipping points'
        },
        'Kongsfjord': {
            region: 'Arctic Ocean',
            description: 'Arctic-Atlantic transition zone in Svalbard',
            habitat: 'Arctic-boreal species transition zone',
            research_focus: 'Climate-driven Arctic "atlantification"'
        },
        'Lithuanian coastal zone': {
            region: 'Baltic Sea',
            description: 'Shallow coastal ecosystem with freshwater inputs',
            habitat: 'Sandy coastal waters with estuarine influence',
            research_focus: 'Coastal zone management and eutrophication'
        },
        'North Sea': {
            region: 'North Sea',
            description: 'Productive temperate shelf ecosystem',
            habitat: 'Continental shelf with diverse benthic communities',
            research_focus: 'Anthropogenic impacts and ecosystem services'
        },
        'Irish Sea': {
            region: 'Irish Sea',
            description: 'Semi-enclosed temperate marine ecosystem',
            habitat: 'Coastal and shelf habitats with tidal dynamics',
            research_focus: 'Marine spatial planning and biodiversity conservation'
        },
        'Porsangerfjord': {
            region: 'Arctic Ocean',
            description: 'Arctic fjord system in northern Norway',
            habitat: 'Subarctic coastal communities with tidal influence',
            research_focus: 'Arctic ecosystem dynamics and fisheries interactions'
        },
        'Sardinia': {
            region: 'Mediterranean Sea',
            description: 'Western Mediterranean island ecosystem',
            habitat: 'Mediterranean shelf communities and canyons',
            research_focus: 'Island biogeography and connectivity'
        }
    };

    /**
     * Helper function to get region info by name
     * @param {string} regionName - Name of the BBT region
     * @returns {object|null} Region information object or null if not found
     */
    window.getBBTRegionInfo = function(regionName) {
        return window.BBTRegionData[regionName] || null;
    };

    /**
     * Helper function to get all region names
     * @returns {string[]} Array of all BBT region names
     */
    window.getAllBBTRegionNames = function() {
        return Object.keys(window.BBTRegionData);
    };

    /**
     * Helper function to get regions by sea area
     * @param {string} seaArea - Sea area name (e.g., 'Baltic Sea', 'Mediterranean Sea')
     * @returns {object[]} Array of regions in that sea area
     */
    window.getBBTRegionsBySeaArea = function(seaArea) {
        return Object.entries(window.BBTRegionData)
            .filter(([name, info]) => info.region === seaArea)
            .map(([name, info]) => ({ name, ...info }));
    };

    // Log initialization in debug mode
    if (window.debug && window.debug.isEnabled()) {
        debug.log('📚 BBT Region Data loaded:', Object.keys(window.BBTRegionData).length, 'regions');
    }

})(window);
