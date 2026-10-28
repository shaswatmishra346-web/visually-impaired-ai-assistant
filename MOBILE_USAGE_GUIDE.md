# Assistive AI for the Visually Impaired - Mobile Usage Guide

## 📱 How to Use on Your Mobile Phone

### Prerequisites
1. **Desktop/Laptop Computer**: Must be running the Assistive AI application (backend + frontend servers)
2. **Mobile Phone**: Smartphone with camera and browser (Chrome, Safari, Firefox, etc.)
3. **Same Wi-Fi Network**: Both devices must be connected to the same Wi-Fi network

### 🚀 Starting the Application

#### Option 1: One-Click Start (Recommended)
1. Double-click the `start_all.bat` file in the `C:\Users\shasw\assistive-ai-platform\` directory
2. Wait for both windows to initialize (may take 30-60 seconds on first run)
3. Backend will be available at: `http://YOUR_COMPUTER_IP:8000`
4. Frontend will be available at: `http://YOUR_COMPUTER_IP:3000`

#### Option 2: Manual Start
1. Double-click `start_backend.bat` (wait for "Application startup complete")
2. Double-click `start_frontend.bat` (wait for "ready - started server")
3. Open browser on mobile phone to: `http://YOUR_COMPUTER_IP:3000`

### 🔍 Finding Your Computer's IP Address

On your desktop/laptop computer:
1. Press `Windows Key + R`, type `cmd`, and press Enter
2. In the command prompt, type: `ipconfig`
3. Look for "IPv4 Address" under your Wi-Fi connection (usually looks like `192.168.x.x` or `10.0.x.x`)
4. This is your computer's IP address on the local network

### 📱 Mobile Phone Setup

1. Ensure your mobile phone is connected to the **same Wi-Fi network** as your computer
2. Open the browser on your mobile phone (Chrome recommended)
3. Navigate to: `http://YOUR_COMPUTER_IP:3000`
   - Replace `YOUR_COMPUTER_IP` with the actual IP address you found in step 3 above
   - Example: `http://192.168.1.100:3000`
4. You should see the Assistive AI application interface
5. Click the **"Start"** button to begin testing

### 🧪 What to Test

Once both servers are running and you've clicked "Start" in the browser:

#### ✅ Object Detection
- Point your phone's camera at objects
- Yellow bounding boxes around detected objects (people, chairs, cars, etc.)
- Labels and distance estimates shown
- Detected objects spoken aloud

#### ✅ OCR (Text Recognition)
- Point camera at text (signs, labels, documents, screens)
- Actual text recognition from images
- Recognized text appears in "Detected Text:" section and spoken aloud
- Fixed common OCR errors (like 0/O, 1/I/l confusions)

#### ✅ Scene Description (NOW REAL!)
- **REAL AI-generated descriptions** of what the camera sees
- **NOT random placeholders anymore!**
- Examples: "A person is sitting at a desk with a laptop" or "A kitchen with counter and appliances"
- Appears in "Scene Description:" section and spoken aloud
- Uses Salesforce/blip-image-captioning-base model running locally

#### ✅ Audio Feedback
- All detected information spoken aloud via browser speech synthesis
- Includes object labels, distances, recognized text, and scene descriptions

### ⚙️ Technical Details

- **Backend**: Python 3.10+ with FastAPI, Uvicorn, ONNX Runtime, Transformers, EasyOCR, pyttsx3
- **Frontend**: Next.js 14.2.5, React 18.2.0, WebSocket for real-time communication
- **AI Models**: 
  - Object Detection: YOLOv8n (ONNX format) - runs locally
  - Scene Description: Salesforce/blip-image-captioning-base (Transformers) - runs locally
  - Text Recognition: EasyOCR - runs locally
  - Text-to-Speech: pyttsx3 (backend) + Web Speech API (frontend)

### 🛠️ Troubleshooting

#### If you encounter issues:

##### "Cannot connect" or "Site unreachable" errors
- Verify mobile phone and computer are on **same Wi-Fi network**
- Double-check you're using the correct IP address
- Ensure backend server is running (check the backend window says "Uvicorn running on http://0.0.0.0:8000")
- Try accessing `http://YOUR_COMPUTER_IP:8000/docs` in mobile browser to verify backend is reachable

##### Camera not working
- Click the camera icon in your browser's address bar
- Allow camera access when prompted
- Try refreshing the page if needed

##### Audio not working
- Ensure your phone's volume is turned up
- Check that browser isn't muted
- Try tapping the screen to interact with the page (some browsers require user interaction to start audio)

##### Application slow or unresponsive
- First run may take 1-2 minutes as AI models load
- Subsequent starts will be much faster (10-30 seconds)
- Close other applications to free up system resources
- The application is designed to run locally for privacy - no internet connection required after initial model download

##### "Connection lost" or WebSocket errors
- Try refreshing the page
- Check if backend server is still running
- Ensure strong Wi-Fi signal between phone and router
- Reduce distance between phone and Wi-Fi router if experiencing interference

### 📁 File Locations

All files are located in: `C:\Users\shasw\assistive-ai-platform\`

- `start_all.bat` - Starts both servers (Recommended)
- `start_backend.bat` - Starts backend only  
- `start_frontend.bat` - Starts frontend only
- `QUICK_START.md` - Detailed technical instructions
- `MOBILE_USAGE_GUIDE.md` - This file

### 🎯 Ready to Test?

**Just double-click `start_all.bat`** on your computer, find your IP address, then open `http://YOUR_COMPUTER_IP:3000` on your mobile phone's browser and click "Start"!

The application is designed to assist visually impaired users with:
- Real-time object detection and obstacle avoidance
- Text recognition from signs, labels, documents  
- Scene description for environmental understanding
- Audio feedback for all detected information

All AI processing happens **locally on your device** for privacy and reliability - no internet connection required after the initial startup.