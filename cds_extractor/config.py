"""
Configuration management for CDS API data extraction.
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Union


class Config:
    """Configuration class for CDS API settings and data extraction parameters."""
    
    # Default CDS API settings
    DEFAULT_CDS_URL = "https://cds.climate.copernicus.eu/api/v2"
    DEFAULT_OUTPUT_FORMAT = "netcdf"
    DEFAULT_OUTPUT_DIR = "extracted_data"
    
    # Supported datasets
    SUPPORTED_DATASETS = {
        'era5': 'reanalysis-era5-single-levels',
        'era5-pressure': 'reanalysis-era5-pressure-levels',
        'ifs': 'seasonal-original-single-levels',
        'ifs-pressure': 'seasonal-original-pressure-levels'
    }
    
    # Common ERA5 variables
    ERA5_VARIABLES = {
        'temperature': '2m_temperature',
        'pressure': 'mean_sea_level_pressure',
        'u_wind': '10m_u_component_of_wind',
        'v_wind': '10m_v_component_of_wind',
        'precipitation': 'total_precipitation',
        'humidity': '2m_relative_humidity',
    }
    
    # Common pressure levels (hPa)
    PRESSURE_LEVELS = [
        '1000', '925', '850', '700', '600', '500', '400', '300', '250', '200', '150', '100', '70', '50', '30', '20', '10'
    ]
    
    def __init__(self, config_dict: Optional[Dict] = None):
        """
        Initialize configuration.
        
        Args:
            config_dict: Optional dictionary of configuration parameters
        """
        self.config = config_dict or {}
        self._validate_config()
    
    def get(self, key: str, default=None):
        """Get configuration value with fallback to default."""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value."""
        self.config[key] = value
    
    def _validate_config(self):
        """Validate configuration parameters."""
        # Ensure output directory exists
        output_dir = self.get('output_dir', self.DEFAULT_OUTPUT_DIR)
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Validate dataset if specified
        dataset = self.get('dataset')
        if dataset and dataset not in self.SUPPORTED_DATASETS:
            raise ValueError(f"Unsupported dataset: {dataset}. "
                           f"Supported datasets: {list(self.SUPPORTED_DATASETS.keys())}")
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'Config':
        """
        Load configuration from a file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            Config instance
        """
        # This is a placeholder for file-based configuration
        # Could be extended to support JSON, YAML, etc.
        config_dict = {}
        return cls(config_dict)
    
    def get_cds_credentials(self) -> Dict[str, str]:
        """
        Get CDS API credentials.
        
        Returns:
            Dictionary with 'url' and 'key' for CDS API authentication
            
        Raises:
            ValueError: If credentials are not found
        """
        # Try to get from config first
        url = self.get('cds_url', self.DEFAULT_CDS_URL)
        key = self.get('cds_key')
        
        # If not in config, try environment variables
        if not key:
            key = os.environ.get('CDS_API_KEY')
        
        # Try to read from CDS API RC file
        if not key:
            cds_rc_path = Path.home() / '.cdsapirc'
            if cds_rc_path.exists():
                try:
                    with open(cds_rc_path, 'r') as f:
                        for line in f:
                            if line.startswith('key:'):
                                key = line.split(':', 1)[1].strip()
                            elif line.startswith('url:'):
                                url = line.split(':', 1)[1].strip()
                except Exception:
                    pass
        
        if not key:
            raise ValueError(
                "CDS API key not found. Please set it via:\n"
                "1. Config parameter 'cds_key'\n"
                "2. Environment variable 'CDS_API_KEY'\n"
                "3. ~/.cdsapirc file\n"
                "Get your API key from: https://cds.climate.copernicus.eu/api-how-to"
            )
        
        return {'url': url, 'key': key}