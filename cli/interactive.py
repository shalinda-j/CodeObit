"""
Interactive mode for AI Software Engineer CLI
"""

import os
import sys
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax

from cli.ai.gemini_client import GeminiClient
from cli.utils.config import ConfigManager
from cli.utils.file_manager import FileManager


class InteractiveCLI:
    """Interactive CLI interface similar to Gemini CLI"""
    
    def __init__(self):
        self.console = Console()
        self.config_manager = ConfigManager()
        self.file_manager = FileManager()
        self.gemini_client = None
        self.session_history = []
        self.color_theme = "auto"
        
    def start(self):
        """Start interactive CLI session"""
        try:
            self.show_welcome()
            self.setup_gemini()
            self.main_loop()
        except KeyboardInterrupt:
            self.console.print("\n[yellow]Session ended by user[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
    
    def show_welcome(self):
        """Display welcome screen with ASCII art and tips"""
        # Create codeobit ASCII art
        codeobit_ascii = """
 ██████╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ██╗████████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔═══██╗██╔══██╗██║╚══██╔══╝
██║     ██║   ██║██║  ██║█████╗  ██║   ██║██████╔╝██║   ██║   
██║     ██║   ██║██║  ██║██╔══╝  ██║   ██║██╔══██╗██║   ██║   
╚██████╗╚██████╔╝██████╔╝███████╗╚██████╔╝██████╔╝██║   ██║   
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   
        """
        
        welcome_panel = Panel(
            f"[bold cyan]{codeobit_ascii}[/bold cyan]\n\n"
            "[bold magenta]codeobit Interactive Development Environment[/bold magenta]\n\n"
            "🚀 [yellow]Vibe coding experience with AI automation[/yellow]\n\n"
            "• [green]Natural conversation[/green] - Describe what you want to build\n"
            "• [yellow]MCP design patterns[/yellow] - Advanced development workflows\n"
            "• [blue]Data collection & memory[/blue] - Intelligent project planning\n"
            "• [magenta]Browser automation[/magenta] - Testing and data gathering\n"
            "• [cyan]Complete lifecycle[/cyan] - From idea to production\n\n"
            "[bold green]Ready for some serious vibe coding! ⚡[/bold green]",
            title="🎯 codeobit Interactive Mode",
            border_style="cyan"
        )
        
        tips = """
[bold cyan]Vibe coding tips:[/bold cyan]
1. Describe your project idea naturally - I'll handle the technical details
2. Ask for browsing data collection to enhance your project
3. Use /project to start comprehensive development planning
4. /browse <url> to collect and save data to project memory

[dim]> create a social media app with real-time features[/dim]
        """
        
        self.console.print(welcome_panel)
        self.console.print(tips)
    
    def setup_gemini(self):
        """Setup and authenticate Gemini API"""
        try:
            config = self.config_manager.load_config()
            api_key = os.getenv('GEMINI_API_KEY')
            
            if config and 'api_key' in config:
                api_key = api_key or config['api_key']
            
            if not api_key:
                self.console.print("[yellow]API key not found. Let's set it up![/yellow]")
                api_key = Prompt.ask(
                    "[blue]Enter your Gemini API key[/blue]",
                    password=True
                )
                
                # Save API key to config
                if config is None:
                    config = {}
                config['api_key'] = api_key
                self.config_manager.save_config(config)
                os.environ['GEMINI_API_KEY'] = api_key
            
            # Initialize Gemini client
            self.gemini_client = GeminiClient()
            
            # Test connection
            with Live(Spinner("dots", "Testing connection..."), console=self.console):
                test_response = self.gemini_client.test_connection()
                
            if test_response:
                self.console.print("[green]✓ Connected to Gemini successfully![/green]")
            else:
                self.console.print("[red]✗ Failed to connect to Gemini[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Setup failed: {e}[/red]")
            sys.exit(1)
    
    def main_loop(self):
        """Main interactive loop"""
        while True:
            try:
                # Get user input
                user_input = Prompt.ask(
                    "[blue]>[/blue]",
                    default=""
                ).strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.startswith('/'):
                    self.handle_command(user_input[1:])
                    continue
                
                # Process with AI
                self.process_ai_request(user_input)
                
            except KeyboardInterrupt:
                if Confirm.ask("\n[yellow]Exit CLI?[/yellow]"):
                    break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
    
    def handle_command(self, command: str):
        """Handle special CLI commands"""
        parts = command.split()
        cmd = parts[0].lower()
        
        if cmd == "help":
            self.show_help()
        elif cmd == "theme":
            self.change_theme(parts[1] if len(parts) > 1 else None)
        elif cmd == "history":
            self.show_history()
        elif cmd == "clear":
            self.console.clear()
        elif cmd == "exit" or cmd == "quit":
            raise KeyboardInterrupt
        elif cmd == "status":
            self.show_status()
        elif cmd == "quickstart":
            self.show_quickstart()
        else:
            self.console.print(f"[red]Unknown command: {command}[/red]")
            self.show_help()
    
    def process_ai_request(self, request: str):
        """Process user request with AI"""
        try:
            # Add to session history
            self.session_history.append({"user": request})
            
            # Show processing indicator
            with Live(
                Spinner("dots", f"Processing: {request[:50]}..."),
                console=self.console
            ):
                # Determine request type and route appropriately
                response = self.route_request(request)
            
            # Display response
            self.display_response(response)
            
            # Add AI response to history
            self.session_history.append({"assistant": response})
            
        except Exception as e:
            self.console.print(f"[red]Failed to process request: {e}[/red]")
    
    def route_request(self, request: str) -> str:
        """Route request to appropriate AI function"""
        request_lower = request.lower()
        
        # Determine intent and route accordingly
        if any(word in request_lower for word in ['requirements', 'user story', 'specification']):
            return self.handle_requirements_request(request)
        elif any(word in request_lower for word in ['design', 'architecture', 'diagram']):
            return self.handle_design_request(request)
        elif any(word in request_lower for word in ['code', 'function', 'class', 'implement']):
            return self.handle_code_request(request)
        elif any(word in request_lower for word in ['test', 'testing', 'unit test']):
            return self.handle_test_request(request)
        elif any(word in request_lower for word in ['security', 'vulnerability', 'secure']):
            return self.handle_security_request(request)
        elif any(word in request_lower for word in ['document', 'docs', 'readme']):
            return self.handle_docs_request(request)
        else:
            # General AI conversation
            if self.gemini_client:
                return self.gemini_client.generate_content(request)
            else:
                return "Error: Gemini client not initialized"
    
    def handle_requirements_request(self, request: str) -> str:
        """Handle requirements-related requests"""
        system_instruction = (
            "You are a business analyst expert. Help create detailed software requirements "
            "including user stories, acceptance criteria, and functional specifications."
        )
        if self.gemini_client:
            return self.gemini_client.generate_content(request, system_instruction=system_instruction)
        return "Error: Gemini client not initialized"
    
    def handle_design_request(self, request: str) -> str:
        """Handle design-related requests"""
        system_instruction = (
            "You are a software architect. Help create system designs, architecture diagrams, "
            "and technical specifications. Focus on scalability, maintainability, and best practices."
        )
        if self.gemini_client:
            return self.gemini_client.generate_content(request, system_instruction=system_instruction)
        return "Error: Gemini client not initialized"
    
    def handle_code_request(self, request: str) -> str:
        """Handle code-related requests"""
        system_instruction = (
            "You are an expert software developer. Generate clean, well-documented, "
            "production-ready code following best practices and industry standards."
        )
        if self.gemini_client:
            return self.gemini_client.generate_content(request, system_instruction=system_instruction)
        return "Error: Gemini client not initialized"
    
    def handle_test_request(self, request: str) -> str:
        """Handle testing-related requests"""
        system_instruction = (
            "You are a QA engineer and testing expert. Create comprehensive test suites, "
            "test cases, and testing strategies for maximum code coverage and quality."
        )
        if self.gemini_client:
            return self.gemini_client.generate_content(request, system_instruction=system_instruction)
        return "Error: Gemini client not initialized"
    
    def handle_security_request(self, request: str) -> str:
        """Handle security-related requests"""
        system_instruction = (
            "You are a cybersecurity expert. Analyze code for vulnerabilities, "
            "suggest security improvements, and provide security best practices."
        )
        if self.gemini_client:
            return self.gemini_client.generate_content(request, system_instruction=system_instruction)
        return "Error: Gemini client not initialized"
    
    def handle_docs_request(self, request: str) -> str:
        """Handle documentation-related requests"""
        system_instruction = (
            "You are a technical writer. Create clear, comprehensive documentation "
            "including README files, API docs, and user guides."
        )
        if self.gemini_client:
            return self.gemini_client.generate_content(request, system_instruction=system_instruction)
        return "Error: Gemini client not initialized"
    
    def display_response(self, response: str):
        """Display AI response with proper formatting"""
        # Check if response contains code
        if "```" in response:
            # Split response into text and code blocks
            parts = response.split("```")
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    # Text part
                    if part.strip():
                        self.console.print(Markdown(part.strip()))
                else:
                    # Code part
                    lines = part.strip().split('\n')
                    if lines:
                        language = lines[0] if lines[0] else "text"
                        code = '\n'.join(lines[1:]) if len(lines) > 1 else lines[0]
                        if code.strip():
                            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
                            self.console.print(syntax)
        else:
            # Regular markdown response
            self.console.print(Markdown(response))
        
        self.console.print()  # Add spacing
    
    def show_help(self):
        """Show help information"""
        help_table = Table(title="Available Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        
        help_table.add_row("/help", "Show this help message")
        help_table.add_row("/theme [theme]", "Change color theme (auto, dark, light)")
        help_table.add_row("/history", "Show session history")
        help_table.add_row("/clear", "Clear screen")
        help_table.add_row("/status", "Show system status")
        help_table.add_row("/quickstart", "Show quick start guide")
        help_table.add_row("/exit", "Exit CLI")
        
        self.console.print(help_table)
        
        examples = """
[bold blue]Example Prompts:[/bold blue]
• "Generate requirements for a todo app"
• "Design a REST API for user authentication"
• "Write a Python function to validate email addresses"
• "Create unit tests for a shopping cart class"
• "Review this code for security vulnerabilities"
• "Write documentation for this API endpoint"
        """
        self.console.print(examples)
    
    def change_theme(self, theme: Optional[str]):
        """Change color theme"""
        if not theme:
            self.console.print(f"[blue]Current theme: {self.color_theme}[/blue]")
            self.console.print("[blue]Available themes: auto, dark, light[/blue]")
            return
        
        if theme in ["auto", "dark", "light"]:
            self.color_theme = theme
            self.console.print(f"[green]Theme changed to: {theme}[/green]")
            # Save theme preference
            config = self.config_manager.load_config() or {}
            if 'ui' not in config:
                config['ui'] = {}
            config['ui']['color_scheme'] = theme
            self.config_manager.save_config(config)
        else:
            self.console.print(f"[red]Invalid theme: {theme}[/red]")
    
    def show_history(self):
        """Show session history"""
        if not self.session_history:
            self.console.print("[yellow]No history available[/yellow]")
            return
        
        for i, entry in enumerate(self.session_history[-10:], 1):  # Show last 10
            if "user" in entry:
                self.console.print(f"[blue]{i}. User:[/blue] {entry['user']}")
            elif "assistant" in entry:
                self.console.print(f"[green]{i}. AI:[/green] {entry['assistant'][:100]}...")
    
    def show_status(self):
        """Show system status"""
        status_table = Table(title="System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="white")
        
        # Check API connection
        try:
            if self.gemini_client and self.gemini_client.test_connection():
                api_status = "[green]Connected[/green]"
            else:
                api_status = "[red]Disconnected[/red]"
        except:
            api_status = "[red]Error[/red]"
        
        status_table.add_row("Gemini API", api_status)
        status_table.add_row("Config", "[green]Loaded[/green]")
        status_table.add_row("Session History", f"{len(self.session_history)} entries")
        status_table.add_row("Theme", self.color_theme)
        
        self.console.print(status_table)
    
    def show_quickstart(self):
        """Show quickstart guide"""
        quickstart = """
# 🚀 Quick Start Guide

## Prerequisites
- Python 3.11+ installed
- Google Gemini API key

## Setup
1. **Get API Key**: Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. **Run CLI**: `python main.py interactive`
3. **Enter API Key** when prompted
4. **Start Building!**

## Example Workflow
```
> Generate requirements for a task management app
> Design the database schema for the requirements above
> Write Python code for the user authentication system
> Create unit tests for the authentication code
> Generate API documentation
```

## Pro Tips
- Be specific in your requests
- Use `/help` for command reference
- Use `/theme` to customize appearance
- Chain requests to build complete solutions
        """
        
        self.console.print(Markdown(quickstart))