"""ZenRows API screenshot capture service."""

import logging
import os
from typing import Optional
import requests
from dotenv import load_dotenv
from screenshots.upload import upload_image_from_bytes
from api.config import CLOUDINARY_FOLDER

load_dotenv()

logger = logging.getLogger(__name__)


def capture_screenshot_with_zenrows(
    url: str,
    wait_for: Optional[str] = None,
    wait: Optional[int] = None
) -> bytes:
    """
    Capture a screenshot using ZenRows API.
    
    Args:
        url: The URL to capture a screenshot of
        wait_for: Optional CSS selector to wait for before capturing (overrides wait if provided)
        wait: Optional wait time in milliseconds before capturing (used only if wait_for is not provided)
        
    Returns:
        The image data as bytes
        
    Raises:
        ValueError: If ZENROWS_API_KEY is not found in environment variables
        requests.exceptions.RequestException: If API request fails
        ValueError: If response is not a valid image
    """
    apikey = os.getenv('ZENROWS_API_KEY')
    
    if not apikey:
        raise ValueError("ZENROWS_API_KEY not found in environment variables")
    
    params = {
        'url': url,
        'apikey': apikey,
        'js_render': 'true',
        'premium_proxy': 'true',
        'screenshot': 'true',
        'custom_headers': 'true',
    }
    
    # If wait_for is provided, it overrides wait
    if wait_for:
        params['wait_for'] = wait_for
    elif wait is not None:
        params['wait'] = wait
    
    headers = {
        "Referer": "https://www.google.com"
    }
    
    logger.info(f'Capturing screenshot with ZenRows for URL: {url}')
    
    try:
        response = requests.get('https://api.zenrows.com/v1/', params=params, headers=headers, timeout=60)
    except requests.exceptions.RequestException as e:
        logger.error(f"ZenRows API request exception: {e}")
        raise requests.exceptions.RequestException(
            f"ZenRows API request failed: {str(e)}"
        ) from e
    
    # Check response status
    if response.status_code != 200:
        error_message = response.text[:500] if response.text else "No error message provided"
        logger.error(f"ZenRows API returned status code {response.status_code}: {error_message}")
        raise requests.exceptions.RequestException(
            f"ZenRows API request failed with status {response.status_code}: {error_message}"
        )
    
    # Validate that response is an image
    content_type = response.headers.get('Content-Type', '').lower()
    is_image = 'image' in content_type
    
    if response.content:
        first_bytes = response.content[:20]
        
        # Check if it's a valid image format
        is_jpeg = first_bytes.startswith(b'\xff\xd8\xff')
        is_png = first_bytes.startswith(b'\x89PNG')
        
        if not (is_jpeg or is_png):
            # Check if it's an error message (JSON or HTML)
            if first_bytes.startswith(b'{') or first_bytes.startswith(b'<'):
                error_text = response.text[:500] if hasattr(response, 'text') else str(response.content[:500])
                logger.error(f"ZenRows API returned error response: {error_text}")
                raise ValueError(f"ZenRows API returned an error instead of an image: {error_text}")
            else:
                logger.warning(f"Unknown image format. First bytes: {first_bytes.hex()}")
                # Still return the content, but log a warning
    
    if not response.content:
        raise ValueError("ZenRows API returned empty response")
    
    logger.info(f"Successfully captured screenshot: {len(response.content)} bytes")
    
    return response.content


def capture_and_upload_with_zenrows(
    url: str,
    wait_for: Optional[str] = None,
    wait: Optional[int] = None,
    folder: Optional[str] = None
) -> str:
    """
    Capture a screenshot using ZenRows API and upload it to Cloudinary.
    
    Args:
        url: The URL to capture a screenshot of
        wait_for: Optional CSS selector to wait for before capturing (overrides wait if provided)
        wait: Optional wait time in milliseconds before capturing (used only if wait_for is not provided)
        folder: Optional Cloudinary folder path. If not provided, uses CLOUDINARY_FOLDER env var.
        
    Returns:
        The Cloudinary URL of the uploaded screenshot
        
    Raises:
        ValueError: If ZENROWS_API_KEY or Cloudinary credentials are not found
        requests.exceptions.RequestException: If API request fails
        Exception: If upload fails
    """
    # Step 1: Capture screenshot and get image bytes
    logger.info(f'Capturing screenshot with ZenRows for URL: {url}')
    image_bytes = capture_screenshot_with_zenrows(url=url, wait_for=wait_for, wait=wait)
    
    # Step 2: Upload to Cloudinary
    # Use folder as-is (endpoint already handles: request.folder or CLOUDINARY_FOLDER or None)
    # This matches ScreenshotOne behavior: pass folder directly, allowing None for root uploads
    public_id = url.replace('https://', '').replace('http://', '').replace('/', '_')[:100]
    
    uploaded_url = upload_image_from_bytes(
        image_bytes=image_bytes,
        folder=folder,
        public_id=public_id
    )
    
    logger.info(f'Screenshot uploaded to Cloudinary: {uploaded_url}')
    
    return uploaded_url

