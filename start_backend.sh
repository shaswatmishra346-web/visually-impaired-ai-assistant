#!/bin/bash
cd "/c/Users/shasw/assistive-ai-platform/backend"

# Use Anaconda Python if available (recommended for AI packages)
if [ -f "/c/Users/shasw/anaconda3/python.exe" ]; then
    echo "Using Anaconda Python..."
    "/c/Users/shasw/anaconda3/python.exe" -m pip install -r requirements.txt
    "/c/Users/shasw/anaconda3/python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
else
    # Fallback to system Python
    echo "Using system Python..."
    pip install -r requirements.txt
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
fi