"""Screenshot capture module with proxy retry logic and cloud upload support."""

from screenshots.capture import capture_screenshot, take_screenshot
from screenshots.upload import upload_screenshot

__all__ = ['capture_screenshot', 'take_screenshot', 'upload_screenshot']

