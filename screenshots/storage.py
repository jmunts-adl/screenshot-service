"""Storage backend abstraction for screenshot uploads (Cloudinary and AWS S3 + CloudFront)."""

import logging
import os
import re
import uuid
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger(__name__)


class StorageBackend(ABC):
    """Abstract interface for uploading image bytes and receiving a public URL."""

    @abstractmethod
    def upload_bytes(
        self,
        data: bytes,
        folder: Optional[str] = None,
        key: Optional[str] = None,
        content_type: str = "image/jpeg",
    ) -> str:
        """
        Upload image bytes and return the public URL.

        Args:
            data: Image bytes to upload.
            folder: Optional folder/path prefix (e.g. "screenshots/2024/12").
            key: Optional object key (filename). If None, a unique key is generated.
            content_type: MIME type (default image/jpeg).

        Returns:
            Public URL of the uploaded file.
        """
        ...


class CloudinaryBackend(StorageBackend):
    """Upload to Cloudinary; returns Cloudinary URL."""

    def __init__(self) -> None:
        self._configured = False

    def _validate_config(self) -> None:
        if not os.getenv("CLOUDINARY_CLOUD_NAME"):
            raise ValueError("CLOUDINARY_CLOUD_NAME not found in environment variables")
        if not os.getenv("CLOUDINARY_API_KEY"):
            raise ValueError("CLOUDINARY_API_KEY not found in environment variables")
        if not os.getenv("CLOUDINARY_API_SECRET"):
            raise ValueError("CLOUDINARY_API_SECRET not found in environment variables")

    def _ensure_configured(self) -> None:
        if self._configured:
            return
        self._validate_config()
        import cloudinary
        import cloudinary.uploader as uploader_module  # noqa: F401

        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME", ""),
            api_key=os.getenv("CLOUDINARY_API_KEY", ""),
            api_secret=os.getenv("CLOUDINARY_API_SECRET", ""),
        )
        self._configured = True

    def upload_bytes(
        self,
        data: bytes,
        folder: Optional[str] = None,
        key: Optional[str] = None,
        content_type: str = "image/jpeg",
    ) -> str:
        self._ensure_configured()
        import cloudinary.uploader

        upload_options: dict = {"resource_type": "image"}
        if folder:
            upload_options["folder"] = folder
        if key:
            upload_options["public_id"] = key

        result = cloudinary.uploader.upload(data, **upload_options)
        uploaded_url = result.get("secure_url") or result.get("url")
        if not uploaded_url:
            raise Exception("Cloudinary upload succeeded but no URL returned")
        logger.info(f"Image uploaded to Cloudinary: {uploaded_url}")
        return uploaded_url


def _sanitize_key(key: str) -> str:
    """Remove or replace characters that are unsafe in S3 object keys."""
    key = key.replace(" ", "_")
    key = re.sub(r"[^\w\-./]", "", key)
    return key[:200] or "image"


class S3Backend(StorageBackend):
    """Upload to S3; return CloudFront URL (delivery via CloudFront)."""

    def __init__(
        self,
        region: str,
        bucket: str,
        cloudfront_domain: str,
        prefix: str = "",
    ) -> None:
        self.region = region
        self.bucket = bucket
        self.cloudfront_domain = cloudfront_domain.rstrip("/")
        if not self.cloudfront_domain.startswith("http"):
            self.cloudfront_domain = f"https://{self.cloudfront_domain}"
        self.prefix = (prefix.strip("/") + "/").lstrip("/") if prefix else ""

    def _validate_config(self) -> None:
        if not self.region:
            raise ValueError("AWS_REGION is required when STORAGE_PROVIDER=aws")
        if not self.bucket:
            raise ValueError("AWS_S3_BUCKET is required when STORAGE_PROVIDER=aws")
        if not self.cloudfront_domain or self.cloudfront_domain == "https://":
            raise ValueError(
                "AWS_CLOUDFRONT_DOMAIN is required when STORAGE_PROVIDER=aws "
                "(e.g. d123abc.cloudfront.net or cdn.example.com)"
            )

    def upload_bytes(
        self,
        data: bytes,
        folder: Optional[str] = None,
        key: Optional[str] = None,
        content_type: str = "image/jpeg",
    ) -> str:
        self._validate_config()

        if not key:
            ext = "jpg" if "jpeg" in content_type else "png"
            key = f"{uuid.uuid4().hex}.{ext}"
        else:
            key = _sanitize_key(key)

        parts = [self.prefix.rstrip("/")]
        if folder:
            parts.append(folder.strip("/"))
        parts.append(key)
        object_key = "/".join(p for p in parts if p).lstrip("/")

        import boto3
        from botocore.exceptions import ClientError

        client = boto3.client("s3", region_name=self.region)
        try:
            client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=data,
                ContentType=content_type,
            )
        except ClientError as e:
            logger.error(f"Failed to upload image to S3: {e}")
            raise Exception(f"S3 upload failed: {e}") from e

        uploaded_url = f"{self.cloudfront_domain.rstrip('/')}/{object_key}"
        logger.info(f"Image uploaded to S3, URL: {uploaded_url}")
        return uploaded_url


def get_storage_backend(provider: Optional[str] = None) -> StorageBackend:
    """
    Return the storage backend for the given provider.
    Uses STORAGE_PROVIDER from environment if provider is None.
    """
    from api.config import (
        AWS_CLOUDFRONT_DOMAIN,
        AWS_REGION,
        AWS_S3_BUCKET,
        AWS_S3_PREFIX,
        STORAGE_PROVIDER,
    )

    effective = (provider or os.getenv("STORAGE_PROVIDER") or STORAGE_PROVIDER or "cloudinary").lower()
    if effective == "cloudinary":
        return CloudinaryBackend()
    if effective == "aws":
        return S3Backend(
            region=AWS_REGION,
            bucket=AWS_S3_BUCKET,
            cloudfront_domain=AWS_CLOUDFRONT_DOMAIN,
            prefix=AWS_S3_PREFIX,
        )
    raise ValueError(f"Unknown STORAGE_PROVIDER: {effective}. Use 'cloudinary' or 'aws'.")
