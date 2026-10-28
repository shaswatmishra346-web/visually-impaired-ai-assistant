# Backend - Assistive AI Platform

This directory contains the backend services for the Assistive AI Platform.

## Structure:
- `app/` - Main application code
  - `api/` - FastAPI routers (WebSocket, inference, auth, OCR, VLM)
  - `core/` - Configuration, security, and logging
  - `models/` - ONNX and PyTorch model wrappers
  - `services/` - OCR, TTS, Redis, and WebSocket service integrations
  - `main.py` - Application entry point
- `Dockerfile` - Containerization configuration
- `requirements.txt` - Python dependencies

## Key Features:
- Real-time object detection via ONNX models (edge-optimized)
- Heavy multimodal reasoning (Vision-Language Models) via PyTorch/Transformers
- OCR processing via EasyOCR
- Redis Pub/Sub for state management and caching
- WebSocket endpoints for real-time video frame streaming
- REST APIs for inference triggering and result retrieval
