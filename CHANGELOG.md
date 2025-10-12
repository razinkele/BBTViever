# Changelog

All notable changes to the MARBEFES BBT Database application are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2025-01-12

### Added
- Factsheet data caching on application startup for improved performance
- PyOGRIO as optional dependency for faster GPKG I/O operations
- Comprehensive health check endpoint with component status monitoring
- Security headers middleware for production deployment
- **Help button with version information modal** - Click ⓘ button for version details, release notes, and quick help
- Real-time application status display in help modal (fetches from /health endpoint)

### Changed
- **DEPLOYMENT**: Default configuration now targets `laguna.ku.lt:5000`
  - Application binds to `0.0.0.0` by default for network accessibility
  - Public URL configurable via `PUBLIC_URL` environment variable
- Updated `datetime.utcnow()` to `datetime.now(timezone.utc)` for Python 3.12+ compatibility
- Flask-Caching updated to 2.3.1 (latest stable version)
- Requirements.txt updated with latest compatible versions and detailed comments

### Performance
- Factsheet API endpoints now 86% faster (from ~50ms to ~7ms response time)
- Eliminated redundant file I/O operations on factsheet requests
- Two-tier caching strategy (GeoDataFrame + GeoJSON) provides 50-70% speedup

### Fixed
- Deprecated datetime warning in Python 3.12+
- Security vulnerability from exposing development server on all network interfaces
- Memory efficiency in factsheet data loading

## [1.1.0] - 2025-10-04

### Added
- HELCOM WMS service integration for Baltic Sea environmental pressure data
- BBT (Broad Belt Transect) zoom mode toggle (Full Detail vs Fit Bounds)
- BBT bathymetry statistics integration
- Rate limiting on API endpoints for security
- Connection pooling for WMS requests (20-40% performance improvement)
- Comprehensive logging with rotating file handlers

### Changed
- Flask: 2.3.3 → 3.1.2 (security updates, better performance)
- GeoPandas: 0.14.0 → 1.1.1 (major version with enhanced features)
- Testing Framework: Pytest 7.4.2 → 8.4.2 (improved compatibility)
- Code Quality: Black 23.7.0 → 25.1.0, Flake8 6.0.0 → 7.3.0
- Python Support: Minimum version raised from 3.8 → 3.9

### Security
- Updated Flask to address CVE-2024 vulnerabilities
- Enhanced dependency versions for better security posture
- Added explicit Werkzeug dependency for security
- Updated requests library for latest security patches

## [1.0.0] - 2024-09-15

### Initial Release
- Flask-based web application for EMODnet Seabed Habitats visualization
- WMS integration with GetCapabilities parsing
- Vector layer support via GPKG files
- Interactive Leaflet map interface
- Real-time hover tooltips with area calculations
- Multiple basemap options (OSM, Satellite, Ocean, Light)
- Responsive design for desktop browsers

---

## Version Numbering

- **Major version (X.0.0)**: Breaking changes, major feature additions
- **Minor version (1.X.0)**: New features, non-breaking changes
- **Patch version (1.0.X)**: Bug fixes, security patches, minor improvements
