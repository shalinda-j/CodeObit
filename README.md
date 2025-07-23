<div align="center">

# CodeObit CLI
### AI-Powered Interactive Development Environment

<img src="https://raw.githubusercontent.com/shalinda-j/CodeObit/main/assets/codeobit-logo.png" alt="CodeObit CLI Logo" width="200" height="200">

**Transform your development workflow with intelligent AI assistance**

[![Version](https://img.shields.io/badge/version-1.0.0--beta-blue?style=for-the-badge)](https://github.com/shalinda-j/CodeObit/releases)
[![Python](https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/status-Public%20Beta-orange?style=for-the-badge)](https://github.com/shalinda-j/CodeObit)

[🚀 Get Started](#-installation) • [📖 Documentation](#-features) • [💬 Community](https://github.com/shalinda-j/CodeObit/discussions) • [🐛 Report Bug](https://github.com/shalinda-j/CodeObit/issues)

</div>

---

## 🌟 What is CodeObit CLI?

CodeObit CLI is a revolutionary AI-powered development environment that transforms how you build software. With multi-AI provider support, intelligent file management, and seamless workflow automation, it's designed for developers who want to focus on creating rather than configuring.

### ⚡ Key Highlights
- **Multi-AI Support**: Seamlessly switch between Gemini, Qwen 3, and OpenAI GPT
- **Natural File References**: Mention files with `@filename.py` syntax
- **Image Analysis**: Upload and analyze diagrams, wireframes, and screenshots
- **Smart Auto-save**: Never lose your work with intelligent version control
- **Web Integration**: Automatically browse and summarize web resources
- **Cross-Platform**: Works on Windows, macOS, and Linux

## ✨ Features

### 🤖 Multi-AI Provider Support

<img src="https://raw.githubusercontent.com/shalinda-j/CodeObit/main/assets/multi-ai-providers.png" alt="Multi-AI Providers" width="600">

Switch seamlessly between the world's leading AI models:

- **🔮 Google Gemini** - Lightning-fast responses with Gemini 2.5-flash/pro
- **🧠 Qwen 3** - Advanced reasoning via OpenRouter integration  
- **⚡ OpenAI GPT-4** - Industry-leading language understanding
- **🔄 Smart Routing** - Automatic model selection based on task complexity

```bash
# List available providers
/providers list

# Switch providers instantly
/provider set qwen3
/provider set openai
/provider set gemini
```

### 📁 Natural File References with @ Syntax

Mention files naturally in conversations:

```bash
# Analyze specific files
"Review the code in @main.py and suggest improvements"

# Compare multiple files  
"Compare @src/auth.py with @tests/test_auth.py"

# Reference entire directories
"Show me the structure of @project/"
```

### 🖼️ Image Upload & Analysis

Upload diagrams, wireframes, and screenshots for AI analysis:

- **Supported Formats**: JPG, PNG, GIF, BMP, WebP, TIFF
- **Smart Processing**: Automatic resizing and optimization
- **AI Analysis**: Describe, explain, and generate code from images

```bash
# Upload and analyze images
/image upload wireframe.png
/image analyze diagram.jpg "Explain this architecture"
```

### 💾 Intelligent Auto-save System

- **Real-time Saving**: Never lose your work
- **Version History**: Track all changes automatically
- **Smart Recovery**: Restore from auto-saves
- **Fallback Protection**: Multiple save mechanisms

### 🌐 Web Integration & Data Collection

Automatically browse and collect web resources:

```bash
# Browse and save to project memory
/browse https://docs.python.org/3/
/browse https://fastapi.tiangolo.com/

# AI automatically summarizes and saves content
```

### 🎯 Interactive Development Environment

Experience "vibe coding" with:

- **🎨 Beautiful ASCII Branding** - Dynamic themes and rich UI
- **💬 Natural Conversations** - Chat with AI about your code
- **🔄 Project Memory** - Persistent context and data collection
- **⚡ Workflow Automation** - Intelligent task completion
- **🐛 Advanced Debugging** - AI-powered error analysis
- **📊 Usage Tracking** - Monitor tokens and project status

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Google Gemini API key

### Setup
1. **Get your API key**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. **Initialize the CLI**:
   ```bash
   python main.py init
   ```
3. **Start interactive mode**:
   ```bash
   python main.py interactive
   # or
   python gemini
   ```

### Interactive Mode Examples

```
> Generate requirements for a task management app

> Design a REST API for user authentication  

> Write Python code for JWT token validation

> Create unit tests for the authentication function above

> Review the code for security vulnerabilities
```

### Traditional Mode Examples

```bash
# Generate requirements
echo "Build an e-commerce platform" > description.txt
python main.py requirements generate --input description.txt

# Create system design
python main.py design architecture --input requirements.md --technology "Python/React"

# Generate code
python main.py code generate --input "Create user auth API" --language Python

# Create tests
python main.py test generate --input app.py --framework pytest
```

### AI-Driven Project Planning Examples

```bash
# Initialize AI-powered project with dependency prediction
python main.py project init --name "E-commerce Platform" --template "web" --output ecommerce_project.json

# Generate comprehensive project plan with AI-driven scheduling
python main.py project plan --input requirements.md --team-size 5 --duration "4 months" --output project_plan.md

# Create AI-generated task management structure
python main.py project tasks --input project_plan.md --output task_structure.md

# Generate detailed project timeline with critical path analysis
python main.py project timeline --input project_plan.md --duration "16 weeks" --output timeline.md

# Get AI-powered project estimation
python main.py project estimate --input requirements.md --team-size 5 --output estimation.md

# Generate comprehensive project status report
python main.py project status --input ecommerce_project.json --output status_report.md
```

## 🎨 Interactive Commands

Within interactive mode, use these special commands:

- `/help` - Show available commands
- `/theme [auto|dark|light]` - Change color theme
- `/history` - View session history
- `/clear` - Clear screen
- `/status` - Show system status
- `/quickstart` - Display quick start guide
- `/exit` - Exit interactive mode

## 🏗️ Architecture

The CLI features a modular design with:

- **AI Integration Layer** - Google Gemini API client with multi-model support
- **Interactive Interface** - Conversational AI with context awareness
- **Command Modules** - Specialized handlers for different engineering workflows
- **Configuration Management** - YAML-based settings with environment variables
- **Rich UI** - Beautiful console output with syntax highlighting

## 🔧 Configuration

Configuration is stored in `config/config.yaml` with support for:

- API keys and model selection
- Output formatting preferences
- Project templates and defaults
- UI themes and display options

## 🤝 Workflow Integration

Perfect for:
- **Requirements Engineering** - Generate user stories and acceptance criteria
- **System Design** - Create architecture diagrams and technical specs
- **Code Development** - Generate, analyze, and optimize code
- **Testing** - Create comprehensive test suites
- **Security** - Vulnerability scanning and security analysis
- **Documentation** - Auto-generate API docs and user guides
- **Project Management** - Track progress and manage tasks

## 📊 AI Model Support

- **Default**: Gemini 2.5-flash (fast, efficient)
- **Complex Tasks**: Gemini 2.5-pro (detailed analysis)
- **Auto-routing**: Intelligent model selection based on request type

Experience the future of software engineering with AI assistance at your fingertips!