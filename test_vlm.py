#!/usr/bin/env python3
"""
Test script to load VLM model directly and see what happens
"""
import torch
from transformers import pipeline
import time

print("Testing VLM model loading...")
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")

try:
    start_time = time.time()
    print("Loading Salesforce/blip-image-captioning-base model...")

    vlm_pipeline = pipeline(
        "image-to-text",
        model="Salesforce/blip-image-captioning-base",
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device=0 if torch.cuda.is_available() else -1
    )

    load_time = time.time() - start_time
    print(f"Model loaded successfully in {load_time:.2f} seconds")

    # Test with a dummy image
    import numpy as np
    from PIL import Image
    import base64

    # Create a small dummy image (10x10 pixels, RGB)
    dummy_image = np.random.randint(0, 255, (10, 10, 3), dtype=np.uint8)
    pil_image = Image.fromarray(dummy_image)

    print("Testing inference with dummy image...")
    inference_start = time.time()

    try:
        # Try with prompt first
        results = vlm_pipeline(
            pil_image,
            prompt="Describe this scene in detail for a visually impaired person, focusing on objects, layout, and any potential hazards or points of interest.",
            max_new_tokens=50
        )
    except TypeError:
        # Fallback to prompt-less version
        results = vlm_pipeline(pil_image, max_new_tokens=50)

    inference_time = time.time() - inference_start
    print(f"Inference completed in {inference_time:.2f} seconds")

    if isinstance(results, list) and len(results) > 0:
        description = results[0].get('generated_text', '').strip()
        print(f"Generated description: {description}")
    else:
        print(f"Results: {results}")

except Exception as e:
    print(f"Error loading or running VLM model: {e}")
    import traceback
    traceback.print_exc()