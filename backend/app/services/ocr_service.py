"""
OCR Service
Handles optical character recognition using EasyOCR with enhancements for accuracy
"""

import time
import logging
import re
from typing import List, Dict, Any, Optional
import numpy as np
import cv2
import easyocr

logger = logging.getLogger(__name__)


class OCRService:
    """Service for optical character recognition with accuracy enhancements"""

    def __init__(self, languages: List[str] = ['en'],
                 gpu: bool = False,
                 confidence_threshold: float = 0.5,
                 enable_postprocessing: bool = True):
        """
        Initialize the OCR service

        Args:
            languages: List of language codes to recognize
            gpu: Whether to use GPU acceleration
            confidence_threshold: Minimum confidence for text detection
            enable_postprocessing: Whether to apply text post-processing for accuracy
        """
        self.languages = languages
        self.gpu = gpu
        self.confidence_threshold = confidence_threshold
        self.enable_postprocessing = enable_postprocessing
        self.reader = None
        self.processing_times = []
        self.text_count = 0
        self.last_results = []

        # Common OCR error corrections
        self.ocr_corrections = {
            # Single character confusions
            r'\b0\b': 'O',  # standalone zero to capital O
            r'\bO\b(?=\d)': '0',  # O followed by digit to zero (contextual)
            r'\b1\b': 'I',  # standalone one to capital I
            r'\b[lI]\b': '1',  # lowercase L or I to one
            r'\b5\b': 'S',  # standalone five to S
            r'\bS\b(?=\d)': '5',  # S followed by digit to 5
            r'\b8\b': 'B',  # standalone eight to B
            r'\bB\b(?=\d)': '8',  # B followed by digit to 8

            # Common word corrections
            r'\bteh\b': 'the',
            r'\bwth\b': 'with',
            r'\bthc\b': 'the',
            r'\bfr\b': 'for',
            r'\bnm\b': 'name',
            r'\bpls\b': 'please',
            r'\bthx\b': 'thanks',
            r'\bu\b': 'you',
            r'\br\b': 'are',
        }

        # Compile regex patterns for efficiency
        self.correction_patterns = [(re.compile(pattern, re.IGNORECASE), replacement)
                                  for pattern, replacement in self.ocr_corrections.items()]

        # Initialize the EasyOCR reader
        self._initialize_reader()

        logger.info(f"OCRService initialized with languages: {languages}, "
                   f"GPU: {gpu}, confidence threshold: {confidence_threshold}, "
                   f"postprocessing: {enable_postprocessing}")

    def _initialize_reader(self):
        """Initialize the EasyOCR reader"""
        try:
            self.reader = easyocr.Reader(self.languages, gpu=self.gpu, verbose=False)
            logger.info("EasyOCR reader initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EasyOCR reader: {e}")
            raise

    def _convert_numpy(self, obj):
        """
        Convert numpy types to native Python types for JSON serialization

        Args:
            obj: Object to convert

        Returns:
            Converted object with native Python types
        """
        if isinstance(obj, (list, tuple)):
            return [self._convert_numpy(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._convert_numpy(value) for key, value in obj.items()}
        elif hasattr(obj, 'item'):  # numpy scalars
            return obj.item()
        elif hasattr(obj, 'tolist'):  # numpy arrays
            return obj.tolist()
        return obj

    def _apply_text_corrections(self, text: str) -> str:
        """
        Apply rule-based text corrections to fix common OCR errors

        Args:
            text: Raw OCR text

        Returns:
            Corrected text
        """
        if not self.enable_postprocessing or not text:
            return text

        corrected_text = text

        # Apply each correction pattern
        for pattern, replacement in self.correction_patterns:
            corrected_text = pattern.sub(replacement, corrected_text)

        # Additional heuristics
        # Fix repeated characters that are likely OCR errors (4+ repeats only to preserve acronyms)
        corrected_text = re.sub(r'([A-Z])\1{3,}', r'\1\1\1', corrected_text)  # Max 3 repeats for caps (preserves AAA, NNN)
        corrected_text = re.sub(r'([a-z])\1{4,}', r'\1\1', corrected_text)  # Max 2 repeats for lowercase

        # Fix common spacing issues
        corrected_text = re.sub(r'\s+', ' ', corrected_text)  # Multiple spaces to single
        corrected_text = corrected_text.strip()

        return corrected_text

    def _calculate_enhanced_confidence(self, original_confidence: float, text: str,
                                     corrected_text: str) -> float:
        """
        Calculate enhanced confidence score based on multiple factors

        Args:
            original_confidence: Original confidence from EasyOCR
            text: Original text
            corrected_text: Text after corrections

        Returns:
            Enhanced confidence score
        """
        # Start with original confidence
        enhanced_conf = original_confidence

        # Boost confidence if text was corrected and looks more plausible
        if text != corrected_text:
            # If we made corrections and the result looks like a real word, boost confidence
            if len(corrected_text) >= 2 and corrected_text.isalpha():
                enhanced_conf = min(0.95, enhanced_conf + 0.1)

        # Adjust based on text length - very short or very long text might be less reliable
        text_len = len(corrected_text.strip())
        if text_len == 0:
            enhanced_conf *= 0.5  # Penalize empty text
        elif text_len < 2:
            enhanced_conf *= 0.8  # Slightly penalize very short text
        elif text_len > 50:
            enhanced_conf *= 0.9  # Slightly penalize very long text (might be multiple lines merged)

        # Boost for alphanumeric text (common in signs, labels, etc.)
        if re.match(r'^[a-zA-Z0-9\s\-.,!?]+$', corrected_text):
            enhanced_conf = min(0.95, enhanced_conf + 0.05)

        # Reduce for text with too many special characters (might be noise)
        special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s]', corrected_text)) / max(len(corrected_text), 1)
        if special_char_ratio > 0.3:
            enhanced_conf *= (1.0 - special_char_ratio * 0.5)  # Reduce confidence

        return max(0.0, min(1.0, enhanced_conf))

    def recognize_text(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Recognize text in an image with accuracy enhancements

        Args:
            image: Input image as numpy array (BGR format)

        Returns:
            List of OCR result dictionaries with enhanced confidence and corrections
        """
        start_time = time.time()

        try:
            # Run OCR
            # easyocr expects a numpy array (BGR format from cv2)
            raw_results = self.reader.readtext(image)

            # Format results with enhancements
            formatted_results = []
            for (bbox, text, confidence) in raw_results:
                # Apply confidence threshold from original detection
                if confidence >= self.confidence_threshold:
                    # Apply text corrections
                    corrected_text = self._apply_text_corrections(text)

                    # Calculate enhanced confidence
                    enhanced_confidence = self._calculate_enhanced_confidence(
                        confidence, text, corrected_text
                    )

                    # Only include if enhanced confidence still meets threshold
                    if enhanced_confidence >= self.confidence_threshold:
                        # Convert bbox numpy types to native Python types
                        converted_bbox = self._convert_numpy(bbox)
                        formatted_results.append({
                            'bbox': converted_bbox,
                            'text': corrected_text,
                            'original_text': text,  # Keep original for debugging
                            'confidence': float(enhanced_confidence),
                            'original_confidence': float(confidence),
                            'text_length': len(corrected_text),
                            'was_corrected': text != corrected_text
                        })

            # Update performance metrics
            end_time = time.time()
            processing_time_ms = (end_time - start_time) * 1000
            self.processing_times.append(processing_time_ms)
            if len(self.processing_times) > 30:  # Keep last 30 frames
                self.processing_times.pop(0)

            self.text_count += len(formatted_results)
            self.last_results = formatted_results

            logger.debug(f"OCR processed {len(raw_results)} raw detections, "
                        f"{len(formatted_results)} passed threshold, "
                        f"{sum(1 for r in formatted_results if r.get('was_corrected', False))} corrected")

            return formatted_results

        except Exception as e:
            logger.error(f"Error during OCR processing: {e}")
            return []

    def get_performance_stats(self) -> Dict[str, Any]:
        """
        Get current performance statistics

        Returns:
            Dictionary with performance metrics
        """
        if not self.processing_times:
            return {
                'avg_processing_time_ms': 0,
                'texts_processed': 0,
                'total_processing_time_ms': sum(self.processing_times) if self.processing_times else 0,
                'correction_rate': 0.0
            }

        avg_time = sum(self.processing_times) / len(self.processing_times)
        correction_count = sum(1 for r in self.last_results if r.get('was_corrected', False))
        correction_rate = correction_count / max(len(self.last_results), 1)

        return {
            'avg_processing_time_ms': avg_time,
            'texts_processed': self.text_count,
            'total_processing_time_ms': sum(self.processing_times),
            'correction_rate': correction_rate,
            'last_results': self.last_results[:5] if self.last_results else []  # Keep last few for debugging
        }

    def update_confidence_threshold(self, threshold: float):
        """Update the confidence threshold for filtering detections"""
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"OCR confidence threshold updated to {self.confidence_threshold}")

    def set_postprocessing_enabled(self, enabled: bool):
        """Enable or disable text post-processing"""
        self.enable_postprocessing = enabled
        logger.info(f"OCR postprocessing {'enabled' if enabled else 'disabled'}")


# Singleton instance for reuse
_ocr_service = None


def get_ocr_service(languages: List[str] = None,
                   gpu: bool = False,
                   confidence_threshold: float = 0.5,
                   enable_postprocessing: bool = True) -> OCRService:
    """
    Get or create the singleton OCR service instance

    Args:
        languages: List of language codes
        gpu: Whether to use GPU acceleration
        confidence_threshold: Minimum confidence for text detection
        enable_postprocessing: Whether to apply text post-processing for accuracy

    Returns:
        OCRService instance
    """
    global _ocr_service
    if _ocr_service is None:
        if languages is None:
            languages = ['en']
        _ocr_service = OCRService(languages, gpu, confidence_threshold, enable_postprocessing)
    return _ocr_service