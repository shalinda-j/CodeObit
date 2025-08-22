@echo off
REM CodeObit CLI Build Script for Windows
REM This script builds a standalone executable for Windows using PyInstaller

echo ========================================
echo CodeObit CLI Windows Build Script
echo ========================================
echo.

REM Set build environment
set BUILD_DIR=%~dp0build
set DIST_DIR=%~dp0dist
set SPEC_FILE=%~dp0codeobit.spec

echo Build Directory: %BUILD_DIR%
echo Distribution Directory: %DIST_DIR%
echo Spec File: %SPEC_FILE%
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.11+ and add it to your PATH
    pause
    exit /b 1
)

echo Python version:
python --version
echo.

REM Check if PyInstaller is available
python -c "import PyInstaller" >nul 2>&1
if errorlevel 1 (
    echo ERROR: PyInstaller is not installed
    echo Installing PyInstaller...
    pip install pyinstaller>=6.0.0
    if errorlevel 1 (
        echo ERROR: Failed to install PyInstaller
        pause
        exit /b 1
    )
)

echo PyInstaller version:
python -c "import PyInstaller; print(PyInstaller.__version__)"
echo.

REM Install/check dependencies
echo Checking dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo Dependencies installed successfully.
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "%DIST_DIR%" (
    rmdir /s /q "%DIST_DIR%"
    echo Removed previous dist directory
)
if exist "%BUILD_DIR%" (
    rmdir /s /q "%BUILD_DIR%"
    echo Removed previous build directory
)
echo.

REM Build the executable
echo Starting PyInstaller build...
echo Command: pyinstaller --clean --noconfirm "%SPEC_FILE%"
echo.

pyinstaller --clean --noconfirm "%SPEC_FILE%"

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Check the output above for error details.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================

REM Check if executable was created
set EXE_PATH=%DIST_DIR%\codeobit.exe
if exist "%EXE_PATH%" (
    echo.
    echo Executable created: %EXE_PATH%
    
    REM Get file size
    for %%A in ("%EXE_PATH%") do (
        set SIZE=%%~zA
    )
    echo File size: %SIZE% bytes
    
    REM Test the executable
    echo.
    echo Testing executable...
    "%EXE_PATH%" --help >nul 2>&1
    if errorlevel 1 (
        echo WARNING: Executable test failed
    ) else (
        echo Executable test passed
    )
    
    echo.
    echo Build artifacts location:
    echo - Executable: %EXE_PATH%
    echo - Build logs: %BUILD_DIR%
    
) else (
    echo ERROR: Executable not found at expected location: %EXE_PATH%
    exit /b 1
)

echo.
echo ========================================
echo Windows build process completed!
echo ========================================
echo.
echo To distribute the application:
echo 1. Copy %EXE_PATH% to target systems
echo 2. No additional dependencies required
echo 3. The executable is ready to run standalone
echo.

pause