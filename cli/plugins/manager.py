"""
Plugin Manager for CodeObit CLI
Handles plugin loading, registration, and lifecycle management
"""

import os
import sys
import json
import importlib
import importlib.util
from pathlib import Path
from typing import Dict, List, Optional, Any, Type, Callable
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import logging

from .base import (
    PluginBase, PluginType, PluginMetadata, PluginContext,
    CommandPlugin, AIProviderPlugin, IntegrationPlugin,
    TemplatePlugin, AnalyzerPlugin, GeneratorPlugin
)
from .registry import PluginRegistry

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages plugin loading, registration, and lifecycle"""
    
    def __init__(self, console: Console, config_manager, project_manager, ai_manager):
        self.console = console
        self.config_manager = config_manager
        self.project_manager = project_manager
        self.ai_manager = ai_manager
        
        # Plugin storage
        self.loaded_plugins: Dict[str, PluginBase] = {}
        self.plugin_paths: List[Path] = []
        
        # Plugin registry
        self.registry = PluginRegistry()
        
        # Plugin context
        self.context = PluginContext(console, config_manager, project_manager, ai_manager)
        
        # Initialize default plugin paths
        self._setup_plugin_paths()
    
    def _setup_plugin_paths(self):
        """Setup default plugin search paths"""
        # Built-in plugins
        builtin_path = Path(__file__).parent / "builtin"
        if builtin_path.exists():
            self.plugin_paths.append(builtin_path)
        
        # User plugins directory
        user_plugins = Path.home() / ".codeobit" / "plugins"
        user_plugins.mkdir(parents=True, exist_ok=True)
        self.plugin_paths.append(user_plugins)
        
        # Project-specific plugins
        if hasattr(self.project_manager, 'current_project_path') and self.project_manager.current_project_path:
            project_plugins = self.project_manager.current_project_path / ".codeobit" / "plugins"
            if project_plugins.exists():
                self.plugin_paths.append(project_plugins)
    
    def add_plugin_path(self, path: Path):
        """Add a custom plugin search path"""
        if path.exists() and path not in self.plugin_paths:
            self.plugin_paths.append(path)
    
    def discover_plugins(self) -> List[Dict[str, Any]]:
        """Discover all available plugins in search paths"""
        discovered = []
        
        for plugin_path in self.plugin_paths:
            if not plugin_path.exists():
                continue
                
            for item in plugin_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Check for plugin manifest
                    manifest_file = item / "plugin.json"
                    if manifest_file.exists():
                        try:
                            with open(manifest_file, 'r') as f:
                                manifest = json.load(f)
                                manifest['path'] = str(item)
                                discovered.append(manifest)
                        except Exception as e:
                            logger.warning(f"Failed to load manifest from {manifest_file}: {e}")
                
                elif item.suffix == '.py' and not item.name.startswith('_'):
                    # Single file plugin - try to extract metadata
                    try:
                        metadata = self._extract_metadata_from_file(item)
                        if metadata:
                            metadata['path'] = str(item)
                            discovered.append(metadata)
                    except Exception as e:
                        logger.warning(f"Failed to extract metadata from {item}: {e}")
        
        return discovered
    
    def _extract_metadata_from_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract plugin metadata from Python file"""
        try:
            spec = importlib.util.spec_from_file_location("temp_plugin", file_path)
            if not spec or not spec.loader:
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for PLUGIN_METADATA or metadata attributes
            if hasattr(module, 'PLUGIN_METADATA'):
                return module.PLUGIN_METADATA
            elif hasattr(module, 'metadata'):
                if isinstance(module.metadata, dict):
                    return module.metadata
                elif isinstance(module.metadata, PluginMetadata):
                    return {
                        'name': module.metadata.name,
                        'version': module.metadata.version,
                        'description': module.metadata.description,
                        'author': module.metadata.author,
                        'type': module.metadata.plugin_type.value,
                        'dependencies': module.metadata.dependencies,
                        'tags': module.metadata.tags
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {e}")
            return None
    
    def load_plugin(self, plugin_info: Dict[str, Any]) -> bool:
        """Load a single plugin"""
        try:
            plugin_path = Path(plugin_info['path'])
            plugin_name = plugin_info['name']
            
            # Skip if already loaded
            if plugin_name in self.loaded_plugins:
                return True
            
            # Load the plugin module
            if plugin_path.is_dir():
                # Directory plugin - look for __init__.py
                init_file = plugin_path / "__init__.py"
                if init_file.exists():
                    spec = importlib.util.spec_from_file_location(
                        f"plugin_{plugin_name}", init_file
                    )
                else:
                    # Look for main.py
                    main_file = plugin_path / "main.py"
                    if main_file.exists():
                        spec = importlib.util.spec_from_file_location(
                            f"plugin_{plugin_name}", main_file
                        )
                    else:
                        logger.error(f"No entry point found for plugin {plugin_name}")
                        return False
            else:
                # Single file plugin
                spec = importlib.util.spec_from_file_location(
                    f"plugin_{plugin_name}", plugin_path
                )
            
            if not spec or not spec.loader:
                logger.error(f"Failed to create spec for plugin {plugin_name}")
                return False
            
            module = importlib.util.module_from_spec(spec)
            
            # Add plugin path to sys.path temporarily
            original_path = sys.path.copy()
            if plugin_path.is_dir():
                sys.path.insert(0, str(plugin_path.parent))
            else:
                sys.path.insert(0, str(plugin_path.parent))
            
            try:
                spec.loader.exec_module(module)
                
                # Find the plugin class
                plugin_class = None
                entry_point = plugin_info.get('entry_point', 'Plugin')
                
                if hasattr(module, entry_point):
                    plugin_class = getattr(module, entry_point)
                else:
                    # Search for plugin classes
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, PluginBase) and 
                            attr != PluginBase):
                            plugin_class = attr
                            break
                
                if not plugin_class:
                    logger.error(f"No plugin class found in {plugin_name}")
                    return False
                
                # Create plugin metadata
                metadata = PluginMetadata(
                    name=plugin_info['name'],
                    version=plugin_info.get('version', '1.0.0'),
                    description=plugin_info.get('description', ''),
                    author=plugin_info.get('author', 'Unknown'),
                    plugin_type=PluginType(plugin_info.get('type', 'command')),
                    dependencies=plugin_info.get('dependencies', []),
                    tags=plugin_info.get('tags', [])
                )
                
                # Instantiate plugin
                plugin_instance = plugin_class(metadata)
                
                # Initialize plugin
                if plugin_instance.initialize(self.context):
                    self.loaded_plugins[plugin_name] = plugin_instance
                    self.registry.register_plugin(plugin_instance)
                    
                    logger.info(f"Successfully loaded plugin: {plugin_name}")
                    return True
                else:
                    logger.error(f"Failed to initialize plugin: {plugin_name}")
                    return False
                    
            finally:
                # Restore original sys.path
                sys.path = original_path
                
        except Exception as e:
            logger.error(f"Error loading plugin {plugin_info.get('name', 'unknown')}: {e}")
            return False
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin"""
        if plugin_name not in self.loaded_plugins:
            return False
        
        try:
            plugin = self.loaded_plugins[plugin_name]
            plugin.cleanup()
            self.registry.unregister_plugin(plugin_name)
            del self.loaded_plugins[plugin_name]
            
            logger.info(f"Successfully unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def reload_plugin(self, plugin_name: str) -> bool:
        """Reload a specific plugin"""
        if plugin_name in self.loaded_plugins:
            plugin_info = None
            # Find plugin info from discovered plugins
            for info in self.discover_plugins():
                if info['name'] == plugin_name:
                    plugin_info = info
                    break
            
            if plugin_info:
                self.unload_plugin(plugin_name)
                return self.load_plugin(plugin_info)
        
        return False
    
    def load_all_plugins(self) -> int:
        """Load all discovered plugins"""
        discovered = self.discover_plugins()
        loaded_count = 0
        
        for plugin_info in discovered:
            if self.load_plugin(plugin_info):
                loaded_count += 1
        
        return loaded_count
    
    def get_plugin(self, plugin_name: str) -> Optional[PluginBase]:
        """Get a loaded plugin by name"""
        return self.loaded_plugins.get(plugin_name)
    
    def get_plugins_by_type(self, plugin_type: PluginType) -> List[PluginBase]:
        """Get all loaded plugins of a specific type"""
        return [
            plugin for plugin in self.loaded_plugins.values()
            if plugin.metadata.plugin_type == plugin_type
        ]
    
    def list_plugins(self) -> Table:
        """List all loaded plugins in a rich table"""
        table = Table(title="Loaded Plugins")
        table.add_column("Name", style="cyan", no_wrap=True)
        table.add_column("Version", style="yellow")
        table.add_column("Type", style="green")
        table.add_column("Status", style="blue")
        table.add_column("Description", style="white")
        
        for plugin in self.loaded_plugins.values():
            status = "✓ Enabled" if plugin.enabled else "✗ Disabled"
            table.add_row(
                plugin.metadata.name,
                plugin.metadata.version,
                plugin.metadata.plugin_type.value,
                status,
                plugin.metadata.description[:50] + "..." if len(plugin.metadata.description) > 50 else plugin.metadata.description
            )
        
        return table
    
    def get_plugin_commands(self) -> Dict[str, Callable]:
        """Get all commands from command plugins"""
        commands = {}
        
        for plugin in self.get_plugins_by_type(PluginType.COMMAND):
            if isinstance(plugin, CommandPlugin):
                plugin_commands = plugin.get_commands()
                commands.update(plugin_commands)
        
        return commands
    
    def cleanup_all_plugins(self):
        """Cleanup all loaded plugins"""
        for plugin_name in list(self.loaded_plugins.keys()):
            self.unload_plugin(plugin_name)