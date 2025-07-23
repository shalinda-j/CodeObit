"""
Interactive mode for AI Software Engineer CLI
"""

import os
import json
import webbrowser
import subprocess
import shlex
from datetime import datetime
from pathlib import Path
import sys
from typing import Optional, Dict, Any, List, Tuple, Union
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
        2. Use /feedback to provide real-time feedback and collaborate
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
        """Main interactive chat loop with enhanced project management"""
        while True:
            try:
                # Show chat prompt with project context and current directory
                project_indicator = self.get_project_indicator()
                current_dir = Path.cwd().name
                
                # Get user input with rich prompt
                user_input = Prompt.ask(
                    f"[cyan]codeobit[/cyan] [dim]{project_indicator}[/dim] [blue]({current_dir})>[/blue]",
                    console=self.console
                ).strip()
                
                # Skip empty inputs
                if not user_input:
                    continue
                
                # Handle shell commands (start with ! or are common shell commands)
                if user_input.startswith('!') or user_input.split()[0].lower() in ['cd', 'ls', 'dir', 'pwd', 'cat', 'echo', 'type', 'cls']:
                    cmd = user_input[1:] if user_input.startswith('!') else user_input
                    result = self.execute_shell_command(cmd)
                    
                    # For Windows, ensure we have output for common commands
                    if sys.platform == 'win32' and not result['output'] and not result['error']:
                        if cmd.lower() == 'pwd':
                            result['output'] = os.getcwd()
                    
                    # Display command output
                    if result['output']:
                        self.console.print(result['output'], end='')
                    if result['error']:
                        self.console.print(f"[red]{result['error']}[/red]")
                    continue
                
                # Handle special commands (start with /)
                if user_input.startswith('/'):
                    if self.handle_special_command(user_input):
                        continue
                
                # Process regular input with AI
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
                
            except KeyboardInterrupt:
                self.console.print("\n[yellow]Type 'exit' or press Ctrl+C again to quit[/yellow]")
                try:
                    # Give user a chance to type 'exit' or press Ctrl+C again
                    user_input = input("\nContinue? (y/n): ").strip().lower()
                    if user_input in ['n', 'no', 'exit', 'quit']:
                        break
                except KeyboardInterrupt:
                    break
            except Exception as e:
                self.console.print(f"[red]Error: {e}[/red]")
                continue
    
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
    
    def handle_feedback(self, feedback: str) -> None:
        """Handle real-time feedback and collaboration"""
        try:
            self.console.print("[blue]Collecting feedback...[/blue]")
            response = self.gemini_client.generate_content(
                f"Collaborate and improve the project based on this feedback: {feedback}",
                system_instruction=(
                    "You are a collaborative AI assistant. Process this feedback for the project "
                    "and provide actionable improvements and updates."
                )
            )
            self.console.print(Markdown(response))
            self._save_project_data()
        except Exception as e:
            self.console.print(f"[red]Feedback processing failed: {e}[/red]")

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
        elif cmd == "feedback":
            if len(parts) < 2:
                self.console.print("[red]Please provide feedback content[/red]")
            else:
                feedback = ' '.join(parts[1:])
                self.handle_feedback(feedback)
        elif cmd == "generate":
            if len(parts) < 2:
                self.console.print("[red]Please specify what to generate (file, function, class, etc.)[/red]")
            else:
                self.handle_generate_command(parts[1:])
        elif cmd == "analyze":
            if len(parts) < 2:
                self.console.print("[red]Please provide a file to analyze[/red]")
            else:
                file_path = parts[1]
                self.analyze_file(file_path)
        elif cmd == "test":
            if len(parts) < 2:
                self.console.print("[red]Please specify what to test (generate, run, file)[/red]")
            else:
                self.handle_test_command(parts[1:])
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
    
    def execute_shell_command(self, command: str, cwd: Optional[str] = None) -> Dict[str, Union[str, int]]:
        """
        Execute a shell command and return the result
        
        Args:
            command: The shell command to execute
            cwd: Working directory for the command
            
        Returns:
            Dict containing command output, error, and return code
        """
        try:
            # Handle cd command separately as it needs to change the working directory
            if command.lower().startswith('cd'):
                try:
                    target_dir = command[2:].strip() or str(Path.home())
                    os.chdir(target_dir)
                    return {
                        'output': f'Changed directory to {os.getcwd()}',
                        'error': '',
                        'return_code': 0
                    }
                except Exception as e:
                    return {
                        'output': '',
                        'error': f'cd: {str(e)}',
                        'return_code': 1
                    }
            
            # On Windows, use 'cmd /c' for command execution
            if sys.platform == 'win32':
                # Map common Unix commands to Windows equivalents
                cmd_map = {
                    'ls': 'dir',
                    'll': 'dir',
                    'pwd': 'cd',
                    'cat': 'type',
                    'clear': 'cls'
                }
                
                # Split command and map if necessary
                parts = command.split()
                if parts and parts[0] in cmd_map:
                    parts[0] = cmd_map[parts[0]]
                    command = ' '.join(parts)
                
                # Execute with cmd /c
                result = subprocess.run(
                    f'cmd /c {command}',
                    cwd=cwd or os.getcwd(),
                    capture_output=True,
                    text=True,
                    shell=True
                )
            else:
                # On Unix-like systems, use shlex for proper argument splitting
                args = shlex.split(command)
                result = subprocess.run(
                    args,
                    cwd=cwd or os.getcwd(),
                    capture_output=True,
                    text=True
                )
            
            return {
                'output': result.stdout,
                'error': result.stderr,
                'return_code': result.returncode
            }
            
        except Exception as e:
            return {
                'output': '',
                'error': f'Error executing command: {str(e)}',
                'return_code': 1
            }
    
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

