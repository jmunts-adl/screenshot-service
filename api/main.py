"""FastAPI application entry point."""

import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from api.config import HOST, PORT, API_TITLE, API_VERSION, API_DESCRIPTION
from api.routes import screenshot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    version=API_VERSION,
    description=API_DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(screenshot.router)


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "healthy", "service": API_TITLE, "version": API_VERSION}
    )


@app.get("/", tags=["root"])
async def root():
    """Root endpoint."""
    return JSONResponse(
        content={
            "service": API_TITLE,
            "version": API_VERSION,
            "docs": "/docs",
            "health": "/health"
        }
    )


if __name__ == "__main__":
    import uvicorn
    logger.info(f"Starting {API_TITLE} on {HOST}:{PORT}")
    uvicorn.run(app, host=HOST, port=PORT)

