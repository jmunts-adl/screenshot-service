"""Screenshot capture using ScreenshotOne API with proxy support."""

import os
import json
import logging
import random
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import requests

logger = logging.getLogger(__name__)

load_dotenv()

SCREENSHOT_DIR = Path('output/screenshots')
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)


def _call_screenshotone_api(
    url: str,
    proxy: Optional[str] = None
) -> str:
    """
    Call ScreenshotOne API and return the screenshot URL without saving.
    
    Args:
        url: The URL to capture a screenshot of
        proxy: Proxy to use. If None, uses SCREENSHOTONE_PROXY env var (simple proxy).
               If provided, uses that proxy string directly (e.g., WEB_UNLOCKER_PROXY value).
        
    Returns:
        Screenshot URL from ScreenshotOne API
        
    Raises:
        ValueError: If SCREENSHOTONE_ACCESS_KEY is not found or no screenshot URL in response
        requests.exceptions.RequestException: If API request fails
    """
    access_key = os.getenv('SCREENSHOTONE_ACCESS_KEY')
    if not access_key:
        raise ValueError('SCREENSHOTONE_ACCESS_KEY not found in environment variables')
    
    # Use provided proxy, or fall back to SCREENSHOTONE_PROXY env var if proxy is None
    if proxy is None:
        proxy = os.getenv('SCREENSHOTONE_PROXY')
    
    # Detect proxy type and log appropriately
    if proxy:
        # Check if this is WEB_UNLOCKER_PROXY (advanced/expensive proxy)
        web_unlocker_proxy = os.getenv('WEB_UNLOCKER_PROXY')
        is_advanced_proxy = web_unlocker_proxy and proxy == web_unlocker_proxy
        proxy_type = 'WEB_UNLOCKER_PROXY (advanced)' if is_advanced_proxy else 'basic proxy'
        
        proxy_preview = proxy[:50] + '...' if len(proxy) > 50 else proxy
        logger.info(f'Capturing screenshot with {proxy_type}: {proxy_preview}')
    else:
        logger.info('Capturing screenshot without proxy')
    
    params = {
        'access_key': access_key,
        'url': url,
        'response_type': 'json',
        'format': 'jpeg',
        'image_quality': 70,
        'cache': 'true',
        'cache_ttl': 2505600,
        'fail_if_content_contains': 'Verify you are human',
        'fail_if_content_contains': 'blocked'
    }
    
    if proxy:
        params['proxy'] = proxy
    
    response = requests.get('https://api.screenshotone.com/take', params=params)
    
    # Parse JSON response for error handling - always attempt to parse (API may return JSON even without proper Content-Type)
    response_json = None
    try:
        response_json = response.json()
    except (ValueError, json.JSONDecodeError):
        # JSON parsing failed
        pass
    
    if response.status_code != 200:
        error_msg = f'API Error {response.status_code}'
        
        if response_json:
            if 'error_message' in response_json:
                error_msg += f': {response_json["error_message"]}'
            if 'returned_status_code' in response_json:
                error_msg += f' (target site returned {response_json["returned_status_code"]})'
            if 'error_code' in response_json:
                error_msg += f' [Error Code: {response_json["error_code"]}]'
            # Always include full JSON details for debugging
            error_msg += f'\nFull error details: {json.dumps(response_json, indent=2)}'
        else:
            # No JSON response, show raw response text
            error_msg += f': {response.text[:500]}'
        
        response.raise_for_status()
        raise requests.exceptions.RequestException(error_msg)
    
    data = response_json if response_json else response.json()
    
    # Check for screenshot URL in multiple possible fields: 'screenshot', 'screenshot_url', or 'cache_url'
    screenshot_url = data.get('screenshot') or data.get('screenshot_url') or data.get('cache_url')
    
    if not screenshot_url:
        raise ValueError(f'No screenshot URL in response: {data}')
    
    # Determine proxy type for logging
    if proxy:
        web_unlocker_proxy = os.getenv('WEB_UNLOCKER_PROXY')
        is_advanced_proxy = web_unlocker_proxy and proxy == web_unlocker_proxy
        if is_advanced_proxy:
            proxy_type = 'WEB_UNLOCKER_PROXY (advanced)'
        else:
            proxy_type = 'basic proxy (SCREENSHOTONE_PROXY)'
    else:
        proxy_type = 'no proxy'
    
    logger.info(f'Screenshot URL obtained successfully using {proxy_type}')
    
    return screenshot_url


