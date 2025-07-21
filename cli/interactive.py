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
        """Main interactive chat loop - stays open like Google CLI"""
        while True:
            try:
                # Show chat prompt with project context
                project_indicator = self.get_project_indicator()
                
                # Get user input with rich prompt
                user_input = Prompt.ask(
                    f"[cyan]codeobit[/cyan] [dim]{project_indicator}[/dim] [blue]>[/blue]",
                    console=self.console
                ).strip()
                
                # Skip empty inputs
                if not user_input:
                    continue
                
                # Handle special commands first
                if user_input.startswith('/'):
                    if self.handle_special_command(user_input):
                        break  # Exit if /exit was called
                    continue
                
                # Show typing indicator
                with self.console.status("[bold green]codeobit is thinking...", spinner="dots"):
                    # Add to session history
                    self.session_history.append({
                        'user': user_input,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    # Process with AI
                    response = self.process_request(user_input)
                    
                    # Update token usage
                    self.update_token_usage(user_input, response)
                
                # Display AI response with proper formatting
                if response:
                    self.display_ai_response(response)
                    
                    # Add response to history
                    self.session_history[-1]['assistant'] = response
                
            except EOFError:
                self.console.print("\n[yellow]Chat ended (Ctrl+D detected)[/yellow]")
                break
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Chat interrupted (Ctrl+C detected)[/yellow]")
                break
            except Exception as e:
                self.console.print(f"[red]Error in chat: {str(e)}[/red]")
    
    def get_project_indicator(self):
        """Get current project indicator for prompt"""
        # Try to get current project name
        try:
            import json
            from pathlib import Path
            project_file = Path("project_data.json")
            if project_file.exists():
                with open(project_file, 'r') as f:
                    data = json.load(f)
                    project_name = data.get('project_name', 'No project')
                    return f"({project_name[:15]}...)" if len(project_name) > 15 else f"({project_name})"
        except:
            pass
        return "(Ready)"
    
    def update_token_usage(self, user_input, response):
        """Update token usage tracking"""
        try:
            import json
            from pathlib import Path
            
            # Estimate token usage (rough approximation)
            input_tokens = len(user_input.split()) * 1.3
            output_tokens = len(response.split()) * 1.3
            total_tokens = int(input_tokens + output_tokens)
            
            # Load or create project data
            project_file = Path("project_data.json")
            if project_file.exists():
                with open(project_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {'project_name': 'Interactive Session', 'tokens_used': 0}
            
            data['tokens_used'] = data.get('tokens_used', 0) + total_tokens
            
            # Save updated data
            with open(project_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception:
            pass  # Fail silently for token tracking
    
    def display_ai_response(self, response):
        """Display AI response with beautiful formatting"""
        # Create response panel with codeobit branding
        response_panel = Panel(
            Markdown(response),
            title="🤖 codeobit Assistant",
            title_align="left",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(response_panel)
    
    def handle_special_command(self, command: str):
        """Handle special slash commands"""
        parts = command[1:].split()  # Remove the '/' prefix
        if not parts:
            return False
            
        cmd = parts[0].lower()
        
        if cmd in ["help", "h"]:
            self.show_help()
        elif cmd in ["theme", "t"]:
            theme = parts[1] if len(parts) > 1 else None
            self.change_theme(theme)
        elif cmd in ["history", "hist"]:
            self.show_history()
        elif cmd in ["clear", "cls", "c"]:
            self.console.clear()
            self.show_welcome()
        elif cmd in ["status", "s"]:
            self.show_status()
        elif cmd in ["quickstart", "q"]:
            self.show_quickstart()
        elif cmd in ["exit", "quit", "bye"]:
            self.console.print("[yellow]Goodbye! Happy coding! 👋[/yellow]")
            return True  # Signal to exit
        else:
            self.console.print(f"[red]Unknown command: /{cmd}[/red]")
            self.console.print("[dim]Type /help for available commands[/dim]")
        
        return False
    
    def show_help(self):
        """Show available commands and usage"""
        help_panel = Panel(
            """[bold cyan]codeobit Interactive Commands:[/bold cyan]

[yellow]Special Commands:[/yellow]
  /help, /h          - Show this help
  /theme [theme]     - Change color theme (auto, dark, light)
  /history, /hist    - Show conversation history
  /clear, /cls, /c   - Clear screen and show welcome
  /status, /s        - Show current project status
  /quickstart, /q    - Show quick start guide
  /exit, /quit, /bye - Exit interactive mode

[yellow]Natural Language:[/yellow]
  Just type your questions or requests naturally!
  
  Examples:
  • "Create a React app with authentication"
  • "Debug this Python error: KeyError"
  • "Browse https://example.com and summarize"
  • "Generate tests for my login function"
  • "Design a database for an e-commerce site"
            """,
            title="codeobit Help",
            border_style="cyan"
        )
        self.console.print(help_panel)
    
    def process_request(self, request: str) -> str:
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
    
