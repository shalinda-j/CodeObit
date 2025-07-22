"""
Search Controller for handling web search operations
"""
from typing import List, Dict, Optional, Any
from ..models.search_model import SearchModel
from ..presenters.search_presenter import SearchPresenter

class SearchController:
    def __init__(self, model: Optional[SearchModel] = None, presenter: Optional[SearchPresenter] = None):
        self.model = model or SearchModel()
        self.presenter = presenter or SearchPresenter()
    
    def handle_command(self, command: str, args: List[str] = None) -> Any:
        """
        Handle search-related commands
        
        Args:
            command: The command to execute (e.g., 'search', 'history', 'clear-history')
            args: Command arguments
            
        Returns:
            Formatted output from the presenter
        """
        args = args or []
        
        try:
            if command == 'search':
                if not args:
                    return "Please provide a search query. Type '/help search' for usage."
                query = ' '.join(args)
                results = self.model.search_web(query)
                return self.presenter.format_search_results(results)
                
            elif command == 'history':
                history = self.model.get_search_history()
                return self.presenter.format_search_history(history)
                
            elif command == 'clear-history':
                self.model.clear_search_history()
                return "Search history cleared."
                
            elif command == 'help':
                return self.presenter.format_help()
                
            else:
                return f"Unknown search command: {command}. Type '/help search' for available commands."
                
        except Exception as e:
            return self.presenter.format_error(str(e))