def capture_screenshot(
    url: str,
    proxy: Optional[str] = None,
    output_path: Optional[Path] = None
) -> Path:
    """
    Capture a screenshot of a URL using ScreenshotOne API.
    
    Args:
        url: The URL to capture a screenshot of
        proxy: Proxy to use. If None, uses SCREENSHOTONE_PROXY env var (simple proxy).
               If provided, uses that proxy string directly (e.g., WEB_UNLOCKER_PROXY value).
        output_path: Optional path to save the screenshot. If None, auto-generates filename.
        
    Returns:
        Path to the saved screenshot file
        
    Raises:
        ValueError: If SCREENSHOTONE_ACCESS_KEY is not found
        requests.exceptions.RequestException: If API request fails
        Exception: If screenshot download or save fails
    """
    screenshot_url = _call_screenshotone_api(url, proxy)
    
    try:
        # Download the screenshot
        img_response = requests.get(screenshot_url, timeout=30)
        img_response.raise_for_status()
        
        # Generate filename if not provided
        if output_path is None:
            filename = url.replace('https://', '').replace('http://', '').replace('/', '_')[:50] + '.jpeg'
            output_path = SCREENSHOT_DIR / filename
        
        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(img_response.content)
        
        proxy_type = 'proxy' if proxy else 'no proxy'
        logger.info(f'Screenshot captured successfully using {proxy_type}. Saved to: {output_path}')
        
        return output_path
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(f'Error downloading screenshot: {e}') from e
    except Exception as e:
        raise Exception(f'Error saving screenshot: {e}') from e


def get_screenshot_url(
    url: str,
    proxy: Optional[str] = None
) -> str:
    """
    Get screenshot URL from ScreenshotOne API without saving the file.
    
    Args:
        url: The URL to capture a screenshot of
        proxy: Optional proxy to use. If None, uses SCREENSHOTONE_PROXY env var.
        
    Returns:
        Screenshot URL from ScreenshotOne API
        
    Raises:
        ValueError: If SCREENSHOTONE_ACCESS_KEY is not found
        requests.exceptions.RequestException: If API request fails
    """
    return _call_screenshotone_api(url, proxy)


def take_screenshot(
    url: str,
    output_path: Optional[Path] = None
) -> Path:
    """
    Capture a screenshot with automatic retry logic.
    
    First attempts with simple proxy (SCREENSHOTONE_PROXY), then falls back to
    better proxy (WEB_UNLOCKER_PROXY) if the first attempt fails.
    
    Args:
        url: The URL to capture a screenshot of
        output_path: Optional path to save the screenshot. If None, auto-generates filename.
        
    Returns:
        Path to the saved screenshot file
        
    Raises:
        Exception: If both simple and advanced proxy attempts fail
    """
    # First attempt: simple proxy (SCREENSHOTONE_PROXY env var)
    simple_proxy = os.getenv('SCREENSHOTONE_PROXY')
    logger.info('Attempting screenshot capture with basic proxy (SCREENSHOTONE_PROXY)')
    
    try:
        random_number = random.randint(1, 10)
        
        # Append random port number to proxy URL (proxy URL doesn't include port)
        proxy_with_random = simple_proxy + f":{random_number}" if simple_proxy else None
        
        result = capture_screenshot(url, proxy=proxy_with_random, output_path=output_path)
        
        # Defensive check: verify result is valid before considering it a success
        if not result or not isinstance(result, Path):
            raise ValueError(f'Invalid screenshot path returned from basic proxy: {result}')
        
        # Log explicit success message before returning - this ensures we only reach here on actual success
        logger.info('Basic proxy succeeded - returning result (no fallback needed)')
        return result
        
    except Exception as e:
        # Only enter this block if an actual exception occurred
        logger.warning(f'Basic proxy attempt failed: {e}. Falling back to WEB_UNLOCKER_PROXY...')
        
        # If simple proxy fails, retry with better proxy
        better_proxy = os.getenv('WEB_UNLOCKER_PROXY')
        if not better_proxy:
            raise Exception(
                f'Simple proxy failed and WEB_UNLOCKER_PROXY not found. '
                f'Original error: {e}'
            ) from e
        
        try:
            logger.info('Attempting screenshot capture with WEB_UNLOCKER_PROXY (fallback)')
            result = capture_screenshot(url, proxy=better_proxy, output_path=output_path)
            
            # Defensive check: verify result is valid
            if not result or not isinstance(result, Path):
                raise ValueError(f'Invalid screenshot path returned from WEB_UNLOCKER_PROXY: {result}')
            
            logger.info('WEB_UNLOCKER_PROXY succeeded (fallback used)')
            return result
            
        except Exception as retry_error:
            logger.error(f'WEB_UNLOCKER_PROXY attempt also failed: {retry_error}')
            raise Exception(
                f'Both simple and advanced proxy attempts failed. '
                f'Simple proxy error: {e}. '
                f'Advanced proxy error: {retry_error}'
            ) from retry_error


