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

# Cloudinary configuration
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")
CLOUDINARY_FOLDER = os.getenv("CLOUDINARY_FOLDER", "")

