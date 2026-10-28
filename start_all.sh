#!/bin/bash
echo "Starting Assistive AI Application..."

# Start backend in background
(
    cd "/c/Users/shasw/assistive-ai-platform/backend"
    if [ -f "/c/Users/shasw/anaconda3/python.exe" ]; then
        "/c/Users/shasw/anaconda3/python.exe" -m pip install -r requirements.txt
        "/c/Users/shasw/anaconda3/python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    else
        pip install -r requirements.txt
        uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    fi
) &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend in background
(
    cd "/c/Users/shasw/assistive-ai-platform/frontend"
    npm install
    npm run dev
) &
FRONTEND_PID=$!

echo "Backend started (PID: $BACKEND_PID) - http://localhost:8000"
echo "Frontend started (PID: $FRONTEND_PID) - http://localhost:3000"
echo ""
echo "To stop both servers:"
echo "kill $BACKEND_PID $FRONTEND_PID"
echo "Or close this terminal window"

# Wait for both processes
wait $BACKEND_PID
wait $FRONTEND_PID