"""
WebSocket Endpoint for Real-time Assistive AI Processing
Handles real-time video frame processing with object detection, OCR, and scene description
"""

import json
import base64
import hashlib
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List, Optional
import numpy as np
import cv2

from ..services.object_detection_service import get_object_detection_service
from ..services.ocr_service import get_ocr_service
from ..services.vlm_service import get_vlm_service
from ..core.geometry import format_detection

router = APIRouter()

logger = logging.getLogger(__name__)

# Maximum frame size in bytes (500KB) to prevent DoS
MAX_FRAME_SIZE = 500_000


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass  # Ignore send errors for disconnected clients


manager = ConnectionManager()


def compute_frame_hash(frame_b64: str) -> str:
    """Compute SHA256 hash of frame for deduplication"""
    return hashlib.sha256(frame_b64.encode()).hexdigest()[:16]


def validate_frame_size(frame_b64: str) -> bool:
    """Validate frame size to prevent DoS attacks. Returns True if valid, False otherwise."""
    if len(frame_b64) > MAX_FRAME_SIZE * 2:  # Base64 is ~33% larger
        return False
    return True


@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)

    # Initialize services
    detection_service = get_object_detection_service()
    ocr_service = get_ocr_service()
    vlm_service = get_vlm_service()

    # Frame deduplication
    last_frame_hash: Optional[str] = None

    try:
        while True:
            # Expect to receive JSON with a base64-encoded frame
            data = await websocket.receive_text()

            try:
                message = json.loads(data)
                frame_b64 = message.get("frame")
                if not frame_b64:
                    await websocket.send_text(json.dumps({"error": "Missing frame"}))
                    continue
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({"error": "Invalid JSON"}))
                continue

            # Validate frame size
            if not validate_frame_size(frame_b64):
                await websocket.send_text(json.dumps({
                    "error": f"Frame size exceeds maximum allowed ({MAX_FRAME_SIZE} bytes decoded)"
                }))
                continue

            # Frame deduplication - skip if identical to last frame
            frame_hash = compute_frame_hash(frame_b64)
            if frame_hash == last_frame_hash:
                # Send cached/previous results instead of reprocessing
                continue
            last_frame_hash = frame_hash

            # Decode base64 image
            try:
                img_data = base64.b64decode(frame_b64)

                # Additional validation: check decoded size
                if len(img_data) > MAX_FRAME_SIZE:
                    await websocket.send_text(json.dumps({
                        "error": f"Decoded frame size exceeds maximum allowed ({MAX_FRAME_SIZE} bytes)"
                    }))
                    continue

                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is None:
                    await websocket.send_text(json.dumps({"error": "Invalid image"}))
                    continue
            except Exception as e:
                await websocket.send_text(json.dumps({"error": f"Could not process image: {e}"}))
                continue

            # Initialize response containers
            detections = []
            ocr_results = []
            scene_description = ""

            # Call object detection service directly
            try:
                detection_result = detection_service.detect_objects(img)
                raw_detections = detection_result.get('detections', [])

                # Format detections with distance and direction estimation
                image_height, image_width = img.shape[:2]

                for det in raw_detections:
                    formatted = format_detection(det, image_width, image_height)
                    detections.append(formatted)

            except Exception as e:
                logger.error(f"Detection failed: {e}")

            # Call OCR service directly
            try:
                ocr_results = ocr_service.recognize_text(img)
            except Exception as e:
                logger.error(f"OCR failed: {e}")

            # Call VLM service directly
            try:
                scene_description = vlm_service.describe_scene(img)
            except Exception as e:
                logger.error(f"VLM failed: {e}")
                scene_description = "Scene description temporarily unavailable"

            # Send back the combined results
            result = {
                "detections": detections,
                "ocr_results": ocr_results,
                "scene_description": scene_description
            }
            await websocket.send_text(json.dumps(result))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)