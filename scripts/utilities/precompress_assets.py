#!/usr/bin/env python3
"""
Pre-compress static assets with Brotli and Gzip for optimal delivery

This script generates pre-compressed versions of static assets (.br and .gz)
that can be served directly by Nginx, eliminating runtime compression overhead.

Benefits:
- Brotli compression: ~20% better than gzip for text-based assets
- Zero CPU overhead during request handling (compression done once)
- Faster response times for users
- Lower server resource usage

Usage:
    python scripts/utilities/precompress_assets.py

Nginx configuration required:
    # Enable pre-compressed file serving
    gzip_static on;
    brotli_static on;
"""

import brotli
import gzip
import os
from pathlib import Path


# File types to compress
COMPRESSIBLE_EXTENSIONS = {
    '.js',
    '.css',
    '.json',
    '.html',
    '.xml',
    '.txt',
    '.md',
    '.svg'
}

# Directories to process
STATIC_DIRS = [
    'static/dist',
    'static/css',
    'static/js',
    'templates'
]


def get_compression_stats(original_size, compressed_size):
    """Calculate compression statistics"""
    reduction = original_size - compressed_size
    reduction_percent = (reduction / original_size * 100) if original_size > 0 else 0
    return reduction, reduction_percent


def compress_file_brotli(file_path, quality=11):
    """
    Compress file with Brotli

    Args:
        file_path: Path to file to compress
        quality: Brotli quality (0-11, default 11 for maximum compression)

    Returns:
        Tuple of (output_path, original_size, compressed_size)
    """
    output_path = Path(f"{file_path}.br")

    with open(file_path, 'rb') as f_in:
        original_data = f_in.read()
        compressed_data = brotli.compress(original_data, quality=quality)

    with open(output_path, 'wb') as f_out:
        f_out.write(compressed_data)

    return output_path, len(original_data), len(compressed_data)


def compress_file_gzip(file_path, compresslevel=9):
    """
    Compress file with Gzip

    Args:
        file_path: Path to file to compress
        compresslevel: Gzip compression level (0-9, default 9 for maximum compression)

    Returns:
        Tuple of (output_path, original_size, compressed_size)
    """
    output_path = Path(f"{file_path}.gz")

    with open(file_path, 'rb') as f_in:
        original_data = f_in.read()

    with gzip.open(output_path, 'wb', compresslevel=compresslevel) as f_out:
        f_out.write(original_data)

    compressed_size = output_path.stat().st_size

    return output_path, len(original_data), compressed_size


def should_compress(file_path, min_size_kb=1):
    """
    Determine if file should be compressed

    Args:
        file_path: Path to check
        min_size_kb: Minimum file size in KB to compress (default 1KB)

    Returns:
        Boolean indicating if file should be compressed
    """
    # Check extension
    if file_path.suffix not in COMPRESSIBLE_EXTENSIONS:
        return False

    # Check if already compressed
    if file_path.suffix in {'.gz', '.br', '.zip', '.bz2'}:
        return False

    # Check minimum size
    size_kb = file_path.stat().st_size / 1024
    if size_kb < min_size_kb:
        return False

    return True


def precompress_directory(directory, verbose=True):
    """
    Pre-compress all eligible files in directory

    Args:
        directory: Directory path to process
        verbose: Print progress messages

    Returns:
        Dictionary with compression statistics
    """
    stats = {
        'files_processed': 0,
        'total_original_size': 0,
        'total_brotli_size': 0,
        'total_gzip_size': 0,
        'files': []
    }

    dir_path = Path(directory)
    if not dir_path.exists():
        if verbose:
            print(f"⚠️  Directory not found: {directory}")
        return stats

    if verbose:
        print(f"\n📁 Processing {directory}/")

    # Find all eligible files
    for file_path in dir_path.rglob('*'):
        if not file_path.is_file():
            continue

        if not should_compress(file_path):
            continue

        try:
            # Compress with Brotli
            br_path, orig_size, br_size = compress_file_brotli(file_path)
            br_reduction, br_percent = get_compression_stats(orig_size, br_size)

            # Compress with Gzip
            gz_path, _, gz_size = compress_file_gzip(file_path)
            gz_reduction, gz_percent = get_compression_stats(orig_size, gz_size)

            # Update stats
            stats['files_processed'] += 1
            stats['total_original_size'] += orig_size
            stats['total_brotli_size'] += br_size
            stats['total_gzip_size'] += gz_size

            file_stats = {
                'path': str(file_path),
                'original_size': orig_size,
                'brotli_size': br_size,
                'gzip_size': gz_size,
                'brotli_reduction': br_percent,
                'gzip_reduction': gz_percent
            }
            stats['files'].append(file_stats)

            if verbose:
                rel_path = file_path.relative_to(dir_path)
                print(f"  ✓ {rel_path}")
                print(f"    Original:  {orig_size:>8,} bytes")
                print(f"    Brotli:    {br_size:>8,} bytes (-{br_percent:.1f}%)")
                print(f"    Gzip:      {gz_size:>8,} bytes (-{gz_percent:.1f}%)")

        except Exception as e:
            if verbose:
                print(f"  ✗ Error compressing {file_path}: {e}")

    return stats


def main():
    """Main pre-compression routine"""
    print("🗜️  Pre-compressing static assets...")
    print("=" * 60)

    total_stats = {
        'files_processed': 0,
        'total_original_size': 0,
        'total_brotli_size': 0,
        'total_gzip_size': 0
    }

    # Process each directory
    for directory in STATIC_DIRS:
        stats = precompress_directory(directory, verbose=True)

        total_stats['files_processed'] += stats['files_processed']
        total_stats['total_original_size'] += stats['total_original_size']
        total_stats['total_brotli_size'] += stats['total_brotli_size']
        total_stats['total_gzip_size'] += stats['total_gzip_size']

    # Print summary
    print("\n" + "=" * 60)
    print("📊 Compression Summary")
    print("=" * 60)

    if total_stats['files_processed'] > 0:
        orig_size = total_stats['total_original_size']
        br_size = total_stats['total_brotli_size']
        gz_size = total_stats['total_gzip_size']

        br_reduction, br_percent = get_compression_stats(orig_size, br_size)
        gz_reduction, gz_percent = get_compression_stats(orig_size, gz_size)

        print(f"\nFiles processed:    {total_stats['files_processed']}")
        print(f"\nOriginal size:      {orig_size:>12,} bytes ({orig_size/1024:,.1f} KB)")
        print(f"Brotli size:        {br_size:>12,} bytes ({br_size/1024:,.1f} KB)")
        print(f"Gzip size:          {gz_size:>12,} bytes ({gz_size/1024:,.1f} KB)")
        print(f"\nBrotli reduction:   {br_reduction:>12,} bytes (-{br_percent:.1f}%)")
        print(f"Gzip reduction:     {gz_reduction:>12,} bytes (-{gz_percent:.1f}%)")

        # Calculate Brotli advantage over Gzip
        if gz_size > 0:
            brotli_advantage = ((gz_size - br_size) / gz_size * 100)
            print(f"\nBrotli vs Gzip:     {brotli_advantage:>12.1f}% smaller")

        print("\n✅ Pre-compression complete!")
        print("\n💡 Next steps:")
        print("   1. Enable brotli_static and gzip_static in Nginx configuration")
        print("   2. Nginx will automatically serve .br and .gz files when available")
        print("   3. Clients supporting Brotli will get ~20% better compression")
    else:
        print("No compressible files found.")

    print("=" * 60)


if __name__ == '__main__':
    main()
