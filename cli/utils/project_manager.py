"""
Project Management System for CodeObit CLI
Handles project creation, saving, loading, and organization in local directories
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table


class ProjectManager:
    """Manages CodeObit projects with proper directory structure"""
    
    def __init__(self, base_projects_dir: Optional[str] = None):
        self.console = Console()
        
        # Set base projects directory
        if base_projects_dir:
            self.base_projects_dir = Path(base_projects_dir)
        else:
            # Default to ~/CodeObit/Projects
            self.base_projects_dir = Path.home() / "CodeObit" / "Projects"
        
        # Ensure base directory exists
        self.base_projects_dir.mkdir(parents=True, exist_ok=True)
        
        # Current project info
        self.current_project_path: Optional[Path] = None
        self.current_project_data: Dict[str, Any] = {}
        
        # Create projects index file
        self.projects_index_file = self.base_projects_dir / "projects_index.json"
        self.load_projects_index()
    
    def load_projects_index(self):
        """Load or create projects index"""
        if self.projects_index_file.exists():
            try:
                with open(self.projects_index_file, 'r', encoding='utf-8') as f:
                    self.projects_index = json.load(f)
            except Exception as e:
                self.console.print(f"[yellow]Warning: Could not load projects index: {e}[/yellow]")
                self.projects_index = {"projects": [], "last_opened": None}
        else:
            self.projects_index = {"projects": [], "last_opened": None}
            self.save_projects_index()
    
    def save_projects_index(self):
        """Save projects index to file"""
        try:
            with open(self.projects_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.projects_index, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.console.print(f"[red]Error saving projects index: {e}[/red]")
    
    def create_project(self, project_name: str, description: str = "", template: str = "default") -> bool:
        """Create a new project with its own directory"""
        try:
            # Sanitize project name for directory
            safe_name = self.sanitize_filename(project_name)
            project_path = self.base_projects_dir / safe_name
            
            # Check if project already exists
            if project_path.exists():
                if not Confirm.ask(f"Project '{project_name}' already exists. Overwrite?"):
                    return False
                shutil.rmtree(project_path)
            
            # Create project directory structure
            project_path.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (project_path / "src").mkdir(exist_ok=True)
            (project_path / "docs").mkdir(exist_ok=True)
            (project_path / "tests").mkdir(exist_ok=True)
            (project_path / "assets").mkdir(exist_ok=True)
            (project_path / "config").mkdir(exist_ok=True)
            (project_path / ".codeobit").mkdir(exist_ok=True)
            
            # Create project metadata
            project_data = {
                "name": project_name,
                "safe_name": safe_name,
                "description": description,
                "template": template,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "version": "1.0.0",
                "path": str(project_path),
                "structure": {
                    "src": "Source code files",
                    "docs": "Documentation",
                    "tests": "Test files",
                    "assets": "Static assets (images, etc.)",
                    "config": "Configuration files",
                    ".codeobit": "CodeObit metadata and cache"
                },
                "requirements": [],
                "design": {},
                "notes": [],
                "web_resources": [],
                "code_analysis": [],
                "tokens_used": 0,
                "files_generated": [],
                "tags": [],
                "status": "active"
            }
            
            # Save project data
            project_file = project_path / "project.json"
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            # Create README.md
            readme_content = f"""# {project_name}

{description}

## Description
{description if description else 'No description provided.'}

## Project Structure

```
{safe_name}/
├── src/           # Source code
├── docs/          # Documentation
├── tests/         # Test files
├── assets/        # Static assets
├── config/        # Configuration files
├── .codeobit/     # CodeObit metadata
└── project.json   # Project configuration
```

## Getting Started

1. Navigate to the project directory
2. Start CodeObit interactive mode
3. Begin developing your project

## Created with CodeObit CLI

