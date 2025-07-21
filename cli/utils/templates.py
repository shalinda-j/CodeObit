"""
Template management for the AI Software Engineer CLI
"""

import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

from cli.utils.file_manager import FileManager

logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages templates for project initialization and generation"""
    
    def __init__(self, templates_dir: str = "templates"):
        """
        Initialize the template manager
        
        Args:
            templates_dir: Directory containing templates
        """
        self.templates_dir = Path(templates_dir)
        self.file_manager = FileManager()
        self.templates_dir.mkdir(parents=True, exist_ok=True)
    
    def get_available_templates(self) -> List[str]:
        """
        Get list of available template names
        
        Returns:
            List[str]: List of template names
        """
        try:
            templates = []
            for template_file in self.templates_dir.glob("*.json"):
                templates.append(template_file.stem)
            return sorted(templates)
        except Exception as e:
            logger.error(f"Failed to get available templates: {e}")
            return []
    
    def load_template(self, template_name: str) -> Dict[str, Any]:
        """
        Load a template by name
        
        Args:
            template_name: Name of the template to load
            
        Returns:
            Dict[str, Any]: Template data
            
        Raises:
            FileNotFoundError: If template doesn't exist
            Exception: If template loading fails
        """
        try:
            template_path = self.templates_dir / f"{template_name}.json"
            
            if not template_path.exists():
                raise FileNotFoundError(f"Template not found: {template_name}")
            
            return self.file_manager.read_json(str(template_path))
            
        except Exception as e:
            logger.error(f"Failed to load template {template_name}: {e}")
            raise
    
    def save_template(self, template_name: str, template_data: Dict[str, Any]) -> None:
        """
        Save a template
        
        Args:
            template_name: Name of the template
            template_data: Template data to save
            
        Raises:
            Exception: If template saving fails
        """
        try:
            template_path = self.templates_dir / f"{template_name}.json"
            self.file_manager.write_json(str(template_path), template_data)
            logger.info(f"Template saved: {template_name}")
            
        except Exception as e:
            logger.error(f"Failed to save template {template_name}: {e}")
            raise
    
    def create_project_template(self, name: str, description: str,
                              project_type: str = "web",
                              technology_stack: Optional[List[str]] = None,
                              phases: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Create a new project template
        
        Args:
            name: Template name
            description: Template description
            project_type: Type of project (web, mobile, desktop, api, etc.)
            technology_stack: List of technologies
            phases: Project phases definition
            
        Returns:
            Dict[str, Any]: Created template data
        """
        if technology_stack is None:
            technology_stack = ["Python", "JavaScript", "HTML", "CSS"]
        
        if phases is None:
            phases = self._get_default_phases()
        
        template_data = {
            "name": name,
            "description": description,
            "project_type": project_type,
            "technology_stack": technology_stack,
            "phases": phases,
            "directory_structure": self._get_default_directory_structure(project_type),
            "required_files": self._get_required_files(project_type),
            "configuration": self._get_default_configuration(project_type),
            "dependencies": self._get_default_dependencies(project_type),
            "scripts": self._get_default_scripts(project_type),
            "documentation": self._get_documentation_template(),
            "quality_gates": self._get_quality_gates(),
            "ci_cd": self._get_cicd_template(project_type)
        }
        
        return template_data
    
    def _get_default_phases(self) -> List[Dict[str, Any]]:
        """Get default project phases"""
        return [
            {
                "name": "Requirements Analysis",
                "description": "Gather and analyze project requirements",
                "duration_weeks": 1,
                "deliverables": ["Requirements Document", "User Stories", "Acceptance Criteria"],
                "tasks": [
                    "Stakeholder interviews",
                    "Requirements gathering",
                    "User story creation",
                    "Requirements validation"
                ]
            },
            {
                "name": "System Design",
                "description": "Design system architecture and components",
                "duration_weeks": 2,
                "deliverables": ["Architecture Document", "Database Design", "API Specification"],
                "tasks": [
                    "Architecture design",
                    "Database schema design",
                    "API design",
                    "Technology selection",
                    "Design review"
                ]
            },
            {
                "name": "Development",
                "description": "Implementation of the system",
                "duration_weeks": 6,
                "deliverables": ["Working Software", "Unit Tests", "Code Documentation"],
                "tasks": [
                    "Environment setup",
                    "Core functionality development",
                    "UI/UX implementation",
                    "API development",
                    "Integration",
                    "Unit testing"
                ]
            },
            {
                "name": "Testing",
                "description": "Comprehensive testing of the system",
                "duration_weeks": 2,
                "deliverables": ["Test Results", "Bug Reports", "Performance Reports"],
                "tasks": [
                    "Integration testing",
                    "System testing",
                    "Performance testing",
                    "Security testing",
                    "User acceptance testing"
                ]
            },
            {
                "name": "Deployment",
                "description": "Deploy system to production",
                "duration_weeks": 1,
                "deliverables": ["Production System", "Deployment Guide", "Monitoring Setup"],
                "tasks": [
                    "Production environment setup",
                    "Deployment automation",
                    "Monitoring configuration",
                    "Go-live activities",
                    "Post-deployment validation"
                ]
            }
        ]
    
    def _get_default_directory_structure(self, project_type: str) -> Dict[str, Any]:
        """Get default directory structure based on project type"""
        base_structure = {
            "src/": "Source code directory",
            "tests/": "Test files directory",
            "docs/": "Documentation directory",
            "config/": "Configuration files",
            "scripts/": "Build and deployment scripts",
            "assets/": "Static assets (images, fonts, etc.)"
        }
        
        if project_type == "web":
            base_structure.update({
                "src/components/": "Reusable components",
                "src/pages/": "Page components",
                "src/utils/": "Utility functions",
                "src/styles/": "CSS/styling files",
                "public/": "Public static files"
            })
        elif project_type == "api":
            base_structure.update({
                "src/routes/": "API route handlers",
                "src/models/": "Data models",
                "src/middleware/": "Middleware functions",
                "src/controllers/": "Business logic controllers",
                "src/services/": "External service integrations"
            })
        elif project_type == "mobile":
            base_structure.update({
                "src/screens/": "Mobile app screens",
                "src/components/": "Reusable UI components",
                "src/navigation/": "Navigation configuration",
                "src/store/": "State management"
            })
        
        return base_structure
    
    def _get_required_files(self, project_type: str) -> List[str]:
        """Get required files based on project type"""
        base_files = [
            "README.md",
            "LICENSE",
            ".gitignore",
            "CHANGELOG.md"
        ]
        
        if project_type == "web":
            base_files.extend([
                "package.json",
                "index.html",
                "src/main.js",
                "src/App.vue"
            ])
        elif project_type == "api":
            base_files.extend([
                "requirements.txt",
                "main.py",
                "config/settings.py",
                "Dockerfile"
            ])
        elif project_type == "python":
            base_files.extend([
                "requirements.txt",
                "setup.py",
                "src/__init__.py",
                "tests/__init__.py"
            ])
        
        return base_files
    
    def _get_default_configuration(self, project_type: str) -> Dict[str, Any]:
        """Get default configuration based on project type"""
        return {
            "environment": {
                "development": {
                    "debug": True,
                    "log_level": "DEBUG"
                },
                "production": {
                    "debug": False,
                    "log_level": "INFO"
                }
            },
            "security": {
                "enable_cors": True,
                "api_rate_limit": "100/hour"
            },
            "database": {
                "type": "postgresql",
                "connection_pool_size": 10
            }
        }
    
    def _get_default_dependencies(self, project_type: str) -> Dict[str, List[str]]:
        """Get default dependencies based on project type"""
        if project_type == "web":
            return {
                "runtime": ["vue", "axios", "vue-router"],
                "development": ["webpack", "eslint", "jest", "cypress"]
            }
        elif project_type == "api":
            return {
                "runtime": ["fastapi", "uvicorn", "pydantic", "sqlalchemy"],
                "development": ["pytest", "black", "flake8", "mypy"]
            }
        elif project_type == "python":
            return {
                "runtime": ["click", "requests", "pydantic"],
                "development": ["pytest", "black", "flake8", "mypy", "pre-commit"]
            }
        else:
            return {
                "runtime": [],
                "development": []
            }
    
    def _get_default_scripts(self, project_type: str) -> Dict[str, str]:
        """Get default scripts based on project type"""
        if project_type == "web":
            return {
                "start": "npm run serve",
                "build": "npm run build",
                "test": "npm run test:unit",
                "lint": "npm run lint"
            }
        elif project_type == "api":
            return {
                "start": "uvicorn main:app --reload",
                "test": "pytest",
                "lint": "flake8 .",
                "format": "black ."
            }
        else:
            return {
                "test": "pytest",
                "lint": "flake8 .",
                "format": "black ."
            }
    
    def _get_documentation_template(self) -> Dict[str, Any]:
        """Get documentation template structure"""
        return {
            "sections": [
                "Overview",
                "Getting Started",
                "Installation",
                "Configuration",
                "Usage",
                "API Reference",
                "Contributing",
                "License"
            ],
            "formats": ["markdown", "html"],
            "auto_generate": True
        }
    
    def _get_quality_gates(self) -> Dict[str, Any]:
        """Get quality gates configuration"""
        return {
            "code_coverage": {
                "minimum": 80,
                "target": 90
            },
            "code_quality": {
                "complexity_threshold": 10,
                "duplication_threshold": 3
            },
            "security": {
                "vulnerability_scan": True,
                "dependency_check": True
            },
            "performance": {
                "load_testing": True,
                "response_time_threshold": "200ms"
            }
        }
    
    def _get_cicd_template(self, project_type: str) -> Dict[str, Any]:
        """Get CI/CD template configuration"""
        return {
            "pipeline_stages": [
                "build",
                "test",
                "security_scan",
                "deploy_staging",
                "integration_test",
                "deploy_production"
            ],
            "triggers": [
                "push_to_main",
                "pull_request"
            ],
            "environments": [
                "development",
                "staging",
                "production"
            ],
            "deployment_strategy": "blue_green"
        }
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get template information without loading full template
        
        Args:
            template_name: Name of the template
            
        Returns:
            Dict[str, Any]: Template metadata
        """
        try:
            template = self.load_template(template_name)
            return {
                "name": template.get("name", template_name),
                "description": template.get("description", ""),
                "project_type": template.get("project_type", "unknown"),
                "technology_stack": template.get("technology_stack", []),
                "phases_count": len(template.get("phases", [])),
                "estimated_duration": sum(phase.get("duration_weeks", 0) for phase in template.get("phases", []))
            }
        except Exception as e:
            logger.error(f"Failed to get template info for {template_name}: {e}")
            return {}
    
    def create_from_template(self, template_name: str, project_name: str,
                           customizations: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Create a project from template with customizations
        
        Args:
            template_name: Name of the template to use
            project_name: Name of the new project
            customizations: Custom values to override template defaults
            
        Returns:
            Dict[str, Any]: Customized project configuration
        """
        try:
            template = self.load_template(template_name)
            
            # Create project configuration from template
            project_config = template.copy()
            project_config["project_name"] = project_name
            
            # Apply customizations
            if customizations:
                project_config = self._apply_customizations(project_config, customizations)
            
            return project_config
            
        except Exception as e:
            logger.error(f"Failed to create project from template {template_name}: {e}")
            raise
    
    def _apply_customizations(self, config: Dict[str, Any], 
                            customizations: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply customizations to project configuration
        
        Args:
            config: Base configuration
            customizations: Customizations to apply
            
        Returns:
            Dict[str, Any]: Customized configuration
        """
        # Deep merge customizations into config
        result = config.copy()
        
        for key, value in customizations.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._apply_customizations(result[key], value)
            else:
                result[key] = value
        
        return result
