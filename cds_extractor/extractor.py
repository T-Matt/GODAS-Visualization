"""
Main data extraction module for CDS API.
"""

import logging
import time
from pathlib import Path
from typing import Dict, List, Optional, Union, Tuple, Any
import datetime

from .auth import CDSAuth
from .config import Config
from .utils import (
    validate_coordinates, validate_vertical_levels, validate_time_range,
    validate_variables, create_output_filename, ensure_output_directory
)

logger = logging.getLogger(__name__)


class CDSExtractor:
    """Main class for extracting IFS/ERA5 data using the CDS API."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the CDS data extractor.
        
        Args:
            config: Configuration instance
        """
        self.config = config or Config()
        self.auth = CDSAuth(self.config)
        self._client = None
        
        # Set up logging
        self._setup_logging()
    
    def _setup_logging(self):
        """Set up logging configuration."""
        log_level = self.config.get('log_level', 'INFO')
        logging.basicConfig(
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def extract_data(self,
                    dataset: str,
                    variables: Union[str, List[str]],
                    longitude: Union[float, List[float]],
                    latitude: Union[float, List[float]],
                    start_date: Union[str, datetime.date],
                    end_date: Union[str, datetime.date],
                    vertical_levels: Optional[Union[int, List[int], str, List[str]]] = None,
                    output_path: Optional[Union[str, Path]] = None,
                    output_format: str = 'netcdf',
                    **kwargs) -> str:
        """
        Extract data from CDS API.
        
        Args:
            dataset: Dataset identifier ('era5', 'era5-pressure', 'ifs', 'ifs-pressure')
            variables: Variable name(s) to extract
            longitude: Longitude coordinate(s)
            latitude: Latitude coordinate(s)  
            start_date: Start date for data extraction
            end_date: End date for data extraction
            vertical_levels: Vertical levels (for pressure level datasets)
            output_path: Output file path (if None, auto-generated)
            output_format: Output format ('netcdf' or 'grib')
            **kwargs: Additional parameters for the API request
            
        Returns:
            Path to the extracted data file
            
        Raises:
            ValueError: If parameters are invalid
            RuntimeError: If data extraction fails
        """
        logger.info(f"Starting data extraction for dataset: {dataset}")
        
        # Validate inputs
        variables = validate_variables(variables, dataset)
        longitude, latitude = validate_coordinates(longitude, latitude)
        start_date_str, end_date_str = validate_time_range(start_date, end_date)
        
        # Get dataset name for API
        if dataset not in self.config.SUPPORTED_DATASETS:
            raise ValueError(f"Unsupported dataset: {dataset}")
        
        api_dataset = self.config.SUPPORTED_DATASETS[dataset]
        
        # Build request parameters
        request_params = self._build_request_params(
            dataset, variables, longitude, latitude, 
            start_date_str, end_date_str, vertical_levels, **kwargs
        )
        
        # Generate output filename if not provided
        if output_path is None:
            output_dir = Path(self.config.get('output_dir', self.config.DEFAULT_OUTPUT_DIR))
            ensure_output_directory(output_dir)
            
            filename = create_output_filename(
                dataset, variables, start_date_str, end_date_str,
                (longitude, latitude), 'nc' if output_format == 'netcdf' else 'grib'
            )
            output_path = output_dir / filename
        else:
            output_path = Path(output_path)
            ensure_output_directory(output_path.parent)
        
        # Execute the request
        try:
            self._execute_request(api_dataset, request_params, output_path)
            logger.info(f"Data extraction completed successfully: {output_path}")
            return str(output_path)
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            raise RuntimeError(f"Failed to extract data: {e}")
    
    def _build_request_params(self,
                            dataset: str,
                            variables: List[str],
                            longitude: List[float],
                            latitude: List[float],
                            start_date: str,
                            end_date: str,
                            vertical_levels: Optional[List[str]] = None,
                            **kwargs) -> Dict[str, Any]:
        """Build request parameters for CDS API."""
        
        # Base parameters
        params = {
            'variable': variables,
            'date': self._build_date_range(start_date, end_date),
            'time': kwargs.get('time', ['00:00', '06:00', '12:00', '18:00']),
            'area': self._build_area_param(latitude, longitude),
            'format': 'netcdf'
        }
        
        # Add pressure levels for pressure level datasets
        if 'pressure' in dataset and vertical_levels:
            levels = validate_vertical_levels(vertical_levels, 'pressure')
            params['pressure_level'] = levels
        
        # Add product type for seasonal data
        if 'ifs' in dataset:
            params['product_type'] = kwargs.get('product_type', 'monthly_mean')
            params['originating_centre'] = kwargs.get('originating_centre', 'ecmwf')
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key not in ['time', 'product_type', 'originating_centre'] and value is not None:
                params[key] = value
        
        logger.debug(f"Built request parameters: {params}")
        return params
    
    def _build_date_range(self, start_date: str, end_date: str) -> List[str]:
        """Build date range list for API request."""
        start_dt = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
        end_dt = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
        
        dates = []
        current_date = start_dt
        while current_date <= end_dt:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += datetime.timedelta(days=1)
        
        return dates
    
    def _build_area_param(self, latitude: List[float], longitude: List[float]) -> List[float]:
        """Build area parameter for API request [North, West, South, East]."""
        north = max(latitude)
        south = min(latitude)
        west = min(longitude)
        east = max(longitude)
        
        return [north, west, south, east]
    
    def _execute_request(self, dataset: str, params: Dict[str, Any], output_path: Path):
        """Execute the CDS API request."""
        client = self.auth.get_client()
        
        logger.info(f"Submitting request to CDS API for dataset: {dataset}")
        logger.debug(f"Request parameters: {params}")
        
        # Submit the request
        request = client.retrieve(dataset, params, str(output_path))
        
        # Wait for completion with progress updates
        self._wait_for_completion(request, output_path)
    
    def _wait_for_completion(self, request, output_path: Path, check_interval: int = 30):
        """Wait for CDS request completion with progress updates."""
        logger.info("Request submitted. Waiting for completion...")
        start_time = time.time()
        
        while True:
            try:
                # Check if file exists (request completed)
                if output_path.exists() and output_path.stat().st_size > 0:
                    elapsed_time = time.time() - start_time
                    logger.info(f"Request completed in {elapsed_time:.1f} seconds")
                    break
                
                # Log progress
                elapsed_time = time.time() - start_time
                logger.info(f"Still waiting... ({elapsed_time:.0f}s elapsed)")
                
                # Wait before next check
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                logger.warning("Request interrupted by user")
                raise
            except Exception as e:
                logger.error(f"Error while waiting for request: {e}")
                raise
    
    def batch_extract(self, requests: List[Dict[str, Any]]) -> List[str]:
        """
        Execute multiple extraction requests in batch.
        
        Args:
            requests: List of request dictionaries, each containing parameters for extract_data()
            
        Returns:
            List of output file paths
            
        Raises:
            RuntimeError: If any batch request fails
        """
        logger.info(f"Starting batch extraction for {len(requests)} requests")
        
        results = []
        failed_requests = []
        
        for i, request in enumerate(requests):
            try:
                logger.info(f"Processing batch request {i+1}/{len(requests)}")
                output_path = self.extract_data(**request)
                results.append(output_path)
                
            except Exception as e:
                error_msg = f"Batch request {i+1} failed: {e}"
                logger.error(error_msg)
                failed_requests.append((i+1, error_msg))
                results.append(None)
        
        if failed_requests:
            error_summary = "\n".join([f"Request {i}: {msg}" for i, msg in failed_requests])
            logger.warning(f"Batch extraction completed with {len(failed_requests)} failures:\n{error_summary}")
        else:
            logger.info("All batch requests completed successfully")
        
        return results
    
    def list_available_variables(self, dataset: str) -> List[str]:
        """
        List available variables for a dataset.
        This is a placeholder - actual implementation would query CDS API.
        
        Args:
            dataset: Dataset identifier
            
        Returns:
            List of available variable names
        """
        # Placeholder implementation - would need actual CDS API query
        if dataset == 'era5':
            return list(self.config.ERA5_VARIABLES.values())
        
        logger.warning(f"Variable listing not implemented for dataset: {dataset}")
        return []