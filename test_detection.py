#!/usr/bin/env python3
"""
Test script to verify detection endpoint image processing
"""
import base64
import numpy as np
import cv2

# Test with the same base64 string we used in curl
test_base64 = "/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxISEhUQEhIVFRUWFhUVFRUVFRUVFRUWFhUVFRUYHSggGBolHRUVITEhJSkrLi4uFx8zODMsNygtLisBCgoKDg0OGxAQGi0lHyUtLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIAKgBLAMBIgACEQEDEQH/xAAcAAABBQEBAQAAAAAAAAAAAAAAAgMEBQYHAAj/xABDEAACAQIEAwYEBgQDAQAAAAABAAIDBBEFEiExBkFREyJhcYGRobEHFCNCUtHwIzNTYnKS/8QAGgEAAwEBAQEAAAAAAAAAAAAAAAECAwQFBv/EACYRAAICAQQCAwEBAAAAAAAAAAABAhEDBBIhMUFRYXGRobH/2gAMAwEAAhEDEQA/AO1bKZpKUpQpSg=="

try:
    print("Decoding base64...")
    img_data = base64.b64decode(test_base64)
    print(f"Decoded {len(img_data)} bytes")

    print("Converting to numpy array...")
    nparr = np.frombuffer(img_data, np.uint8)
    print(f"Numpy array shape: {nparr.shape}")

    print("Decoding with OpenCV...")
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    if img is None:
        print("ERROR: OpenCV failed to decode image (returned None)")
    else:
        print(f"SUCCESS: Image decoded successfully!")
        print(f"Image shape: {img.shape}")
        print(f"Image dtype: {img.dtype}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()