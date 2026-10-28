# Assistive AI for the Visually Impaired - Quick Start

## 🚀 Easiest Way to Run (Double-Click)

Simply double-click the `start_all.bat` file to start both servers automatically!

## 📋 What the Batch Files Do

### `start_all.bat` (Recommended)
- Starts both backend and frontend in separate windows
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Handles dependency installation automatically
- Uses Anaconda Python if available (more reliable for AI packages)

### `start_backend.bat`
- Starts only the backend server
- Installs Python dependencies if needed
- Runs on http://localhost:8000

### `start_frontend.bat`
- Starts only the frontend server  
- Installs Node.js dependencies if needed
- Runs on http://localhost:3000

## 🖥️ How to Use

### Option 1: One-Click Start (Easiest)
1. **Double-click** `start_all.bat` 
2. Wait for both windows to initialize (may take 30-60 seconds on first run)
3. Open your browser to: **http://localhost:3000**
4. Click the **"Start"** button to begin testing

### Option 2: Manual Start
1. Double-click `start_backend.bat` (wait for it to say "Application startup complete")
2. Double-click `start_frontend.bat` (wait for it to say "ready - started server")
3. Open browser to: **http://localhost:3000**
4. Click the **"Start"** button

## 🧪 What to Test

Once both servers are running and you've clicked "Start" in the browser:

### ✅ Object Detection
- Yellow bounding boxes around detected objects (people, chairs, cars, etc.)
- Labels and distance estimates shown

### ✅ OCR (Text Recognition)
- Actual text recognition from signs, labels, documents
- Appears in "Detected Text:" section and spoken aloud
- Fixed common OCR errors (like 0/O, 1/I/l confusions)

### ✅ Scene Description (NOW REAL!)
- **REAL AI-generated descriptions** of what the camera sees
- **NOT random placeholders anymore!**
- Examples: "A person is sitting at a desk with a laptop" or "A kitchen with counter and appliances"
- Appears in "Scene Description:" section and spoken aloud

### ✅ Audio Feedback
- All detected information spoken aloud via browser speech synthesis

## ⚙️ Technical Details

- **Backend**: Python 3.10+ with FastAPI, Uvicorn, ONNX Runtime, Transformers, EasyOCR, pyttsx3
- **Frontend**: Next.js 14.2.5, React 18.2.0, WebSocket for real-time communication
- **AI Models**: 
  - Object Detection: YOLOv8n (ONNX format) - runs locally
  - Scene Description: Salesforce/blip-image-captioning-base (Transformers) - runs locally
  - Text Recognition: EasyOCR - runs locally
  - Text-to-Speech: pyttsx3 (backend) + Web Speech API (frontend)

## 🛠️ Troubleshooting

If you encounter issues:

### "Python/pip not found" errors
- The batch files try to use Anaconda Python first (more reliable)
- If that fails, they fall back to system Python
- Make sure you have Python 3.10+ installed

### "npm not found" errors
- Make sure you have Node.js 18+ installed
- Download from: https://nodejs.org/

### Port already in use errors (8000 or 3000)
- Close any applications using those ports
- Or restart your computer to clear stuck ports

### Camera not working
- Click the camera icon in your browser's address bar
- Allow camera access when prompted
- Try refreshing the page if needed

### First run takes longer
- Initial startup may take 1-2 minutes as AI models load
- Subsequent starts will be much faster (10-30 seconds)

## 📁 File Locations

All batch files are located in: `C:\Users\shasw\assistive-ai-platform\`

- `start_all.bat` - Starts both servers (Recommended)
- `start_backend.bat` - Starts backend only  
- `start_frontend.bat` - Starts frontend only
- `QUICK_START.md` - These instructions

## 🎯 Ready to Test?

**Just double-click `start_all.bat`** and follow the steps above!

The application is designed to assist visually impaired users with:
- Real-time object detection and obstacle avoidance
- Text recognition from signs, labels, documents  
- Scene description for environmental understanding
- Audio feedback for all detected information