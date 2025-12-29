"""Screenshot capture using Playwright sync API with stealth mode."""

from pathlib import Path
from playwright.sync_api import sync_playwright, Error as PlaywrightError
from playwright_stealth import stealth_sync
from typing import Optional

# Create output directory
OUTPUT_DIR = Path('output/screenshots')
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def capture_screenshot(
    url: str,
    output_path: Optional[Path] = None,
    proxy: Optional[str] = None,
    viewport_width: int = 1400,
    viewport_height: int = 900,
    wait_selector: str = "body[jscontroller], main, article",
    wait_timeout: int = 20000,
    navigation_timeout: int = 60000,
    headless: bool = True,
    full_page: bool = True,
    image_format: str = "jpeg",
    image_quality: int = 85
) -> Path:
    """
    Capture a screenshot of a URL using Playwright sync API with stealth mode.
    
    Args:
        url: The URL to capture a screenshot of
        output_path: Optional path to save the screenshot. If None, auto-generates filename.
        proxy: Optional proxy URL to use. Format: "http://host:port" or "https://host:port".
               If None, no proxy is used.
        viewport_width: Browser viewport width in pixels (default: 1400)
        viewport_height: Browser viewport height in pixels (default: 900)
        wait_selector: CSS selector to wait for before taking screenshot (default: "body[jscontroller], main, article")
        wait_timeout: Timeout in milliseconds for waiting for selector (default: 20000)
        navigation_timeout: Timeout in milliseconds for page navigation (default: 60000)
        headless: Whether to run browser in headless mode (default: True)
        full_page: Whether to capture full page screenshot (default: True)
        image_format: Image format - "jpeg" or "png" (default: "jpeg")
        image_quality: JPEG quality (1-100, only applies to JPEG format) (default: 85)
        
    Returns:
        Path to the saved screenshot file
        
    Raises:
        Exception: If screenshot capture fails
    """
    # Generate filename if not provided
    if output_path is None:
        filename = url.replace('https://', '').replace('http://', '').replace('/', '_')[:50]
        extension = 'jpg' if image_format == 'jpeg' else image_format
        output_path = OUTPUT_DIR / f"{filename}.{extension}"
    
    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"Taking screenshot of {url} with stealth mode...")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            proxy_dict = {"server": proxy} if proxy else None
            context = browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height},
                proxy=proxy_dict
            )
            page = context.new_page()
            
            # Apply stealth settings to the page
            stealth_sync(page)
            
            # Try networkidle first, fall back to load if it times out
            try:
                page.goto(url, wait_until="networkidle", timeout=navigation_timeout)
            except PlaywrightError:
                # If networkidle times out, try with "load" instead
                print("networkidle timed out, trying with 'load' wait strategy...")
                page.goto(url, wait_until="load", timeout=navigation_timeout)
            
            # Wait for something real on the page, not just "load"
            # Make selector wait optional - if it fails, continue anyway
            try:
                page.wait_for_selector(wait_selector, timeout=wait_timeout)
            except PlaywrightError:
                print(f"Selector '{wait_selector}' not found, proceeding with screenshot anyway...")
                # Wait a bit for any dynamic content
                page.wait_for_timeout(2000)
            
            # Take screenshot
            page.screenshot(
                path=str(output_path),
                full_page=full_page,
                type=image_format,
                quality=image_quality if image_format == "jpeg" else None
            )
            
            browser.close()
        
        print(f"Screenshot saved to: {output_path}")
        print(f"File size: {output_path.stat().st_size} bytes")
        
        return output_path
        
    except PlaywrightError as e:
        error_msg = str(e)
        # Check if this is a browser installation error
        if "Executable doesn't exist" in error_msg or "chromium" in error_msg.lower():
            raise Exception(
                f"Playwright browsers are not installed. Please run:\n"
                f"  playwright install chromium\n\n"
                f"Original error: {error_msg}"
            ) from e
        # Check if it's a proxy connection error
        if proxy and ("proxy" in error_msg.lower() or "connection" in error_msg.lower() or "network" in error_msg.lower()):
            raise Exception(
                f"Proxy connection failed. Please verify the proxy URL is correct and accessible.\n"
                f"Proxy: {proxy}\n"
                f"Original error: {error_msg}"
            ) from e
        # Check if it's a timeout error
        if "Timeout" in error_msg:
            raise Exception(
                f"Page navigation or loading timed out. The page may be slow or blocking requests.\n"
                f"Original error: {error_msg}"
            ) from e
        raise Exception(f"Playwright error: {error_msg}") from e
    except Exception as e:
        raise Exception(f"Error capturing screenshot: {e}") from e


if __name__ == '__main__':
    # Example usage
    URL = "http://www.glassdoor.com/Reviews/Employee-Review-The-Forum-Group-RVW5662855.htm"
    
    screenshot_path = capture_screenshot(URL)
    print(f"Successfully captured screenshot: {screenshot_path}")

