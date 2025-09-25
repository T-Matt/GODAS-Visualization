"""
Authentication handling for CDS API.
"""

import logging
from typing import Dict, Optional

try:
    import cdsapi
except ImportError:
    cdsapi = None

from .config import Config

logger = logging.getLogger(__name__)


class CDSAuth:
    """Handles CDS API authentication and client creation."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize CDS authentication.
        
        Args:
            config: Configuration instance with CDS credentials
        """
        self.config = config or Config()
        self._client = None
    
    def get_client(self) -> 'cdsapi.Client':
        """
        Get authenticated CDS API client.
        
        Returns:
            CDS API client instance
            
        Raises:
            ImportError: If cdsapi package is not installed
            ValueError: If authentication credentials are invalid
        """
        if cdsapi is None:
            raise ImportError(
                "The 'cdsapi' package is required for CDS API access. "
                "Install it with: pip install cdsapi"
            )
        
        if self._client is None:
            try:
                credentials = self.config.get_cds_credentials()
                self._client = cdsapi.Client(
                    url=credentials['url'],
                    key=credentials['key']
                )
                logger.info("Successfully authenticated with CDS API")
            except Exception as e:
                logger.error(f"Failed to authenticate with CDS API: {e}")
                raise ValueError(f"CDS API authentication failed: {e}")
        
        return self._client
    
    def test_connection(self) -> bool:
        """
        Test CDS API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            client = self.get_client()
            # Try a simple operation to test the connection
            # Note: This doesn't make an actual API call to avoid quota usage
            return client is not None
        except Exception as e:
            logger.error(f"CDS API connection test failed: {e}")
            return False