#!/usr/bin/env python3
"""
Convert BBT bathymetry CSV to JSON format for the web application.

Usage:
    python scripts/csv_to_bathymetry_json.py [--input CSV_FILE] [--output JSON_FILE]
"""

import csv
import json
import argparse
from datetime import datetime
from pathlib import Path


def csv_to_json(csv_path: str, json_path: str):
    """Convert CSV bathymetry data to JSON format."""

    print(f"📂 Reading CSV from: {csv_path}")

    statistics = {}
    valid_count = 0

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            bbt_name = row['BBT_Name'].strip()

            try:
                min_depth = float(row['Min_Depth_m'])
                max_depth = float(row['Max_Depth_m'])
                avg_depth = float(row['Avg_Depth_m'])

                statistics[bbt_name] = {
                    'min_depth_m': round(min_depth, 1),
                    'max_depth_m': round(max_depth, 1),
                    'avg_depth_m': round(avg_depth, 1),
                    'std_depth_m': None,  # Not available from CSV
                    'sample_count': None,  # Not available from CSV
                    'notes': row.get('Notes', '').strip() or None
                }
                valid_count += 1
                print(f"  ✓ {bbt_name}: {min_depth}m - {max_depth}m (avg: {avg_depth}m)")

            except (ValueError, KeyError) as e:
                print(f"  ✗ Skipping {bbt_name}: {e}")
                statistics[bbt_name] = None

    # Create output structure
    output_data = {
        'metadata': {
            'source': 'Manual bathymetry data',
            'url': 'https://portal.emodnet-bathymetry.eu/',
            'method': 'Manual data entry from bathymetric charts and literature',
            'unit': 'meters below sea level',
            'generated': datetime.now().isoformat(),
            'bbt_count': len(statistics),
            'valid_count': valid_count,
            'data_source': 'CSV import'
        },
        'statistics': statistics
    }

    # Write JSON
    output_path = Path(json_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2)

    print(f"\n✅ JSON created: {json_path}")
    print(f"📊 Total BBT areas: {len(statistics)}")
    print(f"📊 With data: {valid_count}")
    print(f"📊 Without data: {len(statistics) - valid_count}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert BBT bathymetry CSV to JSON format'
    )
    parser.add_argument(
        '--input',
        default='data/bbt_bathymetry_manual.csv',
        help='Input CSV file path'
    )
    parser.add_argument(
        '--output',
        default='data/bbt_bathymetry_stats.json',
        help='Output JSON file path'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🌊 BBT Bathymetry CSV to JSON Converter")
    print("=" * 70)
    print()

    csv_to_json(args.input, args.output)

    print("\n" + "=" * 70)
    print("🎉 Conversion complete!")
    print("=" * 70)


if __name__ == '__main__':
    main()
