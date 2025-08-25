#!/bin/bash

# CodeObit UI Startup Script
# This script starts the web-based UI for CodeObit CLI

echo "================================================"
echo "         CodeObit UI - Starting Up"
echo "================================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.11 or later."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✓ Python version: $PYTHON_VERSION"

# Create virtual environment if it doesn't exist
if [ ! -d "venv_ui" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv_ui
fi

# Activate virtual environment
source venv_ui/bin/activate

# Install/upgrade pip
echo "Updating pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "Installing dependencies..."
pip install flask flask-cors flask-socketio python-socketio watchdog --quiet

# Check if other requirements are installed
if [ -f "requirements.txt" ]; then
    echo "Installing project requirements..."
    pip install -r requirements.txt --quiet
fi

# Set environment variables
export FLASK_APP=ui_app.py
export FLASK_ENV=development
export DEBUG=True

# Create necessary directories
mkdir -p ui/templates ui/build/static uploads

echo ""
echo "================================================"
echo "     CodeObit UI is starting..."
echo "================================================"
echo ""
echo "  🌐 Web UI: http://localhost:5000"
echo "  📡 WebSocket: ws://localhost:5000"
echo ""
echo "  Press Ctrl+C to stop the server"
echo ""
echo "================================================"
echo ""

# Start the Flask application
python3 ui_app.py