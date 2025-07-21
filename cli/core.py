"""
Core CLI application class and main command router
"""

import argparse
import sys
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from cli.utils.config import ConfigManager
from cli.commands.requirements import RequirementsCommand
from cli.commands.design import DesignCommand
from cli.commands.code import CodeCommand
from cli.commands.test import TestCommand
from cli.commands.security import SecurityCommand
from cli.commands.docs import DocsCommand
from cli.commands.project import ProjectCommand
from cli.commands.browse import BrowseCommand
from cli.commands.debug import DebugCommand
from cli.commands.qa import QACommand

class AISoftwareEngineerCLI:
    """Main CLI application class"""
    
    def __init__(self):
        self.console = Console()
        self.config_manager = ConfigManager()
        self.commands = {
            'requirements': RequirementsCommand(),
            'design': DesignCommand(),
            'code': CodeCommand(),
            'test': TestCommand(),
            'security': SecurityCommand(),
            'docs': DocsCommand(),
            'project': ProjectCommand(),
            'browse': BrowseCommand(),
            'debug': DebugCommand(),
            'qa': QACommand()
        }
    
    def create_parser(self):
        """Create the argument parser with all commands"""
        parser = argparse.ArgumentParser(
            description="AI Software Engineer CLI - Comprehensive AI-powered software engineering workflows",
            prog="ai-engineer"
        )
        
        parser.add_argument(
            '--version', 
            action='version', 
            version='AI Software Engineer CLI v1.0.0'
        )
        
        parser.add_argument(
            '--config', 
            help='Path to configuration file',
            default='config/config.yaml'
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Add subcommands
        for name, command in self.commands.items():
            command.add_parser(subparsers)
        
        # Add special commands
        init_parser = subparsers.add_parser('init', help='Initialize AI Engineer CLI')
        init_parser.add_argument('--api-key', help='Google Gemini API key')
        
        help_parser = subparsers.add_parser('help', help='Show detailed help')
        help_parser.add_argument('topic', nargs='?', help='Help topic')
        
        # Add interactive mode
        interactive_parser = subparsers.add_parser('interactive', help='Start interactive Gemini-style CLI')
        interactive_parser.add_argument('--theme', choices=['auto', 'dark', 'light'], 
                                      help='Color theme for interactive mode')
        
        return parser
    
    def show_welcome(self):
        """Display welcome message and basic info"""
        # Create ASCII art for codeobit
        codeobit_ascii = """
 ██████╗ ██████╗ ██████╗ ███████╗ ██████╗ ██████╗ ██╗████████╗
██╔════╝██╔═══██╗██╔══██╗██╔════╝██╔═══██╗██╔══██╗██║╚══██╔══╝
██║     ██║   ██║██║  ██║█████╗  ██║   ██║██████╔╝██║   ██║   
██║     ██║   ██║██║  ██║██╔══╝  ██║   ██║██╔══██╗██║   ██║   
╚██████╗╚██████╔╝██████╔╝███████╗╚██████╔╝██████╔╝██║   ██║   
 ╚═════╝ ╚═════╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝   
        """
        
        welcome_panel = Panel.fit(
            f"[bold cyan]{codeobit_ascii}[/bold cyan]\n\n"
            "[bold magenta]codeobit AI Software Engineer CLI[/bold magenta]\n"
            "Comprehensive AI-powered development lifecycle automation\n"
            "[dim]Powered by Google Gemini AI with MCP design patterns[/dim]\n\n"
            "[yellow]🚀 Vibe coding experience with intelligent project automation[/yellow]",
            title="Welcome to codeobit",
            border_style="cyan"
        )
        self.console.print(welcome_panel)
        
        # Show available commands table
        table = Table(title="Available Commands")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        commands_info = {
            'init': 'Initialize codeobit with API key and configuration',
            'interactive': 'Start conversational AI coding session',
            'requirements': 'Generate user stories and acceptance criteria',
            'design': 'Create system architecture with MCP patterns',
            'code': 'AI-powered code generation and optimization',
            'test': 'Automated testing with browser automation',
            'security': 'Security analysis and vulnerability scanning',
            'docs': 'Generate comprehensive documentation',
            'project': 'Project planning with data collection and memory',
            'browse': 'Collect web data and save to project memory',
            'debug': 'Advanced debugging with AI assistance',
            'qa': 'Quality assurance automation and testing'
        }
        
        for cmd, desc in commands_info.items():
            table.add_row(cmd, desc)
        
        self.console.print(table)
        
        # Project summary and token usage
        self.show_project_status()
        
        self.console.print("\n[dim]Use 'codeobit <command> --help' for detailed command help[/dim]")
        self.console.print("[bold green]Ready for vibe coding! 🔥[/bold green]")
    
    def init_cli(self, args):
        """Initialize CLI configuration"""
        self.console.print("[bold yellow]Initializing AI Software Engineer CLI...[/bold yellow]")
        
        # Check for API key
        api_key = args.api_key or os.getenv('GEMINI_API_KEY')
        if not api_key:
            self.console.print("[red]Error: No API key provided.[/red]")
            self.console.print("Please provide API key using --api-key or set GEMINI_API_KEY environment variable")
            return False
        
        # Validate API key by making a test call
        from cli.ai.gemini_client import GeminiClient
        try:
            client = GeminiClient(api_key)
            test_result = client.test_connection()
            if test_result:
                self.console.print("[green]✓ API key validated successfully[/green]")
            else:
                self.console.print("[red]✗ API key validation failed[/red]")
                return False
        except Exception as e:
            self.console.print(f"[red]✗ API key validation error: {e}[/red]")
            return False
        
        # Create configuration
        config_data = {
            'api_key': api_key,
            'default_model': 'gemini-2.5-flash',
            'project_directory': str(Path.cwd()),
            'output_format': 'rich'
        }
        
        self.config_manager.save_config(config_data)
        self.console.print("[green]✓ CLI initialized successfully[/green]")
        self.console.print(f"Configuration saved to: {self.config_manager.config_path}")
        
        return True
    
    def show_project_status(self):
        """Display current project status and token usage"""
        import json
        from datetime import datetime
        
        # Check for existing project data
        project_file = Path("project_data.json")
        tokens_used = 0
        current_project = "No active project"
        
        if project_file.exists():
            try:
                with open(project_file, 'r') as f:
                    data = json.load(f)
                    tokens_used = data.get('tokens_used', 0)
                    current_project = data.get('project_name', 'Unnamed Project')
            except:
                pass
        
        # Create status panel
        status_panel = Panel.fit(
            f"[bold cyan]Project:[/bold cyan] {current_project}\n"
            f"[bold yellow]Tokens Used:[/bold yellow] {tokens_used:,}\n"
            f"[bold green]Status:[/bold green] Ready for development\n"
            f"[bold blue]Memory:[/bold blue] Active data collection enabled",
            title="Project Status",
            border_style="green"
        )
        self.console.print(status_panel)
    
    def start_interactive_mode(self, args):
        """Start interactive Gemini-style CLI mode"""
        from cli.interactive import InteractiveCLI
        
        interactive_cli = InteractiveCLI()
        if hasattr(args, 'theme') and args.theme:
            interactive_cli.color_theme = args.theme
        interactive_cli.start()
    
    def show_help(self, topic=None):
        """Show detailed help information"""
        if topic and topic in self.commands:
            # Show specific command help
            self.commands[topic].show_detailed_help(self.console)
        else:
            # Show general help
            self.show_welcome()
    
    def run(self):
        """Main run method"""
        parser = self.create_parser()
        
        # If no arguments provided, show welcome
        if len(sys.argv) == 1:
            self.show_welcome()
            return
        
        args = parser.parse_args()
        
        # Load configuration
        self.config_manager.load_config(args.config)
        
        # Handle special commands
        if args.command == 'init':
            self.init_cli(args)
            return
        elif args.command == 'interactive':
            self.start_interactive_mode(args)
            return
        elif args.command == 'help':
            self.show_help(args.topic if hasattr(args, 'topic') else None)
            return
        elif not args.command:
            self.show_welcome()
            return
        
        # Check if CLI is initialized (except for init command)
        if not self.config_manager.is_initialized():
            self.console.print("[red]CLI not initialized. Run 'ai-engineer init' first.[/red]")
            return
        
        # Execute command
        if args.command in self.commands:
            try:
                self.commands[args.command].execute(args, self.config_manager, self.console)
            except Exception as e:
                self.console.print(f"[red]Command execution failed: {e}[/red]")
        else:
            self.console.print(f"[red]Unknown command: {args.command}[/red]")
