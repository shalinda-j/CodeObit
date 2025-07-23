# 📱 codeobit on Termux - Mobile AI Development

Run the complete codeobit AI Software Engineer tool on your Android device using Termux!

## 🚀 Quick Installation

### Step 1: Install Termux
1. Download Termux from [F-Droid](https://f-droid.org/packages/com.termux/) (recommended)
2. Or from [GitHub Releases](https://github.com/termux/termux-app/releases)

### Step 2: Setup Termux Environment
```bash
# Update packages
pkg update && pkg upgrade -y

# Install essential packages
pkg install -y python git wget curl nano vim

# Install Python packages build dependencies
pkg install -y python-pip libffi openssl libjpeg-turbo

# Install additional tools for development
pkg install -y nodejs-lts tree htop
```

### Step 3: Install codeobit
```bash
# Clone the repository
git clone https://github.com/your-repo/codeobit-v1.git
cd codeobit-v1

# Install Python dependencies
pip install -r requirements.txt

# Make the main script executable
chmod +x main.py
```

### Step 4: Initial Setup
```bash
# Initialize codeobit with your Gemini API key
python main.py init --api-key YOUR_GEMINI_API_KEY

# Or set environment variable
export GEMINI_API_KEY="your_api_key_here"
echo 'export GEMINI_API_KEY="your_api_key_here"' >> ~/.bashrc
```

## 📋 Termux-Specific Requirements

### Required Termux Packages
```bash
# Core packages
pkg install -y python python-pip git wget curl

# Build dependencies
pkg install -y clang make cmake pkg-config
pkg install -y libffi libffi-dev openssl openssl-dev
pkg install -y libjpeg-turbo libjpeg-turbo-dev

# Optional but recommended
pkg install -y nodejs-lts tree htop nano vim
```

### Python Dependencies (Termux compatible)
```bash
# Install in this order to avoid conflicts
pip install --upgrade pip setuptools wheel
pip install pyyaml requests click rich
pip install google-genai beautifulsoup4

# Selenium may need special handling on Termux
pip install selenium --no-deps
```

## 🎯 Usage on Termux

### Interactive Mode (Recommended for Mobile)
```bash
# Start interactive AI coding session
python main.py interactive

# Or use the quick launcher
python main.py
```

### Command Examples
```bash
# Generate requirements
python main.py requirements generate --input "Build a mobile app"

# Create system design
python main.py design architecture --input requirements.md

# Generate code
python main.py code generate --input "Create REST API" --language Python

# Project planning
python main.py project init --name "Mobile Project" --template "mobile"
```

### Mobile-Optimized Commands
```bash
# Browse and collect data (mobile-friendly)
python main.py browse --url "https://example.com" --save-data

# Generate mobile-specific documentation
python main.py docs generate --format markdown --mobile-optimized

# Run QA checks
python main.py qa check --project-path .
```

## 📱 Mobile Optimization Features

### Touch-Friendly Interface
- Larger text output for mobile screens
- Simplified navigation commands
- Voice-to-text integration (future)

### Storage Management
```bash
# Check project storage usage
python main.py project status

# Clean up temporary files
python main.py project cleanup

# Export project data
python main.py project export --format json
```

### Network Optimization
- Reduced API calls for mobile data saving
- Offline mode support for cached responses
- Compression for large outputs

## 🔧 Termux Configuration

### Create Termux Shortcuts
```bash
# Create shortcut directory
mkdir -p ~/.shortcuts

# Create codeobit shortcut
cat > ~/.shortcuts/codeobit << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd ~/codeobit-v1
python main.py "$@"
EOF

chmod +x ~/.shortcuts/codeobit
```

### Storage Access
```bash
# Allow Termux to access Android storage
termux-setup-storage

# Create symlinks for easy access
ln -s /storage/emulated/0/Download ~/downloads
ln -s /storage/emulated/0/Documents ~/documents
```

### Useful Aliases
```bash
# Add to ~/.bashrc
echo 'alias cb="python ~/codeobit-v1/main.py"' >> ~/.bashrc
echo 'alias cbi="python ~/codeobit-v1/main.py interactive"' >> ~/.bashrc
echo 'alias cbhelp="python ~/codeobit-v1/main.py help"' >> ~/.bashrc

# Reload bashrc
source ~/.bashrc
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Package Installation Failures
```bash
# Update package lists
pkg update

# Force reinstall problematic packages
pkg reinstall python python-pip

# Clear pip cache
pip cache purge
```

#### 2. SSL Certificate Issues
```bash
# Update CA certificates
pkg install ca-certificates

# Or skip SSL verification (not recommended)
pip install --trusted-host pypi.org --trusted-host pypi.python.org package_name
```

#### 3. Memory Issues
```bash
# Check available memory
free -h

# Clear system cache
python -m pip cache purge

# Use swap file if needed
termux-setup-storage
```

#### 4. Selenium WebDriver Issues
```bash
# Install headless browser for mobile
pkg install chromium

# Set browser path
export CHROME_BIN=/data/data/com.termux/files/usr/bin/chromium-browser
```

### Performance Tips
1. **Use Interactive Mode**: More efficient for mobile usage
2. **Cache API Responses**: Set up local caching
3. **Limit Concurrent Operations**: Mobile devices have limited resources
4. **Use WiFi When Possible**: For heavy API operations

## 📊 Mobile-Specific Features

### Screen Adaptation
- Auto-adjusts output for mobile screen sizes
- Simplified table formatting
- Touch-friendly prompts

### Battery Optimization
- Reduced CPU-intensive operations
- Smart API call batching
- Background task management

### Data Usage Monitoring
```bash
# Check data usage
python main.py project stats --include-network

# Enable data-saving mode
python main.py config set data_saving_mode true
```

## 🔮 Advanced Mobile Features

### Integration with Android Apps
```bash
# Share files with Android apps
termux-share file.py

# Open URLs in Android browser
termux-open-url "https://example.com"

# Send notifications
termux-notification --title "codeobit" --content "Task completed"
```

### Voice Integration (Future)
```bash
# Speech-to-text (when available)
termux-speech-to-text

# Text-to-speech for outputs
termux-tts-speak "Build completed successfully"
```

## 📝 Mobile Development Workflow

### 1. Project Setup on Mobile
```bash
# Create new mobile project
cb project init --name "MobileApp" --template "mobile" --platform "android"

# Generate requirements for mobile app
cb requirements generate --input "Social media mobile app" --platform "mobile"
```

### 2. Mobile-First Development
```bash
# Generate mobile-optimized code
cb code generate --input "User authentication" --platform "mobile" --framework "react-native"

# Create mobile tests
cb test generate --input "Login functionality" --platform "mobile" --framework "jest"
```

### 3. Mobile Deployment
```bash
# Generate mobile deployment config
cb devops pipeline --project-type "mobile" --platform "github"

# Create mobile-specific documentation
cb docs generate --type "mobile-readme" --include-screenshots
```

Ready to code on the go! 🚀📱
