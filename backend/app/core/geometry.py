"""
Geometry Utilities
Shared utilities for distance estimation and direction calculation.
Used by both inference API and WebSocket handler to avoid code duplication.
"""

from typing import Dict

# Average heights of objects in meters (rough estimates for distance calculation)
AVG_HEIGHTS: Dict[str, float] = {
    "person": 1.7,
    "bicycle": 1.0,
    "car": 1.5,
    "motorcycle": 1.2,
    "airplane": 3.0,
    "bus": 3.2,
    "train": 3.5,
    "truck": 2.5,
    "boat": 2.0,
    "traffic light": 0.8,
    "fire hydrant": 1.0,
    "stop sign": 0.6,
    "parking meter": 1.0,
    "bench": 0.5,
    "bird": 0.2,
    "cat": 0.25,
    "dog": 0.5,
    "horse": 1.8,
    "sheep": 0.8,
    "cow": 1.5,
    "elephant": 3.3,
    "bear": 1.0,
    "zebra": 1.5,
    "giraffe": 5.0,
    "backpack": 0.5,
    "umbrella": 0.9,
    "handbag": 0.3,
    "tie": 0.1,
    "suitcase": 0.6,
    "frisbee": 0.03,
    "skis": 0.15,
    "snowboard": 0.15,
    "sports ball": 0.22,
    "kite": 0.5,
    "baseball bat": 0.75,
    "baseball glove": 0.25,
    "skateboard": 0.1,
    "surfboard": 0.6,
    "tennis racket": 0.7,
    "bottle": 0.25,
    "wine glass": 0.2,
    "cup": 0.1,
    "fork": 0.2,
    "knife": 0.2,
    "spoon": 0.15,
    "bowl": 0.15,
    "banana": 0.15,
    "apple": 0.1,
    "sandwich": 0.1,
    "orange": 0.1,
    "broccoli": 0.2,
    "carrot": 0.2,
    "hot dog": 0.15,
    "pizza": 0.05,
    "donut": 0.05,
    "cake": 0.1,
    "chair": 0.9,
    "couch": 0.9,
    "potted plant": 0.5,
    "bed": 0.6,
    "dining table": 0.8,
    "toilet": 0.7,
    "tv": 0.6,
    "laptop": 0.03,
    "mouse": 0.04,
    "remote": 0.02,
    "keyboard": 0.02,
    "cell phone": 0.15,
    "microwave": 0.3,
    "oven": 0.6,
    "toaster": 0.3,
    "sink": 0.6,
    "refrigerator": 1.7,
    "book": 0.03,
    "clock": 0.3,
    "vase": 0.3,
    "scissors": 0.1,
    "teddy bear": 0.3,
    "hair drier": 0.2,
    "toothbrush": 0.2
}

# Configurable focal factor for distance estimation (adjustable per camera setup)
DEFAULT_FOCAL_FACTOR = 0.5
MIN_DISTANCE = 0.1  # meters


def estimate_distance(bbox_height: int, image_height: int, label: str, focal_factor: float = DEFAULT_FOCAL_FACTOR) -> float:
    """
    Estimate distance to object based on bounding box height and known average height.

    Args:
        bbox_height: Height of bounding box in pixels
        image_height: Height of original image in pixels
        label: Object class label
        focal_factor: Camera focal factor (adjust for your camera setup)

    Returns:
        Estimated distance in meters (minimum MIN_DISTANCE)
    """
    if bbox_height <= 0:
        return 0.0

    avg_height = AVG_HEIGHTS.get(label, 1.0)  # default 1.0m if unknown
    # Distance ≈ (known_height * image_height) / bbox_height * focal_factor
    distance = (avg_height * image_height) / bbox_height * focal_factor
    return max(MIN_DISTANCE, distance)


def get_direction(box_center_x: float, image_width: float) -> str:
    """
    Determine direction based on horizontal position.

    Args:
        box_center_x: X coordinate of box center
        image_width: Width of original image

    Returns:
        Direction string: "left", "center", or "right"
    """
    if box_center_x < image_width * 0.33:
        return "left"
    elif box_center_x > image_width * 0.66:
        return "right"
    else:
        return "center"


def format_detection(det: dict, image_width: int, image_height: int, focal_factor: float = DEFAULT_FOCAL_FACTOR) -> dict:
    """
    Format a raw detection with distance and direction.

    Args:
        det: Raw detection dict with 'bbox', 'confidence', 'class_name'
        image_width: Width of original image
        image_height: Height of original image
        focal_factor: Camera focal factor for distance estimation

    Returns:
        Formatted detection with bbox, label, confidence, distance, direction
    """
    x1, y1, x2, y2 = det['bbox']
    confidence = det['confidence']
    class_name = det['class_name']

    box_center_x = (x1 + x2) / 2
    bbox_height = y2 - y1
    distance = estimate_distance(bbox_height, image_height, class_name, focal_factor)
    direction = get_direction(box_center_x, image_width)

    return {
        'bbox': [float(x1), float(y1), float(x2), float(y2)],
        'label': class_name,
        'confidence': float(confidence),
        'distance': float(distance),
        'direction': direction
    }