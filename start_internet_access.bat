@echo off
title Mining Detection System - Internet Access
color 0A

echo ============================================
echo   Mining Detection System
echo   Internet Access via Ngrok
echo ============================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\Activate.ps1" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Check if ngrok exists
if not exist "ngrok.exe" (
    echo ERROR: ngrok.exe not found!
    echo.
    echo Please download ngrok:
    echo 1. Go to https://ngrok.com/download
    echo 2. Download for Windows
    echo 3. Extract ngrok.exe to this folder
    echo.
    pause
    exit /b 1
)

echo [1/3] Starting Streamlit Application...
echo.
start "Mining Detection - Streamlit" powershell -Command "& { Set-Location '%CD%'; .\.venv\Scripts\Activate.ps1; streamlit run app_enhanced.py }"

echo Waiting for Streamlit to initialize...
timeout /t 8 /nobreak > nul

echo.
echo [2/3] Creating Internet Tunnel with Ngrok...
echo.
echo ============================================
echo   YOUR INTERNET URL WILL APPEAR BELOW
echo ============================================
echo.

REM Start ngrok
ngrok http 8501

REM If ngrok closes, cleanup
echo.
echo Tunnel closed. Press any key to exit...
pause > nul
