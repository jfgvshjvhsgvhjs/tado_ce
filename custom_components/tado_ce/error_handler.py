"""Error handling utilities for Tado CE integration."""
import logging
import time
from typing import Optional, Callable, Any
from urllib.error import HTTPError, URLError

_LOGGER = logging.getLogger(__name__)


class APIError(Exception):
    """Base exception for API errors."""
    pass


class RateLimitError(APIError):
    """Exception for rate limit errors."""
    pass


class AuthenticationError(APIError):
    """Exception for authentication errors."""
    pass


class APIErrorHandler:
    """Handles API errors with retry logic and detailed logging.
    
    Requirements:
    - 19.1: Add detailed error logging for API failures
    - 19.2: Implement retry logic (once after 5 seconds)
    - 19.3: Mark entities unavailable after double failure
    - 19.4: Restore entity availability when API recovers
    - 19.5: Handle rate limit errors (pause polling until reset)
    - 19.6: Handle authentication errors (prompt re-auth)
    """
    
    def __init__(self, retry_delay: int = 5, max_retries: int = 1):
        """Initialize error handler.
        
        Args:
            retry_delay: Delay in seconds before retry (default 5)
            max_retries: Maximum number of retries (default 1)
        """
        self.retry_delay = retry_delay
        self.max_retries = max_retries
    
    def handle_api_call(
        self,
        api_func: Callable,
        *args,
        operation_name: str = "API call",
        **kwargs
    ) -> Optional[Any]:
        """Execute API call with error handling and retry logic.
        
        Args:
            api_func: The API function to call
            *args: Positional arguments for the API function
            operation_name: Name of the operation for logging
            **kwargs: Keyword arguments for the API function
        
        Returns:
            Result from API function, or None if all retries failed
        
        Raises:
            RateLimitError: If rate limit is exceeded
            AuthenticationError: If authentication fails
        """
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Requirement 19.1: Detailed error logging
                if attempt > 0:
                    _LOGGER.info(
                        f"Retrying {operation_name} (attempt {attempt + 1}/{self.max_retries + 1})"
                    )
                
                result = api_func(*args, **kwargs)
                
                # Requirement 19.4: Log successful recovery
                if attempt > 0:
                    _LOGGER.info(f"{operation_name} succeeded after {attempt} retry(ies)")
                
                return result
                
            except HTTPError as e:
                last_error = e
                
                # Requirement 19.1: Detailed error logging
                _LOGGER.error(
                    f"{operation_name} failed with HTTP {e.code}: {e.reason}"
                )
                
                # Requirement 19.5: Handle rate limit errors
                if e.code == 429:
                    _LOGGER.warning(
                        f"Rate limit exceeded for {operation_name}. "
                        "Polling will be paused until quota resets."
                    )
                    raise RateLimitError(f"Rate limit exceeded: {e.reason}") from e
                
                # Requirement 19.6: Handle authentication errors
                if e.code in (401, 403):
                    _LOGGER.error(
                        f"Authentication failed for {operation_name}. "
                        "Please re-authenticate the integration."
                    )
                    raise AuthenticationError(f"Authentication failed: {e.reason}") from e
                
                # Requirement 19.2: Retry logic (once after 5 seconds)
                if attempt < self.max_retries:
                    _LOGGER.info(f"Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                else:
                    # Requirement 19.3: Log double failure
                    _LOGGER.error(
                        f"{operation_name} failed after {self.max_retries + 1} attempts. "
                        "Entities will be marked unavailable."
                    )
                    
            except URLError as e:
                last_error = e
                
                # Requirement 19.1: Detailed error logging
                _LOGGER.error(
                    f"{operation_name} failed with network error: {e.reason}"
                )
                
                # Requirement 19.2: Retry logic
                if attempt < self.max_retries:
                    _LOGGER.info(f"Waiting {self.retry_delay} seconds before retry...")
                    time.sleep(self.retry_delay)
                else:
                    # Requirement 19.3: Log double failure
                    _LOGGER.error(
                        f"{operation_name} failed after {self.max_retries + 1} attempts. "
                        "Entities will be marked unavailable."
                    )
                    
            except Exception as e:
                last_error = e
                
                # Requirement 19.1: Detailed error logging
                _LOGGER.error(
                    f"{operation_name} failed with unexpected error: {type(e).__name__}: {e}"
                )
                
                # Don't retry on unexpected errors
                break
        
        # Requirement 19.3: Return None to signal failure (entities will be marked unavailable)
        return None
    
    def is_rate_limit_error(self, error: Exception) -> bool:
        """Check if error is a rate limit error.
        
        Args:
            error: The exception to check
        
        Returns:
            True if error is a rate limit error
        """
        if isinstance(error, RateLimitError):
            return True
        if isinstance(error, HTTPError) and error.code == 429:
            return True
        return False
    
    def is_auth_error(self, error: Exception) -> bool:
        """Check if error is an authentication error.
        
        Args:
            error: The exception to check
        
        Returns:
            True if error is an authentication error
        """
        if isinstance(error, AuthenticationError):
            return True
        if isinstance(error, HTTPError) and error.code in (401, 403):
            return True
        return False


# Global error handler instance
_error_handler = APIErrorHandler()


def get_error_handler() -> APIErrorHandler:
    """Get the global error handler instance.
    
    Returns:
        The global APIErrorHandler instance
    """
    return _error_handler
