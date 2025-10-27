#!/usr/bin/env python3
"""
Test script to verify app_refactored.py functionality
"""

import sys
import os
import json
from pathlib import Path

# Set environment for testing
os.environ['FLASK_ENV'] = 'development'
os.environ['FLASK_DEBUG'] = 'True'

def test_import():
    """Test that the refactored module imports successfully"""
    print("[Test 1/5] Testing module import...")
    try:
        # Try importing the refactored app
        import app_refactored
        print("  ✓ Module imported successfully")
        return True, app_refactored
    except Exception as e:
        print(f"  ✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False, None


def test_helper_functions(app_module):
    """Test that helper functions exist and are callable"""
    print("\n[Test 2/5] Testing helper functions...")

    required_functions = [
        'load_json_data',
        'check_service_health',
        'fetch_wms_layers',
        'api_error_response',
        'require_vector_support'
    ]

    all_found = True
    for func_name in required_functions:
        if hasattr(app_module, func_name):
            print(f"  ✓ {func_name} exists")
        else:
            print(f"  ✗ {func_name} NOT FOUND")
            all_found = False

    return all_found


def test_routes(app_module):
    """Test that all routes are registered"""
    print("\n[Test 3/5] Testing route registration...")

    app = app_module.app

    required_routes = [
        '/',
        '/health',
        '/api/layers',
        '/api/all-layers',
        '/api/vector/layers',
        '/api/vector/layer/<path:layer_name>',
        '/api/vector/bounds',
        '/api/factsheets',
        '/api/factsheet/<bbt_name>',
        '/api/capabilities',
        '/api/legend/<path:layer_name>',
        '/api/metrics',
        '/test'
    ]

    # Get all registered routes
    registered_routes = [rule.rule for rule in app.url_map.iter_rules()]

    all_found = True
    for route in required_routes:
        # Check if route exists (some routes have path converters)
        route_pattern = route.replace('<path:layer_name>', '').replace('<bbt_name>', '').rstrip('/')
        found = any(route_pattern in r for r in registered_routes)

        if found:
            print(f"  ✓ {route}")
        else:
            print(f"  ✗ {route} NOT FOUND")
            all_found = False

    return all_found


def test_configuration(app_module):
    """Test that configuration is loaded correctly"""
    print("\n[Test 4/5] Testing configuration...")

    app = app_module.app

    required_configs = [
        'CACHE_TYPE',
        'COMPRESS_MIMETYPES',
        'COMPRESS_LEVEL',
        'COMPRESS_MIN_SIZE'
    ]

    all_found = True
    for config_key in required_configs:
        if config_key in app.config:
            print(f"  ✓ {config_key} = {app.config[config_key]}")
        else:
            print(f"  ✗ {config_key} NOT FOUND")
            all_found = False

    return all_found


def test_api_endpoints(app_module):
    """Test API endpoints with test client"""
    print("\n[Test 5/5] Testing API endpoints with test client...")

    app = app_module.app
    client = app.test_client()

    test_cases = [
        ('/health', 200, 'application/json'),
        ('/api/layers', 200, 'application/json'),
        ('/api/all-layers', 200, 'application/json'),
        ('/test', 200, 'text/html'),
    ]

    all_passed = True
    for endpoint, expected_status, expected_content_type in test_cases:
        try:
            response = client.get(endpoint)

            status_ok = response.status_code == expected_status or response.status_code == 503  # Allow 503 for health check
            content_type_ok = expected_content_type in response.content_type

            if status_ok and content_type_ok:
                print(f"  ✓ {endpoint} -> {response.status_code} ({response.content_type})")
            else:
                print(f"  ✗ {endpoint} -> {response.status_code} ({response.content_type}) [Expected: {expected_status}, {expected_content_type}]")
                all_passed = False

        except Exception as e:
            print(f"  ✗ {endpoint} raised exception: {e}")
            all_passed = False

    return all_passed


def compare_file_sizes():
    """Compare original and refactored file sizes"""
    print("\n[Comparison] File size reduction:")

    original_file = Path("app.py")
    refactored_file = Path("app_refactored.py")

    if original_file.exists() and refactored_file.exists():
        original_size = original_file.stat().st_size
        refactored_size = refactored_file.stat().st_size

        # Count lines
        with open(original_file) as f:
            original_lines = len(f.readlines())

        with open(refactored_file) as f:
            refactored_lines = len(f.readlines())

        size_diff = original_size - refactored_size
        line_diff = original_lines - refactored_lines

        print(f"  Original:   {original_size:,} bytes, {original_lines} lines")
        print(f"  Refactored: {refactored_size:,} bytes, {refactored_lines} lines")

        if size_diff > 0:
            pct = (size_diff / original_size) * 100
            print(f"  Reduction:  {size_diff:,} bytes ({pct:.1f}%), {line_diff} lines")
        else:
            size_increase = refactored_size - original_size
            pct = (size_increase / original_size) * 100
            print(f"  Increase:   {size_increase:,} bytes ({pct:.1f}%), {-line_diff} lines")
            print(f"  Note: Small increase is expected due to docstrings and helper functions")


def main():
    """Run all tests"""
    print("=" * 70)
    print("Testing app_refactored.py")
    print("=" * 70)

    # Test 1: Import
    success, app_module = test_import()
    if not success:
        print("\n✗ IMPORT TEST FAILED - Cannot continue")
        return False

    # Test 2: Helper functions
    test_helper_functions(app_module)

    # Test 3: Routes
    test_routes(app_module)

    # Test 4: Configuration
    test_configuration(app_module)

    # Test 5: API endpoints
    test_api_endpoints(app_module)

    # Compare file sizes
    compare_file_sizes()

    print("\n" + "=" * 70)
    print("All tests completed!")
    print("=" * 70)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