This project was created using [CodeObit CLI](https://github.com/codeobit/codeobit-cli) - an AI-powered development environment.

Created on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
            
            with open(project_path / "README.md", 'w', encoding='utf-8') as f:
                f.write(readme_content)
            
            # Create .gitignore
            gitignore_content = """# CodeObit
.codeobit/cache/
*.log

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Dependencies
node_modules/
__pycache__/
*.pyc
vendor/

# Build outputs
dist/
build/
*.exe
*.dll
*.so

# Environment
.env
.env.local
.env.production

# Temporary files
*.tmp
*.temp
"""
            
            with open(project_path / ".gitignore", 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            
            # Update projects index
            project_info = {
                "name": project_name,
                "safe_name": safe_name,
                "path": str(project_path),
                "description": description,
                "created_at": project_data["created_at"],
                "updated_at": project_data["updated_at"],
                "template": template,
                "status": "active"
            }
            
            # Remove existing project with same name
            self.projects_index["projects"] = [
                p for p in self.projects_index["projects"] 
                if p["name"] != project_name
            ]
            
            # Add new project
            self.projects_index["projects"].append(project_info)
            self.projects_index["last_opened"] = project_name
            self.save_projects_index()
            
            # Set as current project
            self.current_project_path = project_path
            self.current_project_data = project_data
            
            self.console.print(f"[green]✓ Created project '{project_name}' at {project_path}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error creating project: {e}[/red]")
            return False
    
    def load_project(self, project_name_or_path: str) -> bool:
        """Load an existing project"""
        try:
            project_path = None
            
            # Check if it's a direct path
            if os.path.exists(project_name_or_path):
                project_path = Path(project_name_or_path)
            else:
                # Search by name in projects index
                for project in self.projects_index["projects"]:
                    if project["name"] == project_name_or_path or project["safe_name"] == project_name_or_path:
                        project_path = Path(project["path"])
                        break
            
            if not project_path or not project_path.exists():
                self.console.print(f"[red]Project '{project_name_or_path}' not found[/red]")
                return False
            
            # Load project data
            project_file = project_path / "project.json"
            if not project_file.exists():
                self.console.print(f"[red]Invalid project: project.json not found in {project_path}[/red]")
                return False
            
            with open(project_file, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Update last accessed time
            project_data["last_accessed"] = datetime.now().isoformat()
            
            # Save updated data
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            # Set as current project
            self.current_project_path = project_path
            self.current_project_data = project_data
            
            # Update projects index
            self.projects_index["last_opened"] = project_data["name"]
            self.save_projects_index()
            
            # Change to project directory
            os.chdir(project_path)
            
            self.console.print(f"[green]✓ Loaded project '{project_data['name']}' from {project_path}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error loading project: {e}[/red]")
            return False
    
    def save_current_project(self) -> bool:
        """Save current project data"""
        if not self.current_project_path or not self.current_project_data:
            return False
        
        try:
            # Update timestamp
            self.current_project_data["updated_at"] = datetime.now().isoformat()
            
            # Save to project.json
            project_file = self.current_project_path / "project.json"
            with open(project_file, 'w', encoding='utf-8') as f:
                json.dump(self.current_project_data, f, indent=2, ensure_ascii=False)
            
            # Update projects index
            for project in self.projects_index["projects"]:
                if project["name"] == self.current_project_data["name"]:
                    project["updated_at"] = self.current_project_data["updated_at"]
                    break
            
            self.save_projects_index()
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error saving project: {e}[/red]")
            return False
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        return self.projects_index["projects"]
    
    def delete_project(self, project_name: str, confirm: bool = True) -> bool:
        """Delete a project"""
        try:
            # Find project
            project_info = None
            for project in self.projects_index["projects"]:
                if project["name"] == project_name:
                    project_info = project
                    break
            
            if not project_info:
                self.console.print(f"[red]Project '{project_name}' not found[/red]")
                return False
            
            project_path = Path(project_info["path"])
            
            # Confirm deletion
            if confirm:
                if not Confirm.ask(f"Are you sure you want to delete project '{project_name}' and all its files?"):
                    return False
            
            # Delete project directory
            if project_path.exists():
                shutil.rmtree(project_path)
            
            # Remove from projects index
            self.projects_index["projects"] = [
                p for p in self.projects_index["projects"] 
                if p["name"] != project_name
            ]
            
            # Update last opened if it was this project
            if self.projects_index["last_opened"] == project_name:
                self.projects_index["last_opened"] = None
            
            self.save_projects_index()
            
            # Clear current project if it was this one
            if self.current_project_data.get("name") == project_name:
                self.current_project_path = None
                self.current_project_data = {}
            
            self.console.print(f"[green]✓ Deleted project '{project_name}'[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error deleting project: {e}[/red]")
            return False
    
    def show_projects_table(self):
        """Display projects in a formatted table"""
        projects = self.list_projects()
        
        if not projects:
            self.console.print("[yellow]No projects found. Create your first project with '/project new'[/yellow]")
            return
        
        table = Table(title="CodeObit Projects")
        table.add_column("Name", style="cyan", width=20)
        table.add_column("Description", style="white", width=30)
        table.add_column("Created", style="green", width=12)
        table.add_column("Updated", style="yellow", width=12)
        table.add_column("Status", style="magenta", width=8)
        table.add_column("Path", style="blue", width=30)
        
        for project in sorted(projects, key=lambda x: x.get("updated_at", x.get("created_at", "")), reverse=True):
            created = datetime.fromisoformat(project["created_at"]).strftime("%m/%d/%Y")
            updated = datetime.fromisoformat(project["updated_at"]).strftime("%m/%d/%Y")
            
            # Truncate long descriptions and paths
            desc = project.get("description", "No description")[:27] + "..." if len(project.get("description", "")) > 30 else project.get("description", "No description")
            path = project["path"][-27] + "..." if len(project["path"]) > 30 else project["path"]
            
            # Mark current project
            name = project["name"]
            if self.current_project_data.get("name") == project["name"]:
                name = f"→ {name}"
            
            table.add_row(
                name,
                desc,
                created,
                updated,
                project.get("status", "active"),
                path
            )
        
        self.console.print(table)
    
    def get_current_project_info(self) -> Dict[str, Any]:
        """Get current project information"""
        return {
            "path": str(self.current_project_path) if self.current_project_path else None,
            "data": self.current_project_data.copy() if self.current_project_data else {},
            "is_loaded": bool(self.current_project_path and self.current_project_data)
        }
    
    def export_project(self, project_name: str, export_path: str) -> bool:
        """Export project to a different location"""
        try:
            # Find project
            project_info = None
            for project in self.projects_index["projects"]:
                if project["name"] == project_name:
                    project_info = project
                    break
            
            if not project_info:
                self.console.print(f"[red]Project '{project_name}' not found[/red]")
                return False
            
            source_path = Path(project_info["path"])
            target_path = Path(export_path)
            
            # Copy project directory
            shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            
            self.console.print(f"[green]✓ Exported project '{project_name}' to {target_path}[/green]")
            return True
            
        except Exception as e:
            self.console.print(f"[red]Error exporting project: {e}[/red]")
            return False
    
    def sanitize_filename(self, name: str) -> str:
        """Sanitize project name for use as directory name"""
        import re
        # Replace invalid characters with underscores
        safe_name = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Replace spaces with underscores
        safe_name = safe_name.replace(' ', '_')
        # Remove multiple consecutive underscores
        safe_name = re.sub(r'_+', '_', safe_name)
        # Remove leading/trailing underscores
        safe_name = safe_name.strip('_')
        # Ensure it's not empty
        if not safe_name:
            safe_name = f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return safe_name
    
    def update_project_data(self, key: str, value: Any) -> bool:
        """Update current project data"""
        if not self.current_project_data:
            return False
        
        self.current_project_data[key] = value
        return self.save_current_project()
    
    def add_to_project_list(self, list_key: str, item: Any) -> bool:
        """Add item to a project list (requirements, notes, etc.)"""
        if not self.current_project_data:
            return False
        
        if list_key not in self.current_project_data:
            self.current_project_data[list_key] = []
        
        self.current_project_data[list_key].append(item)
        return self.save_current_project()
