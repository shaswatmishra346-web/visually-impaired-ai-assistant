"""
Object Detection Service
Handles real-time object detection using ONNX models
"""

import time
import logging
from typing import Dict, List, Optional
import numpy as np
import cv2
from ..models.onnx_model import get_object_detector

logger = logging.getLogger(__name__)


class ObjectDetectionService:
    """Service for real-time object detection"""

    def __init__(self, model_path: str = None, target_fps: int = 15,
                 max_latency_ms: float = 50.0):
        """
        Initialize the object detection service

        Args:
            model_path: Path to ONNX model file
            target_fps: Target frames per second for processing
            max_latency_ms: Maximum allowed latency per frame in milliseconds
        """
        self.detector = get_object_detector(model_path)
        self.target_fps = target_fps
        self.max_latency_ms = max_latency_ms
        self.frame_times = []
        self.detection_count = 0
        self.last_detections = []

        logger.info(f"ObjectDetectionService initialized with target FPS: {target_fps}, "
                   f"max latency: {max_latency_ms}ms")

    def detect_objects(self, frame: np.ndarray) -> Dict:
        """
        Detect objects in a frame with performance monitoring

        Args:
            frame: Input frame as numpy array (BGR format)

        Returns:
            Dictionary containing detections and performance metrics
        """
        start_time = time.time()

        # Perform detection
        detections = self.detector.detect(frame)

        # Calculate latency
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000

        # Update performance metrics
        self.frame_times.append(latency_ms)
        if len(self.frame_times) > 30:  # Keep last 30 frames for averaging
            self.frame_times.pop(0)

        self.detection_count += 1
        self.last_detections = detections

        # Check if we're meeting performance requirements
        avg_latency = sum(self.frame_times) / len(self.frame_times) if self.frame_times else 0
        fps = 1000 / avg_latency if avg_latency > 0 else 0

        performance_ok = latency_ms <= self.max_latency_ms and fps >= self.target_fps

        result = {
            'detections': detections,
            'latency_ms': latency_ms,
            'avg_latency_ms': avg_latency,
            'fps': fps,
            'performance_ok': performance_ok,
            'frame_id': self.detection_count,
            'timestamp': start_time
        }

        # Log performance warnings
        if latency_ms > self.max_latency_ms:
            logger.warning(f"Detection latency {latency_ms:.2f}ms exceeds max {self.max_latency_ms}ms")

        if fps < self.target_fps:
            logger.warning(f"FPS {fps:.2f} below target {self.target_fps}")

        return result

    def get_performance_stats(self) -> Dict:
        """
        Get current performance statistics

        Returns:
            Dictionary with performance metrics
        """
        if not self.frame_times:
            return {
                'avg_latency_ms': 0,
                'fps': 0,
                'frames_processed': 0,
                'detection_count': self.detection_count
            }

        avg_latency = sum(self.frame_times) / len(self.frame_times)
        fps = 1000 / avg_latency if avg_latency > 0 else 0

        return {
            'avg_latency_ms': avg_latency,
            'fps': fps,
            'frames_processed': len(self.frame_times),
            'detection_count': self.detection_count,
            'last_detections': self.last_detections
        }

    def is_performance_acceptable(self) -> bool:
        """
        Check if current performance meets requirements

        Returns:
            True if performance is acceptable, False otherwise
        """
        stats = self.get_performance_stats()
        return (stats['avg_latency_ms'] <= self.max_latency_ms and
                stats['fps'] >= self.target_fps)


# Singleton instance for reuse
_detection_service = None


def get_object_detection_service(model_path: str = None) -> ObjectDetectionService:
    """
    Get or create the singleton object detection service instance

    Args:
        model_path: Path to ONNX model file

    Returns:
        ObjectDetectionService instance
    """
    global _detection_service
    if _detection_service is None:
        _detection_service = ObjectDetectionService(model_path)
    return _detection_service