# GODAS-Visualization

Exploring different ways of visualizing GODAS data.

## Features

- **CDS Data Pipeline**: Python pipeline for extracting IFS/ERA5 data using the Copernicus Climate Data Store API
- **Data Visualization**: Tools for combining and visualizing NetCDF data (see `CombineNC.ipynb`)

## CDS Data Extraction Pipeline

The repository includes a comprehensive Python pipeline for extracting meteorological data from the Copernicus Climate Data Store (CDS). See [`CDS_EXTRACTOR_README.md`](CDS_EXTRACTOR_README.md) for detailed documentation.

### Quick Start

```python
from cds_extractor import CDSExtractor

# Create extractor
extractor = CDSExtractor()

# Extract ERA5 temperature data
output_file = extractor.extract_data(
    dataset='era5',
    variables=['2m_temperature'],
    longitude=0.1278,   # London
    latitude=51.5074,
    start_date='2023-01-01',
    end_date='2023-01-03'
)
```

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up CDS API credentials (see [CDS_EXTRACTOR_README.md](CDS_EXTRACTOR_README.md) for details)

3. Run examples:
   ```bash
   python examples.py
   ```

4. Or use the command-line interface:
   ```bash
   python extract_cli.py era5 2m_temperature -lon 0.1278 -lat 51.5074 -start 2023-01-01 -end 2023-01-03
   ```

## Repository Structure

```
├── cds_extractor/          # CDS API data extraction pipeline
│   ├── __init__.py         # Package initialization
│   ├── auth.py             # CDS API authentication
│   ├── config.py           # Configuration management
│   ├── extractor.py        # Main extraction functionality
│   └── utils.py            # Utility functions and validation
├── CombineNC.ipynb         # Jupyter notebook for NetCDF data handling
├── examples.py             # Usage examples for CDS extractor
├── extract_cli.py          # Command-line interface for data extraction
├── cdsapirc_template       # Template for CDS API credentials
├── requirements.txt        # Python dependencies
├── CDS_EXTRACTOR_README.md # Detailed CDS extractor documentation
└── README.md               # This file
```
