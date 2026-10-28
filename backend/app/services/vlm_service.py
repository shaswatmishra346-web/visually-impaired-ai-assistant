"""
VLM (Vision-Language Model) Service
Handles scene description using Vision-Language Models (BLIP)
Encapsulates model loading and inference for clean separation of concerns.
"""

import time
import logging
from typing import Optional
import numpy as np
import cv2
import torch
from PIL import Image
from transformers import AutoProcessor, BlipForConditionalGeneration

logger = logging.getLogger(__name__)


class VLMService:
    """Service for Vision-Language Model scene description"""

    def __init__(self, model_name: str = "Salesforce/blip-image-captioning-base",
                 max_new_tokens: int = 100):
        """
        Initialize the VLM service

        Args:
            model_name: HuggingFace model name for BLIP
            max_new_tokens: Maximum tokens for generation
        """
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens
        self._model = None
        self._processor = None
        self._model_loaded = False
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

        # Performance tracking
        self.processing_times = []
        self.description_count = 0
        self.last_description = ""

        logger.info(f"VLMService initialized with model: {model_name}, device: {self._device}")

    def _initialize_model(self):
        """Lazy-load the Vision-Language Model"""
        if self._model_loaded:
            return

        try:
            logger.info("Loading Vision-Language Model (BLIP)...")
            start_time = time.time()

            self._processor = AutoProcessor.from_pretrained(self.model_name)
            self._model = BlipForConditionalGeneration.from_pretrained(
                self.model_name,
                dtype=torch.float16 if self._device == "cuda" else torch.float32,
            )

            # Move to device
            self._model = self._model.to(self._device)
            self._model.eval()  # Set to evaluation mode

            load_time = time.time() - start_time
            logger.info(f"VLM model loaded successfully in {load_time:.2f} seconds")
            self._model_loaded = True

        except Exception as e:
            logger.error(f"Failed to load VLM model: {e}")
            self._model_loaded = False
            raise

    def _preprocess_image(self, image: np.ndarray) -> Image.Image:
        """
        Preprocess OpenCV image for VLM input

        Args:
            image: Input image as numpy array (BGR format from OpenCV)

        Returns:
            PIL Image object ready for VLM processing
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert to PIL Image
        pil_image = Image.fromarray(rgb_image)

        return pil_image

    def describe_scene(self, image: np.ndarray) -> str:
        """
        Generate scene description from an image

        Args:
            image: Input image as numpy array (BGR format)

        Returns:
            Scene description string
        """
        # Initialize model if not already loaded
        if not self._model_loaded:
            self._initialize_model()

        try:
            # Preprocess image for VLM
            pil_image = self._preprocess_image(image)

            # Generate description using BLIP model
            start_time = time.time()

            inputs = self._processor(images=pil_image, return_tensors="pt")
            inputs = {k: v.to(self._device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self._model.generate(**inputs, max_new_tokens=self.max_new_tokens)

            description = self._processor.decode(outputs[0], skip_special_tokens=True).strip()

            generation_time = time.time() - start_time

            # BLIP sometimes returns empty or generic captions, add fallback
            if not description or len(description) < 5:
                description = "Scene contains various objects and elements"

            # Update performance metrics
            self.processing_times.append(generation_time)
            if len(self.processing_times) > 30:
                self.processing_times.pop(0)

            self.description_count += 1
            self.last_description = description

            logger.debug(f"VLM scene description generated in {generation_time:.2f}s: '{description[:50]}...'")

            return description

        except Exception as e:
            logger.error(f"Error in VLM scene description: {e}")
            return "Scene description temporarily unavailable - please ensure device is connected and try again"

    def get_performance_stats(self) -> dict:
        """Get current performance statistics"""
        if not self.processing_times:
            return {
                'avg_processing_time_ms': 0,
                'descriptions_generated': 0,
                'last_description': self.last_description
            }

        avg_time = sum(self.processing_times) / len(self.processing_times)
        return {
            'avg_processing_time_ms': avg_time * 1000,
            'descriptions_generated': self.description_count,
            'last_description': self.last_description
        }

    def warm_up(self):
        """Run a warm-up inference to avoid latency on first real request"""
        if not self._model_loaded:
            self._initialize_model()

        # Create a dummy image for warm-up
        dummy_image = np.zeros((480, 640, 3), dtype=np.uint8)
        try:
            self.describe_scene(dummy_image)
            logger.info("VLM model warm-up completed")
        except Exception as e:
            logger.warning(f"VLM warm-up failed: {e}")


# Singleton instance for reuse
_vlm_service = None


def get_vlm_service(model_name: str = "Salesforce/blip-image-captioning-base",
                   max_new_tokens: int = 100) -> VLMService:
    """
    Get or create the singleton VLM service instance

    Args:
        model_name: HuggingFace model name for BLIP
        max_new_tokens: Maximum tokens for generation

    Returns:
        VLMService instance
    """
    global _vlm_service
    if _vlm_service is None:
        _vlm_service = VLMService(model_name, max_new_tokens)
    return _vlm_service