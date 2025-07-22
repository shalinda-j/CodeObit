"""
Search Presenter for formatting search results
"""
from typing import List, Dict, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table

class SearchPresenter:
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
    
    def format_search_results(self, results: List[Dict]) -> str:
        """
        Format search results as a rich string
        
        Args:
            results: List of search result dictionaries
            
        Returns:
            Formatted string with search results
        """
        if not results:
            return "[yellow]No search results found.[/yellow]"
        
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Title", style="bold")
        table.add_column("URL", style="blue")
        
        for i, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            url = result.get('url', 'No URL')
            table.add_row(str(i), title, url)
        
        return table
    
    def format_search_history(self, history: List[Dict]) -> str:
        """
        Format search history as a rich string
        
        Args:
            history: List of search history items
            
        Returns:
            Formatted string with search history
        """
        if not history:
            return "[dim]No search history available.[/dim]"
        
        table = Table(show_header=True, header_style="bold cyan")
        table.add_column("Time", style="dim", width=20)
        table.add_column("Query", style="green")
        table.add_column("Results", justify="right")
        
        for item in reversed(history):
            time = item.get('timestamp', '').split('.')[0].replace('T', ' ')
            query = item.get('query', '')
            count = str(item.get('result_count', 0))
            table.add_row(time, query, count)
        
        return table
    
    def format_error(self, error: str) -> str:
        """Format an error message"""
        return f"[red]Error: {error}[/red]"
    
    def format_help(self) -> str:
        """Format help text for search functionality"""
        help_text = """
[bold]Search Commands:[/bold]
  /search [query]    - Search the web
  /history          - View search history
  /clear-history    - Clear search history
  /help search      - Show this help

[dim]Examples:
  /search python web scraping
  /history
  /clear-history[/dim]
        """
        return help_text
