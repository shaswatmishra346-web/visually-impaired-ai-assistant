"""
VLM (Vision-Language Model) API Endpoint
Handles scene description requests using the VLMService
"""

import base64
import numpy as np
import cv2
import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.vlm_service import get_vlm_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize VLM service (singleton)
vlm_service = get_vlm_service()

# Maximum frame size in bytes (500KB) to prevent DoS
MAX_FRAME_SIZE = 500_000


class FrameRequest(BaseModel):
    frame: str  # base64 encoded JPEG image


class SceneDescription(BaseModel):
    description: str
    confidence: float  # Model confidence score (estimated)


class VLMResponse(BaseModel):
    description: SceneDescription


def validate_frame_size(frame_b64: str) -> None:
    """Validate frame size to prevent DoS attacks"""
    if len(frame_b64) > MAX_FRAME_SIZE * 2:  # Base64 is ~33% larger
        raise HTTPException(
            status_code=413,
            detail=f"Frame size exceeds maximum allowed ({MAX_FRAME_SIZE} bytes decoded). "
                   f"Please reduce image quality or resolution."
        )


@router.post("/describe", response_model=VLMResponse)
async def describe_scene(request: FrameRequest):
    """
    Generate scene description using Vision-Language Model (BLIP) via VLMService
    """
    # Validate frame size
    validate_frame_size(request.frame)

    try:
        # Decode base64 image
        try:
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

        # Generate description using VLM service
        import time
        start_time = time.time()
        description = vlm_service.describe_scene(img)
        generation_time = time.time() - start_time

        # Calculate a confidence score based on generation characteristics
        # Note: BLIP doesn't provide actual confidence scores, so we use heuristics
        base_confidence = 0.7
        time_bonus = min(0.2, 0.1 * (2.0 / max(generation_time, 0.1)))  # Faster = higher confidence
        length_bonus = min(0.1, len(description) / 200.0)  # Reasonable length = higher confidence
        confidence = min(0.95, base_confidence + time_bonus + length_bonus)

        logger.info(f"VLM scene description generated in {generation_time:.2f}s: '{description[:50]}...' (confidence: {confidence:.2f})")

        return VLMResponse(description=SceneDescription(
            description=description,
            confidence=confidence
        ))

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in VLM scene description: {e}")
        # Fallback to a basic description if VLM fails
        return VLMResponse(description=SceneDescription(
            description="Scene description temporarily unavailable - please ensure device is connected and try again",
            confidence=0.1
        ))


@router.get("/status")
async def get_vlm_status():
    """Get VLM service status and performance stats"""
    try:
        stats = vlm_service.get_performance_stats()
        return {
            "model_loaded": vlm_service._model_loaded,
            "device": vlm_service._device,
            "performance": stats
        }
    except Exception as e:
        logger.error(f"Error getting VLM status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get VLM status: {str(e)}")


@router.post("/warmup")
async def warmup_vlm():
    """Warm up the VLM model to reduce latency on first real request"""
    try:
        vlm_service.warm_up()
        return {"success": True, "message": "VLM model warmed up"}
    except Exception as e:
        logger.error(f"Error warming up VLM: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to warm up VLM: {str(e)}")