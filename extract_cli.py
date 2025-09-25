#!/usr/bin/env python3
"""
Command-line interface for CDS data extraction.

This script provides a simple command-line interface to extract
meteorological data using the CDS API.
"""

import argparse
import sys
from pathlib import Path
import json
import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from cds_extractor import CDSExtractor, Config


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Extract meteorological data using the CDS API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s era5 temperature -lon 0.1278 -lat 51.5074 -start 2023-01-01 -end 2023-01-03
  %(prog)s era5 temperature,pressure -lon -10,30 -lat 35,60 -start 2023-07-01 -end 2023-07-02
  %(prog)s era5-pressure u_component_of_wind,v_component_of_wind -lon -5,10 -lat 40,55 -start 2023-06-15 -end 2023-06-15 -levels 850,500,250

Available datasets: era5, era5-pressure, ifs, ifs-pressure
        """
    )
    
    parser.add_argument('dataset', choices=['era5', 'era5-pressure', 'ifs', 'ifs-pressure'],
                        help='Dataset to extract from')
    parser.add_argument('variables', help='Variable(s) to extract (comma-separated)')
    
    parser.add_argument('-lon', '--longitude', required=True,
                        help='Longitude (single value or west,east for region)')
    parser.add_argument('-lat', '--latitude', required=True,
                        help='Latitude (single value or south,north for region)')
    
    parser.add_argument('-start', '--start-date', required=True,
                        help='Start date (YYYY-MM-DD)')
    parser.add_argument('-end', '--end-date', required=True,
                        help='End date (YYYY-MM-DD)')
    
    parser.add_argument('-levels', '--vertical-levels',
                        help='Vertical levels for pressure-level datasets (comma-separated)')
    parser.add_argument('-time', '--time-steps',
                        help='Time steps (comma-separated, e.g., 00:00,12:00)')
    
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--format', choices=['netcdf', 'grib'], default='netcdf',
                        help='Output format (default: netcdf)')
    parser.add_argument('--output-dir', default='extracted_data',
                        help='Output directory (default: extracted_data)')
    
    parser.add_argument('--config', help='Configuration file path')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Verbose logging')
    parser.add_argument('--quiet', '-q', action='store_true',
                        help='Quiet mode (errors only)')
    
    return parser.parse_args()


def parse_coordinate(coord_str):
    """Parse coordinate string (single value or range)."""
    if ',' in coord_str:
        return [float(x.strip()) for x in coord_str.split(',')]
    else:
        return float(coord_str)


def main():
    """Main command-line interface."""
    args = parse_arguments()
    
    try:
        # Parse coordinates
        longitude = parse_coordinate(args.longitude)
        latitude = parse_coordinate(args.latitude)
        
        # Parse variables
        variables = [v.strip() for v in args.variables.split(',')]
        
        # Parse optional parameters
        vertical_levels = None
        if args.vertical_levels:
            vertical_levels = [v.strip() for v in args.vertical_levels.split(',')]
        
        time_steps = None
        if args.time_steps:
            time_steps = [t.strip() for t in args.time_steps.split(',')]
        
        # Create configuration
        config_dict = {
            'output_dir': args.output_dir,
            'log_level': 'DEBUG' if args.verbose else ('ERROR' if args.quiet else 'INFO')
        }
        
        config = Config(config_dict)
        extractor = CDSExtractor(config)
        
        # Print extraction details
        print(f"Dataset: {args.dataset}")
        print(f"Variables: {variables}")
        print(f"Coordinates: lon={longitude}, lat={latitude}")
        print(f"Time period: {args.start_date} to {args.end_date}")
        if vertical_levels:
            print(f"Vertical levels: {vertical_levels}")
        if time_steps:
            print(f"Time steps: {time_steps}")
        print(f"Output format: {args.format}")
        print("")
        
        # Extract data
        kwargs = {}
        if time_steps:
            kwargs['time'] = time_steps
        
        output_path = extractor.extract_data(
            dataset=args.dataset,
            variables=variables,
            longitude=longitude,
            latitude=latitude,
            start_date=args.start_date,
            end_date=args.end_date,
            vertical_levels=vertical_levels,
            output_path=args.output,
            output_format=args.format,
            **kwargs
        )
        
        print(f"✓ Data extraction completed successfully!")
        print(f"Output file: {output_path}")
        
    except KeyboardInterrupt:
        print("\n✗ Extraction interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()