# CDS Extractor - IFS/ERA5 Data Pipeline

A Python pipeline for extracting IFS and ERA5 data using the Copernicus Climate Data Store (CDS) API. This tool allows users to specify coordinates, variables, time periods, and vertical levels to extract meteorological data in NetCDF or GRIB formats.

## Features

- **Flexible Data Extraction**: Extract data by coordinates, variables, and time periods
- **Multiple Datasets**: Support for ERA5 single levels, ERA5 pressure levels, IFS seasonal data
- **Batch Processing**: Execute multiple extraction requests efficiently
- **Format Support**: Output data in NetCDF or GRIB formats
- **Error Handling**: Comprehensive validation and error handling
- **Authentication**: Multiple methods for CDS API authentication
- **Logging**: Detailed logging for monitoring and debugging

## Installation

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up CDS API Authentication:**
   
   You need to register and get API credentials from the Copernicus Climate Data Store:
   
   - Register at: https://cds.climate.copernicus.eu/#!/home
   - Get your API key from: https://cds.climate.copernicus.eu/api-how-to
   
   Then set up authentication using one of these methods:
   
   **Method 1: Create ~/.cdsapirc file**
   ```
   url: https://cds.climate.copernicus.eu/api/v2
   key: YOUR_API_KEY_HERE
   ```
   
   **Method 2: Environment Variable**
   ```bash
   export CDS_API_KEY="YOUR_API_KEY_HERE"
   ```
   
   **Method 3: In Code**
   ```python
   config = Config({'cds_key': 'YOUR_API_KEY_HERE'})
   ```

## Quick Start

```python
from cds_extractor import CDSExtractor, Config

# Create extractor with default configuration
extractor = CDSExtractor()

# Extract ERA5 temperature data for London
output_file = extractor.extract_data(
    dataset='era5',
    variables=['2m_temperature'],
    longitude=0.1278,   # London longitude
    latitude=51.5074,   # London latitude
    start_date='2023-01-01',
    end_date='2023-01-03'
)

print(f"Data saved to: {output_file}")
```

## Usage Examples

### Single Point Extraction

```python
from cds_extractor import CDSExtractor

extractor = CDSExtractor()

# Extract temperature for a specific location
output_file = extractor.extract_data(
    dataset='era5',
    variables=['2m_temperature', 'mean_sea_level_pressure'],
    longitude=-74.0060,  # New York longitude
    latitude=40.7128,    # New York latitude
    start_date='2023-06-01',
    end_date='2023-06-07',
    time=['00:00', '12:00']  # Only 00 and 12 UTC
)
```

### Regional Extraction

```python
# Extract data for a rectangular region
output_file = extractor.extract_data(
    dataset='era5',
    variables=['2m_temperature', 'total_precipitation'],
    longitude=[-10, 30],  # Western and Eastern bounds
    latitude=[35, 60],    # Southern and Northern bounds
    start_date='2023-07-01',
    end_date='2023-07-31'
)
```

### Pressure Level Data

```python
# Extract wind data at multiple pressure levels
output_file = extractor.extract_data(
    dataset='era5-pressure',
    variables=['u_component_of_wind', 'v_component_of_wind'],
    longitude=[-5, 10],
    latitude=[40, 55],
    start_date='2023-06-15',
    end_date='2023-06-20',
    vertical_levels=['850', '500', '250']  # hPa levels
)
```

### Batch Processing

```python
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
    }
]

# Execute batch extraction
results = extractor.batch_extract(requests)
```

### Custom Configuration

```python
from cds_extractor import Config, CDSExtractor

# Create custom configuration
config = Config({
    'output_dir': 'my_data',
    'cds_key': 'your_api_key',
    'log_level': 'DEBUG'
})

extractor = CDSExtractor(config)
```

## Supported Datasets

| Dataset ID | Description | CDS Dataset Name |
|------------|-------------|------------------|
| `era5` | ERA5 single levels | `reanalysis-era5-single-levels` |
| `era5-pressure` | ERA5 pressure levels | `reanalysis-era5-pressure-levels` |
| `ifs` | IFS seasonal single levels | `seasonal-original-single-levels` |
| `ifs-pressure` | IFS seasonal pressure levels | `seasonal-original-pressure-levels` |

