# Changelog

All notable changes to the EMODnet Viewer project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-09-17

### Security
- Updated Flask from 2.3.3 to 3.1.2 to address 2024 CVE vulnerabilities
- Updated requests from 2.31.0 to 2.32.3 for security patches
- Added explicit Werkzeug dependency (3.1.0+) for enhanced security
- Verified no Flask-CORS vulnerabilities (CVE-2024-6221) as package not used

### Added
- Enhanced vector layer support with GeoPandas 1.1.1
- Improved development tooling with updated dependencies
- Better Python version support (3.9-3.12)
- Comprehensive dependency security audit

### Changed
- **BREAKING**: Minimum Python version raised from 3.8 to 3.9
- Updated GeoPandas from 0.14.0 to 1.1.1 (major version upgrade)
- Updated Fiona from 1.9.5 to 1.10.1 for better compatibility
- Updated pyproj from 3.6.1 to 3.7.1 for latest geospatial features
- Updated testing framework: pytest 7.4.2 → 8.4.2
- Updated code quality tools:
  - Black: 23.7.0 → 25.1.0
  - Flake8: 6.0.0 → 7.3.0
  - isort: 5.12.0 → 6.0.1
  - mypy: Added 1.18.1

### Improved
- Enhanced documentation with security update information
- Better development environment setup instructions
- Updated project metadata and classifiers
- Improved dependency management and organization

### Development
- Separated production and development dependencies more clearly
- Updated pre-commit hooks and development tools
- Enhanced testing configuration with better coverage
- Updated documentation tools: Sphinx 7.1.2 → 8.1.3

## [1.0.0] - 2024-09-14

### Added
- Initial stable release of EMODnet Viewer
- Flask-based web application for EMODnet WMS layer visualization
- Vector layer support with GPKG file processing
- Interactive map interface with Leaflet
- Real-time hover tooltips and area calculations
- Comprehensive API endpoints for WMS and vector data
- Development tools and testing framework

### Features
- Single-file Flask application architecture
- EMODnet WMS integration with multiple marine habitat layers
- Responsive web interface with layer selection
- Geospatial data processing with GeoPandas
- GPKG file support for local vector data
- Development server and monitoring tools