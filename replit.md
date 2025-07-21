# AI Software Engineer CLI

## Overview

This repository contains a comprehensive AI-powered CLI tool for software engineering workflows using Google Gemini. The application provides automated assistance across the entire software development lifecycle, from requirements analysis to documentation generation.

## User Preferences

Preferred communication style: Simple, everyday language.

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

### 4. Data Models (`cli/models/`)
- **Project**: Project structure and metadata
- **Task**: Task management with status tracking
- **Milestone**: Project milestone definitions
- **Phase**: Project phase management

### 5. Utilities (`cli/utils/`)
- **ConfigManager**: Configuration file handling
- **FileManager**: File system operations
- **TemplateManager**: Project template management

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