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
            'project': ProjectCommand()
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
        
        return parser
    
    def show_welcome(self):
        """Display welcome message and basic info"""
        welcome_panel = Panel.fit(
            "[bold blue]AI Software Engineer CLI[/bold blue]\n"
            "Comprehensive AI-powered software engineering workflows\n"
            "Powered by Google Gemini AI",
            title="Welcome",
            border_style="blue"
        )
        self.console.print(welcome_panel)
        
        # Show available commands table
        table = Table(title="Available Commands")
        table.add_column("Command", style="cyan", no_wrap=True)
        table.add_column("Description", style="white")
        
        commands_info = {
            'init': 'Initialize the CLI with API key and configuration',
            'requirements': 'Analyze and manage project requirements',
            'design': 'Generate system architecture and design documents',
            'code': 'AI-powered code generation and analysis',
            'test': 'Automated testing and test case generation',
            'security': 'Security analysis and vulnerability scanning',
            'docs': 'Automated documentation generation',
            'project': 'Project management and task tracking'
        }
        
        for cmd, desc in commands_info.items():
            table.add_row(cmd, desc)
        
        self.console.print(table)
        self.console.print("\nUse 'ai-engineer <command> --help' for detailed command help")
    
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
