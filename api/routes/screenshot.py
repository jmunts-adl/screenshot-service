"""Screenshot capture API routes."""

import logging
from fastapi import APIRouter, HTTPException, status, Depends
from api.models.schemas import (
    CaptureRequest, 
    CaptureResponse, 
    CaptureUploadRequest, 
    CaptureUploadResponse,
    ZenRowsCaptureRequest,
    ZenRowsCaptureResponse,
    UploadScreenshotOneRequest,
    UploadScreenshotOneResponse
)
from api.services.screenshot_service import (
    capture_screenshot_url, 
    capture_and_upload_screenshot,
    upload_screenshotone_url_to_cloudinary
)
from api.services.zenrows_service import capture_and_upload_with_zenrows
from api.dependencies.auth import verify_token
from api.config import CLOUDINARY_FOLDER

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/capture", tags=["screenshot"])


@router.post(
    "",
    response_model=CaptureResponse,
    status_code=status.HTTP_200_OK,
    summary="Capture a screenshot",
    description="Capture a screenshot of the provided URL using ScreenshotOne API. "
                "Returns the screenshot URL without saving the file locally. "
                "Uses retry logic: attempts with basic proxy first, then falls back to advanced proxy if needed. "
                "Requires Bearer token authentication via Authorization header.",
    response_description="The screenshot URL from ScreenshotOne API"
)
async def capture_screenshot(
    request: CaptureRequest,
    _: None = Depends(verify_token)
) -> CaptureResponse:
    """
    Capture a screenshot of a URL.
    
    Requires Bearer token authentication. Include the token in the Authorization header:
    `Authorization: Bearer <your-token>`
    
    Args:
        request: Capture request containing URL and optional proxy
        
    Returns:
        CaptureResponse with screenshot URL and original URL
        
    Raises:
        HTTPException: 401 if authentication fails, 500 if screenshot capture fails
    """
    try:
        # Convert HttpUrl to string for the capture function
        url_str = str(request.url)
        
        # Use retry logic if no proxy is provided, otherwise use the provided proxy
        use_retry = request.proxy is None
        
        screenshot_url = capture_screenshot_url(
            url=url_str,
            proxy=request.proxy,
            use_retry=use_retry
        )
        
        logger.info(f"Successfully captured screenshot for URL: {url_str}")
        
        return CaptureResponse(
            screenshot_url=screenshot_url,
            url=url_str
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to capture screenshot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to capture screenshot: {str(e)}"
        )


@router.post(
    "/and-upload",
    response_model=CaptureUploadResponse,
    status_code=status.HTTP_200_OK,
    summary="Capture and upload a screenshot",
    description="Capture a screenshot of the provided URL using ScreenshotOne API, "
                "download it, and upload it to Cloudinary. Returns the Cloudinary URL. "
                "Uses retry logic: attempts with basic proxy first, then falls back to advanced proxy if needed. "
                "Requires Bearer token authentication via Authorization header.",
    response_description="The Cloudinary URL of the uploaded screenshot"
)
async def capture_and_upload_screenshot_endpoint(
    request: CaptureUploadRequest,
    _: None = Depends(verify_token)
) -> CaptureUploadResponse:
    """
    Capture a screenshot and upload it to Cloudinary.
    
    Requires Bearer token authentication. Include the token in the Authorization header:
    `Authorization: Bearer <your-token>`
    
    Args:
        request: Capture and upload request containing URL, optional proxy, and optional folder
        
    Returns:
        CaptureUploadResponse with Cloudinary URL, ScreenshotOne URL, original URL, and folder
        
    Raises:
        HTTPException: 401 if authentication fails, 500 if capture or upload fails
    """
    try:
        # Convert HttpUrl to string for the capture function
        url_str = str(request.url)
        
        # Use retry logic if no proxy is provided, otherwise use the provided proxy
        use_retry = request.proxy is None
        
        # Determine folder to use
        folder = request.folder or CLOUDINARY_FOLDER or None
        
        screenshot_url, uploaded_url = capture_and_upload_screenshot(
            url=url_str,
            proxy=request.proxy,
            use_retry=use_retry,
            folder=folder
        )
        
        logger.info(f"Successfully captured and uploaded screenshot for URL: {url_str}")
        
        return CaptureUploadResponse(
            uploaded_url=uploaded_url,
            screenshot_url=screenshot_url,
            url=url_str,
            folder=folder
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to capture and upload screenshot: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to capture and upload screenshot: {str(e)}"
        )


