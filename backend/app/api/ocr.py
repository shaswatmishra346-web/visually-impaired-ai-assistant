"""
OCR API Endpoint
Handles optical character recognition requests using the OCRService
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import numpy as np
import cv2
import time
import logging
from typing import List, Dict, Any

from ..services.ocr_service import get_ocr_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize OCR service (singleton)
ocr_service = get_ocr_service()

# Maximum frame size in bytes (500KB) to prevent DoS
MAX_FRAME_SIZE = 500_000

class FrameRequest(BaseModel):
    frame: str  # base64 encoded JPEG image

class OCRResult(BaseModel):
    text: str
    confidence: float
    bbox: list  # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] quadrilateral

class OCRResponse(BaseModel):
    results: list[OCRResult]
    processing_time_ms: float
    texts_processed: int

def preprocess_image_for_service(img: np.ndarray) -> np.ndarray:
    """
    Preprocess image for compatibility with OCR service
    """
    # Ensure image is in correct format (BGR numpy array)
    if isinstance(img, np.ndarray):
        return img
    else:
        # Convert from other formats if needed
        return np.array(img)

def validate_frame_size(frame_b64: str) -> None:
    """Validate frame size to prevent DoS attacks"""
    if len(frame_b64) > MAX_FRAME_SIZE * 2:  # Base64 is ~33% larger
        raise HTTPException(
            status_code=413,
            detail=f"Frame size exceeds maximum allowed ({MAX_FRAME_SIZE} bytes decoded). "
                   f"Please reduce image quality or resolution."
        )

@router.post("/ocr", response_model=OCRResponse)
async def perform_ocr(request: FrameRequest):
    """
    Optical Character Recognition using EasyOCR via OCR service.
    """
    # Validate frame size
    validate_frame_size(request.frame)

    try:
        # Decode base64 image
        img_data = base64.b64decode(request.frame)

        # Additional validation: check decoded size
        if len(img_data) > MAX_FRAME_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"Decoded frame size exceeds maximum allowed ({MAX_FRAME_SIZE} bytes)."
            )

        nparr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not process image: {e}")

    # Preprocess image for service
    img_processed = preprocess_image_for_service(img)

    # Record start time for performance measurement
    start_time = time.time()

    # Perform OCR using service
    ocr_results = ocr_service.recognize_text(img_processed)

    # Calculate processing time
    end_time = time.time()
    processing_time_ms = (end_time - start_time) * 1000

    # Format results for response
    formatted_results = []
    for result in ocr_results:
        formatted_results.append(OCRResult(
            text=result['text'],
            confidence=result['confidence'],
            bbox=result['bbox']
        ))

    # Get performance stats from service
    perf_stats = ocr_service.get_performance_stats()

    response = OCRResponse(
        results=formatted_results,
        processing_time_ms=processing_time_ms,
        texts_processed=perf_stats.get('texts_processed', 0)
    )

    return response