#!/usr/bin/env python3
"""
Create a simple test image and encode it in base64
"""
import numpy as np
import cv2
import base64

# Create a simple 100x100 red image (BGR format for OpenCV)
img = np.zeros((100, 100, 3), dtype=np.uint8)
img[:] = [0, 0, 255]  # Red in BGR

# Encode as JPEG
_, buffer = cv2.imencode('.jpg', img)
img_bytes = buffer.tobytes()

# Encode to base64
img_base64 = base64.b64encode(img_bytes).decode('utf-8')

print(f"Base64 encoded image ({len(img_base64)} characters):")
print(img_base64)
print()

# Also save the image to verify it's correct
cv2.imwrite('/c/Users/shasw/assistive-ai-platform/test_red_square.jpg', img)
print("Saved test image as test_red_square.jpg")