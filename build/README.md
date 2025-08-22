# CodeObit CLI Build System

This directory contains the build system for creating standalone executables of the CodeObit CLI for Windows, Linux, and macOS.

## 🎯 Overview

The build system uses PyInstaller to create self-contained executables that don't require Python to be installed on the target system. This makes distribution and deployment much easier for end users.

## 📋 Prerequisites

### System Requirements
- **Python 3.11+** installed and accessible from command line
- **pip** package manager
- **Internet connection** for downloading dependencies

### Platform-Specific Requirements

#### Windows
- Windows 10 or later
- Windows Developer Tools (automatically installed with Python)

#### Linux
- Modern Linux distribution (Ubuntu 20.04+, CentOS 8+, etc.)
- Build essentials: `sudo apt install build-essential` (Ubuntu/Debian)

#### macOS
- macOS 10.14 or later
- Xcode Command Line Tools: `xcode-select --install`
- Homebrew (recommended): `brew install upx` for compression

## 🚀 Quick Start

### Method 1: Cross-Platform Build Script (Recommended)
```bash
# Navigate to project root
cd /path/to/CodeObit-1

# Run the cross-platform build script
python build/build.py
```

### Method 2: Platform-Specific Scripts

#### Windows
```cmd
# Open Command Prompt in project root
cd C:\path\to\CodeObit-1

# Run Windows build script
build\build_windows.bat
```

#### Linux/macOS
```bash
# Navigate to project root
cd /path/to/CodeObit-1

# Make script executable and run
chmod +x build/build_linux.sh
./build/build_linux.sh
```

### Method 3: Manual PyInstaller
```bash
# Install build dependencies
pip install -r requirements-build.txt

# Run PyInstaller with spec file
pyinstaller --clean --noconfirm codeobit.spec
```

## 📁 Build Artifacts

After a successful build, you'll find the following in the `dist/` directory:

### Windows
- `codeobit.exe` - Standalone executable
- `codeobit-windows-x64.zip` - Distribution package

### Linux
- `codeobit` - Standalone executable
- `codeobit-linux-x64.tar.gz` - Distribution package

### macOS
- `codeobit` - Standalone executable
- `codeobit-macos-x64.tar.gz` - Distribution package

## ⚙️ Build Configuration

### PyInstaller Spec File (`codeobit.spec`)
The main configuration file that defines:
- Entry point script
- Hidden imports for AI providers and modules
- Data files to include
- Platform-specific settings
- Optimization options

### Key Configuration Options
```python
# Enable UPX compression (reduces file size)
upx=True

# Console application (shows terminal output)
console=True

# One-file bundle (everything in single executable)
# Set to False for one-folder bundle
```

### Customizing the Build

#### Adding New Dependencies
If you add new dependencies to the project:

1. Update `requirements.txt` with the new package
2. Add hidden imports to `codeobit.spec` if needed:
   ```python
   hidden_imports = [
       # ... existing imports ...
       'your_new_module',
       'your_new_module.submodule',
   ]
   ```

#### Including Additional Data Files
To include additional data files in the executable:

1. Add them to the `data_files` list in `codeobit.spec`:
   ```python
   data_files = [
       # ... existing files ...
       ('path/to/your/file.txt', 'destination/folder'),
   ]
   ```

## 🔧 Troubleshooting

### Common Issues

#### 1. Import Errors
**Problem**: `ModuleNotFoundError` when running the executable

**Solution**: Add missing modules to `hidden_imports` in `codeobit.spec`

#### 2. Missing Data Files
**Problem**: Application can't find configuration or template files

**Solution**: Add missing files to `data_files` in `codeobit.spec`

#### 3. Large Executable Size
**Solutions**:
- Enable UPX compression: `upx=True`
- Exclude unnecessary modules in `excludes` list
- Use one-folder bundle instead of one-file

#### 4. Slow Startup
**Problem**: Executable takes long time to start

**Solutions**:
- Use one-folder bundle (faster startup)
- Reduce number of hidden imports
- Exclude heavy unused libraries

