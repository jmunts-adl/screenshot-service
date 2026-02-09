"""Cloud service upload for screenshots (Cloudinary or AWS S3 + CloudFront)."""

import os
import logging
from pathlib import Path
from typing import Optional

import requests

from screenshots.storage import StorageBackend, get_storage_backend

logger = logging.getLogger(__name__)

_backend: Optional[StorageBackend] = None


def _get_backend() -> StorageBackend:
    global _backend
    if _backend is None:
        _backend = get_storage_backend()
    return _backend


def upload_image_from_bytes(
    image_bytes: bytes,
    folder: Optional[str] = None,
    public_id: Optional[str] = None
) -> str:
    """
    Upload an image to the configured storage (Cloudinary or AWS) from bytes.

    Args:
        image_bytes: The image data as bytes
        folder: Optional folder path (e.g. "screenshots/2024/12")
        public_id: Optional key/filename. If not provided, a unique key is generated.

    Returns:
        URL of the uploaded file (Cloudinary or CloudFront when using AWS)

    Raises:
        ValueError: If storage credentials are not configured
        Exception: If upload fails
    """
    backend = _get_backend()
    return backend.upload_bytes(
        data=image_bytes,
        folder=folder,
        key=public_id,
    )


def upload_screenshot(
    file_path: Path,
    service: str = "cloudinary",
    folder: Optional[str] = None
) -> str:
    """
    Upload a screenshot file to the configured storage.

    Args:
        file_path: Path to the screenshot file to upload
        service: Ignored; storage is determined by STORAGE_PROVIDER env.
        folder: Optional folder path (e.g. "screenshots/2024/12")

    Returns:
        URL of the uploaded file

    Raises:
        ValueError: If storage credentials are not configured
        Exception: If upload fails
    """
    if service not in ("cloudinary", "aws"):
        raise ValueError(f"Service '{service}' is not supported. Use 'cloudinary' or 'aws' (or set STORAGE_PROVIDER).")

    with open(file_path, "rb") as f:
        file_data = f.read()

    public_id = file_path.stem
    return upload_image_from_bytes(
        image_bytes=file_data,
        folder=folder,
        public_id=public_id
    )


def upload_screenshot_from_url(
    image_url: str,
    folder: Optional[str] = None,
    default_folder: Optional[str] = None
) -> str:
    """
    Download an image from a URL and upload it to the configured storage.

    Args:
        image_url: URL of the image to download and upload
        folder: Optional folder path (takes precedence over default_folder)
        default_folder: Optional default folder (e.g. from config)

    Returns:
        URL of the uploaded file

    Raises:
        ValueError: If storage credentials are not configured
        requests.exceptions.RequestException: If download fails
        Exception: If upload fails
    """
    upload_folder = folder or default_folder or os.getenv("CLOUDINARY_FOLDER")

    logger.info(f"Downloading image from URL: {image_url}")
    img_response = requests.get(image_url, timeout=30)
    img_response.raise_for_status()

    public_id = image_url.replace("https://", "").replace("http://", "").replace("/", "_")[:100]

    uploaded_url = upload_image_from_bytes(
        image_bytes=img_response.content,
        folder=upload_folder,
        public_id=public_id
    )

    folder_used = upload_folder or "root"
    logger.info(f"Screenshot uploaded to folder '{folder_used}': {uploaded_url}")
    return uploaded_url
