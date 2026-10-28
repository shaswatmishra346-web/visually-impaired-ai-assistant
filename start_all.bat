@echo off
title Assistive AI Full Application
echo Starting Assistive AI Application...
echo Starting backend and frontend in separate windows...
echo.

REM Start backend in a new window
start "Assistive AI Backend" cmd /k "%~dp0start_backend.bat"

REM Wait a moment for backend to start
timeout /t 3 >nul

REM Start frontend in a new window
start "Assistive AI Frontend" cmd /k "%~dp0start_frontend.bat"

echo.
echo Both servers are starting in separate windows.
echo Backend will be available at: http://localhost:8000
echo Frontend will be available at: http://localhost:3000
echo.
echo To stop the servers, close each window or press Ctrl+C in each.
echo.
pause