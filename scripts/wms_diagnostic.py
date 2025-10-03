#!/usr/bin/env python3
"""
WMS diagnostic script for troubleshooting EMODnet service connectivity
"""
import sys
import requests
import time
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET
from urllib.parse import urlencode

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.config import get_config


class WMSDiagnostic:
    """WMS diagnostic and troubleshooting tool"""

    def __init__(self, base_url, timeout=10, verbose=False):
        self.base_url = base_url
        self.timeout = timeout
        self.verbose = verbose
        self.results = {
            'connectivity': {},
            'capabilities': {},
            'layers': {},
            'performance': {}
        }

    def print_status(self, message, status='info'):
        """Print status message with formatting"""
        symbols = {
            'info': 'ℹ️',
            'success': '✅',
            'warning': '⚠️',
            'error': '❌',
            'testing': '🔍'
        }
        print(f"{symbols.get(status, 'ℹ️')} {message}")

    def test_basic_connectivity(self):
        """Test basic connectivity to WMS service"""
        self.print_status("Testing basic connectivity...", 'testing')

        try:
            start_time = time.time()
            response = requests.get(self.base_url, timeout=self.timeout)
            response_time = time.time() - start_time

            self.results['connectivity'] = {
                'accessible': True,
                'status_code': response.status_code,
                'response_time': round(response_time, 3),
                'content_length': len(response.content),
                'headers': dict(response.headers)
            }

            self.print_status(f"Connection successful - Status: {response.status_code}, "
                              f"Time: {response_time:.3f}s", 'success')

            if self.verbose:
                print(f"  📊 Response headers:")
                for key, value in response.headers.items():
                    print(f"    {key}: {value}")

            return True

        except requests.exceptions.Timeout:
            self.results['connectivity'] = {'accessible': False, 'error': 'timeout'}
            self.print_status(f"Connection timeout after {self.timeout}s", 'error')
            return False

        except requests.exceptions.ConnectionError as e:
            self.results['connectivity'] = {'accessible': False, 'error': f'connection_error: {str(e)}'}
            self.print_status(f"Connection error: {str(e)}", 'error')
            return False

        except Exception as e:
            self.results['connectivity'] = {'accessible': False, 'error': f'unexpected_error: {str(e)}'}
            self.print_status(f"Unexpected error: {str(e)}", 'error')
            return False

    def test_getcapabilities(self):
        """Test GetCapabilities request"""
        self.print_status("Testing GetCapabilities request...", 'testing')

        params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetCapabilities'
        }

        try:
            start_time = time.time()
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response_time = time.time() - start_time

            self.results['capabilities'] = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': round(response_time, 3),
                'content_length': len(response.content),
                'content_type': response.headers.get('Content-Type', 'unknown')
            }

            if response.status_code == 200:
                self.print_status(f"GetCapabilities successful - Time: {response_time:.3f}s", 'success')

                # Try to parse XML
                try:
                    root = ET.fromstring(response.content)
                    self.results['capabilities']['xml_valid'] = True

                    # Extract service info
                    service_title = self._find_text(root, './/Title')
                    service_abstract = self._find_text(root, './/Abstract')

                    self.print_status(f"Service Title: {service_title or 'Unknown'}", 'info')
                    if service_abstract and self.verbose:
                        print(f"  📝 Abstract: {service_abstract[:100]}...")

                    self.results['capabilities']['service_title'] = service_title
                    self.results['capabilities']['service_abstract'] = service_abstract

                except ET.ParseError as e:
                    self.results['capabilities']['xml_valid'] = False
                    self.results['capabilities']['parse_error'] = str(e)
                    self.print_status(f"XML parsing failed: {str(e)}", 'error')

            else:
                self.print_status(f"GetCapabilities failed - Status: {response.status_code}", 'error')

            if self.verbose and response.content:
                print(f"  📄 Response preview (first 200 chars):")
                preview = response.text[:200].replace('\n', ' ')
                print(f"    {preview}...")

            return response.status_code == 200

        except Exception as e:
            self.results['capabilities'] = {'success': False, 'error': str(e)}
            self.print_status(f"GetCapabilities error: {str(e)}", 'error')
            return False

    def analyze_layers(self):
        """Analyze available layers"""
        self.print_status("Analyzing available layers...", 'testing')

        if not self.results['capabilities'].get('success'):
            self.print_status("Cannot analyze layers - GetCapabilities failed", 'warning')
            return False

        params = {
            'service': 'WMS',
            'version': '1.3.0',
            'request': 'GetCapabilities'
        }

        try:
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            root = ET.fromstring(response.content)

            # Remove namespaces for easier parsing
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}')[1]

            layers = []
            layer_elements = root.findall('.//Layer')

            for layer_elem in layer_elements:
                name_elem = layer_elem.find('Name')
                title_elem = layer_elem.find('Title')

                if name_elem is not None and name_elem.text:
                    layer_info = {
                        'name': name_elem.text,
                        'title': title_elem.text if title_elem is not None else name_elem.text
                    }

                    # Check for scale denominators
                    min_scale = layer_elem.find('MinScaleDenominator')
                    max_scale = layer_elem.find('MaxScaleDenominator')

                    if min_scale is not None:
                        layer_info['min_scale'] = float(min_scale.text)
                    if max_scale is not None:
                        layer_info['max_scale'] = float(max_scale.text)

                    # Check for bounding box
                    bbox = layer_elem.find('EX_GeographicBoundingBox')
                    if bbox is not None:
                        west = self._find_text(bbox, 'westBoundLongitude')
                        east = self._find_text(bbox, 'eastBoundLongitude')
                        south = self._find_text(bbox, 'southBoundLatitude')
                        north = self._find_text(bbox, 'northBoundLatitude')

                        if all([west, east, south, north]):
                            layer_info['bbox'] = {
                                'west': float(west), 'east': float(east),
                                'south': float(south), 'north': float(north)
                            }

                    layers.append(layer_info)

            # Filter out workspace-prefixed layers
            data_layers = [layer for layer in layers if ':' not in layer['name']]

            self.results['layers'] = {
                'total_layers': len(layers),
                'data_layers': len(data_layers),
                'layers': data_layers[:20]  # Limit to first 20 for display
            }

            self.print_status(f"Found {len(data_layers)} data layers (of {len(layers)} total)", 'success')

            if self.verbose and data_layers:
                print("  📋 Available layers:")
                for i, layer in enumerate(data_layers[:10]):  # Show first 10
                    bbox_info = ""
                    if 'bbox' in layer:
                        bbox = layer['bbox']
                        bbox_info = f" (Extent: {bbox['west']:.1f}, {bbox['south']:.1f} to {bbox['east']:.1f}, {bbox['north']:.1f})"

                    scale_info = ""
                    if 'min_scale' in layer or 'max_scale' in layer:
                        min_s = layer.get('min_scale', 'N/A')
                        max_s = layer.get('max_scale', 'N/A')
                        scale_info = f" [Scale: {min_s} - {max_s}]"

                    print(f"    {i+1}. {layer['name']} - {layer['title']}{bbox_info}{scale_info}")

                if len(data_layers) > 10:
                    print(f"    ... and {len(data_layers) - 10} more layers")

            return len(data_layers) > 0

        except Exception as e:
            self.results['layers'] = {'success': False, 'error': str(e)}
            self.print_status(f"Layer analysis error: {str(e)}", 'error')
            return False

    def test_getmap_request(self, layer_name=None):
        """Test GetMap request for a specific layer"""
        if not layer_name and self.results.get('layers', {}).get('layers'):
            layer_name = self.results['layers']['layers'][0]['name']

        if not layer_name:
            self.print_status("No layer available for GetMap test", 'warning')
            return False

        self.print_status(f"Testing GetMap request for layer: {layer_name}", 'testing')

        params = {
            'service': 'WMS',
            'version': '1.1.0',
            'request': 'GetMap',
            'layers': layer_name,
            'bbox': '-180,-90,180,90',
            'width': '256',
            'height': '256',
            'srs': 'EPSG:4326',
            'format': 'image/png'
        }

        try:
            start_time = time.time()
            response = requests.get(self.base_url, params=params, timeout=self.timeout)
            response_time = time.time() - start_time

            success = response.status_code == 200 and 'image' in response.headers.get('Content-Type', '')

            self.results['performance']['getmap'] = {
                'success': success,
                'status_code': response.status_code,
                'response_time': round(response_time, 3),
                'content_length': len(response.content),
                'content_type': response.headers.get('Content-Type', 'unknown'),
                'layer_tested': layer_name
            }

            if success:
                self.print_status(f"GetMap successful - Time: {response_time:.3f}s, "
                                  f"Size: {len(response.content)} bytes", 'success')
            else:
                self.print_status(f"GetMap failed - Status: {response.status_code}, "
                                  f"Type: {response.headers.get('Content-Type')}", 'error')

            return success

        except Exception as e:
            self.results['performance']['getmap'] = {'success': False, 'error': str(e), 'layer_tested': layer_name}
            self.print_status(f"GetMap error: {str(e)}", 'error')
            return False

    def _find_text(self, element, xpath):
        """Helper to find text in XML element"""
        try:
            found = element.find(xpath)
            return found.text if found is not None else None
        except:
            return None

    def run_full_diagnostic(self):
        """Run complete diagnostic suite"""
        self.print_status("Starting WMS diagnostic suite", 'info')
        print("=" * 60)

        tests = [
            (self.test_basic_connectivity, "Basic Connectivity"),
            (self.test_getcapabilities, "GetCapabilities"),
            (self.analyze_layers, "Layer Analysis"),
            (self.test_getmap_request, "GetMap Test")
        ]

        passed_tests = 0
        for test_func, test_name in tests:
            print(f"\n🔍 {test_name}")
            print("-" * 40)
            success = test_func()
            if success:
                passed_tests += 1
            print()

        # Summary
        print("=" * 60)
        print("📊 DIAGNOSTIC SUMMARY")
        print("=" * 60)

        total_tests = len(tests)
        print(f"Tests passed: {passed_tests}/{total_tests}")

        if passed_tests == total_tests:
            self.print_status("All tests passed! WMS service is functioning correctly.", 'success')
        elif passed_tests >= total_tests // 2:
            self.print_status("Partial functionality detected. Some features may not work.", 'warning')
        else:
            self.print_status("Critical issues detected. Service may be unavailable.", 'error')

        return passed_tests, total_tests

    def export_results(self, output_file):
        """Export diagnostic results to JSON file"""
        import json
        try:
            with open(output_file, 'w') as f:
                json.dump(self.results, f, indent=2, default=str)
            self.print_status(f"Results exported to {output_file}", 'success')
        except Exception as e:
            self.print_status(f"Failed to export results: {str(e)}", 'error')


