"""
Plugin Registry for CodeObit CLI
Manages plugin relationships, dependencies, and metadata
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Optional, Any
from dataclasses import asdict
import logging

from .base import PluginBase, PluginType, PluginMetadata

logger = logging.getLogger(__name__)

class PluginRegistry:
    """Registry for managing plugin metadata and relationships"""
    
    def __init__(self, registry_file: Optional[Path] = None):
        if registry_file is None:
            registry_file = Path.home() / ".codeobit" / "plugin_registry.json"
        
        self.registry_file = registry_file
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory registry
        self.plugins: Dict[str, PluginMetadata] = {}
        self.dependencies: Dict[str, Set[str]] = {}
        self.dependents: Dict[str, Set[str]] = {}
        
        # Load existing registry
        self.load_registry()
    
    def load_registry(self):
        """Load plugin registry from file"""
        if not self.registry_file.exists():
            return
        
        try:
            with open(self.registry_file, 'r') as f:
                data = json.load(f)
            
            # Load plugin metadata
            for plugin_name, plugin_data in data.get('plugins', {}).items():
                metadata = PluginMetadata(
                    name=plugin_data['name'],
                    version=plugin_data['version'],
                    description=plugin_data['description'],
                    author=plugin_data['author'],
                    plugin_type=PluginType(plugin_data['plugin_type']),
                    dependencies=plugin_data.get('dependencies', []),
                    python_requires=plugin_data.get('python_requires', '>=3.11'),
                    tags=plugin_data.get('tags', []),
                    homepage=plugin_data.get('homepage', ''),
                    repository=plugin_data.get('repository', ''),
                    license=plugin_data.get('license', 'MIT'),
                    entry_point=plugin_data.get('entry_point', '')
                )
                self.plugins[plugin_name] = metadata
            
            # Load dependency relationships
            self.dependencies = {
                name: set(deps) for name, deps in data.get('dependencies', {}).items()
            }
            self.dependents = {
                name: set(deps) for name, deps in data.get('dependents', {}).items()
            }
            
        except Exception as e:
            logger.error(f"Failed to load plugin registry: {e}")
    
    def save_registry(self):
        """Save plugin registry to file"""
        try:
            data = {
                'plugins': {
                    name: {
                        **asdict(metadata),
                        'plugin_type': metadata.plugin_type.value
                    }
                    for name, metadata in self.plugins.items()
                },
                'dependencies': {
                    name: list(deps) for name, deps in self.dependencies.items()
                },
                'dependents': {
                    name: list(deps) for name, deps in self.dependents.items()
                }
            }
            
            with open(self.registry_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save plugin registry: {e}")
    
    def register_plugin(self, plugin: PluginBase):
        """Register a plugin in the registry"""
        plugin_name = plugin.metadata.name
        self.plugins[plugin_name] = plugin.metadata
        
        # Update dependency relationships
        deps = set(plugin.metadata.dependencies)
        self.dependencies[plugin_name] = deps
        
        # Update dependents for each dependency
        for dep in deps:
            if dep not in self.dependents:
                self.dependents[dep] = set()
            self.dependents[dep].add(plugin_name)
        
        self.save_registry()
        logger.info(f"Registered plugin: {plugin_name}")
    
    def unregister_plugin(self, plugin_name: str):
        """Unregister a plugin from the registry"""
        if plugin_name not in self.plugins:
            return
        
        # Remove from plugins
        del self.plugins[plugin_name]
        
        # Remove dependency relationships
        deps = self.dependencies.get(plugin_name, set())
        if plugin_name in self.dependencies:
            del self.dependencies[plugin_name]
        
        # Remove from dependents of its dependencies
        for dep in deps:
            if dep in self.dependents:
                self.dependents[dep].discard(plugin_name)
                if not self.dependents[dep]:
                    del self.dependents[dep]
        
        # Remove from dependents
        if plugin_name in self.dependents:
            del self.dependents[plugin_name]
        
        self.save_registry()
        logger.info(f"Unregistered plugin: {plugin_name}")
    
    def get_plugin_metadata(self, plugin_name: str) -> Optional[PluginMetadata]:
        """Get metadata for a specific plugin"""
        return self.plugins.get(plugin_name)
    
    def get_dependencies(self, plugin_name: str) -> Set[str]:
        """Get direct dependencies of a plugin"""
        return self.dependencies.get(plugin_name, set())
    
    def get_dependents(self, plugin_name: str) -> Set[str]:
        """Get plugins that depend on this plugin"""
        return self.dependents.get(plugin_name, set())
    
    def get_all_dependencies(self, plugin_name: str, visited: Optional[Set[str]] = None) -> Set[str]:
        """Get all dependencies (including transitive) of a plugin"""
        if visited is None:
            visited = set()
        
        if plugin_name in visited:
            # Circular dependency detected
            logger.warning(f"Circular dependency detected involving {plugin_name}")
            return set()
        
        visited.add(plugin_name)
        all_deps = set()
        
        direct_deps = self.get_dependencies(plugin_name)
        all_deps.update(direct_deps)
        
        for dep in direct_deps:
            all_deps.update(self.get_all_dependencies(dep, visited.copy()))
        
        return all_deps
    
    def get_load_order(self, plugin_names: List[str]) -> List[str]:
        """Get the correct load order for a list of plugins based on dependencies"""
        # Topological sort to resolve dependencies
        in_degree = {}
        graph = {}
        
        # Initialize
        for plugin_name in plugin_names:
            in_degree[plugin_name] = 0
            graph[plugin_name] = []
        
        # Build graph and calculate in-degrees
        for plugin_name in plugin_names:
            deps = self.get_dependencies(plugin_name)
            for dep in deps:
                if dep in plugin_names:  # Only consider dependencies in the list
                    graph[dep].append(plugin_name)
                    in_degree[plugin_name] += 1
        
        # Kahn's algorithm for topological sorting
        queue = [plugin for plugin in plugin_names if in_degree[plugin] == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for circular dependencies
        if len(result) != len(plugin_names):
            remaining = [p for p in plugin_names if p not in result]
            logger.warning(f"Circular dependencies detected among plugins: {remaining}")
            # Add remaining plugins at the end
            result.extend(remaining)
        
        return result
    
    def find_plugins_by_type(self, plugin_type: PluginType) -> List[str]:
        """Find all plugins of a specific type"""
        return [
            name for name, metadata in self.plugins.items()
            if metadata.plugin_type == plugin_type
        ]
    
    def find_plugins_by_tag(self, tag: str) -> List[str]:
        """Find all plugins with a specific tag"""
        return [
            name for name, metadata in self.plugins.items()
            if tag in metadata.tags
        ]
    
    def validate_dependencies(self, plugin_name: str) -> List[str]:
        """Validate that all dependencies of a plugin are available"""
        missing_deps = []
        deps = self.get_dependencies(plugin_name)
        
        for dep in deps:
            if dep not in self.plugins:
                missing_deps.append(dep)
        
        return missing_deps
    
    def get_registry_stats(self) -> Dict[str, Any]:
        """Get statistics about the plugin registry"""
        type_counts = {}
        for plugin_type in PluginType:
            type_counts[plugin_type.value] = len(self.find_plugins_by_type(plugin_type))
        
        return {
            'total_plugins': len(self.plugins),
            'by_type': type_counts,
            'total_dependencies': sum(len(deps) for deps in self.dependencies.values()),
            'plugins_with_deps': len([p for p in self.dependencies.values() if p])
        }
    
    def export_registry(self, export_path: Path):
        """Export registry to a different location"""
        try:
            with open(self.registry_file, 'r') as src:
                data = src.read()
            
            with open(export_path, 'w') as dst:
                dst.write(data)
                
            logger.info(f"Registry exported to {export_path}")
            
        except Exception as e:
            logger.error(f"Failed to export registry: {e}")
    
    def import_registry(self, import_path: Path, merge: bool = True):
        """Import registry from another location"""
        try:
            if not merge:
                # Clear current registry
                self.plugins.clear()
                self.dependencies.clear()
                self.dependents.clear()
            
            # Load and merge with existing registry
            with open(import_path, 'r') as f:
                data = json.load(f)
            
            # Import plugins
            for plugin_name, plugin_data in data.get('plugins', {}).items():
                metadata = PluginMetadata(
                    name=plugin_data['name'],
                    version=plugin_data['version'],
                    description=plugin_data['description'],
                    author=plugin_data['author'],
                    plugin_type=PluginType(plugin_data['plugin_type']),
                    dependencies=plugin_data.get('dependencies', []),
                    python_requires=plugin_data.get('python_requires', '>=3.11'),
                    tags=plugin_data.get('tags', []),
                    homepage=plugin_data.get('homepage', ''),
                    repository=plugin_data.get('repository', ''),
                    license=plugin_data.get('license', 'MIT'),
                    entry_point=plugin_data.get('entry_point', '')
                )
                self.plugins[plugin_name] = metadata
            
            # Import dependencies
            for name, deps in data.get('dependencies', {}).items():
                self.dependencies[name] = set(deps)
            
            # Import dependents
            for name, deps in data.get('dependents', {}).items():
                self.dependents[name] = set(deps)
            
            self.save_registry()
            logger.info(f"Registry imported from {import_path}")
            
        except Exception as e:
            logger.error(f"Failed to import registry: {e}")