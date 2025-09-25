#!/usr/bin/env python3
"""
Example usage of the CDS Extractor for IFS/ERA5 data extraction.

This script demonstrates how to use the CDSExtractor class to extract
meteorological data from the Copernicus Climate Data Store.
"""

import sys
import datetime
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from cds_extractor import CDSExtractor, Config


def example_single_point_extraction():
    """Example: Extract ERA5 data for a single point."""
    print("=== Single Point ERA5 Extraction Example ===")
    
    # Create configuration
    config = Config({
        'output_dir': 'examples/output',
        'log_level': 'INFO'
    })
    
    # Create extractor
    extractor = CDSExtractor(config)
    
    try:
        # Extract temperature data for London
        output_file = extractor.extract_data(
            dataset='era5',
            variables=['2m_temperature'],
            longitude=0.1278,  # London longitude
            latitude=51.5074,  # London latitude
            start_date='2023-01-01',
            end_date='2023-01-03',
            time=['00:00', '12:00']  # Only 00 and 12 UTC
        )
        
        print(f"✓ Data extracted successfully: {output_file}")
        
    except Exception as e:
        print(f"✗ Extraction failed: {e}")
        return False
    
    return True


def example_regional_extraction():
    """Example: Extract ERA5 data for a regional area."""
    print("\n=== Regional ERA5 Extraction Example ===")
    
    config = Config({'output_dir': 'examples/output'})
    extractor = CDSExtractor(config)
    
    try:
        # Extract multiple variables for European region
        output_file = extractor.extract_data(
            dataset='era5',
            variables=[
                '2m_temperature',
                'mean_sea_level_pressure',
                'total_precipitation'
            ],
            longitude=[-10, 30],  # Western and Eastern bounds
            latitude=[35, 60],    # Southern and Northern bounds
            start_date='2023-07-01',
            end_date='2023-07-02'
        )
        
        print(f"✓ Regional data extracted: {output_file}")
        
    except Exception as e:
        print(f"✗ Regional extraction failed: {e}")
        return False
    
    return True


def example_pressure_level_extraction():
    """Example: Extract ERA5 pressure level data."""
    print("\n=== Pressure Level ERA5 Extraction Example ===")
    
    config = Config({'output_dir': 'examples/output'})
    extractor = CDSExtractor(config)
    
    try:
        # Extract wind components at multiple pressure levels
        output_file = extractor.extract_data(
            dataset='era5-pressure',
            variables=[
                'u_component_of_wind',
                'v_component_of_wind'
            ],
            longitude=[-5, 10],
            latitude=[40, 55],
            start_date='2023-06-15',
            end_date='2023-06-15',
            vertical_levels=['850', '500', '250']  # hPa levels
        )
        
        print(f"✓ Pressure level data extracted: {output_file}")
        
    except Exception as e:
        print(f"✗ Pressure level extraction failed: {e}")
        return False
    
    return True


def example_batch_extraction():
    """Example: Batch extraction of multiple requests."""
    print("\n=== Batch Extraction Example ===")
    
    config = Config({'output_dir': 'examples/output'})
    extractor = CDSExtractor(config)
    
    # Define multiple requests
    requests = [
        {
            'dataset': 'era5',
            'variables': ['2m_temperature'],
            'longitude': 2.3522,  # Paris
            'latitude': 48.8566,
            'start_date': '2023-01-01',
            'end_date': '2023-01-01'
        },
        {
            'dataset': 'era5',
            'variables': ['2m_temperature'],
            'longitude': -0.1276,  # London
            'latitude': 51.5074,
            'start_date': '2023-01-01',
            'end_date': '2023-01-01'
        },
        {
            'dataset': 'era5',
            'variables': ['2m_temperature'],
            'longitude': 13.4050,  # Berlin
            'latitude': 52.5200,
            'start_date': '2023-01-01',
            'end_date': '2023-01-01'
        }
    ]
    
    try:
        results = extractor.batch_extract(requests)
        successful = [r for r in results if r is not None]
        print(f"✓ Batch extraction completed: {len(successful)}/{len(requests)} successful")
        
        for i, result in enumerate(results):
            if result:
                print(f"  Request {i+1}: {result}")
            else:
                print(f"  Request {i+1}: FAILED")
                
    except Exception as e:
        print(f"✗ Batch extraction failed: {e}")
        return False
    
    return True


def example_configuration():
    """Example: Different configuration options."""
    print("\n=== Configuration Example ===")
    
    # Example with custom configuration
    custom_config = Config({
        'output_dir': 'custom_output',
        'cds_url': 'https://cds.climate.copernicus.eu/api/v2',
        'log_level': 'DEBUG'
    })
    
    print("Available datasets:")
    for key, value in custom_config.SUPPORTED_DATASETS.items():
        print(f"  {key}: {value}")
    
    print("\nCommon ERA5 variables:")
    for key, value in custom_config.ERA5_VARIABLES.items():
        print(f"  {key}: {value}")
    
    print("\nPressure levels:")
    print(f"  {custom_config.PRESSURE_LEVELS}")
    
    return True


def test_authentication():
    """Test CDS API authentication."""
    print("\n=== Authentication Test ===")
    
    config = Config()
    extractor = CDSExtractor(config)
    
    try:
        # Test connection (doesn't make actual API calls)
        if extractor.auth.test_connection():
            print("✓ CDS API authentication appears to be configured correctly")
            return True
        else:
            print("✗ CDS API authentication test failed")
            return False
            
    except Exception as e:
        print(f"✗ Authentication error: {e}")
        print("\nTo set up CDS API authentication:")
        print("1. Register at https://cds.climate.copernicus.eu/#!/home")
        print("2. Get your API key from https://cds.climate.copernicus.eu/api-how-to")
        print("3. Set up credentials using one of these methods:")
        print("   - Create ~/.cdsapirc file with your URL and key")
        print("   - Set CDS_API_KEY environment variable")
        print("   - Pass credentials in Config constructor")
        return False


def main():
    """Run all examples."""
    print("CDS Extractor Examples")
    print("=" * 50)
    
    # Create output directory
    Path("examples/output").mkdir(parents=True, exist_ok=True)
    
    # Run examples
    examples = [
        ("Authentication Test", test_authentication),
        ("Configuration", example_configuration),
        # Note: Actual data extraction examples are commented out 
        # to avoid making real API calls during testing
        # ("Single Point Extraction", example_single_point_extraction),
        # ("Regional Extraction", example_regional_extraction),
        # ("Pressure Level Extraction", example_pressure_level_extraction),
        # ("Batch Extraction", example_batch_extraction),
    ]
    
    results = []
    for name, func in examples:
        try:
            success = func()
            results.append((name, success))
        except Exception as e:
            print(f"✗ {name} failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    for name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {name}")
    
    total_success = sum(1 for _, success in results if success)
    print(f"\nResults: {total_success}/{len(results)} examples passed")
    
    if total_success == len(results):
        print("🎉 All examples completed successfully!")
    else:
        print("⚠️  Some examples failed. Check the output above for details.")


if __name__ == "__main__":
    main()