def main():
    """Main diagnostic entry point"""
    parser = argparse.ArgumentParser(description='EMODnet WMS Diagnostic Tool')
    parser.add_argument('--url', help='WMS base URL (default: from config)')
    parser.add_argument('--timeout', type=int, default=10, help='Request timeout in seconds (default: 10)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--output', '-o', help='Export results to JSON file')
    parser.add_argument('--layer', help='Specific layer to test')

    # Individual test options
    parser.add_argument('--connectivity-only', action='store_true', help='Test connectivity only')
    parser.add_argument('--capabilities-only', action='store_true', help='Test GetCapabilities only')
    parser.add_argument('--layers-only', action='store_true', help='Analyze layers only')

    args = parser.parse_args()

    # Get WMS URL from config if not provided
    if not args.url:
        config = get_config()
        args.url = config.WMS_BASE_URL

    print("🔍 EMODnet WMS Diagnostic Tool")
    print("=" * 60)
    print(f"Target URL: {args.url}")
    print(f"Timeout: {args.timeout}s")
    print(f"Verbose: {'Yes' if args.verbose else 'No'}")
    print("=" * 60)

    diagnostic = WMSDiagnostic(args.url, args.timeout, args.verbose)

    # Run specific tests if requested
    if args.connectivity_only:
        diagnostic.test_basic_connectivity()
    elif args.capabilities_only:
        diagnostic.test_getcapabilities()
    elif args.layers_only:
        diagnostic.analyze_layers()
    else:
        # Run full diagnostic
        passed, total = diagnostic.run_full_diagnostic()

        if args.layer:
            print(f"\n🎯 Testing specific layer: {args.layer}")
            diagnostic.test_getmap_request(args.layer)

    # Export results if requested
    if args.output:
        diagnostic.export_results(args.output)


if __name__ == '__main__':
    main()