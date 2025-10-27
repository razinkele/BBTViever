"""
Version information for emodnet-viewer package.

This module provides a single source of truth for version information
used throughout the application (health checks, logs, documentation).

Attributes:
    __version__ (str): Current version string (semantic versioning)
    __version_info__ (tuple): Version as tuple for programmatic comparison
    __version_date__ (str): Release date in ISO format (YYYY-MM-DD)
    __version_name__ (str): Friendly release name
"""

__version__ = "1.2.12"
__version_info__ = (1, 2, 12)
__version_date__ = "2025-10-27"
__version_name__ = "Framework Updates + Code Quality Improvements"


def get_version_string() -> str:
    """
    Get formatted version string for display.

    Returns:
        str: Formatted version string (e.g., "1.2.2 (2025-10-13)")
    """
    return f"{__version__} ({__version_date__})"


def get_version_dict() -> dict:
    """
    Get version information as dictionary for API responses.

    Returns:
        dict: Dictionary with version, date, and name
    """
    return {
        "version": __version__,
        "version_date": __version_date__,
        "version_name": __version_name__,
        "version_tuple": __version_info__
    }
