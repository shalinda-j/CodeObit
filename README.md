# 🚀 AI Software Engineer CLI

A comprehensive AI-powered CLI tool for software engineering workflows using Google Gemini 2.5. Features both traditional command-line interface and interactive Gemini-style conversation mode.

## ✨ Features

### 🔥 Interactive Mode (New!)
Experience the power of conversational AI with our new interactive mode, similar to the official Gemini CLI:

```bash
python main.py interactive
```

Or use the quick launcher:
```bash
python gemini
```

**Interactive Features:**
- 🎨 Color themes (auto, dark, light)
- 💬 Natural conversation with context awareness
- 🔄 Session history tracking
- ⚡ Intelligent request routing
- 🎯 Specialized AI roles for different tasks

### 🛠️ Traditional Commands
- `requirements` - Analyze and manage project requirements
- `design` - Generate system architecture and design documents  
- `code` - AI-powered code generation and analysis
- `test` - Automated testing and test case generation
- `security` - Security analysis and vulnerability scanning
- `docs` - Automated documentation generation
- `project` - Project management and task tracking

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