## Common Variables

### ERA5 Single Levels
- `2m_temperature` - 2 metre temperature
- `mean_sea_level_pressure` - Mean sea level pressure
- `10m_u_component_of_wind` - 10 metre U wind component
- `10m_v_component_of_wind` - 10 metre V wind component
- `total_precipitation` - Total precipitation
- `2m_relative_humidity` - 2 metre relative humidity

### ERA5 Pressure Levels
- `temperature` - Temperature
- `u_component_of_wind` - U component of wind
- `v_component_of_wind` - V component of wind
- `geopotential` - Geopotential
- `relative_humidity` - Relative humidity
- `specific_humidity` - Specific humidity

## API Reference

### CDSExtractor

Main class for data extraction.

#### Methods

**`__init__(config=None)`**
- `config`: Optional Config instance

**`extract_data(dataset, variables, longitude, latitude, start_date, end_date, **kwargs)`**
- `dataset`: Dataset identifier ('era5', 'era5-pressure', 'ifs', 'ifs-pressure')
- `variables`: Single variable or list of variables
- `longitude`: Single longitude or [west, east] bounds
- `latitude`: Single latitude or [south, north] bounds
- `start_date`: Start date (YYYY-MM-DD format or date object)
- `end_date`: End date (YYYY-MM-DD format or date object)
- `vertical_levels`: Pressure levels (for pressure level datasets)
- `output_path`: Custom output path (optional)
- `output_format`: 'netcdf' or 'grib' (default: 'netcdf')

Returns: Path to extracted data file

**`batch_extract(requests)`**
- `requests`: List of request dictionaries

Returns: List of output file paths

### Config

Configuration management class.

#### Methods

**`__init__(config_dict=None)`**
- `config_dict`: Optional configuration dictionary

**`get(key, default=None)`**
Get configuration value with fallback to default

**`set(key, value)`**
Set configuration value

**`get_cds_credentials()`**
Get CDS API credentials from config, environment, or ~/.cdsapirc

## Error Handling

The extractor includes comprehensive error handling:

- **Authentication Errors**: Clear messages when CDS API credentials are missing or invalid
- **Validation Errors**: Parameter validation with helpful error messages
- **API Errors**: Handling of CDS API request failures with retry logic
- **File Errors**: Proper handling of file I/O operations

## Logging

The extractor uses Python's logging module with configurable levels:

```python
config = Config({'log_level': 'DEBUG'})  # DEBUG, INFO, WARNING, ERROR
```

## Output Files

Output files are automatically named using this pattern:
```
{dataset}_{variables}_{start_date}_to_{end_date}_{coordinates}.{format}
```

Example: `era5_2m_temperature_2023-01-01_to_2023-01-03_0.1278lon_51.5074lat.nc`

## Command Line Usage

Run the examples script to test functionality:

```bash
python examples.py
```

## Requirements

See `requirements.txt` for full dependency list. Key dependencies:
- `cdsapi>=0.5.1` - CDS API client
- `netcdf4>=1.6.0` - NetCDF file support
- `xarray>=2023.1.0` - Data array handling
- `numpy>=1.24.0` - Numerical operations

## Troubleshooting

### Authentication Issues
- Verify your CDS API key is correct
- Check that ~/.cdsapirc file is properly formatted
- Ensure you've accepted the terms for the datasets you're accessing

### Request Failures
- Large requests may take time - be patient
- Check CDS service status if requests consistently fail
- Verify variable names are correct for the dataset

### Installation Issues
- Ensure you have Python 3.8+ installed
- Some dependencies may require system libraries (e.g., HDF5, NetCDF)

## License

This project is part of the GODAS-Visualization repository. See repository license for details.

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## References

- [Copernicus Climate Data Store](https://cds.climate.copernicus.eu/)
- [CDS API Documentation](https://cds.climate.copernicus.eu/api-how-to)
- [ERA5 Documentation](https://confluence.ecmwf.int/display/CKB/ERA5%3A+data+documentation)
- [IFS Documentation](https://www.ecmwf.int/en/forecasts/documentation-and-support)