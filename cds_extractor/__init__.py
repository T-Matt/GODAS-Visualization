"""
CDS Extractor - A Python pipeline for extracting IFS/ERA5 data using the CDS API.

This package provides tools for:
- Authenticating with the Copernicus Climate Data Store API
- Extracting IFS and ERA5 data by coordinates, variables, and time periods
- Saving data in NetCDF and GRIB formats
- Batch processing and error handling
"""

__version__ = "1.0.0"
__author__ = "GODAS-Visualization Project"

from .extractor import CDSExtractor
from .config import Config

__all__ = ['CDSExtractor', 'Config']