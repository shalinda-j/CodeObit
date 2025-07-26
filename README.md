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
- **Advanced Project Management**: Organized project structure with dedicated folders
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

### 📁 Advanced Project Management

Organized project structure with proper directory management:

- **Structured Projects**: Each project gets its own dedicated folder
- **Standard Layout**: Automatic creation of `src/`, `docs/`, `tests/`, `assets/`, `config/` directories
- **Project Metadata**: JSON-based project configuration and metadata
- **Multi-Project Support**: Switch between multiple projects seamlessly
- **Project Templates**: Pre-configured project structures
- **Export/Import**: Easy project sharing and backup

```bash
# Create a new project
/project new "My Web App" --type web

# Load an existing project
/project load "My Web App"

# List all projects
/project list

# Export project
/project export "My Web App" --format zip
```

### 💾 Intelligent Auto-save System

- **Real-time Saving**: Never lose your work
- **Project-based Saving**: Data saved to proper project directories
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
- **📁 Project Organization** - Structured file management and organization
- **⚡ Workflow Automation** - Intelligent task completion
- **🐛 Advanced Debugging** - AI-powered error analysis
- **📊 Usage Tracking** - Monitor tokens and project status
- **🔀 Project Switching** - Seamlessly switch between multiple projects

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- API keys for your preferred AI providers (optional - can be configured interactively)

### 🔑 Multi-Provider Setup

CodeObit CLI supports **multiple AI providers** with **instant switching** and **interactive setup**. Configure your API keys using environment variables (recommended) or set them up interactively during first use.

#### Environment Variables (Recommended)

Set environment variables for your preferred providers:

**Windows (Command Prompt):**
```cmd
set GEMINI_API_KEY=your_gemini_api_key_here
set OPENAI_API_KEY=your_openai_api_key_here
set OPENROUTER_API_KEY=your_openrouter_api_key_here
set CLAUDE_API_KEY=your_anthropic_api_key_here
```

**Windows (PowerShell):**
```powershell
$env:GEMINI_API_KEY="your_gemini_api_key_here"
$env:OPENAI_API_KEY="your_openai_api_key_here"
$env:OPENROUTER_API_KEY="your_openrouter_api_key_here"
$env:CLAUDE_API_KEY="your_anthropic_api_key_here"
```

**macOS/Linux:**
```bash
export GEMINI_API_KEY="your_gemini_api_key_here"
export OPENAI_API_KEY="your_openai_api_key_here"
export OPENROUTER_API_KEY="your_openrouter_api_key_here"
export CLAUDE_API_KEY="your_anthropic_api_key_here"
```

#### Getting API Keys

- **Google Gemini**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
- **OpenAI GPT**: Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
- **Claude**: Visit [Anthropic Console](https://console.anthropic.com/)
- **Qwen 3**: Visit [OpenRouter](https://openrouter.ai/keys) (uses OpenRouter)
- **DeepSeek**: Visit [DeepSeek Platform](https://platform.deepseek.com/)

#### Interactive Setup (No Pre-configuration Required!)

Don't have API keys set up? No problem! CodeObit CLI will guide you through interactive setup:

```bash
# Start without any API keys - interactive setup will guide you
python main.py interactive

# Or use provider shortcuts for instant setup
!gpt     # Launches OpenAI GPT setup if not configured
!gemini  # Launches Google Gemini setup if not configured
!claude  # Launches Claude setup if not configured
!qwen    # Launches Qwen setup if not configured
```

### Setup
1. **Optional: Configure API keys** (see above) - or skip and set up interactively
2. **Initialize the CLI** (creates project structure):
   ```bash
   python main.py init
   ```
3. **Start interactive mode**:
   ```bash
   python main.py interactive
   # or use the shortcut
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

### General Commands
- `/help` - Show available commands
- `/theme [auto|dark|light]` - Change color theme
- `/history` - View session history
- `/clear` - Clear screen
- `/status` - Show system status
- `/quickstart` - Display quick start guide
- `/exit` - Exit interactive mode

### AI Provider Commands
- `/providers list` - List all available AI providers
- `/provider set [gemini|openai|qwen3]` - Switch AI provider
- `/provider status` - Show current provider status

### Project Management Commands
- `/project new <name> [--type <template>]` - Create a new project
- `/project load <name>` - Load an existing project
- `/project list` - List all available projects
- `/project delete <name>` - Delete a project
- `/project export <name> [--format zip]` - Export a project
- `/project current` - Show current project information
- `/project save` - Manually save current project

### File and Image Commands
- `/image upload <path>` - Upload and analyze images
- `/browse <url>` - Browse and summarize web content

## 🏗️ Architecture

The CLI features a modular design with:

- **AI Integration Layer** - Multi-provider support (Gemini, OpenAI, Qwen 3)
- **Project Management System** - Structured project organization and management
- **Interactive Interface** - Conversational AI with context awareness
- **Command Modules** - Specialized handlers for different engineering workflows
- **Configuration Management** - YAML-based settings with environment variables
- **File Management** - Advanced file handling with @ syntax references
- **Rich UI** - Beautiful console output with syntax highlighting

### Project Structure

Each CodeObit project follows a standard structure:

```
~/CodeObit/Projects/
├── MyProject/
│   ├── src/              # Source code files
│   ├── docs/             # Documentation
│   ├── tests/            # Test files
│   ├── assets/           # Static assets
│   ├── config/           # Configuration files
│   ├── .codeobit/        # CodeObit metadata
│   └── project.json      # Project configuration
```

## 🔧 Configuration

Configuration is stored in `config/config.yaml` with support for:

- **API Keys and Models** - Multi-provider AI configuration
- **Project Settings** - Default project templates and structure
- **Output Formatting** - Customizable output preferences
- **UI Themes** - Dark, light, and auto themes
- **Project Paths** - Configurable project storage locations
- **Auto-save Settings** - Intelligent saving preferences

### Project Configuration

Each project contains a `project.json` file with:

```json
{
  "name": "My Project",
  "description": "Project description",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "type": "web",
  "version": "1.0.0",
  "metadata": {
    "languages": ["Python", "JavaScript"],
    "frameworks": ["FastAPI", "React"],
    "tags": ["web", "api", "frontend"]
  }
}
```

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