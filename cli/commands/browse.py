"""
Browse command for web data collection and memory storage
"""

import json
import requests
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

from cli.commands.base import BaseCommand
from cli.ai.gemini_client import GeminiClient


class BrowseCommand(BaseCommand):
    """Browse and collect web data for projects"""
    
    def add_parser(self, subparsers):
        parser = subparsers.add_parser('browse', help='Collect web data and save to project memory')
        parser.add_argument('url', help='URL to browse and collect data from')
        parser.add_argument('--save-to', help='Save collected data to specific file')
        parser.add_argument('--summarize', action='store_true', help='Summarize content with AI')
        parser.add_argument('--extract', choices=['text', 'links', 'images', 'all'], 
                          default='text', help='What to extract from the page')
        return parser
    
    def execute(self, args, config_manager, console):
        """Execute browse command"""
        console.print(f"[yellow]🌐 Browsing: {args.url}[/yellow]")
        
        try:
            # Fetch web content
            response = requests.get(args.url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract data based on user preference
            extracted_data = self.extract_content(soup, args.extract, args.url)
            
            # Summarize with AI if requested
            if args.summarize:
                extracted_data['ai_summary'] = self.summarize_content(
                    extracted_data['text'], config_manager
                )
            
            # Save to project memory
            self.save_to_memory(extracted_data, args.url, args.save_to)
            
            console.print("[green]✓ Data collected and saved to project memory[/green]")
            console.print(f"[cyan]Content length: {len(extracted_data.get('text', ''))} characters[/cyan]")
            
            if args.summarize and 'ai_summary' in extracted_data:
                console.print("\n[bold blue]AI Summary:[/bold blue]")
                console.print(extracted_data['ai_summary'])
                
        except requests.RequestException as e:
            console.print(f"[red]✗ Failed to fetch URL: {e}[/red]")
        except Exception as e:
            console.print(f"[red]✗ Error processing data: {e}[/red]")
    
    def extract_content(self, soup, extract_type, url):
        """Extract specified content from webpage"""
        data = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'title': soup.title.string if soup.title else '',
        }
        
        if extract_type in ['text', 'all']:
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.extract()
            data['text'] = soup.get_text().strip()
        
        if extract_type in ['links', 'all']:
            data['links'] = [a.get('href') for a in soup.find_all('a', href=True)]
        
        if extract_type in ['images', 'all']:
            data['images'] = [img.get('src') for img in soup.find_all('img', src=True)]
        
        return data
    
    def summarize_content(self, text, config_manager):
        """Summarize content using AI"""
        try:
            client = GeminiClient()
            prompt = f"""
            Please provide a concise summary of the following web content.
            Focus on key information that would be useful for software development:
            
            {text[:2000]}...
            """
            return client.generate_content(prompt)
        except Exception as e:
            return f"Summary generation failed: {e}"
    
    def save_to_memory(self, data, url, custom_file=None):
        """Save collected data to project memory"""
        # Create memory directory if it doesn't exist
        memory_dir = Path("project_memory")
        memory_dir.mkdir(exist_ok=True)
        
        if custom_file:
            file_path = memory_dir / custom_file
        else:
            # Generate filename from URL
            safe_name = url.replace('://', '_').replace('/', '_').replace('?', '_')[:50]
            file_path = memory_dir / f"browse_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Save data
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Update project memory index
        self.update_memory_index(str(file_path), data)
    
    def update_memory_index(self, file_path, data):
        """Update the project memory index"""
        index_file = Path("project_memory/index.json")
        
        if index_file.exists():
            with open(index_file, 'r') as f:
                index = json.load(f)
        else:
            index = {"entries": [], "last_updated": None}
        
        # Add new entry
        index["entries"].append({
            "file": file_path,
            "url": data.get('url'),
            "title": data.get('title'),
            "timestamp": data.get('timestamp'),
            "type": "web_browse"
        })
        
        index["last_updated"] = datetime.now().isoformat()
        
        # Save updated index
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)