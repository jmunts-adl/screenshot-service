"""Bearer token authentication dependency."""

import secrets
import logging
from fastapi import HTTPException, status, Header
from typing import Annotated
from api.config import API_TOKEN, API_TOKEN_REQUIRED

logger = logging.getLogger(__name__)


async def verify_token(
    authorization: Annotated[str | None, Header()] = None
) -> None:
    """
    Verify Bearer token from Authorization header.
    
    Args:
        authorization: Authorization header value (format: "Bearer <token>")
        
    Raises:
        HTTPException: 401 Unauthorized if token is missing, invalid format, or doesn't match
    """
    # If auth is disabled, skip verification
    if not API_TOKEN_REQUIRED:
        return
    
    # Check if API_TOKEN is configured
    if not API_TOKEN:
        logger.error("API_TOKEN not configured but API_TOKEN_REQUIRED is True")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication is misconfigured",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if Authorization header is present
    if not authorization:
        logger.warning("Missing Authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Parse Bearer token from header
    parts = authorization.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        logger.warning(f"Invalid Authorization header format: {authorization[:20]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected: Bearer <token>",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = parts[1].strip()
    
    # Validate token using timing-safe comparison
    if not secrets.compare_digest(token, API_TOKEN):
        logger.warning("Invalid token provided")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Token is valid
    logger.debug("Token verified successfully")