[yellow]Shell Commands:[/yellow]
  !<command>         - Execute shell command (e.g., !ls, !pwd, !cd ..)
  cd <dir>           - Change directory (also works with !cd)
  pwd, ls, dir, etc. - Standard shell commands with ! prefix

[yellow]Search Commands:[/yellow]
  /search [query]  - Search the web
  /history         - View search history
  /clear-history   - Clear search history

[yellow]Code Generation & Analysis:[/yellow]
  /generate <type>   - Generate code (file, function, class, api, test)
  /analyze <file>    - Analyze file for quality, security, performance
  /test <action>     - Test commands (generate, run, analyze)

[yellow]Project Management:[/yellow]
  /project [command]  - Manage project (requirements, design, notes)
  /browse <url>      - Browse and save web resources
  /feedback <message> - Provide real-time feedback and collaboration

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
    
    def change_theme(self, theme: str = None) -> None:
        """Change the color theme of the console
        
        Args:
            theme: The theme to change to ('auto', 'dark', or 'light'). If None, cycles through themes.
        """
        themes = ["auto", "dark", "light"]
        
        if theme and theme.lower() in themes:
            self.color_theme = theme.lower()
        else:
            # Cycle to next theme if no theme specified or invalid theme
            current_idx = themes.index(self.color_theme) if self.color_theme in themes else 0
            self.color_theme = themes[(current_idx + 1) % len(themes)]
        
        # Apply the theme
        if self.color_theme == "dark":
            self.console.style = "white on black"
        elif self.color_theme == "light":
            self.console.style = "black on white"
        else:  # auto
            self.console.style = None
        
        self.console.print(f"[green]Theme set to: {self.color_theme}[/green]")
        
    def display_response(self, response: str) -> None:
        """Display AI response with proper formatting"""
        # Check if response contains code
        if not isinstance(response, str):
            response = str(response)
            
        if "```" in response:
            # Split response into text and code blocks
            parts: List[str] = response.split("```")
            for i, part in enumerate(parts):
                part = part.strip()
                if not part:
                    continue
                    
                if i % 2 == 0:
                    # Text part (markdown)
                    self.console.print(Markdown(part))
                else:
                    # Code part (syntax highlighting)
                    lines: List[str] = part.split('\n')
                    if not lines:
                        continue
                        
                    language: str = lines[0].strip() if lines and lines[0].strip() else "text"
                    code: str = '\n'.join(lines[1:]) if len(lines) > 1 else lines[0]
                    
                    if code.strip():
                        syntax: Syntax = Syntax(
                            code=code,
                            lexer=language,
                            theme="monokai",
                            line_numbers=True,
                            word_wrap=True
                        )
                        self.console.print(syntax)
        else:
            # Regular markdown response
            self.console.print(Markdown(response))
        
        # Add spacing after response
        self.console.print()
    
    def show_history(self):
        """Show conversation history"""
        if not self.session_history:
            self.console.print("[yellow]No conversation history available[/yellow]")
            return
        
        history_panel = Panel(
            "\n".join([
                f"**User:** {item.get('user', 'N/A')}\n**Assistant:** {item.get('assistant', 'N/A')[:100]}..."
                for item in self.session_history[-5:]  # Show last 5 interactions
            ]),
            title="Conversation History",
            border_style="blue"
        )
        self.console.print(history_panel)
    
    def show_status(self):
        """Show current system status"""
        status_table = Table(title="System Status")
        status_table.add_column("Component", style="cyan")
        status_table.add_column("Status", style="green")
        
        status_table.add_row("Gemini Client", "✓ Connected" if self.gemini_client else "✗ Not connected")
        status_table.add_row("Project", self.project_data.get('project_name', 'No project'))
        status_table.add_row("Theme", self.color_theme.title())
        status_table.add_row("History Items", str(len(self.session_history)))
        
        self.console.print(status_table)
    
    def show_quickstart(self):
        """Show quick start guide"""
        quickstart_panel = Panel(
            """[bold cyan]Quick Start Guide[/bold cyan]\n\n
1. **Start a new project**: `/project new "My App"`
2. **Browse web resources**: `/browse https://docs.python.org`
3. **Ask for help**: "How do I create a REST API?"
4. **Generate code**: "Create a Python function to validate emails"
5. **Get requirements**: "Write user stories for a todo app"

[yellow]Pro tip:[/yellow] Just describe what you want to build!
            """,
            title="🚀 Getting Started",
            border_style="green"
        )
        self.console.print(quickstart_panel)
    
    def handle_generate_command(self, args: List[str]):
        """Handle code generation commands"""
        if not args:
            self.console.print("[red]Please specify what to generate (file, function, class, api, etc.)[/red]")
            return
        
        item_type = args[0].lower()
        description = ' '.join(args[1:]) if len(args) > 1 else ""
        
        if item_type == "file":
            self.generate_file(description)
        elif item_type == "function":
            self.generate_function(description)
        elif item_type == "class":
            self.generate_class(description)
        elif item_type == "api":
            self.generate_api(description)
        elif item_type == "test":
            self.generate_test(description)
        else:
            self.console.print(f"[yellow]Generating {item_type}: {description}[/yellow]")
            # Use AI to generate based on description
            if self.gemini_client:
                prompt = f"Generate {item_type} based on this description: {description}"
                response = self.gemini_client.generate_content(prompt)
                self.console.print(Panel(Markdown(response), title=f"Generated {item_type}", border_style="green"))
    
    def generate_file(self, description: str):
        """Generate a complete file based on description"""
        if not description:
            description = Prompt.ask("[blue]What kind of file do you want to generate?[/blue]")
        
        filename = Prompt.ask("[blue]Enter filename (with extension)[/blue]")
        
        if self.gemini_client:
            prompt = f"""Generate a complete, production-ready file for: {description}
            
Filename: {filename}
            
Include:
            - Proper imports and dependencies
            - Well-structured code with comments
            - Error handling where appropriate
            - Best practices for the file type
            
Generate only the file content, no additional explanation."""
            
            with self.console.status("[bold green]Generating file...", spinner="dots"):
                response = self.gemini_client.generate_content(prompt)
            
            # Ask if user wants to save to file
            if Confirm.ask(f"Save generated content to {filename}?"):
                try:
                    with open(filename, 'w', encoding='utf-8') as f:
                        # Extract code from markdown if present
                        if '```' in response:
                            lines = response.split('\n')
                            in_code_block = False
                            code_lines = []
                            for line in lines:
                                if line.strip().startswith('```'):
                                    in_code_block = not in_code_block
                                    continue
                                if in_code_block:
                                    code_lines.append(line)
                            response = '\n'.join(code_lines)
                        
                        f.write(response)
                    self.console.print(f"[green]✓ File saved as {filename}[/green]")
                except Exception as e:
                    self.console.print(f"[red]Error saving file: {e}[/red]")
            else:
                self.console.print(Panel(Markdown(response), title=f"Generated File: {filename}", border_style="green"))
    
    def generate_function(self, description: str):
        """Generate a function based on description"""
        if not description:
            description = Prompt.ask("[blue]Describe the function you want to generate[/blue]")
        
        language = Prompt.ask("[blue]Programming language[/blue]", default="python")
        
        if self.gemini_client:
            prompt = f"""Generate a well-documented {language} function for: {description}
            
Include:
            - Proper function signature with type hints (if applicable)
            - Comprehensive docstring
            - Error handling
            - Input validation
            - Example usage in comments
            
Generate only the function code, no additional explanation."""
            
            with self.console.status("[bold green]Generating function...", spinner="dots"):
                response = self.gemini_client.generate_content(prompt)
            
            self.console.print(Panel(Markdown(f"```{language}\n{response}\n```"), title="Generated Function", border_style="green"))
    
    def generate_class(self, description: str):
        """Generate a class based on description"""
        if not description:
            description = Prompt.ask("[blue]Describe the class you want to generate[/blue]")
        
        language = Prompt.ask("[blue]Programming language[/blue]", default="python")
        
        if self.gemini_client:
            prompt = f"""Generate a well-structured {language} class for: {description}
            
Include:
            - Proper class definition with inheritance if needed
            - Constructor with parameters
            - Essential methods with docstrings
            - Properties and getters/setters if applicable
            - Type hints (if applicable)
            - Example usage
            
Generate only the class code, no additional explanation."""
            
            with self.console.status("[bold green]Generating class...", spinner="dots"):
                response = self.gemini_client.generate_content(prompt)
            
            self.console.print(Panel(Markdown(f"```{language}\n{response}\n```"), title="Generated Class", border_style="green"))
    
    def generate_api(self, description: str):
        """Generate API endpoints based on description"""
        if not description:
            description = Prompt.ask("[blue]Describe the API you want to generate[/blue]")
        
        framework = Prompt.ask("[blue]Framework[/blue]", default="FastAPI")
        
        if self.gemini_client:
            prompt = f"""Generate a complete {framework} API for: {description}
            
Include:
            - All necessary imports
            - Proper route definitions
            - Request/response models
            - Error handling
            - Input validation
            - Documentation strings
            - Example usage
            
Generate production-ready code."""
            
            with self.console.status("[bold green]Generating API...", spinner="dots"):
                response = self.gemini_client.generate_content(prompt)
            
            self.console.print(Panel(Markdown(response), title="Generated API", border_style="green"))
    
    def generate_test(self, description: str):
        """Generate test cases based on description"""
        if not description:
            description = Prompt.ask("[blue]What do you want to test?[/blue]")
        
        test_framework = Prompt.ask("[blue]Test framework[/blue]", default="pytest")
        
        if self.gemini_client:
            prompt = f"""Generate comprehensive {test_framework} tests for: {description}
            
Include:
            - Test setup and teardown
            - Positive test cases
            - Negative test cases
            - Edge cases
            - Mocking if needed
            - Clear test documentation
            
Generate complete, runnable test code."""
            
            with self.console.status("[bold green]Generating tests...", spinner="dots"):
                response = self.gemini_client.generate_content(prompt)
            
            self.console.print(Panel(Markdown(response), title="Generated Tests", border_style="green"))
    
    def analyze_file(self, file_path: str):
        """Analyze the specified file for code quality, security, and improvements"""
        try:
            if not Path(file_path).exists():
                self.console.print(f"[red]File not found: {file_path}[/red]")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if not content.strip():
                self.console.print(f"[yellow]File is empty: {file_path}[/yellow]")
                return
            
            # Determine file type
            file_ext = Path(file_path).suffix
            language_map = {
                '.py': 'Python',
                '.js': 'JavaScript',
                '.ts': 'TypeScript',
                '.java': 'Java',
                '.cpp': 'C++',
                '.c': 'C',
                '.cs': 'C#',
                '.go': 'Go',
                '.rs': 'Rust',
                '.php': 'PHP'
            }
            
            language = language_map.get(file_ext, 'Unknown')
            
            if self.gemini_client:
                prompt = f"""Analyze this {language} code file for:
                
1. **Code Quality**: Structure, readability, maintainability
2. **Performance**: Potential bottlenecks and optimizations
3. **Security**: Vulnerabilities and security best practices
4. **Best Practices**: Adherence to language conventions
5. **Bugs**: Potential issues and edge cases
6. **Improvements**: Specific recommendations
                
File: {file_path}
                
```{language.lower()}
{content}
```
                
Provide detailed analysis with specific line references where applicable."""
                
                with self.console.status(f"[bold green]Analyzing {file_path}...", spinner="dots"):
                    response = self.gemini_client.analyze_code(content, language.lower(), "comprehensive")
                
                self.console.print(Panel(
                    Markdown(response), 
                    title=f"📊 Analysis Report: {file_path}", 
                    border_style="blue"
                ))
                
                # Save analysis to project data
                if 'code_analysis' not in self.project_data:
                    self.project_data['code_analysis'] = []
                
                analysis_record = {
                    'file_path': file_path,
                    'timestamp': datetime.now().isoformat(),
                    'language': language,
                    'analysis': response,
                    'file_size': len(content)
                }
                
                self.project_data['code_analysis'].append(analysis_record)
                self._save_project_data()
                
        except Exception as e:
            self.console.print(f"[red]Error analyzing file: {e}[/red]")
    
    def handle_test_command(self, args: List[str]):
        """Handle testing commands"""
        if not args:
            self.console.print("[red]Please specify test action (generate, run, analyze)[/red]")
            return
        
        action = args[0].lower()
        target = ' '.join(args[1:]) if len(args) > 1 else ""
        
        if action == "generate":
            self.generate_test(target)
        elif action == "run":
            self.run_tests(target)
        elif action == "analyze":
            self.analyze_test_coverage(target)
        else:
            self.console.print(f"[yellow]Unknown test action: {action}[/yellow]")
    
    def run_tests(self, target: str = ""):
        """Run tests using appropriate test runner"""
        # Detect test framework
        test_files = list(Path('.').glob('**/test_*.py')) + list(Path('.').glob('**/*_test.py'))
        
        if not test_files:
            self.console.print("[yellow]No test files found. Use '/test generate' to create tests.[/yellow]")
            return
        
        # Try different test runners
        runners = ['pytest', 'python -m pytest', 'python -m unittest']
        
        for runner in runners:
            try:
                cmd = f"{runner} {target}" if target else runner
                result = self.execute_shell_command(cmd)
                
                if result['return_code'] == 0:
                    self.console.print(f"[green]✓ Tests passed![/green]")
                    if result['output']:
                        self.console.print(result['output'])
                else:
                    self.console.print(f"[red]✗ Tests failed![/red]")
                    if result['error']:
                        self.console.print(f"[red]{result['error']}[/red]")
                return
                
            except Exception:
                continue
        
        self.console.print("[red]No suitable test runner found. Install pytest or use unittest.[/red]")
    
    def analyze_test_coverage(self, target: str = ""):
        """Analyze test coverage"""
        try:
            # Try to run coverage analysis
            cmd = f"coverage run -m pytest {target}" if target else "coverage run -m pytest"
            result1 = self.execute_shell_command(cmd)
            
            if result1['return_code'] == 0:
                result2 = self.execute_shell_command("coverage report")
                if result2['output']:
                    self.console.print(Panel(
                        result2['output'], 
                        title="📈 Test Coverage Report", 
                        border_style="green"
                    ))
                else:
                    self.console.print("[yellow]Coverage data available, but no report generated[/yellow]")
            else:
                self.console.print("[red]Failed to run coverage analysis. Install coverage: pip install coverage[/red]")
                
        except Exception as e:
            self.console.print(f"[red]Error analyzing coverage: {e}[/red]")
