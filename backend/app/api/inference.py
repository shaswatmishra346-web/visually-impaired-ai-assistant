"""
Inference API Endpoints
Handles object detection requests using the ObjectDetectionService
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import base64
import numpy as np
import cv2
import time
import logging
from typing import List, Dict, Any

from ..services.object_detection_service import get_object_detection_service
from ..core.geometry import estimate_distance, get_direction, format_detection, DEFAULT_FOCAL_FACTOR

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize object detection service (singleton)
detection_service = get_object_detection_service()

# Maximum frame size in bytes (500KB) to prevent DoS
MAX_FRAME_SIZE = 500_000

class FrameRequest(BaseModel):
    frame: str  # base64 encoded JPEG image

class Detection(BaseModel):
    bbox: List[float]  # [x_min, y_min, x_max, y_max] in original image coordinates
    label: str
    confidence: float
    distance: float  # estimated distance in meters (approximate)
    direction: str     # "left", "center", "right" based on horizontal position

class DetectionResponse(BaseModel):
    detections: List[Detection]
    latency_ms: float
    fps: float
    performance_ok: bool

def preprocess_image_for_service(img: np.ndarray) -> np.ndarray:
    """
    Preprocess image for compatibility with detection service
    (converts to format expected by OpenCV/NumPy operations)
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

@router.post("/detect", response_model=DetectionResponse)
async def detect_objects(request: FrameRequest):
    """
    Real-time object detection using ONNX YOLO model via detection service.
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

    # Record start time for latency measurement
    start_time = time.time()

    # Perform detection using service
    detection_result = detection_service.detect_objects(img_processed)

    # Calculate latency
    end_time = time.time()
    latency_ms = (end_time - start_time) * 1000

    # Extract detections from service result
    raw_detections = detection_result.get('detections', [])

    # Format detections with distance and direction estimation
    image_height, image_width = img.shape[:2]
    formatted_detections = [
        format_detection(det, image_width, image_height, DEFAULT_FOCAL_FACTOR)
        for det in raw_detections
    ]

    # Get performance stats from service
    perf_stats = detection_service.get_performance_stats()

    response = DetectionResponse(
        detections=formatted_detections,
        latency_ms=latency_ms,
        fps=perf_stats.get('fps', 0.0),
        performance_ok=detection_service.is_performance_acceptable()
    )

    # Log performance warnings
    if latency_ms > 50.0:  # 50ms max latency from SRS
        logger.warning(f"Detection latency {latency_ms:.2f}ms exceeds 50ms threshold")

    if response.fps < 15.0:  # 15 FPS min from SRS
        logger.warning(f"FPS {response.fps:.2f} below 15 FPS minimum")

    return response