# AI Software Engineer CLI

## Overview

This repository contains a comprehensive AI-powered CLI tool for software engineering workflows using Google Gemini. The application provides automated assistance across the entire software development lifecycle, from requirements analysis to documentation generation.

## User Preferences

Preferred communication style: Simple, everyday language.

## Recent Changes (January 2025)

**Major Rebranding to "codeobit" with Enhanced Features**
- Complete interface rebranding with ASCII art "codeobit" logo
- Enhanced project status dashboard with token usage tracking
- Added comprehensive development lifecycle automation
- New MCP design pattern integration for advanced workflows
- "Vibe coding" experience with natural language project automation

**New Command Modules Added**
- `browse` - Web data collection with AI summarization and project memory storage
- `debug` - Advanced debugging with AI-powered error analysis and fix suggestions  
- `qa` - Quality assurance automation including browser testing and performance analysis
- Enhanced all existing commands with MCP design patterns

**Interactive Mode Enhancements**
- Updated with codeobit branding and new welcome experience
- Enhanced tips for vibe coding workflow
- Integrated data collection and project memory features

## System Architecture

### Core Architecture
- **Command-line interface (CLI)** built with Python and argparse
- **Modular command structure** with separate modules for different workflow phases
- **AI integration** via Google Gemini API for intelligent assistance
- **Rich console output** for enhanced user experience
- **Configuration management** with YAML-based settings
- **Template system** for project initialization

### Technology Stack
- **Python 3.x** as the primary language
- **Google Gemini API** for AI-powered features
- **Rich** library for enhanced terminal output
- **Pydantic** for data modeling and validation
- **YAML/JSON** for configuration and data storage
- **argparse** for command-line interface

## Key Components

### 1. CLI Core (`cli/core.py`)
- Main CLI application class and command router
- Argument parsing and command dispatch
- Configuration management integration
- Console initialization with Rich library
- Interactive mode integration and launcher

### 1a. Interactive Interface (`cli/interactive.py`)
- Gemini-style conversational AI interface
- Session history and context management
- Intelligent request routing based on natural language
- Color theme support (auto, dark, light)
- Special commands (/help, /theme, /history, etc.)
- Real-time AI processing with visual indicators

### 2. AI Integration (`cli/ai/`)
- **GeminiClient**: Wrapper for Google Gemini API
- Support for multiple models (flash and pro variants)
- Error handling and connection testing
- API key management via environment variables

### 3. Command Modules (`cli/commands/`)
- **Requirements**: Analysis and management of project requirements
- **Design**: System architecture and design document generation
- **Code**: Code generation, analysis, and optimization
- **Test**: Automated testing and test case generation
- **Security**: Security analysis and vulnerability scanning
- **Docs**: Documentation generation and management
- **Project**: Project management and task tracking

### 4. Enhanced Command Modules (`cli/commands/`)
- **Browse**: Web data collection with AI summarization and memory storage
- **Debug**: Advanced debugging with AI-powered error analysis and solutions
- **QA**: Quality assurance automation with browser testing and performance metrics

### 5. Data Models (`cli/models/`)
- **Project**: Project structure and metadata with token tracking
- **Task**: Task management with status tracking
- **Milestone**: Project milestone definitions
- **Phase**: Project phase management

### 6. Utilities (`cli/utils/`)
- **ConfigManager**: Configuration file handling with enhanced project status
- **FileManager**: File system operations with memory storage capabilities
- **TemplateManager**: Project template management with MCP patterns

## Data Flow

1. **User Input**: Commands entered via CLI with arguments and options
2. **Command Parsing**: Arguments parsed and routed to appropriate command module
3. **Configuration Loading**: API keys and settings loaded from config files
4. **AI Processing**: Gemini API called for intelligent analysis/generation
5. **File Operations**: Results written to files or displayed in console
6. **Rich Output**: Formatted output displayed with syntax highlighting and panels

## External Dependencies

### Required APIs
- **Google Gemini API**: Core AI functionality requiring API key
- API key must be set via `GEMINI_API_KEY` environment variable

### Python Libraries
- **google-genai**: Google Gemini API client
- **rich**: Terminal formatting and display
- **pydantic**: Data validation and modeling
- **pyyaml**: YAML configuration file handling
- **pathlib**: Modern path handling

### Optional Integrations
- **Logging**: File-based logging for debugging and audit trails
- **Templates**: JSON-based project templates for initialization

## Deployment Strategy

### Development Setup
- Local Python environment with pip dependencies
- Environment variable configuration for API keys
- Config directory with YAML settings
- Templates directory for project scaffolding

### Configuration Management
- Default config values with override capabilities
- Environment variable support for sensitive data
- YAML-based configuration files
- Logging configuration with file and console output

### File Structure
- Modular package structure for maintainability
- Separate concerns with dedicated modules
- Template-based project initialization
- Configurable output directories

### Error Handling
- Comprehensive logging throughout the application
- Graceful error handling with user-friendly messages
- API connection testing and validation
- File operation error recovery

The application is designed as a standalone CLI tool that can be installed and run locally, with configuration managed through files and environment variables. The modular architecture allows for easy extension and maintenance of individual command modules.