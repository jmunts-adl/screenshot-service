# Screenshot Service

A standalone microservice for capturing screenshots using ScreenshotOne API and uploading them to configured storage (Cloudinary or AWS S3 + CloudFront).

## Features

- Capture screenshots of URLs using ScreenshotOne API
- Automatic retry logic with proxy fallback (basic proxy → advanced proxy)
- Upload screenshots to Cloudinary or AWS (S3 with CloudFront delivery)
- Bearer token authentication
- RESTful API with FastAPI

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file (see `.env.example`). Storage is chosen via `STORAGE_PROVIDER`:

**Option A: Cloudinary (default)**  
Set `STORAGE_PROVIDER=cloudinary` or omit it. Configure:
```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
CLOUDINARY_FOLDER=screenshots
```

**Option B: AWS (S3 + CloudFront)**  
Set `STORAGE_PROVIDER=aws`. Uploads go to S3; returned URLs are CloudFront. Configure:
```env
STORAGE_PROVIDER=aws
AWS_REGION=eu-west-1
AWS_S3_BUCKET=your-bucket
AWS_CLOUDFRONT_DOMAIN=your-distribution.cloudfront.net
# Optional: AWS_S3_PREFIX=screenshots
```
Use IAM credentials (env `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` or instance role). Ensure the bucket is the CloudFront origin (OAI/OAC recommended).

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

Capture a screenshot and upload it to configured storage (Cloudinary or AWS). `uploaded_url` is a Cloudinary URL or CloudFront URL depending on `STORAGE_PROVIDER`.

**Request:**
```json
{
  "url": "https://example.com",
  "proxy": "optional-proxy-url",
  "folder": "optional-folder-path"
}
```

**Response:**
```json
{
  "uploaded_url": "https://res.cloudinary.com/... or https://xxx.cloudfront.net/...",
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