#### 5. Antivirus False Positives
**Problem**: Antivirus software flags the executable

**Solutions**:
- Submit to antivirus vendors for whitelisting
- Sign the executable with a code signing certificate
- Use one-folder bundle instead of one-file

### Debug Mode
To build with debug information:

```bash
# Edit codeobit.spec and set debug=True
debug=True

# Or use PyInstaller directly
pyinstaller --debug=all codeobit.spec
```

### Verbose Output
For detailed build information:

```bash
pyinstaller --log-level=DEBUG codeobit.spec
```

## 🤖 Automated Builds (CI/CD)

### GitHub Actions
The project includes a GitHub Actions workflow (`.github/workflows/build.yml`) that automatically:

- Builds executables for Windows, Linux, and macOS
- Runs tests on the built executables
- Creates release packages
- Publishes releases on GitHub

### Manual Release Process
1. Tag a new version: `git tag v1.0.0`
2. Push the tag: `git push origin v1.0.0`
3. GitHub Actions will automatically build and create a release

### Local Testing
Before creating a release, test the build locally:

```bash
# Build for current platform
python build/build.py

# Test the executable
./dist/codeobit --help
./dist/codeobit interactive
```

## 📦 Distribution

### End-User Instructions

#### Windows
1. Download `codeobit-windows-x64.zip`
2. Extract the ZIP file
3. Run `codeobit.exe`

#### Linux
1. Download `codeobit-linux-x64.tar.gz`
2. Extract: `tar -xzf codeobit-linux-x64.tar.gz`
3. Make executable: `chmod +x codeobit`
4. Run: `./codeobit`

#### macOS
1. Download `codeobit-macos-x64.tar.gz`
2. Extract: `tar -xzf codeobit-macos-x64.tar.gz`
3. Run: `./codeobit`

### System Requirements for End Users
- **Windows**: Windows 10 or later (x64)
- **Linux**: Modern Linux distribution (x64) with glibc 2.17+
- **macOS**: macOS 10.14 or later (x64)
- **No Python installation required**

## 🛠️ Advanced Configuration

### Custom Icon
To add a custom icon:

1. Create icon files:
   - Windows: `.ico` format
   - Linux/macOS: `.png` format

2. Update `codeobit.spec`:
   ```python
   icon='path/to/your/icon.ico'  # Windows
   icon='path/to/your/icon.png'  # Linux/macOS
   ```

### Code Signing
For production releases, consider code signing:

#### Windows
```bash
# Using signtool (Windows SDK)
signtool sign /f certificate.pfx /p password /t http://timestamp.url codeobit.exe
```

#### macOS
```bash
# Using codesign
codesign -s "Developer ID Application: Your Name" --timestamp codeobit
```

### UPX Compression
To install UPX for smaller executables:

#### Windows
1. Download UPX from https://upx.github.io/
2. Add UPX to PATH
3. PyInstaller will automatically use it

#### Linux
```bash
sudo apt install upx-ucl  # Ubuntu/Debian
sudo yum install upx      # CentOS/RHEL
```

#### macOS
```bash
brew install upx
```

## 📊 Build Statistics

Typical build sizes (with UPX compression):
- **Windows**: ~45-60 MB
- **Linux**: ~50-65 MB  
- **macOS**: ~55-70 MB

Build times:
- **Local build**: 2-5 minutes
- **GitHub Actions**: 5-10 minutes per platform

## 🤝 Contributing

To contribute to the build system:

1. Test your changes on multiple platforms
2. Update this README if adding new features
3. Ensure GitHub Actions workflow still passes
4. Document any new dependencies or requirements

## 📚 References

- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [UPX Documentation](https://upx.github.io/)

## 🐛 Issues

If you encounter build issues:

1. Check this troubleshooting guide
2. Search existing GitHub issues
3. Create a new issue with:
   - Your operating system and version
   - Python version
   - Complete error log
   - Steps to reproduce