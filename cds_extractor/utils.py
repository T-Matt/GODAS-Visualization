"""
Utility functions for data validation and processing.
"""

import logging
from typing import List, Tuple, Union, Optional, Dict, Any
from pathlib import Path
import datetime

logger = logging.getLogger(__name__)


def validate_coordinates(longitude: Union[float, List[float]], 
                        latitude: Union[float, List[float]]) -> Tuple[List[float], List[float]]:
    """
    Validate and normalize longitude and latitude coordinates.
    
    Args:
        longitude: Single longitude or list of longitudes (-180 to 180)
        latitude: Single latitude or list of latitudes (-90 to 90)
        
    Returns:
        Tuple of normalized longitude and latitude lists
        
    Raises:
        ValueError: If coordinates are invalid
    """
    # Convert to lists if single values
    if isinstance(longitude, (int, float)):
        longitude = [float(longitude)]
    if isinstance(latitude, (int, float)):
        latitude = [float(latitude)]
    
    # Validate longitude range
    for lon in longitude:
        if not -180 <= lon <= 180:
            raise ValueError(f"Longitude {lon} must be between -180 and 180")
    
    # Validate latitude range
    for lat in latitude:
        if not -90 <= lat <= 90:
            raise ValueError(f"Latitude {lat} must be between -90 and 90")
    
    logger.debug(f"Validated coordinates: lon={longitude}, lat={latitude}")
    return longitude, latitude


def validate_vertical_levels(levels: Union[int, List[int], str, List[str]], 
                           dataset_type: str = 'pressure') -> List[str]:
    """
    Validate and normalize vertical levels.
    
    Args:
        levels: Vertical levels (pressure levels in hPa or model levels)
        dataset_type: Type of dataset ('pressure' or 'model')
        
    Returns:
        List of validated level strings
        
    Raises:
        ValueError: If levels are invalid
    """
    if isinstance(levels, (int, str)):
        levels = [levels]
    
    # Convert to strings
    levels = [str(level) for level in levels]
    
    if dataset_type == 'pressure':
        # Common pressure levels
        valid_pressure_levels = [
            '1000', '925', '850', '700', '600', '500', '400', '300', 
            '250', '200', '150', '100', '70', '50', '30', '20', '10', '7', '5', '3', '2', '1'
        ]
        for level in levels:
            if level not in valid_pressure_levels:
                logger.warning(f"Pressure level {level} may not be available for all datasets")
    
    logger.debug(f"Validated vertical levels: {levels}")
    return levels


def validate_time_range(start_date: Union[str, datetime.date], 
                       end_date: Union[str, datetime.date]) -> Tuple[str, str]:
    """
    Validate and normalize time range.
    
    Args:
        start_date: Start date (YYYY-MM-DD format or date object)
        end_date: End date (YYYY-MM-DD format or date object)
        
    Returns:
        Tuple of validated date strings in YYYY-MM-DD format
        
    Raises:
        ValueError: If dates are invalid or end_date is before start_date
    """
    def parse_date(date_input: Union[str, datetime.date]) -> datetime.date:
        if isinstance(date_input, str):
            try:
                return datetime.datetime.strptime(date_input, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.datetime.strptime(date_input, '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    raise ValueError(f"Invalid date format: {date_input}. Use YYYY-MM-DD")
        elif isinstance(date_input, datetime.date):
            return date_input
        else:
            raise ValueError(f"Invalid date type: {type(date_input)}")
    
    start_dt = parse_date(start_date)
    end_dt = parse_date(end_date)
    
    if end_dt < start_dt:
        raise ValueError(f"End date {end_dt} cannot be before start date {start_dt}")
    
    # Check if dates are not too far in the future
    today = datetime.date.today()
    if start_dt > today:
        raise ValueError(f"Start date {start_dt} cannot be in the future")
    
    start_str = start_dt.strftime('%Y-%m-%d')
    end_str = end_dt.strftime('%Y-%m-%d')
    
    logger.debug(f"Validated time range: {start_str} to {end_str}")
    return start_str, end_str


def validate_variables(variables: Union[str, List[str]], 
                      dataset: str) -> List[str]:
    """
    Validate variable names for the specified dataset.
    
    Args:
        variables: Single variable name or list of variable names
        dataset: Dataset identifier
        
    Returns:
        List of validated variable names
        
    Raises:
        ValueError: If variables are invalid for the dataset
    """
    if isinstance(variables, str):
        variables = [variables]
    
    # For now, we'll accept any string variables and let the API validate them
    # This could be extended with dataset-specific validation
    if not all(isinstance(var, str) and var.strip() for var in variables):
        raise ValueError("All variables must be non-empty strings")
    
    variables = [var.strip() for var in variables]
    logger.debug(f"Validated variables for {dataset}: {variables}")
    return variables


def create_output_filename(dataset: str, 
                          variables: List[str],
                          start_date: str,
                          end_date: str,
                          coordinates: Optional[Tuple[List[float], List[float]]] = None,
                          format: str = 'nc') -> str:
    """
    Create a standardized output filename.
    
    Args:
        dataset: Dataset name
        variables: List of variable names
        start_date: Start date string
        end_date: End date string
        coordinates: Optional coordinate bounds
        format: File format ('nc' or 'grib')
        
    Returns:
        Generated filename
    """
    # Clean variable names for filename
    var_str = '_'.join(var.replace(' ', '_') for var in variables[:3])  # Limit to first 3 variables
    if len(variables) > 3:
        var_str += f'_and_{len(variables)-3}_more'
    
    # Date range string
    date_str = f"{start_date}_to_{end_date}"
    
    # Coordinate string
    coord_str = ""
    if coordinates:
        lon_list, lat_list = coordinates
        if len(lon_list) == 1 and len(lat_list) == 1:
            coord_str = f"_{lon_list[0]}lon_{lat_list[0]}lat"
        else:
            coord_str = "_regional"
    
    filename = f"{dataset}_{var_str}_{date_str}{coord_str}.{format}"
    
    # Clean filename
    filename = filename.replace(' ', '_').replace('/', '_')
    
    logger.debug(f"Created filename: {filename}")
    return filename


def ensure_output_directory(output_path: Union[str, Path]) -> Path:
    """
    Ensure output directory exists.
    
    Args:
        output_path: Path to output file or directory
        
    Returns:
        Path object for the directory
    """
    path = Path(output_path)
    if path.suffix:  # It's a file
        directory = path.parent
    else:  # It's a directory
        directory = path
    
    directory.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Ensured output directory exists: {directory}")
    return directory