def get_screenshot_url_with_retry(
    url: str
) -> str:
    """
    Get screenshot URL with automatic retry logic.
    
    First attempts with simple proxy (SCREENSHOTONE_PROXY), then falls back to
    better proxy (WEB_UNLOCKER_PROXY) if the first attempt fails.
    
    Args:
        url: The URL to capture a screenshot of
        
    Returns:
        Screenshot URL from ScreenshotOne API
        
    Raises:
        ValueError: If SCREENSHOTONE_ACCESS_KEY is not found
        requests.exceptions.RequestException: If both proxy attempts fail
    """
    # First attempt: simple proxy (SCREENSHOTONE_PROXY env var)
    simple_proxy = os.getenv('SCREENSHOTONE_PROXY')
    logger.info('Attempting screenshot capture with basic proxy (SCREENSHOTONE_PROXY)')
    
    try:
        random_number = random.randint(1, 10)
        
        # Append random port number to proxy URL (proxy URL doesn't include port)
        proxy_with_random = simple_proxy + f":{random_number}" if simple_proxy else None
        
        result = get_screenshot_url(url, proxy=proxy_with_random)
        
        # Defensive check: verify result is valid before considering it a success
        if not result or not isinstance(result, str) or not result.strip():
            raise ValueError(f'Invalid screenshot URL returned from basic proxy: {result}')
        
        # Log explicit success message before returning - this ensures we only reach here on actual success
        logger.info('Basic proxy succeeded - returning result (no fallback needed)')
        return result
        
    except Exception as e:
        # Only enter this block if an actual exception occurred
        logger.warning(f'Basic proxy attempt failed: {e}. Falling back to WEB_UNLOCKER_PROXY...')
        
        # If simple proxy fails, retry with better proxy
        better_proxy = os.getenv('WEB_UNLOCKER_PROXY')
        if not better_proxy:
            raise Exception(
                f'Simple proxy failed and WEB_UNLOCKER_PROXY not found. '
                f'Original error: {e}'
            ) from e
        
        try:
            logger.info('Attempting screenshot capture with WEB_UNLOCKER_PROXY (fallback)')
            result = get_screenshot_url(url, proxy=better_proxy)
            
            # Defensive check: verify result is valid
            if not result or not isinstance(result, str) or not result.strip():
                raise ValueError(f'Invalid screenshot URL returned from WEB_UNLOCKER_PROXY: {result}')
            
            logger.info('WEB_UNLOCKER_PROXY succeeded (fallback used)')
            return result
            
        except Exception as retry_error:
            logger.error(f'WEB_UNLOCKER_PROXY attempt also failed: {retry_error}')
            raise Exception(
                f'Both simple and advanced proxy attempts failed. '
                f'Simple proxy error: {e}. '
                f'Advanced proxy error: {retry_error}'
            ) from retry_error


if __name__ == '__main__':
    url = "https://www.glassdoor.com/Reviews/Employee-Review-FirstService-Residential-E307071-RVW94681350.htm"
    # Generate output path from the URL: strip http(s), replace slashes, and trim long names
    safe_filename = url.replace('https://', '').replace('http://', '').replace('/', '_')[:50] + '.jpeg'
    output_path = Path('output/screenshots') / safe_filename
    take_screenshot(url, output_path)

