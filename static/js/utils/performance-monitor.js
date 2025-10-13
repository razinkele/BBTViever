/**
 * Performance Monitoring Utility
 * Collects client-side performance metrics and sends them to the backend
 *
 * P1 Optimization - Provides real-world performance data for optimization decisions
 */

(function() {
    'use strict';

    class PerformanceMonitor {
        constructor() {
            this.metrics = [];
            this.flushInterval = 10; // Flush after collecting 10 metrics
            this.apiEndpoint = '/api/metrics';
            this.enabled = true;

            // Initialize performance observer if available
            if (typeof PerformanceObserver !== 'undefined') {
                this.initializeObservers();
            } else {
                debug.warn('PerformanceObserver not available in this browser');
                this.enabled = false;
            }

            debug.log('📊 Performance monitoring initialized');
        }

        /**
         * Initialize performance observers for automatic tracking
         */
        initializeObservers() {
            try {
                // Observe navigation timing
                const navObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        this.recordNavigationTiming(entry);
                    }
                });
                navObserver.observe({ entryTypes: ['navigation'] });

                // Observe resource timing (scripts, stylesheets, images)
                const resourceObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (this.shouldTrackResource(entry)) {
                            this.recordResourceTiming(entry);
                        }
                    }
                });
                resourceObserver.observe({ entryTypes: ['resource'] });

                debug.log('📊 Performance observers registered');
            } catch (error) {
                debug.warn('Failed to initialize performance observers:', error);
                this.enabled = false;
            }
        }

        /**
         * Check if resource should be tracked
         */
        shouldTrackResource(entry) {
            // Only track our JavaScript files and GeoJSON API calls
            const url = entry.name;
            return (
                url.includes('/static/js/') ||
                url.includes('/api/vector/layer/') ||
                url.includes('/api/layers') ||
                url.includes('/api/factsheets')
            );
        }

        /**
         * Record navigation timing metrics
         */
        recordNavigationTiming(entry) {
            const timing = {
                type: 'navigation',
                dns_lookup: entry.domainLookupEnd - entry.domainLookupStart,
                tcp_connection: entry.connectEnd - entry.connectStart,
                request_time: entry.responseEnd - entry.requestStart,
                dom_load: entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
                page_load: entry.loadEventEnd - entry.loadEventStart,
                total_time: entry.loadEventEnd - entry.fetchStart,
                timestamp: Date.now()
            };

            debug.log('⏱️ Navigation timing:', timing);
            this.metrics.push(timing);
            this.checkFlush();
        }

        /**
         * Record resource timing metrics
         */
        recordResourceTiming(entry) {
            const timing = {
                type: 'resource',
                name: entry.name.split('/').pop(), // Just filename
                url: entry.name,
                duration: entry.duration,
                size: entry.transferSize || 0,
                cached: entry.transferSize === 0 && entry.decodedBodySize > 0,
                timestamp: Date.now()
            };

            // Only log significant resources (> 10ms)
            if (timing.duration > 10) {
                debug.log(`⏱️ Resource loaded: ${timing.name} (${timing.duration.toFixed(0)}ms, ${timing.cached ? 'cached' : 'network'})`);
            }

            this.metrics.push(timing);
            this.checkFlush();
        }

        /**
         * Manually record layer loading performance
         */
        recordLayerLoad(layerName, duration, cacheHit, featureCount = null) {
            const metric = {
                type: 'layer_load',
                name: layerName,
                duration: duration,
                cacheHit: cacheHit,
                featureCount: featureCount,
                timestamp: Date.now()
            };

            debug.log(`⏱️ Layer load: ${layerName} (${duration.toFixed(0)}ms, ${cacheHit ? 'cache hit' : 'network'})`);

            this.metrics.push(metric);
            this.checkFlush();
        }

        /**
         * Record WMS layer loading performance
         */
        recordWMSLoad(layerName, duration, success) {
            const metric = {
                type: 'wms_load',
                name: layerName,
                duration: duration,
                success: success,
                timestamp: Date.now()
            };

            debug.log(`⏱️ WMS load: ${layerName} (${duration.toFixed(0)}ms, ${success ? 'success' : 'failed'})`);

            this.metrics.push(metric);
            this.checkFlush();
        }

        /**
         * Record user interaction performance
         */
        recordInteraction(action, duration, details = {}) {
            const metric = {
                type: 'interaction',
                action: action,
                duration: duration,
                details: details,
                timestamp: Date.now()
            };

            if (duration > 100) {
                debug.warn(`⚠️ Slow interaction: ${action} took ${duration.toFixed(0)}ms`);
            }

            this.metrics.push(metric);
            this.checkFlush();
        }

        /**
         * Check if we should flush metrics to server
         */
        checkFlush() {
            if (this.metrics.length >= this.flushInterval) {
                this.flush();
            }
        }

        /**
         * Send metrics to server
         */
        flush() {
            if (!this.enabled || this.metrics.length === 0) {
                return;
            }

            const metricsToSend = [...this.metrics];
            this.metrics = []; // Clear immediately

            fetch(this.apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    metrics: metricsToSend,
                    userAgent: navigator.userAgent,
                    connection: this.getConnectionInfo()
                })
            }).then(response => {
                if (response.ok) {
                    debug.log(`📊 Sent ${metricsToSend.length} performance metrics to server`);
                } else {
                    debug.warn('Failed to send performance metrics:', response.status);
                }
            }).catch(error => {
                debug.warn('Error sending performance metrics:', error);
                // Don't retry - metrics are lost
            });
        }

        /**
         * Get network connection information
         */
        getConnectionInfo() {
            if (navigator.connection) {
                return {
                    effectiveType: navigator.connection.effectiveType,
                    downlink: navigator.connection.downlink,
                    rtt: navigator.connection.rtt,
                    saveData: navigator.connection.saveData
                };
            }
            return null;
        }

        /**
         * Force flush all pending metrics
         */
        flushNow() {
            this.flush();
        }

        /**
         * Get performance summary
         */
        getSummary() {
            const summary = {
                total_metrics: this.metrics.length,
                by_type: {}
            };

            for (const metric of this.metrics) {
                if (!summary.by_type[metric.type]) {
                    summary.by_type[metric.type] = 0;
                }
                summary.by_type[metric.type]++;
            }

            return summary;
        }
    }

    // Create global instance
    window.PerformanceMonitor = new PerformanceMonitor();

    // Flush metrics before page unload
    window.addEventListener('beforeunload', () => {
        window.PerformanceMonitor.flushNow();
    });

    debug.log('📦 Performance monitor module loaded');
})();
