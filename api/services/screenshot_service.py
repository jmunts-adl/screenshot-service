"""Screenshot capture service with retry logic."""

import logging
from typing import Optional
from screenshots.capture import get_screenshot_url, get_screenshot_url_with_retry

logger = logging.getLogger(__name__)


def capture_screenshot_url(
    url: str,
    proxy: Optional[str] = None,
    use_retry: bool = True
) -> str:
    """
    Get screenshot URL from ScreenshotOne API.
    
    Args:
        url: The URL to capture a screenshot of
        proxy: Optional proxy to use. If None and use_retry is True, will use retry logic.
        use_retry: If True, uses retry logic (basic proxy then advanced proxy fallback).
                   If False, uses the provided proxy or SCREENSHOTONE_PROXY directly.
        
    Returns:
        Screenshot URL from ScreenshotOne API
        
    Raises:
        ValueError: If SCREENSHOTONE_ACCESS_KEY is not found
        requests.exceptions.RequestException: If API request fails
    """
    if use_retry and proxy is None:
        # Use retry logic: try basic proxy, then fallback to advanced proxy
        logger.info(f'Capturing screenshot with retry logic for URL: {url}')
        return get_screenshot_url_with_retry(url)
    else:
        # Use provided proxy or direct call
        logger.info(f'Capturing screenshot with {"provided proxy" if proxy else "default proxy"} for URL: {url}')
        return get_screenshot_url(url, proxy=proxy)

