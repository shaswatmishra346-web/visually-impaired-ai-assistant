@echo off
title Assistive AI Frontend Server
echo Starting Assistive AI Frontend Server...
echo.

REM Change to frontend directory
cd /d "%~dp0frontend"

REM Install dependencies and start dev server
npm install >nul
npm run dev