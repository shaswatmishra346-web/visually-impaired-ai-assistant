"""
ONNX Model Wrapper for Object Detection
Handles loading and inference with YOLO models in ONNX format
"""

import numpy as np
import onnxruntime as ort
from typing import Dict, List, Tuple
import logging
import cv2

logger = logging.getLogger(__name__)


class ONNXObjectDetector:
    """YOLO Object Detector using ONNX Runtime"""

    def __init__(self, model_path: str, confidence_threshold: float = 0.5,
                 iou_threshold: float = 0.45):
        """
        Initialize the ONNX object detector

        Args:
            model_path: Path to the ONNX model file
            confidence_threshold: Minimum confidence for detection
            iou_threshold: IOU threshold for non-maximum suppression
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.session = None
        self.input_name = None
        self.output_names = None
        self.classes = []

        # COCO dataset classes (80 classes)
        self.classes = [
            'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat',
            'traffic light', 'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat',
            'dog', 'horse', 'sheep', 'cow', 'elephant', 'bear', 'zebra', 'giraffe', 'backpack',
            'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball',
            'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
            'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
            'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake',
            'chair', 'couch', 'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop',
            'mouse', 'remote', 'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
            'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear', 'hair drier',
            'toothbrush'
        ]

        self._load_model()

    def _load_model(self):
        """Load the ONNX model and get input/output details"""
        try:
            # Configure session options for optimal performance
            sess_options = ort.SessionOptions()
            sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            sess_options.intra_op_num_threads = 4

            # Create inference session
            self.session = ort.InferenceSession(
                self.model_path,
                sess_options=sess_options,
                providers=['CUDAExecutionProvider', 'CPUExecutionProvider']
            )

            # Get model input and output details
            self.input_name = self.session.get_inputs()[0].name
            self.output_names = [output.name for output in self.session.get_outputs()]

            logger.info(f"ONNX model loaded successfully from {self.model_path}")
            logger.info(f"Input name: {self.input_name}")
            logger.info(f"Output names: {self.output_names}")

        except Exception as e:
            logger.error(f"Failed to load ONNX model: {e}")
            raise

    def preprocess(self, image: np.ndarray) -> Tuple[np.ndarray, float, Tuple[int, int], Tuple[int, int]]:
        """
        Preprocess image for YOLO model input

        Args:
            image: Input image as numpy array (BGR format)

        Returns:
            Tuple of (preprocessed_image, scale, pad_size, target_size)
            where pad_size = (new_width, new_height) - resized image dimensions
            and target_size = (target_width, target_height) - model input dimensions
        """
        # Get input shape from model
        input_shape = self.session.get_inputs()[0].shape
        target_height, target_width = input_shape[2], input_shape[3]

        # Resize image while maintaining aspect ratio
        img_height, img_width = image.shape[:2]
        scale = min(target_width / img_width, target_height / img_height)
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)

        # Resize and pad to square (resized image placed at top-left)
        resized = cv2.resize(image, (new_width, new_height))
        padded = np.full((target_height, target_width, 3), 114, dtype=np.uint8)  # Gray padding
        padded[:new_height, :new_width] = resized

        # Convert BGR to RGB and normalize
        rgb = cv2.cvtColor(padded, cv2.COLOR_BGR2RGB)
        normalized = rgb.astype(np.float32) / 255.0

        # Transpose to CHW format and add batch dimension
        transposed = np.transpose(normalized, (2, 0, 1))
        batched = np.expand_dims(transposed, axis=0)

        return batched, scale, (new_width, new_height), (target_width, target_height)

    def postprocess(self, outputs: List[np.ndarray], scale: float,
                   pad_size: Tuple[int, int], target_size: Tuple[int, int],
                   original_shape: Tuple[int, int]) -> List[Dict]:
        """
        Postprocess model outputs to get detections

        Args:
            outputs: Raw model outputs
            scale: Scale factor used in preprocessing (original -> resized)
            pad_size: Resized image dimensions (new_width, new_height) - before padding
            target_size: Model input dimensions (target_width, target_height) - after padding
            original_shape: Original image dimensions (height, width)

        Returns:
            List of detection dictionaries with bbox, confidence, and class
        """
        # For YOLOv8, output format is typically [batch, 84, 8400] where 84 = 4 (bbox) + 80 (classes)
        # or [batch, 8400, 84] depending on model version

        predictions = outputs[0]  # Assuming single output

        # Handle different output formats
        if len(predictions.shape) == 3:
            if predictions.shape[1] == 84:  # [batch, 84, 8400]
                predictions = np.transpose(predictions, (0, 2, 1))  # [batch, 8400, 84]
            elif predictions.shape[2] == 84:  # [batch, 8400, 84]
                pass  # Already in correct format

        # Remove batch dimension
        predictions = predictions[0]  # [8400, 84]

        # Extract boxes, scores, and class probabilities
        boxes = predictions[:, :4]  # x, y, width, height (center format)
        scores = predictions[:, 4:]  # class probabilities

        # Get class with highest score for each detection
        class_ids = np.argmax(scores, axis=1)
        confidences = np.max(scores, axis=1)

        # Filter by confidence threshold
        valid_detections = confidences >= self.confidence_threshold
        boxes = boxes[valid_detections]
        class_ids = class_ids[valid_detections]
        confidences = confidences[valid_detections]

        if len(boxes) == 0:
            return []

        # Convert from center (x, y, w, h) to corner (x1, y1, x2, y2) format
        x_center, y_center, width, height = boxes.T
        x1 = x_center - width / 2
        y1 = y_center - height / 2
        x2 = x_center + width / 2
        y2 = y_center + height / 2

        # Boxes are in target space (target_width x target_height)
        # Need to map back to original image space:
        # 1. Clip to valid region (resized image area within padded space)
        # 2. Scale from resized space to original space using 1/scale
        target_width, target_height = target_size
        new_width, new_height = pad_size
        orig_height, orig_width = original_shape

        # Clip boxes to the resized image region (top-left of padded image)
        x1 = np.clip(x1, 0, new_width)
        y1 = np.clip(y1, 0, new_height)
        x2 = np.clip(x2, 0, new_width)
        y2 = np.clip(y2, 0, new_height)

        # Scale from resized space to original space
        x1 = x1 / scale
        y1 = y1 / scale
        x2 = x2 / scale
        y2 = y2 / scale

        # Final clip to original image bounds
        x1 = np.clip(x1, 0, orig_width)
        y1 = np.clip(y1, 0, orig_height)
        x2 = np.clip(x2, 0, orig_width)
        y2 = np.clip(y2, 0, orig_height)

        # Apply Non-Maximum Suppression
        indices = cv2.dnn.NMSBoxes(
            bboxes=np.column_stack([x1, y1, x2 - x1, y2 - y1]).tolist(),
            scores=confidences.tolist(),
            score_threshold=self.confidence_threshold,
            nms_threshold=self.iou_threshold
        )

        if len(indices) == 0:
            return []

        # Flatten indices if needed
        if isinstance(indices, np.ndarray):
            indices = indices.flatten()

        # Build detection results
        detections = []
        for i in indices:
            x1_val, y1_val, x2_val, y2_val = int(x1[i]), int(y1[i]), int(x2[i]), int(y2[i])
            class_id = int(class_ids[i])
            confidence = float(confidences[i])

            detections.append({
                'bbox': [x1_val, y1_val, x2_val, y2_val],
                'confidence': confidence,
                'class_id': class_id,
                'class_name': self.classes[class_id] if class_id < len(self.classes) else 'unknown'
            })

        return detections

    def detect(self, image: np.ndarray) -> List[Dict]:
        """
        Perform object detection on an image

        Args:
            image: Input image as numpy array (BGR format)

        Returns:
            List of detection dictionaries
        """
        try:
            # Preprocess image
            input_batch, scale, pad_size, target_size = self.preprocess(image)
            original_shape = image.shape[:2]

            # Run inference
            outputs = self.session.run(self.output_names, {self.input_name: input_batch})

            # Postprocess results
            detections = self.postprocess(outputs, scale, pad_size, target_size, original_shape)

            return detections

        except Exception as e:
            logger.error(f"Error during object detection: {e}")
            return []

    def draw_detections(self, image: np.ndarray, detections: List[Dict]) -> np.ndarray:
        """
        Draw detection results on image

        Args:
            image: Input image (BGR format)
            detections: List of detection dictionaries

        Returns:
            Image with detections drawn
        """
        annotated = image.copy()

        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            confidence = det['confidence']
            class_name = det['class_name']

            # Draw bounding box
            color = (0, 255, 0)  # Green
            cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)

            # Draw label
            label = f"{class_name}: {confidence:.2f}"
            label_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)[0]
            cv2.rectangle(annotated, (x1, y1 - label_size[1] - 10),
                         (x1 + label_size[0], y1), color, -1)
            cv2.putText(annotated, label, (x1, y1 - 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)

        return annotated


# Singleton instance for reuse
_detector_instance = None


def get_object_detector(model_path: str = None) -> ONNXObjectDetector:
    """
    Get or create the singleton object detector instance

    Args:
        model_path: Path to ONNX model (if None, uses default)

    Returns:
        ONNXObjectDetector instance
    """
    global _detector_instance
    if _detector_instance is None:
        if model_path is None:
            # Default model path - adjust as needed
            model_path = "./app/models/yolov8n.onnx"
        _detector_instance = ONNXObjectDetector(model_path)
    return _detector_instance