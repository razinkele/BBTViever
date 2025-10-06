#!/usr/bin/env python3
"""
CLI tool to calculate bathymetry statistics for BBT areas.

This script uses the BathymetryCalculator utility to fetch and calculate
depth statistics from EMODnet Bathymetry data.

Usage:
    python scripts/calculate_bathymetry.py [options]

Options:
    --gpkg PATH         Path to BBT GPKG file (default: data/vector/BBT.gpkg)
    --layer NAME        Layer name in GPKG (default: BBT areas)
    --output PATH       Output JSON file path (default: data/bbt_bathymetry_stats.json)
    --samples N         Number of sample points per dimension (default: 25)
    --verbose           Enable verbose logging
"""

import argparse
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from emodnet_viewer.utils.bathymetry_calculator import BathymetryCalculator
from emodnet_viewer.utils.logging_config import setup_logging, get_logger


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Calculate bathymetry statistics for BBT areas using EMODnet data"
    )
    parser.add_argument(
        '--gpkg',
        default='data/vector/BBT.gpkg',
        help='Path to BBT GPKG file'
    )
    parser.add_argument(
        '--layer',
        default='BBT areas',
        help='Layer name in GPKG file'
    )
    parser.add_argument(
        '--output',
        default='data/bbt_bathymetry_stats.json',
        help='Output JSON file path'
    )
    parser.add_argument(
        '--samples',
        type=int,
        default=25,
        help='Number of sample points per dimension (total = samples²)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )

    args = parser.parse_args()

    # Setup logging
    log_level = 'DEBUG' if args.verbose else 'INFO'
    setup_logging(log_level)
    logger = get_logger(__name__)

    # Print header
    print("=" * 70)
    print("🌊 BBT Bathymetry Statistics Calculator")
    print("=" * 70)
    print(f"\nConfiguration:")
    print(f"  GPKG file: {args.gpkg}")
    print(f"  Layer: {args.layer}")
    print(f"  Output: {args.output}")
    print(f"  Samples per BBT: {args.samples}² = {args.samples**2} max points")
    print()

    try:
        # Initialize calculator
        calculator = BathymetryCalculator(
            gpkg_path=args.gpkg,
            layer_name=args.layer
        )

        # Load BBT areas
        calculator.load_bbt_areas()

        # Calculate statistics
        logger.info("Starting bathymetry calculation...")
        stats = calculator.calculate_all_bbt_stats(num_samples=args.samples)

        # Save results
        output_path = calculator.save_to_json(args.output)

        # Print summary
        summary = calculator.get_summary()
        print("\n" + "=" * 70)
        print("📋 Summary:")
        print(f"  Total BBT areas: {summary['total_bbt_areas']}")
        print(f"  With bathymetry data: {summary['with_bathymetry_data']}")
        print(f"  Without data: {summary['without_data']}")
        print(f"\n✅ Results saved to: {output_path}")
        print("=" * 70)

        return 0

    except Exception as e:
        logger.error(f"Error during calculation: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
