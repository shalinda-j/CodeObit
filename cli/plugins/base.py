"""
Base Plugin Interface and Types for CodeObit Plugin System
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PluginType(Enum):
    """Types of plugins supported by CodeObit"""
    COMMAND = "command"           # CLI command plugins
    AI_PROVIDER = "ai_provider"   # AI provider integrations
    INTEGRATION = "integration"   # External service integrations
    TEMPLATE = "template"         # Project templates
    FILTER = "filter"            # Content processing filters
    VALIDATOR = "validator"       # Code/data validators
    GENERATOR = "generator"       # Code generators
    ANALYZER = "analyzer"         # Code analyzers

@dataclass
class PluginMetadata:
    """Plugin metadata information"""
    name: str
    version: str
    description: str
    author: str
    plugin_type: PluginType
    dependencies: List[str] = None
    python_requires: str = ">=3.11"
    tags: List[str] = None
    homepage: str = ""
    repository: str = ""
    license: str = "MIT"
    entry_point: str = ""
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []

class PluginHook:
    """Plugin hook system for event-driven architecture"""
    
    def __init__(self):
        self._hooks: Dict[str, List[Callable]] = {}
    
    def register(self, hook_name: str, callback: Callable):
        """Register a callback for a specific hook"""
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)
    
    def trigger(self, hook_name: str, *args, **kwargs):
        """Trigger all callbacks for a specific hook"""
        if hook_name in self._hooks:
            for callback in self._hooks[hook_name]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Hook {hook_name} callback failed: {e}")

class PluginContext:
    """Context object passed to plugins containing CLI state and utilities"""
    
    def __init__(self, console, config_manager, project_manager, ai_manager):
        self.console = console
        self.config_manager = config_manager
        self.project_manager = project_manager
        self.ai_manager = ai_manager
        self.hooks = PluginHook()
        self._data: Dict[str, Any] = {}
    
    def get_data(self, key: str, default=None):
        """Get shared data between plugins"""
        return self._data.get(key, default)
    
    def set_data(self, key: str, value: Any):
        """Set shared data for other plugins"""
        self._data[key] = value

class PluginBase(ABC):
    """Base class for all CodeObit plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        self.metadata = metadata
        self.enabled = True
        self.context: Optional[PluginContext] = None
    
    @abstractmethod
    def initialize(self, context: PluginContext) -> bool:
        """Initialize the plugin with context. Return True if successful."""
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """Cleanup plugin resources. Return True if successful."""
        pass
    
    def get_commands(self) -> Dict[str, Callable]:
        """Return dictionary of command name -> handler function"""
        return {}
    
    def get_config_schema(self) -> Dict[str, Any]:
        """Return JSON schema for plugin configuration"""
        return {}
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """Return plugin status information"""
        return {
            "name": self.metadata.name,
            "version": self.metadata.version,
            "enabled": self.enabled,
            "type": self.metadata.plugin_type.value
        }

class CommandPlugin(PluginBase):
    """Base class for command plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        if metadata.plugin_type != PluginType.COMMAND:
            raise ValueError("CommandPlugin requires COMMAND plugin type")
    
    @abstractmethod
    def add_parser(self, subparsers):
        """Add command parser to CLI subparsers"""
        pass
    
    @abstractmethod
    def handle_command(self, args) -> bool:
        """Handle the command execution"""
        pass

class AIProviderPlugin(PluginBase):
    """Base class for AI provider plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        if metadata.plugin_type != PluginType.AI_PROVIDER:
            raise ValueError("AIProviderPlugin requires AI_PROVIDER plugin type")
    
    @abstractmethod
    def generate_content(self, prompt: str, system_instruction: Optional[str] = None, 
                        temperature: float = 0.7) -> str:
        """Generate content using the AI provider"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test connection to the AI provider"""
        pass
    
    def get_models(self) -> List[str]:
        """Return list of available models"""
        return []
    
    def get_pricing_info(self) -> Dict[str, Any]:
        """Return pricing information"""
        return {}

class IntegrationPlugin(PluginBase):
    """Base class for integration plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        if metadata.plugin_type != PluginType.INTEGRATION:
            raise ValueError("IntegrationPlugin requires INTEGRATION plugin type")
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Authenticate with the external service"""
        pass
    
    @abstractmethod
    def get_api_endpoints(self) -> Dict[str, str]:
        """Return available API endpoints"""
        pass

class TemplatePlugin(PluginBase):
    """Base class for template plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        if metadata.plugin_type != PluginType.TEMPLATE:
            raise ValueError("TemplatePlugin requires TEMPLATE plugin type")
    
    @abstractmethod
    def get_templates(self) -> Dict[str, Any]:
        """Return available templates"""
        pass
    
    @abstractmethod
    def generate_project(self, template_name: str, project_path: Path, 
                        variables: Dict[str, Any]) -> bool:
        """Generate project from template"""
        pass

class AnalyzerPlugin(PluginBase):
    """Base class for code analyzer plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        if metadata.plugin_type != PluginType.ANALYZER:
            raise ValueError("AnalyzerPlugin requires ANALYZER plugin type")
    
    @abstractmethod
    def analyze_code(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code and return insights"""
        pass
    
    def get_supported_languages(self) -> List[str]:
        """Return list of supported programming languages"""
        return []

class GeneratorPlugin(PluginBase):
    """Base class for code generator plugins"""
    
    def __init__(self, metadata: PluginMetadata):
        super().__init__(metadata)
        if metadata.plugin_type != PluginType.GENERATOR:
            raise ValueError("GeneratorPlugin requires GENERATOR plugin type")
    
    @abstractmethod
    def generate_code(self, specification: Dict[str, Any]) -> str:
        """Generate code from specification"""
        pass
    
    def get_supported_patterns(self) -> List[str]:
        """Return list of supported code patterns"""
        return []