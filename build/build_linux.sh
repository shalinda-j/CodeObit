#!/bin/bash
# CodeObit CLI Build Script for Linux
# This script builds a standalone executable for Linux using PyInstaller

set -e  # Exit on any error

echo "========================================"
echo "CodeObit CLI Linux Build Script"
echo "========================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BUILD_DIR="$PROJECT_ROOT/build"
DIST_DIR="$PROJECT_ROOT/dist"
SPEC_FILE="$PROJECT_ROOT/codeobit.spec"

echo "Project Root: $PROJECT_ROOT"
echo "Build Directory: $BUILD_DIR"
echo "Distribution Directory: $DIST_DIR"
echo "Spec File: $SPEC_FILE"
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.11+ using your package manager:"
    echo "  Ubuntu/Debian: sudo apt update && sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

echo "Python version:"
python3 --version
echo

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed"
    echo "Please install pip3 using your package manager"
    exit 1
fi

# Check if PyInstaller is available
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "PyInstaller not found. Installing..."
    pip3 install --user pyinstaller>=6.0.0
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to install PyInstaller"
        exit 1
    fi
fi

echo "PyInstaller version:"
python3 -c "import PyInstaller; print(PyInstaller.__version__)"
echo

# Install/check dependencies
echo "Checking dependencies..."
cd "$PROJECT_ROOT"
pip3 install --user -r requirements.txt --quiet
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi
echo "Dependencies installed successfully."
echo

# Clean previous builds
echo "Cleaning previous builds..."
if [ -d "$DIST_DIR" ]; then
    rm -rf "$DIST_DIR"
    echo "Removed previous dist directory"
fi
if [ -d "$BUILD_DIR" ]; then
    # Don't remove build directory completely, just the PyInstaller build files
    rm -rf "$BUILD_DIR"/*.log "$BUILD_DIR"/*.toc "$BUILD_DIR"/*.pyz 2>/dev/null || true
    echo "Cleaned previous build artifacts"
fi
echo

# Build the executable
echo "Starting PyInstaller build..."
echo "Command: python3 -m PyInstaller --clean --noconfirm '$SPEC_FILE'"
echo

cd "$PROJECT_ROOT"
python3 -m PyInstaller --clean --noconfirm "$SPEC_FILE"

if [ $? -ne 0 ]; then
    echo
    echo "ERROR: Build failed!"
    echo "Check the output above for error details."
    exit 1
fi

echo
echo "========================================"
echo "Build completed successfully!"
echo "========================================"

# Check if executable was created
EXE_PATH="$DIST_DIR/codeobit"
if [ -f "$EXE_PATH" ]; then
    echo
    echo "Executable created: $EXE_PATH"
    
    # Get file size
    SIZE=$(stat -c%s "$EXE_PATH" 2>/dev/null || stat -f%z "$EXE_PATH" 2>/dev/null || echo "unknown")
    echo "File size: $SIZE bytes"
    
    # Make executable
    chmod +x "$EXE_PATH"
    echo "Executable permissions set"
    
    # Test the executable
    echo
    echo "Testing executable..."
    if "$EXE_PATH" --help >/dev/null 2>&1; then
        echo "Executable test passed"
    else
        echo "WARNING: Executable test failed"
    fi
    
    echo
    echo "Build artifacts location:"
    echo "- Executable: $EXE_PATH"
    echo "- Build logs: $BUILD_DIR"
    
else
    echo "ERROR: Executable not found at expected location: $EXE_PATH"
    exit 1
fi

echo
echo "========================================"
echo "Linux build process completed!"
echo "========================================"
echo
echo "To distribute the application:"
echo "1. Copy $EXE_PATH to target systems"
echo "2. Ensure execute permissions: chmod +x codeobit"
echo "3. No additional dependencies required"
echo "4. The executable is ready to run standalone"
echo
echo "To create a distributable archive:"
echo "cd $DIST_DIR && tar -czf codeobit-linux-x64.tar.gz codeobit"
echo