@router.post(
    "/upload",
    response_model=UploadScreenshotOneResponse,
    status_code=status.HTTP_200_OK,
    summary="Upload a ScreenshotOne URL to Cloudinary",
    description="Upload an existing ScreenshotOne cache URL to Cloudinary. "
                "Downloads the image from the ScreenshotOne URL and uploads it to Cloudinary. "
                "Returns the Cloudinary URL. "
                "Requires Bearer token authentication via Authorization header.",
    response_description="The Cloudinary URL of the uploaded screenshot"
)
async def upload_screenshotone_url_endpoint(
    request: UploadScreenshotOneRequest,
    _: None = Depends(verify_token)
) -> UploadScreenshotOneResponse:
    """
    Upload a ScreenshotOne URL to Cloudinary.
    
    Requires Bearer token authentication. Include the token in the Authorization header:
    `Authorization: Bearer <your-token>`
    
    Args:
        request: Upload request containing ScreenshotOne URL and optional folder
        
    Returns:
        UploadScreenshotOneResponse with Cloudinary URL, original ScreenshotOne URL, and folder
        
    Raises:
        HTTPException: 401 if authentication fails, 500 if upload fails
    """
    try:
        # Convert HttpUrl to string for the upload function
        screenshot_url_str = str(request.screenshot_url)
        
        # Determine folder to use
        folder = request.folder or CLOUDINARY_FOLDER or None
        
        uploaded_url = upload_screenshotone_url_to_cloudinary(
            screenshot_url=screenshot_url_str,
            folder=folder
        )
        
        logger.info(f"Successfully uploaded ScreenshotOne URL to Cloudinary: {screenshot_url_str}")
        
        return UploadScreenshotOneResponse(
            uploaded_url=uploaded_url,
            screenshot_url=screenshot_url_str,
            folder=folder
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to upload ScreenshotOne URL to Cloudinary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload ScreenshotOne URL to Cloudinary: {str(e)}"
        )


@router.post(
    "/zenrows",
    response_model=ZenRowsCaptureResponse,
    status_code=status.HTTP_200_OK,
    summary="Capture and upload a screenshot using ZenRows",
    description="Capture a screenshot of the provided URL using ZenRows API and upload it to Cloudinary. "
                "Returns the Cloudinary URL. "
                "Uses JavaScript rendering and premium proxy. "
                "Requires Bearer token authentication via Authorization header.",
    response_description="The Cloudinary URL of the uploaded screenshot"
)
async def capture_with_zenrows_endpoint(
    request: ZenRowsCaptureRequest,
    _: None = Depends(verify_token)
) -> ZenRowsCaptureResponse:
    """
    Capture a screenshot using ZenRows API and upload it to Cloudinary.
    
    Requires Bearer token authentication. Include the token in the Authorization header:
    `Authorization: Bearer <your-token>`
    
    Args:
        request: ZenRows capture request containing URL, optional wait_for CSS selector, and optional folder
        
    Returns:
        ZenRowsCaptureResponse with Cloudinary URL, original URL, and folder
        
    Raises:
        HTTPException: 401 if authentication fails, 500 if capture or upload fails
    """
    try:
        # Convert HttpUrl to string for the capture function
        url_str = str(request.url)
        
        # Determine folder to use
        folder = request.folder or CLOUDINARY_FOLDER or None
        
        uploaded_url = capture_and_upload_with_zenrows(
            url=url_str,
            wait_for=request.wait_for,
            folder=folder
        )
        
        logger.info(f"Successfully captured and uploaded screenshot with ZenRows for URL: {url_str}")
        
        return ZenRowsCaptureResponse(
            uploaded_url=uploaded_url,
            url=url_str,
            folder=folder
        )
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Configuration error: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Failed to capture and upload screenshot with ZenRows: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to capture and upload screenshot with ZenRows: {str(e)}"
        )

