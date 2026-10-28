# Frontend - Assistive AI Platform

This directory contains the frontend application for the Assistive AI Platform.

## Structure:
- `src/` - Source code
  - `components/` - Reusable UI widgets (camera stream, object detection display, OCR display, etc.)
  - `hooks/` - Custom React hooks (WebSocket, audio, camera, inference)
  - `pages/` - Next.js application pages (home, settings, help, about)
- `Dockerfile` - Containerization configuration
- `package.json` - Node.js dependencies and scripts

## Key Features:
- Camera integration for video frame capture
- Real-time WebSocket connection to backend for frame streaming
- Audio output via Text-to-Speech for scene descriptions and alerts
- High-contrast mode and screen reader accessibility (WCAG 2.1 AA compliant)
- Emergency alert prioritization (safety proximity alerts override standard descriptions)
