"""
File mention system for CodeObit CLI with @ syntax support
Allows users to mention files and folders using @filename or @folder/ syntax
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

class FileMentionProcessor:
    """Process file mentions with @ syntax"""
    
    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.file_cache: Dict[str, str] = {}
        
    def process_mentions(self, text: str) -> Tuple[str, List[Dict]]:
        """
        Process @ mentions in text and return processed text with file contents
        
        Args:
            text: Text containing @ mentions
            
        Returns:
            Tuple of (processed_text, mentioned_files_info)
        """
        # Pattern to match @filename or @folder/
        mention_pattern = r'@([a-zA-Z0-9_\-./\\]+)'
        mentions = re.findall(mention_pattern, text)
        
        if not mentions:
            return text, []
        
        mentioned_files = []
        processed_text = text
        
        for mention in mentions:
            file_info = self._resolve_mention(mention)
            if file_info:
                mentioned_files.append(file_info)
                # Replace mention with file info in text
                replacement = f"[File: {file_info['path']}]\n{file_info['content']}\n[End of {file_info['path']}]"
                processed_text = processed_text.replace(f"@{mention}", replacement)
        
        return processed_text, mentioned_files
    
    def _resolve_mention(self, mention: str) -> Optional[Dict]:
        """
        Resolve a file mention to actual file content
        
        Args:
            mention: The mentioned file/folder path
            
        Returns:
            Dictionary with file info or None if not found
        """
        try:
            # Handle different path formats
            path = Path(mention)
            
            # If it's a directory, list contents
            if path.is_dir():
                return self._process_directory(path)
            
            # If it's a file, read content
            elif path.is_file():
                return self._process_file(path)
            
            # Try to find the file in current directory or common locations
            else:
                found_path = self._search_file(mention)
                if found_path:
                    if found_path.is_file():
                        return self._process_file(found_path)
                    elif found_path.is_dir():
                        return self._process_directory(found_path)
            
            return None
            
        except Exception as e:
            self.console.print(f"[red]Error resolving @{mention}: {e}[/red]")
            return None
    
    def _process_file(self, path: Path) -> Dict:
        """Process a single file"""
        try:
            # Check if file is too large (> 100KB)
            if path.stat().st_size > 100 * 1024:
                return {
                    'path': str(path),
                    'type': 'file',
                    'content': f"[File too large: {path.stat().st_size} bytes. Showing first 1000 characters]\n" + 
                              path.read_text(encoding='utf-8', errors='ignore')[:1000] + "\n[...truncated]",
                    'size': path.stat().st_size,
                    'extension': path.suffix
                }
            
            # Read full content for smaller files
            content = path.read_text(encoding='utf-8', errors='ignore')
            
            return {
                'path': str(path),
                'type': 'file',
                'content': content,
                'size': len(content),
                'extension': path.suffix
            }
            
        except Exception as e:
            return {
                'path': str(path),
                'type': 'file',
                'content': f"[Error reading file: {e}]",
                'size': 0,
                'extension': path.suffix
            }
    
    def _process_directory(self, path: Path) -> Dict:
        """Process a directory by listing its contents"""
        try:
            contents = []
            for item in sorted(path.iterdir()):
                if item.name.startswith('.'):
                    continue  # Skip hidden files
                
                item_type = "dir" if item.is_dir() else "file"
                size = item.stat().st_size if item.is_file() else 0
                contents.append(f"{item_type}: {item.name} ({size} bytes)" if item.is_file() else f"{item_type}: {item.name}/")
            
            content = f"Directory listing for {path}:\n" + "\n".join(contents[:50])  # Limit to 50 items
            if len(list(path.iterdir())) > 50:
                content += f"\n... and {len(list(path.iterdir())) - 50} more items"
            
            return {
                'path': str(path),
                'type': 'directory',
                'content': content,
                'size': len(list(path.iterdir())),
                'extension': ''
            }
            
        except Exception as e:
            return {
                'path': str(path),
                'type': 'directory',
                'content': f"[Error reading directory: {e}]",
                'size': 0,
                'extension': ''
            }
    
    def _search_file(self, filename: str) -> Optional[Path]:
        """Search for a file in current directory and common locations"""
        search_paths = [
            Path.cwd(),
            Path.cwd() / "src",
            Path.cwd() / "lib",
            Path.cwd() / "cli",
            Path.cwd() / "tests",
        ]
        
        for search_path in search_paths:
            if not search_path.exists():
                continue
                
            # Direct path match
            direct_path = search_path / filename
            if direct_path.exists():
                return direct_path
            
            # Search recursively (limit depth to avoid performance issues)
            try:
                for item in search_path.rglob(filename):
                    if item.is_file() or item.is_dir():
                        return item
            except (PermissionError, OSError):
                continue
        
        return None
    
    def show_file_preview(self, file_path: str) -> None:
        """Show a preview of a file with syntax highlighting"""
        try:
            path = Path(file_path)
            if not path.exists():
                self.console.print(f"[red]File not found: {file_path}[/red]")
                return
            
            if path.is_dir():
                # Show directory listing
                items = list(path.iterdir())[:20]  # Show first 20 items
                content = "\n".join([f"{'📁' if item.is_dir() else '📄'} {item.name}" for item in items])
                
                panel = Panel(
                    content,
                    title=f"📁 Directory: {path.name}",
                    border_style="blue"
                )
                self.console.print(panel)
                return
            
            # Read file content
            content = path.read_text(encoding='utf-8', errors='ignore')
            
            # Limit content size for display
            if len(content) > 2000:
                content = content[:2000] + "\n... (truncated)"
            
            # Detect language for syntax highlighting
            language = self._detect_language(path.suffix)
            
            if language:
                syntax = Syntax(content, language, theme="monokai", line_numbers=True)
                panel = Panel(
                    syntax,
                    title=f"📄 {path.name}",
                    border_style="green"
                )
            else:
                panel = Panel(
                    content,
                    title=f"📄 {path.name}",
                    border_style="green"
                )
            
            self.console.print(panel)
            
        except Exception as e:
            self.console.print(f"[red]Error showing file preview: {e}[/red]")
    
    def _detect_language(self, extension: str) -> Optional[str]:
        """Detect programming language from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.json': 'json',
            '.xml': 'xml',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.sql': 'sql',
            '.sh': 'bash',
            '.bat': 'batch',
            '.ps1': 'powershell',
            '.dockerfile': 'dockerfile',
            '.md': 'markdown',
            '.txt': 'text'
        }
        return language_map.get(extension.lower())
    
    def list_available_files(self, directory: str = ".") -> List[str]:
        """List available files in a directory for auto-completion"""
        try:
            path = Path(directory)
            if not path.exists() or not path.is_dir():
                return []
            
            files = []
            for item in path.iterdir():
                if item.name.startswith('.'):
                    continue
                
                if item.is_file():
                    files.append(item.name)
                elif item.is_dir():
                    files.append(f"{item.name}/")
            
            return sorted(files)
            
        except Exception:
            return []

# Global instance
_file_mention_processor: Optional[FileMentionProcessor] = None

def get_file_mention_processor() -> FileMentionProcessor:
    """Get or create global file mention processor"""
    global _file_mention_processor
    if _file_mention_processor is None:
        _file_mention_processor = FileMentionProcessor()
    return _file_mention_processor
