/**
 * MARBEFES Project Datasets Database
 *
 * This module contains comprehensive information about all 25 datasets from the MARBEFES project
 * (Marine Biodiversity and Ecosystem Functioning across European Seas).
 * Each BBT region is mapped to its relevant datasets with links to VLIZ IMIS repository.
 *
 * @module MARBEFESDatasets
 * @version 1.2.4
 * @description Dataset metadata for all 11 BBT regions from VLIZ repository
 *
 * Data source: https://www.vliz.be/en/imis?module=project&proid=5393
 *
 * Usage:
 *   const datasets = window.MARBEFESDatasets['Heraklion'];
 *   console.log(datasets.length); // Number of datasets for Heraklion
 */

(function(window) {
    'use strict';

    /**
     * MARBEFES Datasets by BBT Region
     * Each dataset includes: id, title, link, description, and category
     */
    window.MARBEFESDatasets = {
        'Archipelago': [
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ],

        'Balearic': [
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ],

        'Bay of Gdansk': [
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ],

        'Gulf of Biscay': [
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ],

        'Heraklion': [
            {
                id: '8604',
                title: 'Copepoda and Cladocera in the Gulf of Herakleion',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8604',
                description: 'Marine zooplankton community data (Copepoda, Cladocera) from Gulf of Herakleion, Crete (2014).',
                category: 'Biological',
                year: '2014'
            },
            {
                id: '8605',
                title: 'Molluscan macrofauna near waste water treatment plant',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8605',
                description: 'Molluscan assemblages near Heraklion waste water treatment plant - anthropogenic impact study (2015).',
                category: 'Biological',
                year: '2015'
            },
            {
                id: '8606',
                title: 'Macrobenthic fauna from continental shelf (2014-2015)',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8606',
                description: 'Comprehensive macrobenthic community survey from Heraklion Gulf continental shelf (2014-2015).',
                category: 'Biological',
                year: '2014-2015'
            },
            {
                id: '8607',
                title: 'Macrobenthic fauna from continental shelf (2010)',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8607',
                description: 'Baseline macrobenthic fauna survey from Heraklion Gulf continental shelf (2010).',
                category: 'Biological',
                year: '2010'
            },
            {
                id: '8608',
                title: 'Hyperbenthic macrofauna from continental shelf',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8608',
                description: 'Hyperbenthic (near-bottom) macrofauna assemblages from Heraklion Gulf continental shelf (2019).',
                category: 'Biological',
                year: '2019'
            },
            {
                id: '8610',
                title: 'Seaweeds from continental shelf',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8610',
                description: 'Marine macroalgae (seaweed) diversity and distribution from Heraklion Gulf shelf (2014-2015).',
                category: 'Biological',
                year: '2014-2015'
            },
            {
                id: '8611',
                title: 'Shallow Coastal Ichthyofauna in Gournes',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8611',
                description: 'Coastal fish fauna survey in shallow waters of Gournes, Crete (2023).',
                category: 'Biological',
                year: '2023'
            },
            {
                id: '8884',
                title: 'Sessile Benthic Assemblages - Photographic Quadrats',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8884',
                description: 'Long-term photographic monitoring of sessile benthic communities in Northern Crete (2008-2024).',
                category: 'Biological',
                year: '2008-2024'
            },
            {
                id: '8906',
                title: 'Bathymetric distribution and temporal trends of macrobenthic communities',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8906',
                description: 'Multi-year analysis of macrobenthic community depth distribution and temporal changes in Heraklion Bay.',
                category: 'Biological',
                year: 'Multi-year'
            },
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ],

        'Hornsund': [
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ],

        'Irish Sea': [
            {
                id: '8920',
                title: 'Blue Carbon Data from the Irish Sea',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8920',
                description: 'Marine carbon sequestration and blue carbon ecosystem data from Irish Sea (2023-2026).',
                category: 'Environmental',
                year: '2023-2026'
            },
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ],

        'Kongsfjord': [
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ],

        'Lithuanian coastal zone': [
            {
                id: '8887',
                title: 'Integrated Dataset: Hydrological, Meteorological & Visitor Metrics',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8887',
                description: 'Multi-parameter dataset including hydrology, meteorology, chlorophyll-a, and coastal tourism data for Klaipėda (2020-2023).',
                category: 'Environmental',
                year: '2020-2023'
            },
            {
                id: '8899',
                title: 'Travel Cost Analysis of Klaipėda Beach Visitors',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8899',
                description: 'Economic valuation survey of beach recreation and tourism at Klaipėda Beach (2024).',
                category: 'Socio-Economic',
                year: '2024'
            },
            {
                id: '8907',
                title: 'Environmental and recreational monitoring of Melnragė Beach',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8907',
                description: 'Water quality, chlorophyll, and human activity monitoring at Melnragė Beach (2024).',
                category: 'Environmental',
                year: '2024'
            },
            {
                id: '8919',
                title: 'Microplankton trait data from Curonian Lagoon',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8919',
                description: 'FlowCam analysis of microplankton functional traits in Lithuanian Curonian Lagoon (2024).',
                category: 'Biological',
                year: '2024'
            },
            {
                id: '89054',
                title: 'Zooplankton data of the Eastern Gotland Basin, Baltic Sea (2016, 2024) produced with ZooScan',
                link: 'https://marineinfo.org/doc/dataset/89054',
                description: 'ZooScan automated imaging analysis of zooplankton communities in Eastern Gotland Basin, Baltic Sea (2016, 2024).',
                category: 'Biological',
                year: '2016, 2024'
            },
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ],

        'North Sea': [
            {
                id: '8686',
                title: 'Ecological Value Assessment (EVA)',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8686',
                description: 'Comprehensive ecological valuation methodology for Belgian Coast marine ecosystems.',
                category: 'Socio-Economic',
                year: 'Ongoing'
            },
            {
                id: '8783',
                title: 'Socio-Cultural Valuation of Nature and Biodiversity at Belgian Coast',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8783',
                description: 'Social perception and cultural values of marine biodiversity along the Belgian coastal area.',
                category: 'Socio-Economic',
                year: 'Ongoing'
            },
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ],

        'Sardinia': [
            {
                id: '8915',
                title: 'Daily car parking and weather in Oristano',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8915',
                description: 'Coastal tourism intensity proxy through car parking occupancy and meteorological conditions (2022-2024).',
                category: 'Socio-Economic',
                year: '2022-2024'
            },
            {
                id: '8917',
                title: 'Macrozoobenthic assemblages in S\'Ena Arrubia Lagoon',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8917',
                description: 'Seasonal (winter/summer) macrozoobenthic community structure in coastal lagoon ecosystem (2021).',
                category: 'Biological',
                year: '2021'
            },
            {
                id: '8886',
                title: 'Social data from cultural ecosystem valuation',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8886',
                description: 'Questionnaire data on cultural ecosystem services across European case studies (Sep 2023 - Jun 2026).',
                category: 'Socio-Economic',
                year: '2023-2026'
            },
            {
                id: '8900',
                title: 'Stakeholder consultation results from MARBEFES BBT Areas',
                link: 'https://www.vliz.be/en/imis?module=dataset&dasid=8900',
                description: 'Ecological, economic, and socio-cultural consultation results across European marine areas (2023).',
                category: 'Socio-Economic',
                year: '2023'
            }
        ]
    };

    /**
     * Helper function to get datasets for a specific BBT region
     * @param {string} bbtName - Name of the BBT region
     * @returns {Array|null} Array of dataset objects or null if not found
     */
    window.getMARBEFESDatasets = function(bbtName) {
        return window.MARBEFESDatasets[bbtName] || null;
    };

    /**
     * Helper function to get dataset count for a BBT region
     * @param {string} bbtName - Name of the BBT region
     * @returns {number} Number of datasets available
     */
    window.getMARBEFESDatasetCount = function(bbtName) {
        const datasets = window.MARBEFESDatasets[bbtName];
        return datasets ? datasets.length : 0;
    };

    /**
     * Helper function to get all BBT regions with datasets
     * @returns {string[]} Array of BBT region names with available datasets
     */
    window.getBBTRegionsWithData = function() {
        return Object.keys(window.MARBEFESDatasets);
    };

    /**
     * Helper function to get category icon
     * @param {string} category - Dataset category
     * @returns {string} Emoji icon for category
     */
    window.getDatasetCategoryIcon = function(category) {
        const icons = {
            'Biological': '🔬',
            'Socio-Economic': '👥',
            'Environmental': '🌊'
        };
        return icons[category] || '📊';
    };

    // Log initialization in debug mode
    if (window.debug && window.debug.isEnabled()) {
        const totalDatasets = Object.values(window.MARBEFESDatasets)
            .reduce((sum, datasets) => sum + datasets.length, 0);
        const uniqueDatasets = new Set(
            Object.values(window.MARBEFESDatasets)
                .flat()
                .map(d => d.id)
        ).size;
        debug.log('📚 MARBEFES Datasets loaded:', totalDatasets, 'references to', uniqueDatasets, 'unique datasets across', Object.keys(window.MARBEFESDatasets).length, 'BBT regions');
    }

})(window);
