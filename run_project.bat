"@echo off
title AI Resume Analyzer Launcher
echo ==============================================
echo Starting AI Resume Analyzer System
echo ==============================================

:: Step 1: Check if Python is installed
python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python passing the "Add Python to PATH" checkbox!
    pause
    exit /b
)

:: Step 2: Auto-Create Virtual Environment if it doesn't exist
IF NOT EXIST "backend\.venv" (
    echo.
    echo [1/3] Creating a local virtual environment... Please wait...
    python -m venv backend\.venv
)

:: Step 3: Install/Verify dependencies
echo.
echo [2/3] Checking and installing required AI dependencies... (This might take a minute the very first time)
call backend\.venv\Scripts\activate.bat
pip install -r backend\requirements.txt >nul 2>&1

:: Step 4: Boot the Server
echo.
echo [3/3] Booting up the internal AI server...
:: This opens a separate minimizeable console window specifically for the server
start "AI Backend Server" cmd /k "cd backend && call .venv\Scripts\activate.bat && uvicorn main:app --host 127.0.0.1 --port 8000"

:: Wait a moment for the server to initialize
timeout /t 4 /nobreak >nul

:: Step 5: Launch the Frontend!
echo.
echo Server started! Launching the Web Interface...
start frontend\index.html

echo.
echo IMPORTANT: A separate black window was opened to run your AI Model. 
echo Please keep that black window running while using the App!
echo.
echo You can now close this launcher window.
pause
"