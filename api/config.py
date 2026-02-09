"""Configuration for the API service."""

import os
from dotenv import load_dotenv

load_dotenv()

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))

# API configuration
API_TITLE = "Screenshot Capture Service"
API_VERSION = "1.0.0"
API_DESCRIPTION = (
    "A microservice for capturing screenshots using ScreenshotOne API. "
    "Protected endpoints require Bearer token authentication via the Authorization header."
)

# Authentication configuration
API_TOKEN = os.getenv("API_TOKEN", "")
API_TOKEN_REQUIRED = os.getenv("API_TOKEN_REQUIRED", "true").lower() in ("true", "1", "yes")

# Storage provider: "cloudinary" or "aws" (default: cloudinary)
STORAGE_PROVIDER = os.getenv("STORAGE_PROVIDER", "cloudinary")

# Cloudinary configuration (used when STORAGE_PROVIDER=cloudinary)
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "")

# AWS configuration (used when STORAGE_PROVIDER=aws)
# CloudFront domain is required for delivery URLs (e.g. d123abc.cloudfront.net or cdn.example.com)
AWS_REGION = os.getenv("AWS_REGION", "")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET", "")
AWS_S3_PREFIX = os.getenv("AWS_S3_PREFIX", "")
AWS_CLOUDFRONT_DOMAIN = os.getenv("AWS_CLOUDFRONT_DOMAIN", "")

