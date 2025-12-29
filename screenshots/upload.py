"""Cloud service upload for screenshots."""

import os
import logging
from io import BytesIO
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import requests

logger = logging.getLogger(__name__)

load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
    api_key=os.getenv("CLOUDINARY_API_KEY", ""),
    api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
)


def _validate_cloudinary_config():
    """Validate that Cloudinary credentials are configured."""
    if not os.getenv("CLOUDINARY_CLOUD_NAME"):
        raise ValueError("CLOUDINARY_CLOUD_NAME not found in environment variables")
    
    if not os.getenv("CLOUDINARY_API_KEY"):
        raise ValueError("CLOUDINARY_API_KEY not found in environment variables")
    
    if not os.getenv("CLOUDINARY_API_SECRET"):
        raise ValueError("CLOUDINARY_API_SECRET not found in environment variables")


def upload_image_from_bytes(
    image_bytes: bytes,
    folder: Optional[str] = None,
    public_id: Optional[str] = None
) -> str:
    """
    Upload an image to Cloudinary from bytes.
    
    Args:
        image_bytes: The image data as bytes
        folder: Optional Cloudinary folder path (e.g., "screenshots/2024/12")
        public_id: Optional public ID for the image. If not provided, Cloudinary will generate one.
        
    Returns:
        URL of the uploaded file in Cloudinary
        
    Raises:
        ValueError: If Cloudinary credentials are not configured
        Exception: If upload fails
    """
    _validate_cloudinary_config()
    
    try:
        upload_options = {
            "resource_type": "image",
        }
        
        if folder:
            upload_options["folder"] = folder
        
        if public_id:
            upload_options["public_id"] = public_id
        
        result = cloudinary.uploader.upload(
            image_bytes,
            **upload_options
        )
        
        uploaded_url = result.get("secure_url") or result.get("url")
        if not uploaded_url:
            raise Exception("Cloudinary upload succeeded but no URL returned")
        
        logger.info(f"Image uploaded to Cloudinary: {uploaded_url}")
        return uploaded_url
        
    except Exception as e:
        logger.error(f"Failed to upload image to Cloudinary: {e}")
        raise Exception(f"Cloudinary upload failed: {e}") from e


def upload_screenshot(
    file_path: Path,
    service: str = "cloudinary",
    folder: Optional[str] = None
) -> str:
    """
    Upload a screenshot to a cloud service.
    
    Args:
        file_path: Path to the screenshot file to upload
        service: Cloud service to use (default: "cloudinary")
        folder: Optional Cloudinary folder path (e.g., "screenshots/2024/12")
        
    Returns:
        URL of the uploaded file
        
    Raises:
        ValueError: If Cloudinary credentials are not configured
        Exception: If upload fails
    """
    if service != "cloudinary":
        raise ValueError(f"Service '{service}' is not supported. Only 'cloudinary' is currently supported.")
    
    _validate_cloudinary_config()
    
    try:
        # Read file
        with open(file_path, 'rb') as f:
            file_data = f.read()
        
        # Use the filename without extension as the public_id
        public_id = file_path.stem
        
        return upload_image_from_bytes(
            image_bytes=file_data,
            folder=folder,
            public_id=public_id
        )
        
    except Exception as e:
        logger.error(f"Failed to upload screenshot to Cloudinary: {e}")
        raise Exception(f"Cloudinary upload failed: {e}") from e


def upload_screenshot_from_url(
    image_url: str,
    folder: Optional[str] = None,
    default_folder: Optional[str] = None
) -> str:
    """
    Download an image from a URL and upload it to Cloudinary.
    
    This is a convenience function that combines download and upload.
    For pure upload functionality, use upload_image_from_bytes() directly.
    
    Args:
        image_url: URL of the image to download and upload
        folder: Optional Cloudinary folder path (takes precedence over default_folder)
        default_folder: Optional default folder from environment variable
        
    Returns:
        URL of the uploaded file in Cloudinary
        
    Raises:
        ValueError: If Cloudinary credentials are not configured
        requests.exceptions.RequestException: If download fails
        Exception: If upload fails
    """
    _validate_cloudinary_config()
    
    # Determine folder to use (request folder > default folder > env var > None)
    upload_folder = folder
    if not upload_folder:
        upload_folder = default_folder or os.getenv("CLOUDINARY_FOLDER")
    
    try:
        # Download image from URL
        logger.info(f"Downloading image from URL: {image_url}")
        img_response = requests.get(image_url, timeout=30)
        img_response.raise_for_status()
        
        # Generate a public_id from the URL (sanitized)
        public_id = image_url.replace('https://', '').replace('http://', '').replace('/', '_')[:100]
        
        # Upload using the pure upload function
        uploaded_url = upload_image_from_bytes(
            image_bytes=img_response.content,
            folder=upload_folder,
            public_id=public_id
        )
        
        folder_used = upload_folder or "root"
        logger.info(f"Screenshot uploaded to Cloudinary folder '{folder_used}': {uploaded_url}")
        return uploaded_url
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to download image from URL: {e}")
        raise requests.exceptions.RequestException(f"Error downloading image: {e}") from e
    except Exception as e:
        logger.error(f"Failed to upload screenshot to Cloudinary: {e}")
        raise Exception(f"Cloudinary upload failed: {e}") from e

