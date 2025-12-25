import os
import requests
from dotenv import load_dotenv

load_dotenv()


def test_screenshot_with_proxy(target_url: str) -> requests.Response:
    """
    Test screenshot capture using ScreenshotOne API with proxy.
    
    Args:
        target_url: The URL to capture a screenshot of
        
    Returns:
        The response object from the ScreenshotOne API
    """
    proxy = os.getenv('WEB_UNLOCKER_PROXY')
    api_key = os.getenv('SCREENSHOTONE_ACCESS_KEY')
    api_url = "https://api.screenshotone.com/take"
    
    if not proxy:
        raise ValueError("WEB_UNLOCKER_PROXY not found in environment variables")
    if not api_key:
        raise ValueError("SCREENSHOTONE_ACCESS_KEY not found in environment variables")
    
    # According to ScreenshotOne API docs, the API key parameter must be 'access_key', not 'key'
    params = {
        'access_key': api_key,
        'url': target_url,
        'proxy': proxy,
        'response_type': 'json',  # To get a JSON API result for better error handling
        'format': 'jpeg',         # Example: request jpeg image
    }
    
    response = requests.get(api_url, params=params)
    print(response.url)
    print(f"Status code: {response.status_code}")
    print(response.text[:500])
    
    return response


if __name__ == '__main__':
    target_url = "https://www.glassdoor.com/Reviews/Employee-Review-Wise-E637715-RVW94482642.htm"
    test_screenshot_with_proxy(target_url)

