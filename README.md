# Screenshot Service

A standalone microservice for capturing screenshots using ScreenshotOne API and uploading them to Cloudinary.

## Features

- Capture screenshots of URLs using ScreenshotOne API
- Automatic retry logic with proxy fallback (basic proxy → advanced proxy)
- Upload screenshots to Cloudinary
- Bearer token authentication
- RESTful API with FastAPI

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with the following variables:
```env
# Server configuration
HOST=0.0.0.0
PORT=8000

# Authentication
API_TOKEN=your-secret-token-here
API_TOKEN_REQUIRED=true

# ScreenshotOne API
SCREENSHOTONE_ACCESS_KEY=your-access-key
SCREENSHOTONE_PROXY=your-basic-proxy-url
WEB_UNLOCKER_PROXY=your-advanced-proxy-url

# Cloudinary
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
CLOUDINARY_FOLDER=screenshots
```

## Running the Service

```bash
python -m api.main
```

Or using uvicorn directly:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /capture

Capture a screenshot and return the ScreenshotOne URL.

**Request:**
```json
{
  "url": "https://example.com",
  "proxy": "optional-proxy-url"
}
```

**Response:**
```json
{
  "screenshot_url": "https://api.screenshotone.com/...",
  "url": "https://example.com"
}
```

### POST /capture/and-upload

Capture a screenshot and upload it to Cloudinary.

**Request:**
```json
{
  "url": "https://example.com",
  "proxy": "optional-proxy-url",
  "folder": "optional-cloudinary-folder"
}
```

**Response:**
```json
{
  "uploaded_url": "https://res.cloudinary.com/...",
  "screenshot_url": "https://api.screenshotone.com/...",
  "url": "https://example.com",
  "folder": "screenshots"
}
```

### GET /health

Health check endpoint.

### GET /

Root endpoint with service information.

## Authentication

All endpoints (except `/health` and `/`) require Bearer token authentication:

```
Authorization: Bearer <your-token>
```

## Documentation

API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

