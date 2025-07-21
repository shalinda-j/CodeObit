"""
Base command class for all CLI commands
"""

from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """Abstract base class for all CLI commands"""
    
    @abstractmethod
    def add_parser(self, subparsers):
        """Add command parser to subparsers"""
        pass
    
    @abstractmethod
    def execute(self, args, config_manager, console):
        """Execute the command"""
        pass
    
    def show_detailed_help(self, console):
        """Show detailed help for this command"""
        console.print(f"[yellow]Help for {self.__class__.__name__} not implemented yet[/yellow]")