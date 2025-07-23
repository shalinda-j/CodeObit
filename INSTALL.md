# 🚀 Installation Guide

Complete installation instructions for codeobit v1.0.0-beta

## 📋 Prerequisites

### System Requirements
- **Python**: 3.11 or higher
- **Operating System**: Windows 10+, macOS 10.15+, or Linux (Ubuntu 20.04+)
- **RAM**: Minimum 4GB (8GB recommended)
- **Storage**: 500MB free space
- **Internet**: Required for AI features and web browsing

### API Requirements
- **Google Gemini API Key** ([Get one here](https://aistudio.google.com/app/apikey))

## 🔧 Installation Methods

### Method 1: Git Clone (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/codeobit-v1.git
cd codeobit-v1

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up API key (see Configuration section below)
```

### Method 2: Download ZIP

1. Download the ZIP file from [GitHub Releases](https://github.com/yourusername/codeobit-v1/releases)
2. Extract to your desired location
3. Follow the same steps as Method 1 starting from creating the virtual environment

## 🔑 Configuration

### Setting up your API Key

#### Option 1: Environment Variable (Recommended)
```bash
# Windows (PowerShell)
$env:GEMINI_API_KEY="your-api-key-here"

# Windows (Command Prompt)
set GEMINI_API_KEY=your-api-key-here

# macOS/Linux
export GEMINI_API_KEY="your-api-key-here"
```

#### Option 2: Configuration File
The API key will be saved automatically when you first run codeobit and enter it through the interactive prompt.

## 🎯 First Run

### Launch codeobit
```bash
# Standard launch
python main.py

# Quick launcher (alternative)
python gemini
```

### Initial Setup
1. **Enter API Key**: When prompted, enter your Google Gemini API key
2. **Test Connection**: codeobit will automatically test the connection
3. **Welcome Screen**: You'll see the codeobit welcome interface
4. **Ready to Code**: Start with `/help` to see available commands

## 🧪 Verify Installation

### Test Basic Functionality
```bash
# In codeobit interactive mode:
/help          # Should show command list
/status        # Should show system status
/quickstart    # Should show quick start guide
```

### Test AI Features (requires API key)
```bash
# Simple AI test
create a hello world function in python

# Code generation test
/generate function "calculate fibonacci sequence"
```

## 🔧 Platform-Specific Setup

### Windows

#### Prerequisites
```powershell
# Check Python version
python --version

# Install Git (if not already installed)
# Download from: https://git-scm.com/download/win
```

#### Common Issues
- **Python not found**: Install Python from [python.org](https://python.org) and add to PATH
- **Permission errors**: Run PowerShell as Administrator
- **Virtual environment issues**: Use `py -m venv` instead of `python -m venv`

### macOS

#### Prerequisites
```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.11+
brew install python@3.11

# Install Git (if not already installed)
brew install git
```

#### Common Issues
- **Command Line Tools**: Install with `xcode-select --install`
- **Permission issues**: Use `sudo` carefully or adjust permissions

### Linux (Ubuntu/Debian)

#### Prerequisites
```bash
# Update package list
sudo apt update

# Install Python 3.11+
sudo apt install python3.11 python3.11-venv python3-pip

# Install Git
sudo apt install git

# Install additional dependencies
sudo apt install curl wget
```

#### Common Issues
- **Python version**: Ensure you're using Python 3.11+ with `python3.11 --version`
- **Virtual environment**: Use `python3.11 -m venv` instead of `python -m venv`

### Linux (CentOS/RHEL/Fedora)

#### Prerequisites
```bash
# For Fedora:
sudo dnf install python3.11 python3-pip git

# For CentOS/RHEL:
sudo yum install python3.11 python3-pip git
```

## 🚀 Advanced Setup

### Development Installation
```bash
# Clone with development dependencies
git clone https://github.com/yourusername/codeobit-v1.git
cd codeobit-v1

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install with development dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Set up pre-commit hooks
pre-commit install  # If available
```

### Docker Installation (Optional)
```bash
# Build Docker image
docker build -t codeobit:beta .

# Run in container
docker run -it -e GEMINI_API_KEY="your-key" codeobit:beta
```

## 🔍 Troubleshooting

### Common Issues

#### API Key Issues
```
Error: Gemini API key is required
```
**Solution**: Set the `GEMINI_API_KEY` environment variable or enter it when prompted

#### Python Version Issues
```
Error: Python 3.11+ is required
```
**Solution**: Install Python 3.11 or higher and ensure it's in your PATH

#### Import Errors
```
ModuleNotFoundError: No module named 'rich'
```
**Solution**: Install dependencies with `pip install -r requirements.txt`

#### Permission Errors
```
Permission denied: /path/to/project
```
**Solution**: 
- On Windows: Run as Administrator or check folder permissions
- On macOS/Linux: Use `sudo` or adjust file permissions with `chmod`

### Network Issues
- **Connection timeout**: Check internet connection and firewall settings
- **SSL/TLS errors**: Update certificates or disable SSL verification temporarily
- **Proxy issues**: Configure proxy settings in your environment

### Getting Help

If you encounter issues:

1. **Check the logs**: Look for error messages in the terminal
2. **Review requirements**: Ensure all prerequisites are met
3. **Update dependencies**: Run `pip install --upgrade -r requirements.txt`
4. **Search issues**: Check [GitHub Issues](https://github.com/yourusername/codeobit-v1/issues)
5. **Ask for help**: Join our [Discord](https://discord.gg/codeobit) or create an issue

## 📱 Optional Components

### Web Browser Support (for /browse command)
```bash
# Chrome/Chromium (recommended)
# Install Chrome from: https://www.google.com/chrome/

# Or install Chromium
# Ubuntu: sudo apt install chromium-browser
# macOS: brew install chromium
# Windows: Download from chromium.org
```

### Test Framework Support
```bash
# For test generation and execution
pip install pytest pytest-cov

# For specific testing frameworks
pip install unittest2  # Enhanced unittest
pip install nose2      # Alternative test runner
```

## ✅ Installation Complete!

You should now have codeobit successfully installed and ready to use.

### Next Steps:
1. **Read the README**: Familiarize yourself with features and commands
2. **Try examples**: Start with simple code generation tasks
3. **Join community**: Connect with other users on Discord
4. **Provide feedback**: Help us improve by reporting issues and suggestions

---

**Welcome to the future of AI-powered development! 🎯⚡️**

Need help? Contact us at support@codeobit.dev or join our [Discord community](https://discord.gg/codeobit).
