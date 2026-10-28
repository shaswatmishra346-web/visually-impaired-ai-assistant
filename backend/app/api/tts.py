"""
TTS API Endpoint
Handles text-to-speech conversion requests using the TTSService
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import time
import logging
from typing import Optional

from ..services.tts_service import get_tts_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize TTS service (singleton)
tts_service = get_tts_service()

class TTSRequest(BaseModel):
    text: str
    priority: Optional[int] = None  # None = standard priority
    block: bool = False  # Whether to wait for speech to complete

class TTSResponse(BaseModel):
    success: bool
    message: str
    queued: bool
    queue_size: int
    is_speaking: bool

@router.post("/speak", response_model=TTSResponse)
async def speak_text(request: TTSRequest):
    """
    Convert text to speech using the TTS service.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # Speak the text using the service
        tts_service.speak(
            text=request.text,
            priority=request.priority,
            block=request.block
        )

        # Get current status
        is_speaking = tts_service.is_busy()
        queue_size = tts_service.get_queue_size()

        response = TTSResponse(
            success=True,
            message="Text queued for speech synthesis",
            queued=True,
            queue_size=queue_size,
            is_speaking=is_speaking
        )

        logger.info(f"TTS request queued: '{request.text[:50]}{'...' if len(request.text) > 50 else ''}' "
                   f"(priority={request.priority}, block={request.block})")

        return response

    except Exception as e:
        logger.error(f"Error in TTS request: {e}")
        raise HTTPException(status_code=500, detail=f"TTS processing failed: {str(e)}")

@router.post("/speak/emergency", response_model=TTSResponse)
async def speak_emergency(request: TTSRequest):
    """
    Speak emergency text with highest priority.
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    try:
        # Speak the text as emergency (highest priority)
        tts_service.speak_emergency(
            text=request.text,
            block=request.block
        )

        # Get current status
        is_speaking = tts_service.is_busy()
        queue_size = tts_service.get_queue_size()

        response = TTSResponse(
            success=True,
            message="Emergency text queued for speech synthesis",
            queued=True,
            queue_size=queue_size,
            is_speaking=is_speaking
        )

        logger.warning(f"Emergency TTS request queued: '{request.text[:50]}{'...' if len(request.text) > 50 else ''}' "
                      f"(block={request.block})")

        return response

    except Exception as e:
        logger.error(f"Error in emergency TTS request: {e}")
        raise HTTPException(status_code=500, detail=f"Emergency TTS processing failed: {str(e)}")

@router.get("/status")
async def get_tts_status():
    """
    Get current TTS service status.
    """
    try:
        is_speaking = tts_service.is_busy()
        queue_size = tts_service.get_queue_size()

        return {
            "is_speaking": is_speaking,
            "queue_size": queue_size,
            "service_available": tts_service.engine is not None
        }
    except Exception as e:
        logger.error(f"Error getting TTS status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get TTS status: {str(e)}")

@router.post("/stop")
async def stop_tts():
    """
    Stop the TTS service and clear the queue.
    """
    try:
        tts_service.stop()
        return {
            "success": True,
            "message": "TTS service stopped"
        }
    except Exception as e:
        logger.error(f"Error stopping TTS service: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to stop TTS service: {str(e)}")