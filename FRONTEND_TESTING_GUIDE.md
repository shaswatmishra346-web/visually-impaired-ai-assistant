# Assistive AI Frontend - Testing Guide

Share this file with your testers to help them run the frontend locally.

## 📱 What This Is
The frontend for the Assistive AI for the Visually Impaired platform - a Next.js (React) web application that provides:
- Real-time object detection & obstacle avoidance
- Text recognition (OCR) for signs, labels, documents
- Scene description using AI
- Audio feedback via speech and haptic cues

## 🔧 Prerequisites
Make sure your tester has installed:
- **Node.js 18+** (Download from [nodejs.org](https://nodejs.org))
- **Git** (to clone the repo, if needed)
- Optional: **Docker & Docker Compose** (for containerized setup)

## 📝 Local Setup Instructions

### Option A: Direct Local Run (Recommended for Testing)
1. **Get the code**:
   ```bash
   # If they already have the code:
   cd /path/to/assistive-ai-platform/frontend
   
   # If they need to clone (adjust URL as needed):
   # git clone <repository-url>
   # cd assistive-ai-platform/frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   # (This may go quickly if node_modules already exists)
   ```

3. **Start the development server**:
   ```bash
   npm run dev
   # Or: next dev
   ```

4. **Open in browser**:
   - Visit: **http://localhost:3000**
   - You should see the application interface

5. **To stop testing**:
   - Press `Ctrl + C` in the terminal

### Option B: Docker Container (All Services)
1. **Get the code** (project root, not just frontend):
   ```bash
   cd /path/to/assistive-ai-platform
   ```

2. **Build and start all services**:
   ```bash
   docker-compose up --build
   ```

3. **Access the frontend**:
   - Visit: **http://localhost:3000**
   - Backend API: http://localhost:8000

4. **To stop**:
   - Press `Ctrl + C` in the terminal
   - Or run: `docker-compose down` in another terminal

## 🎯 What to Test
Ask your friend to:
1. Verify the page loads without errors
2. Check if any UI elements are visible
3. Look for console errors (F12 → Console tab)
4. Test basic navigation if multiple pages exist
5. Note any issues or missing features

## 🛠️ Troubleshooting
- **"command not found: npm"** → Install Node.js 18+
- **Port 3000 already in use** → Close other apps using port 3000, or run: `npx kill-port 3000`
- **Missing dependencies** → Delete `node_modules` and `package-lock.json`, then run `npm install` again
- **Build fails** → Ensure Node.js ≥ 18 (`node --version` to check)
- **Blank screen** → Check browser console (F12) for errors

## ❓ Need Help?
If your friend encounters issues, they should:
1. Check the terminal output for error messages
2. Look at the browser console (F12) for frontend errors
3. Verify they're in the `frontend/` directory when running npm commands
4. Ensure they have Node.js 18+ installed

---
*File generated for sharing with testers. Frontend code located in: ./frontend/*