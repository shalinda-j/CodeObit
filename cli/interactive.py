"""
Interactive mode for AI Software Engineer CLI
"""

import os
import json
import webbrowser
from datetime import datetime
from pathlib import Path
import sys
from typing import Optional, Dict, Any, List, Tuple
from urllib.parse import urlparse

from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.spinner import Spinner
from rich.table import Table
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.progress import Progress

from cli.ai.gemini_client import GeminiClient
from cli.utils.config import ConfigManager
from cli.utils.file_manager import FileManager

# MCP Components
from cli.web.models.search_model import SearchModel
from cli.web.controllers.search_controller import SearchController
from cli.web.presenters.search_presenter import SearchPresenter


class InteractiveCLI:
    """Interactive CLI interface similar to Gemini CLI"""
    
    def __init__(self):
        self.console = Console()
        self.config_manager = ConfigManager()
        self.file_manager = FileManager()
        self.gemini_client = None
        self.session_history = []
        self.color_theme = "auto"
        self.project_data = self._load_project_data()
        self.current_project = self.project_data.get('name', 'Interactive Session')
        
        # Initialize MCP components for web search
        self.search_model = SearchModel()
        self.search_presenter = SearchPresenter(console=self.console)
        self.search_controller = SearchController(
            model=self.search_model,
            presenter=self.search_presenter
        )
        
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
    
    def _load_project_data(self) -> dict:
        """Load or initialize project data"""
        try:
            project_file = Path("project_data.json")
            if project_file.exists():
                with open(project_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {
                    'project_name': 'Interactive Session',
                    'tokens_used': 0,
                    'web_resources': [],
                    'requirements': [],
                    'design': {},
                    'notes': []
                }
                with open(project_file, 'w') as f:
                    json.dump(data, f, indent=2)
            return data
        except Exception as e:
            self.console.print(f"[red]Error loading project data: {e}[/red]")
            return {}

    def _save_project_data(self):
        """Save project data to file"""
        try:
            with open("project_data.json", 'w') as f:
                json.dump(self.project_data, f, indent=2)
        except Exception as e:
            self.console.print(f"[red]Error saving project data: {e}[/red]")

    def show_welcome(self):
        """Display welcome screen with ASCII art and tips"""
        # Create codeobit ASCII art
        codeobit_ascii = """
 ██████╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ██╗████████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔═══██╗██╔══██╗██║╚══██╔══╝
██║     ██║   ██║██║  ██║█████╗  ██║   ██║██████╔╝██║   ██║   
██║     ██║   ██║██║  ██║██╔══╝  ██║   ██║██╔══██╗██║   ██║   
╚██████╗╚██████╔╝██████╔╝███████╗╚██████╔╝██████╔╝██║   ██║   
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ⚠   ╚═╝   
        """
        
        project_name = self.project_data.get('project_name', 'New Project')
        
        welcome_panel = Panel(
            f"[bold cyan]{codeobit_ascii}[/bold cyan]\n\n"
            f"[bold magenta]codeobit Interactive Development Environment[/bold magenta]\n"
            f"[dim]Project: {project_name}[/dim]\n\n"
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
2. Use /browse <url> to collect web resources
3. Use /project to manage your project
4. Type /help for all available commands

[dim]> create a social media app with real-time features[/dim]
[dim]> /browse https://example.com/design-patterns[/dim]
[dim]> /project requirements "Add user authentication"[/dim]
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
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if a string is a valid URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _browse_web(self, url: str):
        """
        Browse a URL, extract content, and save to project memory
        
        Args:
            url: The URL to browse and extract content from
            
        Returns:
            str: Status message with the result of the operation
        """
        try:
            import requests
            from bs4 import BeautifulSoup
            import hashlib
            from urllib.parse import urlparse
            
            self.console.print(f"[blue]🌐 Fetching {url}...[/blue]")
            
            # Validate and clean URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Generate a unique ID for this resource
            url_hash = hashlib.md5(url.encode()).hexdigest()
            timestamp = datetime.now().isoformat()
            
            # Add to browsing history
            if not hasattr(self, 'browsing_history'):
                self.browsing_history = []
                
            self.browsing_history.append({
                'url': url,
                'timestamp': timestamp,
                'id': url_hash
            })
            
            # Fetch the URL with timeout
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Referer': 'https://www.google.com/'
            }
            
            response = requests.get(
                url, 
                headers=headers,
                timeout=10,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                return f"[red]Error: Could not fetch URL (Status {response.status_code})[/red]"
            
            # Parse the content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract relevant information
            title = soup.title.string.strip() if soup.title else 'No title'
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'iframe', 'noscript']):
                element.decompose()
                
            # Extract main content (try to get article or main content)
            main_content = soup.find('article') or soup.find('main') or soup
            text_content = ' '.join(p.get_text().strip() for p in main_content.find_all(['p', 'h1', 'h2', 'h3', 'li']))
            
            # Clean up whitespace
            text_content = ' '.join(text_content.split())
            
            # Extract metadata
            meta_description = ''
            if soup.find('meta', attrs={'name': 'description'}):
                meta_description = soup.find('meta', attrs={'name': 'description'})['content']
            
            # Extract links
            links = [a['href'] for a in soup.find_all('a', href=True)]
            
            # Summarize the content using AI
            summary = self._summarize_web_content(title, text_content[:15000])  # Increased content size limit
            
            # Create resource object
            domain = urlparse(url).netloc
            resource = {
                'id': url_hash,
                'url': url,
                'domain': domain,
                'title': title,
                'description': meta_description,
                'content': text_content[:50000],  # Store first 50k chars
                'summary': summary,
                'timestamp': timestamp,
                'content_type': response.headers.get('Content-Type', '').split(';')[0],
                'status_code': response.status_code,
                'links': links[:100],  # Store first 100 links
                'word_count': len(text_content.split()),
                'project': self.project_data.get('name', 'default')
            }
            
            # Initialize web_resources if it doesn't exist
            if 'web_resources' not in self.project_data:
                self.project_data['web_resources'] = []
            
            # Check if URL already exists in resources
            existing_idx = next((i for i, r in enumerate(self.project_data['web_resources']) 
                              if r.get('url') == url), None)
            
            if existing_idx is not None:
                # Update existing resource
                self.project_data['web_resources'][existing_idx].update(resource)
                action = "updated"
            else:
                # Add new resource
                self.project_data['web_resources'].append(resource)
                action = "saved"
            
            # Save to project file
            self._save_project_data()
            
            # Format response
            response_panel = Panel(
                f"[bold green]✓ Resource {action} to project memory[/bold green]\n"
                f"[cyan]Title:[/cyan] {title}\n"
                f"[cyan]URL:[/cyan] {url}\n"
                f"[cyan]Domain:[/cyan] {domain}\n"
                f"[cyan]Words:[/cyan] {resource['word_count']:,}\n"
                f"[cyan]Summary:[/cyan] {summary}",
                title=f"🌐 {domain}",
                border_style="green"
            )
            
            return response_panel
            
        except requests.exceptions.RequestException as e:
            return f"[red]Error fetching URL: {str(e)}[/red]"
        except Exception as e:
            import traceback
            return f"[red]Error processing URL: {str(e)}\n\n{traceback.format_exc()}[/red]"
    
    def _summarize_web_content(self, title: str, content: str) -> str:
        """Generate a summary of web content using AI"""
        if not self.gemini_client:
            return "[yellow]AI client not available. Could not generate summary.[/yellow]"
        
        prompt = f"""Please summarize the following web content in a concise way, focusing on key points 
        that would be useful for a software development project. Include any technical details, 
        best practices, or important concepts mentioned.

        Title: {title}
        
        Content:
        {content}
        """
        
        try:
            return self.gemini_client.generate_content(prompt)
        except Exception as e:
            return f"[yellow]Could not generate summary: {str(e)}[/yellow]"
    
    def _handle_project_command(self, args: List[str]) -> str:
        """Handle project management commands"""
        if not args:
            return self._show_project_status()
            
        subcmd = args[0].lower()
        
        if subcmd in ["new", "init"]:
            return self._init_project(args[1:] if len(args) > 1 else [])
        elif subcmd == "requirements":
            return self._manage_requirements(args[1:] if len(args) > 1 else [])
        elif subcmd == "design":
            return self._manage_design(args[1:] if len(args) > 1 else [])
        elif subcmd == "notes":
            return self._manage_notes(args[1:] if len(args) > 1 else [])
        elif subcmd == "status":
            return self._show_project_status()
        elif subcmd in ["help", "h"]:
            return self._show_project_help()
        else:
            return f"[red]Unknown project command: {subcmd}[/red]\n{self._show_project_help()}"
    
    def _show_project_status(self) -> str:
        """Show current project status"""
        if not self.project_data:
            return "[yellow]No active project. Use /project new to create one.[/yellow]"
        
        project_name = self.project_data.get('project_name', 'Unnamed Project')
        requirements = self.project_data.get('requirements', [])
        resources = self.project_data.get('web_resources', [])
        notes = self.project_data.get('notes', [])
        
        status = f"[bold cyan]Project: {project_name}[/bold cyan]\n"
        status += f"[bold]Requirements:[/bold] {len(requirements)}\n"
        status += f"[bold]Resources:[/bold] {len(resources)}\n"
        status += f"[bold]Notes:[/bold] {len(notes)}\n"
        
        if requirements:
            status += "\n[bold]Top Requirements:[/bold]\n"
            for i, req in enumerate(requirements[:3], 1):
                status += f"  {i}. {req.get('description', 'No description')[:60]}...\n"
        
        return status
    
    def _init_project(self, args: List[str]) -> str:
        """Initialize a new project"""
        if not args:
            project_name = Prompt.ask("[blue]Enter project name[/blue]")
        else:
            project_name = ' '.join(args)
        
        self.project_data = {
            'project_name': project_name,
            'created_at': datetime.now().isoformat(),
            'tokens_used': 0,
            'web_resources': [],
            'requirements': [],
            'design': {},
            'notes': []
        }
        
        self._save_project_data()
        return f"[green]✓ Created new project: {project_name}[/green]"
    
    def _manage_requirements(self, args: List[str]) -> str:
        """Manage project requirements"""
        if not args:
            # List all requirements
            requirements = self.project_data.get('requirements', [])
            if not requirements:
                return "[yellow]No requirements added yet. Use /project requirements add <description>[/yellow]"
            
            result = "[bold]Project Requirements:[/bold]\n"
            for i, req in enumerate(requirements, 1):
                result += f"  {i}. {req.get('description', 'No description')}\n"
            return result
        
        action = args[0].lower()
        
        if action == "add":
            if len(args) < 2:
                return "[red]Please provide a requirement description[/red]"
                
            requirement = {
                'description': ' '.join(args[1:]),
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            if 'requirements' not in self.project_data:
                self.project_data['requirements'] = []
                
            self.project_data['requirements'].append(requirement)
            self._save_project_data()
            return "[green]✓ Added requirement[/green]"
            
        return f"[red]Unknown requirements command: {action}[/red]"
    
    def _manage_design(self, args: List[str]) -> str:
        """Manage project design elements"""
        return "[yellow]Design management coming soon![/yellow]"
    
    def _manage_notes(self, args: List[str]) -> str:
        """Manage project notes"""
        if not args:
            # List all notes
            notes = self.project_data.get('notes', [])
            if not notes:
                return "[yellow]No notes added yet. Use /project notes add <note>[/yellow]"
            
            result = "[bold]Project Notes:[/bold]\n"
            for i, note in enumerate(notes, 1):
                result += f"  {i}. {note.get('content', 'No content')[:60]}...\n"
            return result
        
        action = args[0].lower()
        
        if action == "add":
            if len(args) < 2:
                return "[red]Please provide note content[/red]"
                
            note = {
                'content': ' '.join(args[1:]),
                'created_at': datetime.now().isoformat()
            }
            
            if 'notes' not in self.project_data:
                self.project_data['notes'] = []
                
            self.project_data['notes'].append(note)
            self._save_project_data()
            return "[green]✓ Added note[/green]"
            
        return f"[red]Unknown notes command: {action}[/red]"
    
    def _show_project_help(self) -> str:
        """Show help for project commands"""
        return """[bold]Project Management Commands:[/bold]
  /project new <name>      - Create a new project
  /project requirements    - List requirements
  /project requirements add <desc> - Add a requirement
  /project design          - View/Edit design
  /project notes           - View notes
  /project notes add <note> - Add a note
  /project status         - Show project status
  /project help           - Show this help
        """

    def handle_special_command(self, command: str):
        """Handle special slash commands"""
        parts = command[1:].split()  # Remove the '/' prefix
        if not parts:
            return False
            
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
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
        elif cmd == "browse":
            if len(parts) < 2:
                self.console.print("[red]Please provide a URL to browse[/red]")
            else:
                url = parts[1]
                if not self._is_valid_url(url):
                    url = f"https://{url}"  # Try adding https:// if missing
                if not self._is_valid_url(url):
                    self.console.print("[red]Invalid URL. Please include http:// or https://[/red]")
                else:
                    result = self._browse_web(url)
                    self.console.print(result)
        elif cmd == "project":
            result = self._handle_project_command(parts[1:] if len(parts) > 1 else [])
            self.console.print(result)
        # Search commands
        elif cmd in ["search", "find", "lookup"]:
            self.console.print(self.search_controller.handle_command('search', args))
            return True
            
        elif cmd == "history" and not args:  # Only handle /history without arguments
            self.console.print(self.search_controller.handle_command('history'))
            return True
            
        elif cmd == "clear-history":
            self.console.print(self.search_controller.handle_command('clear-history'))
            return True
            
        elif cmd == "help" and args and args[0] == "search":
            self.console.print(self.search_controller.handle_command('help'))
            return True
            
        elif cmd in ["exit", "quit", "bye"]:
            self.console.print("[yellow]Goodbye! Happy coding! 👋[/yellow]")
            return True  # Signal to exit
            
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

[yellow]Search Commands:[/yellow]
  /search [query]  - Search the web
  /history         - View search history
  /clear-history   - Clear search history

[yellow]Project Management:[/bold]
  /project [command]  - Manage project (requirements, design, notes)
  /browse <url>      - Browse and save web resources

[yellow]Natural Language:[/yellow]
  Just type your questions or requests naturally!
  
  Examples:
  • "Create a React app with authentication"
  • "Debug this Python error: KeyError"
  • "Generate tests for my login function"
  • "Design a database for an e-commerce site"
            """,
            title="codeobit Help",
            border_style="cyan"
        )
        self.console.print(help_panel)
        
        # Show project-specific help if available
        if self.project_data:
            self.console.print("\n[bold]Project Management Help:[/bold]")
            self.console.print(self._show_project_help())
    
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
    
