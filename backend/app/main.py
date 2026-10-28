"""
Main application entry point for the Assistive AI Platform.

This file initializes the FastAPI application, configures middleware,
and includes all API routers.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api import inference, ocr, vlm, tts, websocket
from .services.object_detection_service import get_object_detection_service
from .services.vlm_service import get_vlm_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Maximum frame size in bytes (500KB) to prevent DoS
MAX_FRAME_SIZE = 500_000


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown"""
    # Startup
    logger.info("Starting Assistive AI Platform...")

    # Warm up object detection model
    try:
        logger.info("Warming up object detection model...")
        detection_service = get_object_detection_service()
        # Create a dummy image for warm-up
        import numpy as np
        dummy_img = np.zeros((480, 640, 3), dtype=np.uint8)
        detection_service.detect_objects(dummy_img)
        logger.info("Object detection model warmed up successfully")
    except Exception as e:
        logger.warning(f"Object detection warm-up failed: {e}")

    # Warm up VLM model
    try:
        logger.info("Warming up VLM model...")
        vlm_service = get_vlm_service()
        vlm_service.warm_up()
        logger.info("VLM model warmed up successfully")
    except Exception as e:
        logger.warning(f"VLM warm-up failed: {e}")

    # Initialize OCR service (loads model on first use)
    try:
        from .services.ocr_service import get_ocr_service
        get_ocr_service()
        logger.info("OCR service initialized")
    except Exception as e:
        logger.warning(f"OCR service initialization failed: {e}")

    logger.info("Assistive AI Platform started successfully")

    yield

    # Shutdown
    logger.info("Shutting down Assistive AI Platform...")
    try:
        from .services.tts_service import get_tts_service
        tts_service = get_tts_service()
        tts_service.stop()
        logger.info("TTS service stopped")
    except Exception as e:
        logger.error(f"Error stopping TTS service: {e}")

    logger.info("Assistive AI Platform shut down complete")


app = FastAPI(
    title="Assistive AI Platform",
    description="Real-time computer vision and multimodal AI for visually impaired users",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to trusted origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler for validation errors
@app.exception_handler(413)
async def request_entity_too_large_handler(request: Request, exc):
    return JSONResponse(
        status_code=413,
        content={"detail": "Frame size exceeds maximum allowed (500KB). Please reduce image quality or resolution."}
    )


@app.middleware("http")
async def validate_frame_size(request: Request, call_next):
    """Middleware to validate frame size in requests"""
    # Check content length for frame endpoints
    if request.url.path in ["/detect", "/ocr", "/describe"]:
        content_length = request.headers.get("content-length")
        if content_length and int(content_length) > MAX_FRAME_SIZE * 2:  # Base64 is ~33% larger
            return JSONResponse(
                status_code=413,
                content={"detail": "Request too large. Maximum frame size is 500KB."}
            )
    return await call_next(request)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Assistive AI Platform"}


@app.get("/")
async def root():
    return {
        "service": "Assistive AI Platform",
        "version": "1.0.0",
        "description": "Real-time computer vision and multimodal AI for visually impaired users",
        "endpoints": {
            "health": "/health",
            "detect": "/detect",
            "ocr": "/ocr",
            "describe": "/describe",
            "tts": "/speak",
            "websocket": "/ws/{client_id}"
        }
    }


# Include routers
app.include_router(inference.router, prefix="/api", tags=["inference"])
app.include_router(ocr.router, prefix="/api", tags=["ocr"])
app.include_router(vlm.router, prefix="/api", tags=["vlm"])
app.include_router(tts.router, prefix="/api", tags=["tts"])

# Add WebSocket route directly (include_router doesn't properly include websocket routes)
app.router.websocket("/ws/{client_id}")(websocket.websocket_endpoint)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)