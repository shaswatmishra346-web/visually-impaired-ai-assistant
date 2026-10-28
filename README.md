# Assistive AI for the Visually Impaired Platform

A real-time computer vision and multimodal AI system designed to assist visually impaired users with object detection, obstacle avoidance, text reading, and scene description.

## Features

- Real-time object detection and obstacle distance/direction estimation
- Text recognition (OCR) for signs, labels, currency, documents
- Scene description using Vision-Language Models (VLMs)
- Audio feedback via speech, audio cues, and haptic feedback
- Hybrid edge-cloud architecture: safety-critical functions on-device, richer reasoning in cloud
- Responsive web interface with accessibility features (WCAG 2.1 AA)

## Prerequisites

- Python 3.10+
- Node.js 18+
- Docker & Docker Compose
- CUDA-compatible GPU (recommended for local model inference)

## Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd assistive-ai-platform
   ```

2. Start infrastructure services (Redis):
   ```bash
   docker-compose up -d redis
   ```

3. Build and run the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. Build and run the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Alternatively, use Docker Compose to start all services:
   ```bash
   docker-compose up --build
   ```

## Architecture

- **Client Frontend**: Next.js web application (React Native mobile app optional)
- **API Gateway**: FastAPI backend handling WebSocket connections and request routing
- **Inference Engine**: ONNX Runtime for object detection, PyTorch/Transformers for VLMs, EasyOCR for OCR
- **State & Caching Layer**: Redis for temporary frame hashes and inference outputs
- **Communication**: WebSocket for real-time video frame transmission

## Model Sources

- Object Detection: ONNX-optimized YOLO model (e.g., YOLOv8n)
- Scene Description: Mini-LLaVA or similar lightweight Vision-Language Model
- OCR: EasyOCR (pre-trained models)
- Text-to-Speech: pyttsx3 or gTTS

## Safety Features

- Emergency proximity alerts override standard scene descriptions
- Token-based authentication for WebSocket endpoints
- TLS encryption in transit (to be implemented in production)
- Ephemeral frame storage with automatic purging

## Accessibility

- High-contrast visual elements
- Screen reader compatibility (ARIA labels)
- Audio-first navigation
- Haptic feedback for crucial alerts
- Voice command support (optional)

## Development Guidelines

- Follow the modular structure: backend (app/api, app/core, app/models, app/services) and frontend (components, hooks, pages)
- Maintain real-time performance targets: <50ms for detection, 15 FPS video processing
- Prioritize offline functionality for core safety features
- Regularly commit changes and write unit/integration tests

## Acknowledgements

This project was created as a final year project with the goal of assisting visually impaired individuals in gaining independence and confidence in everyday environments.