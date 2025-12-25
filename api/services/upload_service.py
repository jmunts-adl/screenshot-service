"""Screenshot capture and upload service."""

import logging
from typing import Optional
from screenshots.capture import get_screenshot_url, get_screenshot_url_with_retry
from screenshots.upload import upload_screenshot_from_url
from api.config import CLOUDINARY_FOLDER

logger = logging.getLogger(__name__)


def capture_and_upload_screenshot(
    url: str,
    proxy: Optional[str] = None,
    use_retry: bool = True,
    folder: Optional[str] = None
) -> tuple[str, str]:
    """
    Capture a screenshot and upload it to Cloudinary.
    
    Args:
        url: The URL to capture a screenshot of
        proxy: Optional proxy to use. If None and use_retry is True, will use retry logic.
        use_retry: If True, uses retry logic (basic proxy then advanced proxy fallback).
                   If False, uses the provided proxy or SCREENSHOTONE_PROXY directly.
        folder: Optional Cloudinary folder path. If not provided, uses CLOUDINARY_FOLDER env var.
        
    Returns:
        Tuple of (screenshot_url, uploaded_url):
        - screenshot_url: The ScreenshotOne URL
        - uploaded_url: The Cloudinary URL
        
    Raises:
        ValueError: If SCREENSHOTONE_ACCESS_KEY or Cloudinary credentials are not found
        requests.exceptions.RequestException: If API request or download fails
        Exception: If upload fails
    """
    # Step 1: Capture screenshot and get ScreenshotOne URL
    if use_retry and proxy is None:
        logger.info(f'Capturing screenshot with retry logic for URL: {url}')
        screenshot_url = get_screenshot_url_with_retry(url)
    else:
        logger.info(f'Capturing screenshot with {"provided proxy" if proxy else "default proxy"} for URL: {url}')
        screenshot_url = get_screenshot_url(url, proxy=proxy)
    
    logger.info(f'Screenshot captured, ScreenshotOne URL: {screenshot_url}')
    
    # Step 2: Upload to Cloudinary
    uploaded_url = upload_screenshot_from_url(
        image_url=screenshot_url,
        folder=folder,
        default_folder=CLOUDINARY_FOLDER
    )
    
    logger.info(f'Screenshot uploaded to Cloudinary: {uploaded_url}')
    
    return screenshot_url, uploaded_url

