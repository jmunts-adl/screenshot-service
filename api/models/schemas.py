"""Pydantic schemas for API request/response models."""

from pydantic import BaseModel, HttpUrl, Field


class CaptureRequest(BaseModel):
    """Request model for screenshot capture endpoint."""
    
    url: HttpUrl = Field(..., description="The URL to capture a screenshot of")
    proxy: str | None = Field(None, description="Optional proxy to use for the capture")


class CaptureResponse(BaseModel):
    """Response model for screenshot capture endpoint."""
    
    screenshot_url: str = Field(..., description="The URL of the captured screenshot from ScreenshotOne")
    url: str = Field(..., description="The original URL that was captured")


class CaptureUploadRequest(BaseModel):
    """Request model for screenshot capture and upload endpoint."""
    
    url: HttpUrl = Field(..., description="The URL to capture a screenshot of")
    proxy: str | None = Field(None, description="Optional proxy to use for the capture")
    folder: str | None = Field(None, description="Optional Cloudinary folder path (e.g., 'screenshots/2024/12')")


class CaptureUploadResponse(BaseModel):
    """Response model for screenshot capture and upload endpoint."""
    
    uploaded_url: str = Field(..., description="The URL of the uploaded screenshot in Cloudinary")
    screenshot_url: str = Field(..., description="The URL of the captured screenshot from ScreenshotOne")
    url: str = Field(..., description="The original URL that was captured")
    folder: str | None = Field(None, description="The Cloudinary folder where the file was saved")


class ZenRowsCaptureRequest(BaseModel):
    """Request model for ZenRows screenshot capture and upload endpoint."""
    
    url: HttpUrl = Field(..., description="The URL to capture a screenshot of")
    wait_for: str | None = Field(None, description="Optional CSS selector to wait for before capturing")
    folder: str | None = Field(None, description="Optional Cloudinary folder path (e.g., 'screenshots/2024/12')")


class ZenRowsCaptureResponse(BaseModel):
    """Response model for ZenRows screenshot capture and upload endpoint."""
    
    uploaded_url: str = Field(..., description="The URL of the uploaded screenshot in Cloudinary")
    url: str = Field(..., description="The original URL that was captured")
    folder: str | None = Field(None, description="The Cloudinary folder where the file was saved")


class UploadScreenshotOneRequest(BaseModel):
    """Request model for uploading a ScreenshotOne URL to Cloudinary."""
    
    screenshot_url: HttpUrl = Field(..., description="The ScreenshotOne URL to upload")
    folder: str | None = Field(None, description="Optional Cloudinary folder path (e.g., 'screenshots/2024/12')")


class UploadScreenshotOneResponse(BaseModel):
    """Response model for uploading a ScreenshotOne URL to Cloudinary."""
    
    uploaded_url: str = Field(..., description="The URL of the uploaded screenshot in Cloudinary")
    screenshot_url: str = Field(..., description="The original ScreenshotOne URL that was uploaded")
    folder: str | None = Field(None, description="The Cloudinary folder where the file was saved")

