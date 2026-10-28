@echo off
title Assistive AI Backend Server
echo Starting Assistive AI Backend Server...
echo.

REM Change to backend directory
cd /d "%~dp0backend"

REM Check if virtual environment exists, if not use system python with pip
if exist "..\anaconda3\python.exe" (
    echo Using Anaconda Python...
    "..\anaconda3\python.exe" -m pip install -r requirements.txt >nul
    "..\anaconda3\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
) else (
    echo Using system Python...
    pip install -r requirements.txt >nul
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
)