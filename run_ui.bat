@echo off
REM CodeObit UI Startup Script for Windows
REM This script starts the web-based UI for CodeObit CLI

echo ================================================
echo          CodeObit UI - Starting Up
echo ================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed. Please install Python 3.11 or later.
    pause
    exit /b 1
)

REM Display Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Python version: %PYTHON_VERSION%

REM Create virtual environment if it doesn't exist
if not exist "venv_ui" (
    echo Creating virtual environment...
    python -m venv venv_ui
)

REM Activate virtual environment
call venv_ui\Scripts\activate.bat

REM Install/upgrade pip
echo Updating pip...
python -m pip install --upgrade pip --quiet

REM Install requirements
echo Installing dependencies...
pip install flask flask-cors flask-socketio python-socketio watchdog --quiet

REM Check if other requirements are installed
if exist "requirements.txt" (
    echo Installing project requirements...
    pip install -r requirements.txt --quiet
)

REM Set environment variables
set FLASK_APP=ui_app.py
set FLASK_ENV=development
set DEBUG=True

REM Create necessary directories
if not exist "ui\templates" mkdir ui\templates
if not exist "ui\build\static" mkdir ui\build\static
if not exist "uploads" mkdir uploads

echo.
echo ================================================
echo      CodeObit UI is starting...
echo ================================================
echo.
echo   Web UI: http://localhost:5000
echo   WebSocket: ws://localhost:5000
echo.
echo   Press Ctrl+C to stop the server
echo.
echo ================================================
echo.

REM Start the Flask application
python ui_app.py

pause